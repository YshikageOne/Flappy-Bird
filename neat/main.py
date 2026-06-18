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
pygame.display.set_caption("Flappy Bird NEAT by Clyde")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 30)

#assets
backgroundImg = pygame.transform.scale(pygame.image.load(os.path.join(sprites, "background-night.png")).convert(), (screenWidth, screenHeight))
floorImg = pygame.transform.scale(pygame.image.load(os.path.join(sprites, "base.png")).convert_alpha(), (screenWidth, floorHeight))
birdImg = pygame.transform.scale(pygame.image.load(os.path.join(sprites, "redbird-midflap.png")).convert_alpha(), (birdWidth, birdHeight))
pipeImg = pygame.transform.scale(pygame.image.load(os.path.join(sprites, "pipe-green.png")).convert_alpha(), (pipeWidth, pipeImgHeight))
pipeTopImg = pygame.transform.flip(pipeImg, False, True)

generation = 0

#turning our genomes into players
def eval_genomes(genomes, config):
    global generation
    generation += 1

    nNetworks = [] #neural network
    birds = [] #players
    currentAlive = []

    for genome_id, genome in genomes:
        network = neat.nn.FeedForwardNetwork.create(genome, config) #makes the neural network using the config
        nNetworks.append(network)
        birds.append(Bird(screenHeight // 2))
        genome.fitness = 0
        currentAlive.append(genome)

    pipes = [Pipe(screenWidth)]
    score = 0

    #game will keep running until all birds die
    running = True
    while running and len(birds) > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                if currentAlive:
                    saveWinner(max(currentAlive, key = lambda g: g.fitness))
                pygame.quit()
                sys.exit()


        #deciding which pipe to focus
        pipeIndex = 0
        if len(pipes) > 1 and birds[0].x > pipes[0].x + pipeWidth:
            pipeIndex = 1
        pipe = pipes[pipeIndex]

        #each bird thinks and moves
        for i in range(len(birds) - 1, -1, -1):
            bird = birds[i]
            bird.move()
            currentAlive[i].fitness += 0.1 #reward for staying alive

            output = nNetworks[i].activate((
                bird.y, #bird's height
                bird.y - (pipe.gapY - pipeGap // 2), #top pipe edge distance
                bird.y - (pipe.gapY + pipeGap // 2), #bottom pipe edge distance
            ))

            if output[0] > 0.5: #output either -1 or 1 so jump or no jump
                bird.jump()


            #death check
            dead = pipe.collide(bird) or bird.y - birdRadius <= 0 or bird.y + birdRadius >= floorY
            if dead: #eliminate the dead ones
                currentAlive[i].fitness -= 1
                birds.pop(i)
                nNetworks.pop(i)
                currentAlive.pop(i)

        #reward the living
        for currentPipe in pipes:
            currentPipe.move()
            if not currentPipe.passed and currentPipe.x + pipeWidth < birdXposition:
                currentPipe.passed = True
                score += 1
                for genome in currentAlive:
                   genome.fitness += 5

        if pipes[-1].x <= screenWidth - pipeSpacing:
            pipes.append(Pipe(screenWidth))
        pipes = [currentPipe for currentPipe in pipes if currentPipe.x + pipeWidth > 0]

        #draw
        screen.blit(backgroundImg, (0,0))
        for currentPipe in pipes:
            currentPipe.draw(screen, pipeTopImg, pipeImg)

        screen.blit(floorImg, (0, floorY))

        for currentBird in birds:
            currentBird.draw(screen, birdImg)

        info = font.render(f"Gen: {generation}  Alive: {len(birds)}  Score: {score}", True, white)
        screen.blit(info, (10, 10))

        pygame.display.flip()
        clock.tick(screenFPS)


def run(configPath):
    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        configPath,
    )

    population = neat.Population(config)

    population.add_reporter(neat.StdOutReporter(True)) #summary of each generation
    population.add_reporter(neat.StatisticsReporter()) #collect stats overtime for graphing

    winner = population.run(eval_genomes, 50)  #run up to 50 gens
    print("\nBest genome:\n", winner)

def saveWinner(genome):
    path = os.path.join(os.path.dirname(__file__), "winner.pkl")
    with open(path, "wb") as f:
        pickle.dump(genome, f)
    print("winner saved to", path)

if __name__ == "__main__":
    configPath = os.path.join(os.path.dirname(__file__), "config.txt")
    run(configPath)
