import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from shared.settings import *
from shared.entities.bird import Bird
from shared.entities.pipe import Pipe

#start
pygame.init()
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption(gameTitle)
clock = pygame.time.Clock()

def reset(): #retrying
    return Bird(screenHeight // 2), [], False, False, 0

bird, pipes, gameStart, gameOver, score = reset()

bird = Bird(screenHeight // 2)
pipes = []
gameStart = False
gameOver = False
deathPlayed = False

#assets
backgroundImg = pygame.image.load(os.path.join(sprites, "background-night.png")).convert()
backgroundImg = pygame.transform.scale(backgroundImg, (screenWidth, screenHeight))

floorImg = pygame.image.load(os.path.join(sprites, "base.png")).convert_alpha()
floorImg = pygame.transform.scale(floorImg, (screenWidth, floorHeight))

birdImg = pygame.image.load(os.path.join(sprites, "redbird-upflap.png")).convert_alpha()
birdImg = pygame.transform.scale(birdImg, (birdWidth, birdHeight))

pipeImg = pygame.image.load(os.path.join(sprites, "pipe-green.png")).convert_alpha()
pipeImg = pygame.transform.scale(pipeImg, (pipeWidth, pipeImgHeight))
pipeTopImg = pygame.transform.flip(pipeImg, False, True)

digitImg = [pygame.image.load(os.path.join(sprites, f"{i}.png")).convert_alpha() for i in range(10)]

gameOverImg = pygame.image.load(os.path.join(sprites, "gameover.png")).convert_alpha()
messageImg = pygame.image.load(os.path.join(sprites, "message.png")).convert_alpha()
messageAlpha = 255

#sounds
wingSound = pygame.mixer.Sound(os.path.join(audio, "wing.wav"))
pointSound = pygame.mixer.Sound(os.path.join(audio, "point.wav"))
hitSound = pygame.mixer.Sound(os.path.join(audio, "hit.wav"))
dieSound = pygame.mixer.Sound(os.path.join(audio, "die.wav"))
swooshSound = pygame.mixer.Sound(os.path.join(audio, "swoosh.wav"))

def drawScore(screen, score):
    scoreString = str(score)
    totalWidth = sum(digitImg[int(digit)].get_width() for digit in scoreString)
    x = screenWidth // 2 - totalWidth - 2

    for digit in scoreString:
        image = digitImg[int(digit)]
        screen.blit(image, (x, 80))
        x += image.get_width()

#game loop
running = True
while running:

    #input
    for event in pygame.event.get():

        #quitting the game
        if event.type == pygame.QUIT:
            running = False

        #bird control
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if gameOver:
                    bird, pipes, gameStart, gameOver, score = reset()
                    deathPlayed = False
                    swooshSound.play()
                    messageAlpha = 255
                else:
                    gameStart = True
                    bird.jump()
                    wingSound.play()

    #update (when the game starts)
    if gameStart:
        bird.move()

        if not gameOver:
            for pipe in pipes:
                pipe.move()
                if pipe.collide(bird):
                    bird.collided = True

                if not pipe.passed and pipe.x + pipeWidth < bird.x:
                    pipe.passed = True
                    score += 1
                    pointSound.play()

            if not pipes or pipes[-1].x <= screenWidth - pipeSpacing:
                pipes.append(Pipe(screenWidth))

            # removes previous pipes
            pipes = [onScreenPipe for onScreenPipe in pipes if onScreenPipe.x + pipeWidth > 0]

            if bird.collided:
                gameOver = True
                hitSound.play()

    #draw
    screen.blit(backgroundImg,(0, 0))

    #pipe
    for pipe in pipes:
        pipe.draw(screen, pipeTopImg, pipeImg)

    screen.blit(floorImg, (0, floorY))
    bird.draw(screen, birdImg)

    drawScore(screen, score)

    if gameOver and bird.y + birdRadius >= floorY:
        rect = gameOverImg.get_rect(center=(screenWidth // 2, screenHeight // 2))
        screen.blit(gameOverImg, rect)

    if gameOver and bird.landed and not deathPlayed:
        dieSound.play()
        deathPlayed = True

    if not gameStart:
        messageImg.set_alpha(255)
        rect = messageImg.get_rect(center=(screenWidth // 2, screenHeight // 2))
        screen.blit(messageImg, rect)
    elif messageAlpha > 0:
        messageAlpha -= 8
        messageImg.set_alpha(messageAlpha)
        rect = messageImg.get_rect(center=(screenWidth // 2, screenHeight // 2))
        screen.blit(messageImg, rect)


    #flip
    pygame.display.flip()
    clock.tick(screenFPS)


pygame.quit()