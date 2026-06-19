# Flappy Bird + NEAT AI by Clyde

A Python recreation of **Flappy Bird** made with [Pygame](https://www.pygame.org/), plus an AI that teaches itself to play using the **NEAT** algorithm.

## Download

No Python needed — grab a build from [Releases](../../releases):

| Platform | Version | What you get |
| --- | --- | --- |
| Windows | v1.0.0 | `Flappy Bird.exe` — Space to flap. `Flappy Bird AI.exe` — AI plays on its own. |
| Android | v1.1.1 | APK — tap the screen to flap. |

## Modes

Run from source with Python 3:

| Mode | Run | What it does |
| --- | --- | --- |
| Play | `python game/main.py` | Play it yourself. Press `Space` to flap. |
| Train | `python neat/main.py` | Watch 50 birds learn to play. Press `S` to save the best one. |
| Watch | `python neat/play.py` | Watch the trained AI play on its own. |

## Setup

```bash
pip install pygame neat-python
```

> Note: `neat/play.py` needs a `winner.pkl`, so train at least once first.

## How the AI works

Each bird is run by a small neural network. Every frame it gets 3 inputs (the bird's height and the distance to the top and bottom of the next gap) and outputs one value. If that value is above `0.5`, the bird flaps. Birds earn fitness for surviving and passing pipes, and the best ones evolve over generations.

## Project structure

```
game/         Human-playable game (Pygame)
android/      Android port (Kivy) — touch to flap
neat/         AI training + playback (config.txt, winner.pkl)
shared/       Shared code & assets (settings, bird, pipe, sprites, audio)
```

## Credits

- Assets: [samuelcust/flappy-bird-assets](https://github.com/samuelcust/flappy-bird-assets/tree/master)
- Inspiration: [Code Bullet](https://www.youtube.com/watch?v=WSW-5m8lRMs&t=141s)
