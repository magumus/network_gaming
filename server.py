import socket
from _thread import *
import pickle
import pygame
import random
import pika

server = "localhost"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen(2)
print("Waiting for a connection, Server Started")

# RabbitMQ bağlantısını oluştur
try:
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='game_queue')
except pika.exceptions.AMQPConnectionError as e:
    print(f"RabbitMQ Connection Error: {e}")
    exit()

rows = 4
cols = 7
alien_cooldown = 500
last_alien_shot = pygame.time.get_ticks()
players = [pygame.Rect(200, 600, 50, 50), pygame.Rect(400, 600, 50, 50)]
player_health = [3, 3]
bullets = []
alien_bullets = []
aliens = []
alien_direction = 1
scores = [0, 0]
game_over = False
chat_messages = []
player_names = ["", ""]

def create_aliens():
    for row in range(rows):
        for item in range(cols):
            alien = pygame.Rect(100 + item * 80, 100 + row * 80, 40, 40)
            aliens.append(alien)

create_aliens()

def move_aliens():
    global alien_direction
    for alien in aliens:
        alien.x += alien_direction
        if alien.x >= 760 or alien.x <= 0:
            alien_direction *= -1
            break

def threaded_client(conn, player):
    global last_alien_shot, game_over
    try:
        conn.send(pickle.dumps((players[player], bullets, aliens, player_health, alien_bullets, scores, game_over, chat_messages, player_names)))
    except IndexError:
        print(f"Player index {player} out of range.")
        conn.close()
        return

    reply = ""
    while True:
        try:
            data = conn.recv(2048)
            if not data:
                print("Disconnected")
                break
            else:
                try:
                    data = pickle.loads(data)
                except (pickle.UnpicklingError, EOFError) as e:
                    print(f"Data unpickling error: {e}")
                    continue

                if player < len(players):
                    players[player] = data[0]
                if data[1] is not None:
                    bullets.append((data[1], player))
                if data[2] is not None:
                    chat_messages.append(data[2])
                if data[3] is not None:
                    player_names[player] = data[3]

                time_now = pygame.time.get_ticks()
                if time_now - last_alien_shot > alien_cooldown and len(aliens) > 0:
                    attacking_alien = random.choice(aliens)
                    alien_bullet = pygame.Rect(attacking_alien.x + attacking_alien.width // 2, attacking_alien.y + attacking_alien.height, 5, 10)
                    alien_bullets.append(alien_bullet)
                    last_alien_shot = time_now

                for bullet, bullet_player in bullets[:]:
                    bullet.y -= 3
                    if bullet.y < 0:
                        bullets.remove((bullet, bullet_player))
                    else:
                        for alien in aliens:
                            if bullet.colliderect(alien):
                                bullets.remove((bullet, bullet_player))
                                aliens.remove(alien)
                                scores[bullet_player] += 1
                                if len(aliens) == 0:
                                    game_over = True
                                break

                for alien_bullet in alien_bullets[:]:
                    alien_bullet.y += 5
                    if alien_bullet.y > 800:
                        alien_bullets.remove(alien_bullet)
                    else:
                        for i, player_rect in enumerate(players):
                            if alien_bullet.colliderect(player_rect):
                                alien_bullets.remove(alien_bullet)
                                player_health[i] -= 1
                                if player_health[i] <= 0:
                                    players[i] = pygame.Rect(-100, -100, 0, 0)
                                    print(f"Player {i+1} has been destroyed!")

                move_aliens()

                reply = (players, bullets, aliens, player_health, alien_bullets, scores, game_over, chat_messages, player_names)
                channel.basic_publish(exchange='', routing_key='game_queue', body=pickle.dumps(reply))
                print("Received: ", data)
                print("Sending : ", reply)

            conn.sendall(pickle.dumps(reply))
        except Exception as e:
            print(f"Error: {e}")
            break

    print("Lost connection")
    conn.close()

currentPlayer = 0
while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    start_new_thread(threaded_client, (conn, currentPlayer))
    currentPlayer += 1
