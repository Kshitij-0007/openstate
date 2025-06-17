# Openstate - Ninja Stealth Game

A 2D stealth platformer game built with Python and Pygame where you play as a ninja navigating maze-like levels filled with patrolling guards.

## Game Features

- **Stealth Gameplay**: Avoid detection by guards with cone-of-vision logic
- **Guard AI**: Guards pursue the player when detected and return to patrol routes
- **Procedurally Generated Levels**: Each level has a unique maze layout
- **Moving Maze Elements**: Dynamic obstacles that require timing to navigate
- **Collectibles**: Gather scrolls in each level for bonus stars
- **Hiding Mechanics**: Use shadows and bushes to hide from guards
- **Star Rating System**: Earn up to 3 stars per level based on performance
- **Game Over System**: "Ninja Captured" screen with restart and menu options

## Controls

- **W**: Jump/Move up
- **A/D**: Move left/right
- **S**: Crouch or hide (context-sensitive)
- **Ctrl**: Hide in bushes or shadows

## Game Objectives

- Collect all scrolls/coins (for stars)
- Avoid detection by guards
- Reach the exit to complete level
- Earn stars based on performance:
  - 1 star: reach exit
  - +1 star: collect all scrolls
  - +1 star: no detection

## Installation

1. Make sure you have Python 3.6+ installed
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Run the game:
   ```
   python main.py
   ```

## Project Structure

```
openstate/
├── assets/
│   ├── images/
│   └── sounds/
├── src/
│   ├── __init__.py
│   ├── game.py
│   ├── player.py
│   ├── guard.py
│   ├── level.py
│   ├── maze_generator.py
│   ├── scroll.py
│   ├── tile.py
│   └── ui.py
├── main.py
└── requirements.txt
```

## Development

This game is built with a modular architecture to make it easy to extend:

- **Player Class**: Handles player movement, collision detection, and hiding mechanics
- **Guard Class**: Implements guard AI, patrol routes, player detection, and pursuit behavior
- **Level Class**: Manages level layout, scrolls, moving walls, and exit placement
- **Maze Generator**: Creates procedurally generated maze layouts
- **UI Class**: Handles all game UI elements including star rating, game over screen, and timer

## Future Enhancements

- Additional player abilities (wall climbing, smoke bombs)
- More enemy types with different behaviors
- Power-ups and special items
- Level editor
- Save/load game progress
