# DOC: Snake Game Implementation And Requirements

## Overview
This project is a terminal-based Snake game implemented in Python using the standard library `curses` module.

Main file:
- `snake_game.py`

The game renders a fixed-size board in terminal text mode, updates on a timer, and handles keyboard input in a non-blocking loop.

## Functional Requirements
- Grid size: `20 x 20`
- Snake movement: up/down/left/right using arrow keys
- Food: black square blocks
- Score: increments by 1 per pickup
- Score display: upper-right corner (`PTS XX`)
- Win condition: score reaches `10`
- Lose condition: collision with wall or snake body
- Restart: `R`
- Quit: `Q`

## Technical Requirements
- Python 3 (tested with Python 3.13 in this workspace)
- Terminal with `curses` support
- Minimum terminal size: `46 x 26`
- No third-party Python packages required

Optional runtime capability:
- macOS `afplay` for distinct movement/pickup sound cues

## Module Dependencies
Standard-library imports used:
- `curses`
- `random`
- `shutil`
- `subprocess`
- `pathlib.Path`

No external dependencies are installed.

## Constants
Key constants that define behavior:
- `GRID_SIZE = 20`
- `CELL_WIDTH = 2`
- `TICK_MS = 140`
- `WIN_SCORE = 10`
- `MIN_HEIGHT = GRID_SIZE + 6`
- `MIN_WIDTH = GRID_SIZE * CELL_WIDTH + 6`

Audio constants:
- `AFPLAY_PATH = shutil.which("afplay")`
- `SOUND_FILES["move"] = /System/Library/Sounds/Tink.aiff`
- `SOUND_FILES["pickup"] = /System/Library/Sounds/Pop.aiff`

## Architecture
### `SnakeGame` class
Responsibilities:
- Stores game state (`snake`, `direction`, `food`, `score`, `game_over`)
- Handles reset and movement logic
- Validates collisions
- Draws the UI frame, board, entities, and overlays

Core methods:
- `reset()`: initializes a new game state
- `spawn_food()`: picks random free cell not occupied by snake
- `handle_key(key)`: processes controls and direction changes
- `update()`: advances game by one tick and applies rules
- `draw()`: full render cycle per frame
- `draw_frame()`, `draw_board()`, `draw_cell()`, `draw_overlay()`: rendering helpers

### Runtime functions
- `configure_screen(screen)`: configures `curses` modes and colors
- `play_sound(event)`: plays macOS sound via `afplay`, else falls back to beep/flash
- `ensure_terminal_size(screen)`: enforces minimum terminal dimensions
- `run(screen)`: main loop (`draw -> input -> update`)
- `main()`: entrypoint (`curses.wrapper(run)`)

## Game Loop
Per iteration:
1. Draw current state
2. Read one key with non-blocking timeout
3. Handle control input
4. Advance one simulation tick

Timing uses `screen.timeout(TICK_MS)` so the loop updates regularly even without input.

## Collision And Rule Details
- Reverse-direction turns are rejected to prevent instant self-collision.
- Wall collision and self-collision set `game_over`.
- On pickup:
  - score increments
  - pickup sound is played
  - if score >= win score, game ends with win message
  - otherwise spawn new food
- On non-pickup movement:
  - tail segment is removed
  - movement sound is played

## Audio Behavior
`play_sound(event)` checks:
1. Does event map to a configured file?
2. Is `afplay` available and sound file present?

If yes, plays asynchronously with `subprocess.Popen` and discards process output.
If no, falls back to `curses.beep()` and then `curses.flash()` on error.

## Error Handling
- Terminal too small: raises `RuntimeError` with required and actual dimensions.
- Sound fallback ensures game continues even when sound playback is unavailable.

## Running
From workspace root:

```bash
/opt/homebrew/bin/python3 python-python/snake_game.py
```

or

```bash
python3 python-python/snake_game.py
```
