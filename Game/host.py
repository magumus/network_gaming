import pygame
import socket
import subprocess
import sys
import pickle

lobby_server_address = ("localhost", 5556)

pygame.init()

# Ekran boyutları ve pencere başlığı
width = 800
height = 700
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Host Game")

# Renk tanımlamaları
white = (255, 255, 255)
black = (0, 0, 0)
grey = (100, 100, 100)
green = (0, 255, 0)
red = (255, 0, 0)

# Yazı tipleri
font = pygame.font.SysFont('Arial', 40)
small_font = pygame.font.SysFont('Arial', 24)

# Arka plan resmi
bg = pygame.image.load("img/bg.png")

def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_obj, text_rect)

def draw_button(text, font, color, surface, rect, bg_color):
    pygame.draw.rect(surface, bg_color, rect, border_radius=10)
    draw_text(text, font, color, surface, rect.centerx, rect.centery)

def connect_to_lobby_server():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(lobby_server_address)
        print("connect_to_lobby_server: Connection established")  # Debug message
        return client
    except socket.error as e:
        print(f"connect_to_lobby_server: Connection error: {e}")  # Debug message
        return None

def send_to_lobby_server(client, data):
    if client is None:
        print("send_to_lobby_server: No connection to server.")
        return None
    try:
        print(f"send_to_lobby_server: Sending data to server: {data}")  # Debug message
        client.send(pickle.dumps(data))
        client.settimeout(5.0)  # Set a timeout for the response
        response = pickle.loads(client.recv(4096))
        client.settimeout(None)  # Reset timeout after successful receive
        print(f"send_to_lobby_server: Received response from server: {response}")  # Debug message
        return response
    except socket.timeout:
        print("send_to_lobby_server: Request timed out.")  # Debug message
        return None
    except socket.error as e:
        print(f"send_to_lobby_server: Socket error: {e}")  # Debug message
        return None

def host_game(win):
    username = ""
    game_name = ""
    input_active = "username"
    
    while True:
        win.blit(bg, (0, 0))
        draw_text('Enter Username:', small_font, white, win, width // 2, height // 2 - 100)
        draw_text('Enter Game Name:', small_font, white, win, width // 2, height // 2)
        
        username_rect = pygame.Rect(width // 2 - 100, height // 2 - 80, 200, 40)
        game_name_rect = pygame.Rect(width // 2 - 100, height // 2 + 20, 200, 40)
        enter_button = pygame.Rect(width // 2 - 50, height // 2 + 100, 100, 50)

        pygame.draw.rect(win, grey, username_rect, border_radius=10)
        pygame.draw.rect(win, grey, game_name_rect, border_radius=10)
        draw_button('Enter', small_font, white, win, enter_button, grey)

        draw_text(username, small_font, white, win, username_rect.centerx, username_rect.centery)
        draw_text(game_name, small_font, white, win, game_name_rect.centerx, game_name_rect.centery)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if username_rect.collidepoint(event.pos):
                    input_active = "username"
                elif game_name_rect.collidepoint(event.pos):
                    input_active = "game_name"
                elif enter_button.collidepoint(event.pos):
                    if username and game_name:
                        client = connect_to_lobby_server()
                        if client:
                            send_to_lobby_server(client, ("ADD", {"username": username, "game_name": game_name}))
                            server_process = subprocess.Popen([sys.executable, "server.py"])  # Sunucuyu başlat
                            return username, game_name, server_process
            if event.type == pygame.KEYDOWN:
                if input_active == "username":
                    if event.key == pygame.K_BACKSPACE:
                        username = username[:-1]
                    else:
                        username += event.unicode
                elif input_active == "game_name":
                    if event.key == pygame.K_BACKSPACE:
                        game_name = game_name[:-1]
                    else:
                        game_name += event.unicode

if __name__ == "__main__":
    host_game(win)
