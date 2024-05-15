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
rows = 5
cols = 5
alien_cooldown = 1000  # bullet cooldown in milliseconds
last_alien_shot = pygame.time.get_ticks()
players = [pygame.Rect(200, 500, 50, 50), pygame.Rect(400, 500, 50, 50)]
bullets = []
aliens = []
alien_direction = 1  # Alien movement direction

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
        if alien.x >= 560 or alien.x <= 0:
            alien_direction *= -1
            break

def threaded_client(conn, player):
    global last_alien_shot
    conn.send(pickle.dumps((players[player], bullets, aliens)))
    reply = ""
    while True:
        try:
            data = pickle.loads(conn.recv(2048))
            players[player] = data[0]
            if data[1] is not None:
                bullets.append(data[1])

            if not data:
                print("Disconnected")
                break
            else:
                # Alien shooting logic
                time_now = pygame.time.get_ticks()
                if time_now - last_alien_shot > alien_cooldown and len(aliens) > 0:
                    attacking_alien = random.choice(aliens)
                    alien_bullet = pygame.Rect(attacking_alien.x + attacking_alien.width // 2, attacking_alien.y + attacking_alien.height, 5, 10)
                    bullets.append(alien_bullet)
                    last_alien_shot = time_now

                # Update aliens
                move_aliens()

                # Send updated game state to client
                reply = (players, bullets, aliens)
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
