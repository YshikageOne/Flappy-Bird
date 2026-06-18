import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
import neat
import pickle
from shared.settings import *
from shared.entities.bird import Bird
from shared.entities.pipe import Pipe

#start
pygame.init()
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Flappy Bird AI by Clyde")
clock = pygame.time.Clock()

#load the trained brain
configPath = os.path.join(os.path.dirname(__file__), "config.txt")
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation, configPath)

with open(os.path.join(os.path.dirname(__file__), "winner.pkl"), "rb") as f:
    genome = pickle.load(f)
network = neat.nn.FeedForwardNetwork.create(genome, config)

def reset():
    return Bird(screenHeight // 2), [], False, False, 0

bird, pipes, gameStart, gameOver, score = reset()
deathPlayed = False

#assets
backgroundImg = pygame.transform.scale(pygame.image.load(os.path.join(sprites, "background-night.png")).convert(), (screenWidth, screenHeight))
floorImg = pygame.transform.scale(pygame.image.load(os.path.join(sprites, "base.png")).convert_alpha(), (screenWidth, floorHeight))
birdImg = pygame.transform.scale(pygame.image.load(os.path.join(sprites, "redbird-upflap.png")).convert_alpha(), (birdWidth, birdHeight))
pipeImg = pygame.transform.scale(pygame.image.load(os.path.join(sprites, "pipe-green.png")).convert_alpha(), (pipeWidth, pipeImgHeight))
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
    totalWidth = sum(digitImg[int(d)].get_width() for d in scoreString)
    x = screenWidth // 2 - totalWidth // 2
    for d in scoreString:
        image = digitImg[int(d)]
        screen.blit(image, (x, 80))
        x += image.get_width()

#game loop
running = True
while running:

    #input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if gameOver:
                bird, pipes, gameStart, gameOver, score = reset()
                deathPlayed = False
                messageAlpha = 255
                swooshSound.play()
            elif not gameStart:
                gameStart = True
                swooshSound.play()

    #update
    if gameStart:
        bird.move()

        if not gameOver:
            #make sure a pipe exists for the AI to sense
            if not pipes or pipes[-1].x <= screenWidth - pipeSpacing:
                pipes.append(Pipe(screenWidth))

            #pick the pipe ahead of the bird
            pipeIndex = 0
            if len(pipes) > 1 and bird.x > pipes[0].x + pipeWidth:
                pipeIndex = 1
            pipe = pipes[pipeIndex]

            #THE AI DECIDES (same 3 inputs as training)
            output = network.activate((
                bird.y,
                bird.y - (pipe.gapY - pipeGap // 2),
                bird.y - (pipe.gapY + pipeGap // 2),
            ))
            if output[0] > 0.5:
                bird.jump()
                wingSound.play()

            #move pipes, collision, scoring
            for currentPipe in pipes:
                currentPipe.move()
                if currentPipe.collide(bird):
                    bird.collided = True
                if not currentPipe.passed and currentPipe.x + pipeWidth < bird.x:
                    currentPipe.passed = True
                    score += 1
                    pointSound.play()

            pipes = [p for p in pipes if p.x + pipeWidth > 0]

            if bird.collided:
                gameOver = True
                hitSound.play()

    #draw
    screen.blit(backgroundImg, (0, 0))
    for currentPipe in pipes:
        currentPipe.draw(screen, pipeTopImg, pipeImg)
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

    pygame.display.flip()
    clock.tick(screenFPS)

pygame.quit()