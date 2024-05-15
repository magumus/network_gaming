import pygame
from network import Network

pygame.init()

width = 600
height = 800
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Space Invaders Multiplayer")

bg = pygame.image.load("img/bg.png")
spaceship_img = pygame.image.load("img/spaceship.png")
bullet_img = pygame.image.load("img/bullet.png")
alien_img = pygame.image.load("img/alien1.png")  # Tüm uzaylılar için aynı resim kullanılıyor

clock = pygame.time.Clock()
spaceship_width = 50
spaceship_height = 50

def redrawWindow(win, players, bullets, aliens):
    win.blit(bg, (0, 0))
    for player in players:
        win.blit(spaceship_img, (player.x, player.y))
    for bullet in bullets:
        win.blit(bullet_img, (bullet.x, bullet.y))
    for alien in aliens:
        win.blit(alien_img, (alien.x, alien.y))
    pygame.display.update()

def main():
    run = True
    n = Network()
    p, bullets, aliens = n.getP()
    player = pygame.Rect(p[0], p[1], spaceship_width, spaceship_height)

    while run:
        clock.tick(60)
        data = n.send((player, None))
        players = data[0]
        bullets = data[1]
        aliens = data[2]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x > 0:
            player.x -= 5
        if keys[pygame.K_RIGHT] and player.x < width - player.width:
            player.x += 5
        if keys[pygame.K_SPACE]:
            bullet = pygame.Rect(player.x + player.width // 2, player.y, 5, 10)
            bullets.append(bullet)
            n.send((player, bullet))

        for bullet in bullets:
            bullet.y -= 5
            if bullet.y < 0:
                bullets.remove(bullet)

        redrawWindow(win, players, bullets, aliens)

    pygame.quit()

if __name__ == "__main__":
    main()
