import pickle
import socket
import subprocess
import pygame
import sys
from host import host_game
from join import join_game

pygame.init()

# Ekran boyutları ve pencere başlığı
width = 800
height = 700
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Space Invaders Multiplayer")

# Renk tanımlamaları
white = (255, 255, 255)
black = (0, 0, 0)
grey = (100, 100, 100)
green = (0, 255, 0)

# Yazı tipleri
font = pygame.font.SysFont('Arial', 40)
small_font = pygame.font.SysFont('Arial', 24)

def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_obj, text_rect)

def connect_to_lobby_server():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("localhost", 5556))
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

def start_game(client, lobby):
    send_to_lobby_server(client, ("START", {"game_name": lobby["game"]["game_name"]}))

def lobby_screen(username, lobby, is_host):
    chat_font = pygame.font.SysFont('Arial', 24)
    chat_input_box = pygame.Rect(420, 660, 360, 30)
    chat_box = pygame.Rect(420, 20, 360, 620)
    chat_text = ''
    messages = []
    ready = False

    client = connect_to_lobby_server()

    run = True
    while run:
        win.fill(black)
        pygame.draw.line(win, grey, (400, 0), (400, 700), 2)
        draw_text(f'Username: {username}', small_font, white, win, 150, 20)
        draw_text(f'Game Name: {lobby["game"]["game_name"]}', small_font, white, win, 150, 50)

        # Get updated lobby info from server
        updated_lobby = send_to_lobby_server(client, ("GET", None))
        if updated_lobby:
            for updated in updated_lobby:
                if updated["game"]["game_name"] == lobby["game"]["game_name"]:
                    lobby = updated
                    break

        # Debugging: Print the current state of players
        print(f"Players: {lobby['players']}")

        for i, player in enumerate(lobby["players"]):
            if isinstance(player, dict):
                player_text = player["username"]
                if player["ready"]:
                    player_text += " ✓"
                draw_text(player_text, small_font, white, win, 150, 80 + i * 30)
            else:
                print(f"Invalid player data: {player}")

        pygame.draw.rect(win, white, chat_input_box, 2)
        chat_surf = chat_font.render(chat_text, True, white)
        win.blit(chat_surf, (chat_input_box.x + 5, chat_input_box.y + 5))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                send_to_lobby_server(client, ("LEAVE", {"username": username, "game_name": lobby["game"]["game_name"]}))
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if chat_text:
                        messages.append((username, chat_text))
                        send_to_lobby_server(client, ("MESSAGE", {"game_name": lobby["game"]["game_name"], "message": f"{username}: {chat_text}"}))
                        chat_text = ''
                elif event.key == pygame.K_BACKSPACE:
                    chat_text = chat_text[:-1]
                else:
                    chat_text += event.unicode
            if not is_host and event.type == pygame.MOUSEBUTTONDOWN:
                if ready_button.collidepoint(event.pos):
                    ready = not ready
                    send_to_lobby_server(client, ("READY", {"username": username, "game_name": lobby["game"]["game_name"], "ready": ready}))

        # Display messages
        for i, msg in enumerate(lobby["messages"]):
            message_surface = chat_font.render(msg, True, white)
            win.blit(message_surface, (chat_box.x + 5, chat_box.y + 5 + i * 30))

        if not is_host:
            ready_button = pygame.Rect(20, 660, 200, 30)
            pygame.draw.rect(win, green if ready else grey, ready_button)
            draw_text('Ready' if not ready else 'Unready', small_font, white, win, ready_button.centerx, ready_button.centery)
        else:
            play_button = pygame.Rect(20, 660, 200, 30)
            pygame.draw.rect(win, grey, play_button)
            draw_text('Play', small_font, white, win, play_button.centerx, play_button.centery)

            if play_button.collidepoint(pygame.mouse.get_pos()):
                if pygame.mouse.get_pressed()[0]:
                    start_game(client, lobby)

        if lobby.get("started", False):
            run = False

        pygame.display.update()

    game_loop(win, username)

def game_loop(win, username):
    run = True
    while run:
        win.fill(black)
        draw_text('Game started!', font, white, win, width // 2, height // 2)
        draw_text(f'Player: {username}', small_font, white, win, width // 2, height // 2 + 40)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        pygame.display.update()

def main_menu():
    while True:
        win.fill(black)
        draw_text('Space Invaders Multiplayer', font, white, win, width // 2, height // 4)

        mx, my = pygame.mouse.get_pos()

        button_1 = pygame.Rect(width // 2 - 100, height // 2 - 60, 200, 50)
        button_2 = pygame.Rect(width // 2 - 100, height // 2, 200, 50)
        button_3 = pygame.Rect(width // 2 - 100, height // 2 + 60, 200, 50)
        button_4 = pygame.Rect(width // 2 - 100, height // 2 + 120, 200, 50)

        if button_1.collidepoint((mx, my)):
            if pygame.mouse.get_pressed()[0]:
                pass  # client.py başlatılır (oyun oynama kısmı)
        if button_2.collidepoint((mx, my)):
            if pygame.mouse.get_pressed()[0]:
                username, game_name = host_game(win)
                lobby_screen(username, {"game": {"game_name": game_name}, "players": [{"username": username, "ready": False}], "messages": []}, True)
        if button_3.collidepoint((mx, my)):
            if pygame.mouse.get_pressed()[0]:
                result = join_game(win)
                if result:
                    username, lobby = result
                    lobby_screen(username, lobby, False)
        if button_4.collidepoint((mx, my)):
            if pygame.mouse.get_pressed()[0]:
                pygame.quit()
                sys.exit()

        pygame.draw.rect(win, grey, button_1)
        pygame.draw.rect(win, grey, button_2)
        pygame.draw.rect(win, grey, button_3)
        pygame.draw.rect(win, grey, button_4)

        draw_text('Play', font, white, win, width // 2, height // 2 - 35)
        draw_text('Host', font, white, win, width // 2, height // 2 + 25)
        draw_text('Join', font, white, win, width // 2, height // 2 + 85)
        draw_text('Exit', font, white, win, width // 2, height // 2 + 145)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

if __name__ == "__main__":
    main_menu()
