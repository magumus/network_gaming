import socket
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

def join_to_lobby_server(client, data):
    try:
        print(f"join_to_lobby_server: Sending data to server: {data}")  # Debug message
        client.send(pickle.dumps(data))
        client.settimeout(5.0)  # Set a timeout for the response
        response = pickle.loads(client.recv(4096))
        client.settimeout(None)  # Reset timeout after successful receive
        print(f"join_to_lobby_server: Received response from server: {response}")  # Debug message
        return response
    except socket.timeout:
        print("join_to_lobby_server: Request timed out.")  # Debug message
        return None
    except socket.error as e:
        print(f"join_to_lobby_server: Socket error: {e}")  # Debug message
        return None

def join_game(win):
    width = 800
    height = 700

    white = (255, 255, 255)
    black = (0, 0, 0)
    grey = (100, 100, 100)
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

    input_box_user = pygame.Rect(width // 2 - 100, height // 2 - 30, 200, 50)
    user_text = ''
    active_box = None
    run = True
    no_lobbies_message = ''

    print("join_game: Starting the join game process")  # Debug message

    while run:
        win.fill(black)
        draw_text('Enter Username', font, white, win, width // 2, height // 4)

        draw_text('Username:', small_font, white, win, width // 2 - 150, height // 2 - 5)

        if no_lobbies_message:
            draw_text(no_lobbies_message, small_font, white, win, width // 2, height // 2 + 100)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box_user.collidepoint(event.pos):
                    active_box = 'user'
                else:
                    active_box = None
            if event.type == pygame.KEYDOWN:
                if active_box == 'user':
                    if event.key == pygame.K_RETURN:
                        run = False
                    elif event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                    else:
                        user_text += event.unicode

        input_text_box(win, small_font, input_box_user, user_text)

        pygame.display.update()

    print(f"join_game: Username entered: {user_text}")  # Debug message

    client = connect_to_lobby_server()
    if client:
        lobbies = join_to_lobby_server(client, ("GET", None))
    else:
        lobbies = []

    print(f"join_game: Lobbies received: {lobbies}")  # Debug message

    if not lobbies:
        no_lobbies_message = "No lobbies available. Please try again later."
        run = True

    selected_lobby = None
    while selected_lobby is None:
        win.fill(black)
        draw_text('Select a Game to Join', font, white, win, width // 2, height // 4)

        if no_lobbies_message:
            draw_text(no_lobbies_message, small_font, white, win, width // 2, height // 2 + 100)

        for i, lobby in enumerate(lobbies):
            lobby_rect = pygame.Rect(width // 2 - 100, height // 2 - 30 + i * 60, 200, 50)
            pygame.draw.rect(win, grey, lobby_rect)
            draw_text(f"{lobby['game']['game_name']} by {lobby['game']['username']}", small_font, white, win, width // 2, height // 2 - 5 + i * 60)
            if lobby_rect.collidepoint(pygame.mouse.get_pos()):
                if pygame.mouse.get_pressed()[0]:
                    selected_lobby = lobby
                    print(f"join_game: Lobby selected: {selected_lobby}")  # Debug message
                    response = join_to_lobby_server(client, ("JOIN", {"username": user_text, "game_name": lobby['game']['game_name']}))
                    if response is None:
                        selected_lobby = None  # Retry joining if failed

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box_user.collidepoint(event.pos):
                    active_box = 'user'
                else:
                    active_box = None

        pygame.display.update()

    print(f"join_game: Successfully joined lobby: {selected_lobby}")  # Debug message

    return user_text, selected_lobby

if __name__ == "__main__":
    join_game(pygame.display.set_mode((800, 700)))
