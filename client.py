import pygame
from network import Network

pygame.init()

width = 800
height = 700
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Space Invaders Multiplayer")

bg = pygame.image.load("img/bg.png")
spaceship_img = pygame.image.load("img/spaceship.png")
bullet_img = pygame.image.load("img/bullet.png")
alien_img = pygame.image.load("img/alien1.png")  # Tüm uzaylılar için aynı resim kullanılıyor

clock = pygame.time.Clock()
spaceship_width = 50
spaceship_height = 50

# Fire cooldown
bullet_cooldown = 500  # milliseconds
last_bullet_shot = pygame.time.get_ticks()

def draw_scores(win, scores):
    font = pygame.font.SysFont('Arial', 24)
    score_text1 = font.render(f"Player 1: {scores[0]}", True, (255, 255, 255))
    score_text2 = font.render(f"Player 2: {scores[1]}", True, (255, 255, 255))
    win.blit(score_text1, (10, 10))
    win.blit(score_text2, (width - score_text2.get_width() - 10, 10))

def draw_game_over(win, scores):
    font = pygame.font.SysFont('Arial', 48)
    if scores[0] > scores[1]:
        winner_text = "Game Over! Player 1 Wins!"
    elif scores[1] > scores[0]:
        winner_text = "Game Over! Player 2 Wins!"
    else:
        winner_text = "Game Over! It's a Tie!"
    text = font.render(winner_text, True, (255, 255, 255))
    win.blit(text, ((width - text.get_width()) // 2, height // 2))
    
    back_button = pygame.Rect(width // 2 - 50, height // 2 + 60, 100, 50)
    pygame.draw.rect(win, (255, 0, 0), back_button, border_radius=10)
    draw_text('Back', font, (255, 255, 255), win, back_button.centerx, back_button.centery)

    return back_button

def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_obj, text_rect)

def redrawWindow(win, players, bullets, aliens, player_health, alien_bullets, scores, game_over, chat_messages, player_names):
    win.blit(bg, (0, 0))
    if game_over:
        back_button = draw_game_over(win, scores)
        return back_button
    else:
        for i, player in enumerate(players):
            if player_health[i] > 0:  # Only draw if the player is alive
                win.blit(spaceship_img, (player.x, player.y))
        for bullet, _ in bullets:  # Unpack tuple to get bullet
            win.blit(bullet_img, (bullet.x, bullet.y))
        for alien_bullet in alien_bullets:
            pygame.draw.rect(win, (255, 0, 0), alien_bullet)  # Draw alien bullets as red rectangles
        for alien in aliens:
            win.blit(alien_img, (alien.x, alien.y))
        draw_scores(win, scores)
        
        # Draw player names
        for i, player_name in enumerate(player_names):
            font = pygame.font.SysFont('Arial', 24)
            player_text = font.render(player_name, True, (255, 255, 255))
            win.blit(player_text, (10, 40 + i * 30))
        
        # Draw chat messages
        for i, msg in enumerate(chat_messages):
            font = pygame.font.SysFont('Arial', 18)
            msg_text = font.render(msg, True, (255, 255, 255))
            win.blit(msg_text, (10, 80 + i * 20))
    
    pygame.display.update()
    return None

def run_client(win):
    run = True
    n = Network()
    initial_data = n.getP()

    if initial_data is None:
        print("Failed to connect to the server.")
        return  # Bağlantı başarısız olursa ana menüye dön

    p, bullets, aliens, player_health, alien_bullets, scores, game_over, chat_messages, player_names = initial_data
    player = pygame.Rect(p[0], p[1], spaceship_width, spaceship_height)
    global last_bullet_shot

    chat_input_box = pygame.Rect(10, 650, 780, 40)
    chat_text = ''

    while run:
        clock.tick(60)
        data = n.send((player, None, None, None))
        players, bullets, aliens, player_health, alien_bullets, scores, game_over, chat_messages, player_names = data

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if chat_text != '':
                        n.send((player, None, f"{player_names[n.p]}: {chat_text}", None))
                        chat_text = ''
                elif event.key == pygame.K_BACKSPACE:
                    chat_text = chat_text[:-1]
                else:
                    chat_text += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN and game_over:
                back_button = draw_game_over(win, scores)
                if back_button.collidepoint(event.pos):
                    return  # Ana menüye geri dön

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x > 0:
            player.x -= 5
        if keys[pygame.K_RIGHT] and player.x < width - player.width:
            player.x += 5
        if keys[pygame.K_SPACE] and not game_over:  # Only allow shooting if the game is not over
            time_now = pygame.time.get_ticks()
            if time_now - last_bullet_shot > bullet_cooldown:
                bullet = pygame.Rect(player.x + player.width // 2, player.y, 5, 10)
                n.send((player, bullet, None, None))
                last_bullet_shot = time_now

        back_button = redrawWindow(win, players, bullets, aliens, player_health, alien_bullets, scores, game_over, chat_messages, player_names)
        if game_over and back_button:
            if back_button.collidepoint(pygame.mouse.get_pos()):
                if pygame.mouse.get_pressed()[0]:
                    return  # Ana menüye geri dön
    
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    run_client(win)
