# Flappy Bird + NEAT AI By Clyde

A Python recreation of **Flappy Bird** made with [Pygame](https://www.pygame.org/), plus an AI that teaches itself to play using the **NEAT** algorithm.

## Modes

| Mode | Run | What it does |
| --- | --- | --- |
| Play | `python game/main.py` | Play it yourself. Press `Space` to flap. |
| Train | `python neat/main.py` | Watch 50 birds learn to play. Press `S` to save the best one. |
| Watch | `python neat/play.py` | Watch the trained AI play on its own. |

## Setup

Requires Python 3 and two packages:

```bash
pip install pygame neat-python
```

> Note: `neat/play.py` needs a `winner.pkl`, so train at least once first.

## How the AI works

Each bird is run by a small neural network. Every frame it gets 3 inputs (the bird's height and the distance to the top and bottom of the next gap) and outputs one value. If that value is above `0.5`, the bird flaps. Birds earn fitness for surviving and passing pipes, and the best ones evolve over generations.

## Project structure

```
game/         Human-playable game
neat/         AI training + playback (config.txt, winner.pkl)
shared/       Shared code & assets (settings, bird, pipe, sprites, audio)
```

## Credits

- Assets: [samuelcust/flappy-bird-assets](https://github.com/samuelcust/flappy-bird-assets/tree/master)
- Inspiration: [Code Bullet](https://www.youtube.com/watch?v=WSW-5m8lRMs&t=141s)
