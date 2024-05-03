import pygame
import random

pygame.init()

screen=pygame.display.set_mode((800,600))
pygame.display.set_caption('Space Shooter Game')
icon=pygame.image.load('icon.png')
pygame.display.set_icon(icon)

background=pygame.image.load('bg.png')

spaceshipimg=pygame.image.load('arcade.png')

alienimg=pygame.image.load('enemy.png')
alienX=random.randint(0,736)
alienY=random.randint(30,150)
alienspeedX=2
alienspeedY=10

spaceshipX=370
spaceshipY=480
changeX=0

running=True
while running:
    screen.blit(background,(0,0))
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False

        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_LEFT:
                changeX=-3
            if event.key==pygame.K_RIGHT:
                changeX=3
        if event.type==pygame.KEYUP:
            changeX=0
    spaceshipX+=changeX

    if spaceshipX<=0:
        spaceshipX=0
    elif spaceshipX>=736:
        spaceshipX=736

    if alienX<=0:
        alienspeedX=2
        alienY+=alienspeedY
    elif alienX>=736:
        alienspeedX=-2
        alienY+=alienspeedY

    alienX+=alienspeedX
    
    screen.blit(spaceshipimg,(spaceshipX,spaceshipY))
    screen.blit(alienimg,(alienX,alienY))
    pygame.display.update()