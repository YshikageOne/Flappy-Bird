import random
import pygame
from shared.settings import *

class Pipe:
    def __init__(self, x):
        self.x = x
        self.gapY = random.randint(gapMin, gapMax)
        self.passed = False

    def move(self):
        self.x -= pipeSpeed

    def draw(self, screen, pipeTopImg, pipeImg):
        """
        deprecated
        #top pipe
        topHeight = self.gapY - pipeGap // 2
        pygame.draw.rect(screen, pipeGreen, (self.x, 0, pipeWidth, topHeight)) #top body
        pygame.draw.rect(screen, pipeGreen, (self.x - 6, topHeight - pipeHeadHeight, pipeHeadWidth, pipeHeadHeight))  #top head

        #bottom pipe
        bottomY = self.gapY + pipeGap // 2
        pygame.draw.rect(screen, pipeGreen, (self.x, bottomY, pipeWidth, floorY - bottomY))  #bottom body
        pygame.draw.rect(screen, pipeGreen, (self.x - 6, bottomY, pipeHeadWidth, pipeHeadHeight))  # bottom head
        """

        topHeight = self.gapY - pipeGap // 2
        bottomY = self.gapY + pipeGap // 2

        screen.blit(pipeTopImg, (self.x, topHeight - pipeImgHeight))
        screen.blit(pipeImg, (self.x, bottomY))

    def collide(self, bird):
        #give the bird a square hitbox
        birdRect = pygame.Rect(bird.x - birdRadius, bird.y - birdRadius, birdRadius * 2, birdRadius * 2)


        topHeight = self.gapY - pipeGap // 2
        bottomY = self.gapY + pipeGap // 2
        topRect = pygame.Rect(self.x, 0, pipeWidth, topHeight)
        bottomRect = pygame.Rect(self.x, bottomY, pipeWidth, floorY - bottomY)

        return birdRect.colliderect(topRect) or birdRect.colliderect(bottomRect)

