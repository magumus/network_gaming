import pygame
import sys
import pickle
import socket
import subprocess
from host import host_game
from join import join_game
from client import run_client  # client.py dosyasından import edilen fonksiyon

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
red = (255, 0, 0)

# Yazı tipleri
font = pygame.font.SysFont('Arial', 40)
unicode_font = pygame.font.SysFont('Arial', 24)
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
        client.connect(("localhost", 5556))
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

def start_game(client, lobby):
    # Tüm oyuncuların hazır olup olmadığını kontrol et (host hariç)
    all_ready = all(player["ready"] for player in lobby["players"] if player["username"] != lobby["game"]["username"])

    if all_ready:
        # Sunucuya oyun başladığını bildirin
        send_to_lobby_server(client, ("START", {"game_name": lobby["game"]["game_name"]}))
        # Host ve ready olan oyuncular için oyunu başlat
        run_client(win)
    else:
        print("Not all players are ready.")

def lobby_screen(username, lobby, is_host, server_process=None):
    chat_font = pygame.font.SysFont('Arial', 24)
    chat_input_box = pygame.Rect(420, 660, 360, 30)
    chat_box = pygame.Rect(420, 20, 360, 620)
    chat_text = ''
    messages = []
    ready = False
    error_message = ""

    client = connect_to_lobby_server()
    if client is None:
        print("Failed to connect to the lobby server.")
        return "menu"

    run = True
    game_started = False
    while run:
        win.blit(bg, (0, 0))
        pygame.draw.line(win, grey, (400, 0), (400, 700), 2)
        draw_text(f'Username: {username}', small_font, white, win, 150, 20)
        draw_text(f'Game Name: {lobby["game"]["game_name"]}', small_font, white, win, 150, 50)

        # Get updated lobby info from server
        updated_lobbies = send_to_lobby_server(client, ("GET", None))
        if updated_lobbies:
            for updated_lobby in updated_lobbies:
                if isinstance(updated_lobby, dict) and updated_lobby["game"]["game_name"] == lobby["game"]["game_name"]:
                    lobby = updated_lobby
                    break

        # Check if the game has started
        if lobby.get("started", False):
            run_client(win)  # Oyun başladığında run_client fonksiyonunu çağır
            return "menu"

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

        pygame.draw.rect(win, white, chat_input_box, 2, border_radius=10)
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
                elif back_button.collidepoint(event.pos):
                    send_to_lobby_server(client, ("LEAVE", {"username": username, "game_name": lobby["game"]["game_name"]}))
                    return "menu"  # Join ekranına geri dön

        # Display messages
        for i, msg in enumerate(lobby["messages"]):
            message_surface = chat_font.render(msg, True, white)
            win.blit(message_surface, (chat_box.x + 5, chat_box.y + 5 + i * 30))

        if not is_host:
            ready_button = pygame.Rect(20, 660, 200, 30)
            pygame.draw.rect(win, green if ready else grey, ready_button, border_radius=10)
            draw_text('Ready' if not ready else 'Unready', small_font, white, win, ready_button.centerx, ready_button.centery)

            back_button = pygame.Rect(230, 660, 100, 30)
            pygame.draw.rect(win, red, back_button, border_radius=10)
            draw_text('Back', small_font, white, win, back_button.centerx, back_button.centery)
        else:
            play_button = pygame.Rect(20, 660, 200, 30)
            pygame.draw.rect(win, grey, play_button, border_radius=10)
            draw_text('Play', small_font, white, win, play_button.centerx, play_button.centery)

            if play_button.collidepoint(pygame.mouse.get_pos()):
                if pygame.mouse.get_pressed()[0]:
                    # Sunucudan güncellenmiş lobi durumunu al
                    updated_lobbies = send_to_lobby_server(client, ("GET", None))
                    if updated_lobbies:
                        for updated_lobby in updated_lobbies:
                            if isinstance(updated_lobby, dict) and updated_lobby["game"]["game_name"] == lobby["game"]["game_name"]:
                                lobby = updated_lobby
                                break
                    if all(player["ready"] for player in lobby["players"] if player["username"] != lobby["game"]["username"]):
                        start_game(client, lobby)
                    else:
                        error_message = "Not all players are ready."

            back_button = pygame.Rect(230, 660, 100, 30)
            pygame.draw.rect(win, red, back_button, border_radius=10)
            draw_text('Back', small_font, white, win, back_button.centerx, back_button.centery)
            
            if back_button.collidepoint(pygame.mouse.get_pos()):
                if pygame.mouse.get_pressed()[0]:
                    send_to_lobby_server(client, ("REMOVE", {"game_name": lobby["game"]["game_name"]}))
                    if server_process:
                        server_process.terminate()  # Server'ı kapat
                    return "menu"  # Ana menüye geri dön

        if error_message:
            draw_text(error_message, small_font, red, win, width // 2, height - 30)

        pygame.display.update()

    # Game started, clear screen and start client.py
    win.fill(black)
    pygame.display.update()

def about_screen():
    while True:
        win.blit(bg, (0, 0))
        draw_text('Hakkımızda', font, white, win, width // 2, height // 4)

        names = ["Ömer Faruk", "Faruk", "Gümüş", "Anıl", "Burak"]
        for i, name in enumerate(names):
            draw_text(name, small_font, white, win, width // 2, height // 2 - 60 + i * 40)
        
        back_button = pygame.Rect(width // 2 - 50, height - 100, 100, 50)
        draw_button('Back', small_font, white, win, back_button, red)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    return  # Ana menüye geri dön

def main_menu():
    while True:
        win.blit(bg, (0, 0))
        draw_text('Space Invaders Multiplayer', font, white, win, width // 2, height // 4)

        mx, my = pygame.mouse.get_pos()

        button_1 = pygame.Rect(width // 2 - 100, height // 2 - 60, 200, 50)
        button_2 = pygame.Rect(width // 2 - 100, height // 2, 200, 50)
        button_3 = pygame.Rect(width // 2 - 100, height // 2 + 60, 200, 50)
        button_4 = pygame.Rect(width // 2 - 100, height // 2 + 120, 200, 50)


        draw_button('Host', font, white, win, button_1, grey)
        draw_button('Join', font, white, win, button_2, grey)
        draw_button('About', font, white, win, button_3, grey)
        draw_button('Exit', font, white, win, button_4, grey)

        if button_1.collidepoint((mx, my)):
            if pygame.mouse.get_pressed()[0]:
                result = host_game(win)
                if result:
                    username, game_name, server_process = result
                    next_screen = lobby_screen(username, {"game": {"game_name": game_name}, "players": [{"username": username, "ready": False}], "messages": []}, True, server_process)
                    if next_screen == "menu":
                        continue  # Ana menüye dön

        if button_2.collidepoint((mx, my)):
            if pygame.mouse.get_pressed()[0]:
                result = join_game(win)
                if result:
                    username, lobby = result
                    next_screen = lobby_screen(username, lobby, False)
                    if next_screen == "menu":
                        continue  # Ana menüye dön
        if button_3.collidepoint((mx, my)):
            if pygame.mouse.get_pressed()[0]:
                about_screen()
        if button_4.collidepoint((mx, my)):
            if pygame.mouse.get_pressed()[0]:
                pygame.quit()
                sys.exit()
            

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

if __name__ == "__main__":
    # Lobby server'ı başlat
    lobby_server_process = subprocess.Popen([sys.executable, "lobby_server.py"])
    
    main_menu()
    
    # Program kapatıldığında lobby server'ı durdur
    lobby_server_process.terminate()
