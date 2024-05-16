import socket
from _thread import *
import pickle
import pygame
import random

server = "localhost"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen(2)
print("Waiting for a connection, Server Started")

# Define game variables
rows = 4
cols = 7
alien_cooldown = 500  # bullet cooldown in milliseconds
last_alien_shot = pygame.time.get_ticks()
players = [pygame.Rect(200, 600, 50, 50), pygame.Rect(400, 600, 50, 50)]  # y koordinatlarını 500'den 600'e değiştirdik
player_health = [3, 3]  # Each player has 3 health points
bullets = []  # Changed to store (bullet, player_index) tuples
alien_bullets = []  # Alien bullets list
aliens = []
alien_direction = 1  # Alien movement direction
scores = [0, 0]  # Skorları tutan liste
game_over = False  # Oyunun bitip bitmediğini belirten değişken

# Create aliens
def create_aliens():
    for row in range(rows):
        for item in range(cols):
            alien = pygame.Rect(100 + item * 80, 100 + row * 80, 40, 40)  # Aralarındaki boşluğu artırdık
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
    conn.send(pickle.dumps((players[player], bullets, aliens, player_health, alien_bullets, scores, game_over)))
    reply = ""
    while True:
        try:
            data = pickle.loads(conn.recv(2048))
            players[player] = data[0]
            if data[1] is not None:
                bullets.append((data[1], player))  # Store bullet with player index

            if not data:
                print("Disconnected")
                break
            else:
                # Alien shooting logic
                time_now = pygame.time.get_ticks()
                if time_now - last_alien_shot > alien_cooldown and len(aliens) > 0:
                    attacking_alien = random.choice(aliens)
                    alien_bullet = pygame.Rect(attacking_alien.x + attacking_alien.width // 2, attacking_alien.y + attacking_alien.height, 5, 10)
                    alien_bullets.append(alien_bullet)
                    last_alien_shot = time_now

                # Update bullets
                for bullet, bullet_player in bullets[:]:
                    bullet.y -= 3  # Bullet speed reduced from 5 to 3
                    if bullet.y < 0:
                        bullets.remove((bullet, bullet_player))
                    else:
                        for alien in aliens:
                            if bullet.colliderect(alien):
                                bullets.remove((bullet, bullet_player))
                                aliens.remove(alien)
                                scores[bullet_player] += 1  # Skoru ilgili oyuncuya artır
                                if len(aliens) == 0:  # Tüm uzaylılar vuruldu
                                    game_over = True
                                break

                # Update alien bullets
                for alien_bullet in alien_bullets[:]:
                    alien_bullet.y += 5  # Alien bullet speed increased
                    if alien_bullet.y > 800:
                        alien_bullets.remove(alien_bullet)
                    else:
                        for i, player_rect in enumerate(players):
                            if alien_bullet.colliderect(player_rect):
                                alien_bullets.remove(alien_bullet)
                                player_health[i] -= 1
                                if player_health[i] <= 0:
                                    players[i] = pygame.Rect(-100, -100, 0, 0)  # Remove player from screen
                                    print(f"Player {i+1} has been destroyed!")

                # Update aliens
                move_aliens()

                # Send updated game state to client
                reply = (players, bullets, aliens, player_health, alien_bullets, scores, game_over)
                print("Received: ", data)
                print("Sending : ", reply)

            conn.sendall(pickle.dumps(reply))
        except:
            break

    print("Lost connection")
    conn.close()

currentPlayer = 0
while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    start_new_thread(threaded_client, (conn, currentPlayer))
    currentPlayer += 1
