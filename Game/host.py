import socket
from cgitb import grey
import subprocess
import pygame
import pickle
import sys

lobby_server_address = ("localhost", 5556)

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
    pygame.init()
    width = 800
    height = 700

    white = (255, 255, 255)
    black = (0, 0, 0)
    font = pygame.font.SysFont('Arial', 40)
    small_font = pygame.font.SysFont('Arial', 24)

    def draw_text(text, font, color, surface, x, y):
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect()
        text_rect.center = (x, y)
        surface.blit(text_obj, text_rect)

    def input_text_box(surface, font, box, text):
        pygame.draw.rect(surface, white, box, 2)
        text_surf = font.render(text, True, white)
        surface.blit(text_surf, (box.x + 5, box.y + 5))

    input_box_user = pygame.Rect(width // 2 - 100, height // 2 - 60, 200, 50)
    input_box_game = pygame.Rect(width // 2 - 100, height // 2, 200, 50)
    user_text = ''
    game_text = ''
    active_box = None
    run = True

    while run:
        win.fill(black)
        draw_text('Enter Username and Game Name', font, white, win, width // 2, height // 4)

        draw_text('Username:', small_font, white, win, width // 2 - 150, height // 2 - 35)
        draw_text('Game Name:', small_font, white, win, width // 2 - 150, height // 2 + 25)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box_user.collidepoint(event.pos):
                    active_box = 'user'
                elif input_box_game.collidepoint(event.pos):
                    active_box = 'game'
                else:
                    active_box = None
            if event.type == pygame.KEYDOWN:
                if active_box == 'user':
                    if event.key == pygame.K_RETURN:
                        active_box = 'game'
                    elif event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                    else:
                        user_text += event.unicode
                elif active_box == 'game':
                    if event.key == pygame.K_RETURN:
                        run = False
                    elif event.key == pygame.K_BACKSPACE:
                        game_text = game_text[:-1]
                    else:
                        game_text += event.unicode

        input_text_box(win, small_font, input_box_user, user_text)
        input_text_box(win, small_font, input_box_game, game_text)

        pygame.display.update()

    client = connect_to_lobby_server()
    if client:
        send_to_lobby_server(client, ("ADD", {"username": user_text, "game_name": game_text}))
        subprocess.Popen([sys.executable, "server.py"])  # Sunucuyu başlat
    return user_text, game_text

if __name__ == "__main__":
    host_game(pygame.display.set_mode((800, 700)))
