import os
import random

from kivy.config import Config

#lock to portrait-ish default window for desktop testing; on Android the
#orientation is forced via buildozer.spec instead
Config.set("graphics", "width", "400")
Config.set("graphics", "height", "720")

from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.image import Image as CoreImage
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.graphics import Color, PopMatrix, PushMatrix, Rectangle, Rotate, Scale, Translate
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.properties import NumericProperty
from kivy.uix.screenmanager import FadeTransition, Screen, ScreenManager
from kivy.uix.widget import Widget
from kivy.metrics import sp
from kivy.utils import platform

#game settings/constants (mirrored from shared/settings.py)

#screen dimension
screenWidth = 400
screenHeight = 720

screenFPS = 60

floorHeight = 120
floorY = screenHeight - floorHeight

gameTitle = "Flappy Bird by Clyde"

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


def applyDeviceAspect():
    #screenWidth stays fixed (keeps pipe spacing/speed feel consistent); screenHeight
    #stretches to match the real device aspect ratio so there's nothing left over
    #for the letterbox bars to fill. Call once, before any screens are built.
    global screenHeight, floorY, gapMax, pipeImgHeight

    winW, winH = Window.size
    if winW <= 0 or winH <= 0:
        return

    screenHeight = round(screenWidth * winH / winW)
    floorY = screenHeight - floorHeight
    gapMax = floorY - pipeGap // 2 - margin
    if gapMax < gapMin:
        gapMax = gapMin

    #pipe art must always reach from the gap to the screen edge, however tall
    #the device turns out to be
    pipeImgHeight = screenHeight


#assets
baseDir = os.path.dirname(os.path.abspath(__file__))
sprites = os.path.join(baseDir, "assets", "sprites")
audio = os.path.join(baseDir, "assets", "audio")
fonts = os.path.join(baseDir, "assets", "fonts")

titleFontPath = os.path.join(fonts, "Fredoka One", "static", "Fredoka-Bold.ttf")
titleFontName = "FredokaTitle"
if os.path.exists(titleFontPath):
    LabelBase.register(name=titleFontName, fn_regular=titleFontPath)
else:
    titleFontName = "Roboto" if platform == "android" else "Georgia"

texNormal = (0, 1, 1, 1, 1, 0, 0, 0)
texFlipped = (0, 0, 1, 0, 1, 1, 0, 1)  # top pipe (Pygame transform.flip)


def aabb(ax, ay, aw, ah, bx, by, bw, bh):
    #axis-aligned bounding box overlap (replaces pygame Rect.colliderect)
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


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


class Pipe:
    def __init__(self, x):
        self.x = x
        self.gapY = random.randint(gapMin, gapMax)
        self.passed = False

    def move(self):
        self.x -= pipeSpeed

    def collide(self, bird):
        #give the bird a square hitbox
        birdX = bird.x - birdRadius
        birdY = bird.y - birdRadius
        size = birdRadius * 2

        topHeight = self.gapY - pipeGap // 2
        bottomY = self.gapY + pipeGap // 2

        hitTop = aabb(birdX, birdY, size, size, self.x, 0, pipeWidth, topHeight)
        hitBottom = aabb(birdX, birdY, size, size, self.x, bottomY, pipeWidth, floorY - bottomY)
        return hitTop or hitBottom


class TitleScreen(Screen):
    overlayOpacity = NumericProperty(0.58)
    titleScale = NumericProperty(0.93)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "title"
        self._sequence = None
        self._introAnims = []
        self._finished = False

        layout = FloatLayout()

        with layout.canvas.before:
            #black letterbox base, fills any leftover space outside the scaled bg
            Color(0, 0, 0, 1)
            self._letterbox = Rectangle(pos=(0, 0), size=Window.size)

            Color(1, 1, 1, 1)
            self._bg = CoreImage(os.path.join(sprites, "background-night.png")).texture
            self._bgRect = Rectangle(
                texture=self._bg, pos=(0, 0), size=(screenWidth, screenHeight), tex_coords=texNormal
            )
            self._overlayColor = Color(0, 0, 0, self.overlayOpacity)
            self._overlay = Rectangle(pos=(0, 0), size=Window.size)
        Window.bind(size=self._resizeBg)
        self._resizeBg()
        self.bind(overlayOpacity=self._syncOverlay, titleScale=self._syncTitleScale)

        self.titleLabel = Label(
            text="Made by Clyde",
            font_name=titleFontName,
            font_size=sp(54),
            color=(1, 0.95, 0.78, 1),
            outline_width=2,
            outline_color=(0.15, 0.08, 0.02, 1),
            halign="center",
            valign="middle",
            opacity=0,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            size_hint=(0.92, 0.22),
        )
        self.titleLabel.bind(size=self.titleLabel.setter("text_size"))
        with self.titleLabel.canvas.before:
            PushMatrix()
            self._titleScaleInstr = Scale(1, 1, 1, origin=self.titleLabel.center)
        with self.titleLabel.canvas.after:
            PopMatrix()
        self.titleLabel.bind(pos=self._syncScaleOrigin, size=self._syncScaleOrigin)

        layout.add_widget(self.titleLabel)
        self.add_widget(layout)

    def _syncOverlay(self, _, value):
        self._overlayColor.rgba = (0, 0, 0, value)

    def _syncTitleScale(self, _, value):
        self._titleScaleInstr.x = value
        self._titleScaleInstr.y = value

    def _syncScaleOrigin(self, *_):
        self._titleScaleInstr.origin = self.titleLabel.center

    def _resizeBg(self, *_):
        winWidth, winHeight = Window.size
        self._letterbox.size = (winWidth, winHeight)

        scale = min(winWidth / screenWidth, winHeight / screenHeight)
        w, h = screenWidth * scale, screenHeight * scale
        self._bgRect.pos = ((winWidth - w) / 2, (winHeight - h) / 2)
        self._bgRect.size = (w, h)

        self._overlay.size = (winWidth, winHeight)

    def _cancelAnims(self):
        if self._sequence:
            self._sequence.cancel(self)
            self._sequence = None
        for anim in self._introAnims:
            anim.cancel(self.titleLabel)
            anim.cancel(self)
        self._introAnims.clear()

    def _runExit(self, *_):
        exitAnim = Animation(
            opacity=0,
            overlayOpacity=0.62,
            titleScale=1.02,
            duration=0.55,
            transition="in_cubic",
        )
        exitAnim.bind(on_complete=self._goToGame)
        exitAnim.start(self)
        self._introAnims.append(exitAnim)

    def on_enter(self):
        self._cancelAnims()
        self._finished = False
        self.opacity = 1
        self.overlayOpacity = 0.58
        self.titleScale = 0.93
        self.titleLabel.opacity = 0

        intro = Animation(
            titleScale=1.0,
            overlayOpacity=0.34,
            duration=0.75,
            transition="out_cubic",
        )
        fadeIn = Animation(opacity=1, duration=0.75, transition="out_cubic")
        intro.start(self)
        fadeIn.start(self.titleLabel)
        self._introAnims.extend([intro, fadeIn])

        self._sequence = Animation(duration=1.35)
        self._sequence.bind(on_complete=self._runExit)
        self._sequence.start(self)

    def on_leave(self):
        self._cancelAnims()

    def _goToGame(self, *_):
        if self._finished:
            return
        self._finished = True
        self.manager.current = "game"

    def on_touch_down(self, touch):
        self._goToGame()
        return True


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "game"
        self.add_widget(FlappyGame())


class FlappyGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        #assets
        self.backgroundImg = CoreImage(os.path.join(sprites, "background-night.png")).texture
        self.floorImg = CoreImage(os.path.join(sprites, "base.png")).texture
        self.birdImg = CoreImage(os.path.join(sprites, "redbird-upflap.png")).texture
        self.pipeImg = CoreImage(os.path.join(sprites, "pipe-green.png")).texture
        self.digitImg = [CoreImage(os.path.join(sprites, f"{i}.png")).texture for i in range(10)]
        self.gameOverImg = CoreImage(os.path.join(sprites, "gameover.png")).texture
        self.messageImg = CoreImage(os.path.join(sprites, "message.png")).texture

        #sounds
        self.wingSound = SoundLoader.load(os.path.join(audio, "wing.wav"))
        self.pointSound = SoundLoader.load(os.path.join(audio, "point.wav"))
        self.hitSound = SoundLoader.load(os.path.join(audio, "hit.wav"))
        self.dieSound = SoundLoader.load(os.path.join(audio, "die.wav"))
        self.swooshSound = SoundLoader.load(os.path.join(audio, "swoosh.wav"))

        #start
        self.reset()
        Window.bind(on_key_down=self.onKeyDown)
        Clock.schedule_interval(self.update, 1.0 / screenFPS)

    def reset(self): #retrying
        self.bird = Bird(screenHeight // 2)
        self.pipes = []
        self.gameStart = False
        self.gameOver = False
        self.deathPlayed = False
        self.score = 0
        self.messageAlpha = 255

    def playSound(self, sound):
        if sound:
            sound.stop()
            sound.play()

    #input
    def flap(self):
        if self.gameOver:
            self.reset()
            self.playSound(self.swooshSound)
        else:
            self.gameStart = True
            self.bird.jump()
            self.playSound(self.wingSound)

    def on_touch_down(self, touch):
        #bird control (touch)
        self.flap()
        return True

    def onKeyDown(self, window, key, scancode, codepoint, modifiers):
        #bird control (spacebar, for desktop testing)
        if key == 32:
            self.flap()

    #update (when the game starts)
    def update(self, dt):
        if self.gameStart:
            self.bird.move()

            if not self.gameOver:
                for pipe in self.pipes:
                    pipe.move()
                    if pipe.collide(self.bird):
                        self.bird.collided = True

                    if not pipe.passed and pipe.x + pipeWidth < self.bird.x:
                        pipe.passed = True
                        self.score += 1
                        self.playSound(self.pointSound)

                if not self.pipes or self.pipes[-1].x <= screenWidth - pipeSpacing:
                    self.pipes.append(Pipe(screenWidth))

                #removes previous pipes
                self.pipes = [onScreenPipe for onScreenPipe in self.pipes if onScreenPipe.x + pipeWidth > 0]

                if self.bird.collided:
                    self.gameOver = True
                    self.playSound(self.hitSound)

            if self.gameOver and self.bird.landed and not self.deathPlayed:
                self.playSound(self.dieSound)
                self.deathPlayed = True

        self.draw()

    #blit helper: convert top-left virtual coords to Kivy's bottom-left origin
    def blit(self, image, x, y, w, h, texCoords=texNormal):
        Rectangle(texture=image, pos=(x, screenHeight - y - h), size=(w, h), tex_coords=texCoords)

    def drawScore(self):
        Color(1, 1, 1, 1)
        scoreString = str(self.score)
        totalWidth = sum(self.digitImg[int(digit)].size[0] for digit in scoreString)
        x = screenWidth / 2 - totalWidth - 2

        for digit in scoreString:
            image = self.digitImg[int(digit)]
            w, h = image.size
            self.blit(image, x, 80, w, h)
            x += w

    #draw
    def draw(self):
        winWidth, winHeight = Window.size
        scale = min(winWidth / screenWidth, winHeight / screenHeight)
        offX = (winWidth - screenWidth * scale) / 2
        offY = (winHeight - screenHeight * scale) / 2

        self.canvas.clear()
        with self.canvas:
            #letterbox background
            Color(0, 0, 0, 1)
            Rectangle(pos=(0, 0), size=(winWidth, winHeight))

            #scale + center the virtual space onto the real screen
            PushMatrix()
            Translate(offX, offY)
            Scale(scale, scale, 1)

            Color(1, 1, 1, 1)
            self.blit(self.backgroundImg, 0, 0, screenWidth, screenHeight)

            #pipe
            for pipe in self.pipes:
                topHeight = pipe.gapY - pipeGap // 2
                bottomY = pipe.gapY + pipeGap // 2
                self.blit(self.pipeImg, pipe.x, topHeight - pipeImgHeight, pipeWidth, pipeImgHeight, texCoords=texFlipped)
                self.blit(self.pipeImg, pipe.x, bottomY, pipeWidth, pipeImgHeight)

            self.blit(self.floorImg, 0, floorY, screenWidth, floorHeight)

            #bird (rotated about its center)
            cx, cy = self.bird.x, screenHeight - self.bird.y
            PushMatrix()
            Rotate(angle=self.bird.angle, origin=(cx, cy), axis=(0, 0, 1))
            Rectangle(texture=self.birdImg,
                      pos=(self.bird.x - birdWidth / 2, (screenHeight - self.bird.y) - birdHeight / 2),
                      size=(birdWidth, birdHeight),
                      tex_coords=texNormal)
            PopMatrix()

            self.drawScore()

            if self.gameOver and self.bird.y + birdRadius >= floorY:
                w, h = self.gameOverImg.size
                self.blit(self.gameOverImg, screenWidth / 2 - w / 2, screenHeight / 2 - h / 2, w, h)

            if not self.gameStart:
                w, h = self.messageImg.size
                Color(1, 1, 1, 1)
                self.blit(self.messageImg, screenWidth / 2 - w / 2, screenHeight / 2 - h / 2, w, h)
            elif self.messageAlpha > 0:
                self.messageAlpha -= 8
                w, h = self.messageImg.size
                Color(1, 1, 1, max(0, self.messageAlpha) / 255)
                self.blit(self.messageImg, screenWidth / 2 - w / 2, screenHeight / 2 - h / 2, w, h)

            PopMatrix()


class FlappyApp(App):
    title = gameTitle

    def build(self):
        self.sm = ScreenManager(transition=FadeTransition(duration=0.45))
        return self.sm

    def on_start(self):
        #wait one frame so Window.size reflects the real fullscreen
        #dimensions on Android, not a stale pre-fullscreen value
        Clock.schedule_once(self._setupScreens, 0)

    def _setupScreens(self, *_):
        applyDeviceAspect()
        self.sm.add_widget(TitleScreen())
        self.sm.add_widget(GameScreen())
        self.sm.current = "title"


if __name__ == "__main__":
    FlappyApp().run()