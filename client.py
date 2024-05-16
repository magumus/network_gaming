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

def redrawWindow(win, players, bullets, aliens, player_health, alien_bullets, scores, game_over):
    win.blit(bg, (0, 0))
    if game_over:
        draw_game_over(win, scores)
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
    pygame.display.update()

def main():
    run = True
    n = Network()
    p, bullets, aliens, player_health, alien_bullets, scores, game_over = n.getP()
    player = pygame.Rect(p[0], p[1], spaceship_width, spaceship_height)
    global last_bullet_shot

    while run:
        clock.tick(60)
        data = n.send((player, None))
        players = data[0]
        bullets = data[1]
        aliens = data[2]
        player_health = data[3]
        alien_bullets = data[4]
        scores = data[5]
        game_over = data[6]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x > 0:
            player.x -= 5
        if keys[pygame.K_RIGHT] and player.x < width - player.width:
            player.x += 5
        if keys[pygame.K_SPACE] and not game_over:  # Only allow shooting if the game is not over
            time_now = pygame.time.get_ticks()
            if time_now - last_bullet_shot > bullet_cooldown:
                bullet = pygame.Rect(player.x + player.width // 2, player.y, 5, 10)
                n.send((player, bullet))
                last_bullet_shot = time_now

        redrawWindow(win, players, bullets, aliens, player_health, alien_bullets, scores, game_over)

    pygame.quit()

if __name__ == "__main__":
    main()
