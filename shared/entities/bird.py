import pygame
from shared.settings import *

class Bird:
    def __init__(self, birdYposition):
        self.x = birdXposition
        self.y = birdYposition
        self.velocity = 0
        self.collided = False
        self.angle = 0
        self.landed = False

    def jump(self):
        self.velocity = jumpStrength

    def move(self):
        self.collided = False
        self.velocity += gravity

        #terminal velocity of the bird
        if self.velocity > 12:
            self.velocity = 12
        self.y += self.velocity

        if not self.landed:
            self.angle = max(-90, min(25, -self.velocity * 8))

        #clamping so bro doesnt leave the screen
        #ceiling
        if self.y - birdRadius < 0:
            self.y = birdRadius
            self.velocity = 0 #stops the bird

        #floor
        if self.y + birdRadius > floorY:
            self.y = floorY - birdRadius
            self.velocity = 0
            self.collided = True
            self.landed = True


    def draw(self, screen, image):
        rotatedImage = pygame.transform.rotate(image, self.angle)
        rect = rotatedImage.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(rotatedImage, rect)

