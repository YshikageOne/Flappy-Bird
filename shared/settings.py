import os
#game settings/constants

#screen dimension
screenWidth = 400
screenHeight = 720

screenFPS = 60

screenGroundHeight = 200
backgroundY = screenHeight - screenGroundHeight

floorHeight = 120
floorY = screenHeight - floorHeight

gameTitle = "Flappy Bird by Clyde"

#colors
skyBlue = (78, 192, 202)
white = (255, 255, 255)
black = (0, 0, 0)
ground = (222, 184, 135)
red = (255, 0, 0)
pipeGreen = (87, 201, 70)

#bird
gravity = 0.5
jumpStrength = -8
birdXposition = 80 #fixed
birdRadius = 16
birdWidth = 45
birdHeight = 32

#pipes
pipeWidth = 70
pipeGap = 180
pipeSpeed = 3
pipeSpacing = 220 #distance of pipe pairs
pipeImgHeight = 500

#gap between top and bottom pipe
margin = 120
gapMin = pipeGap // 2 + margin
gapMax = floorY - pipeGap // 2 - margin

pipeHeadWidth = pipeWidth + 12
pipeHeadHeight = 30

#assets
import sys
if getattr(sys, "frozen", False):   #running as a PyInstaller .exe
    baseDir = sys._MEIPASS
else:                                #running as a normal .py
    baseDir = os.path.dirname(__file__)
sprites = os.path.join(baseDir, "assets", "sprites")
audio = os.path.join(baseDir, "assets", "audio")

