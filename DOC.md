# DOC: Snake Game Implementation And Requirements

## Overview
This project is a terminal-based Snake game implemented in Python using the standard library `curses` module.

Main file:
- `snake_game.py`

The game renders a fixed-size board in terminal text mode, updates on a timer, and handles keyboard input in a non-blocking loop.

## Functional Requirements
- Grid size: `20 x 20`
- Start screen menu with three difficulty levels
- Snake movement: up/down/left/right using arrow keys
- Food: black square blocks
- Score: increments by 1 per pickup
- Score display: upper-right corner (`PTS XX`)
- Selected difficulty display: top row (`LVL EASE`, `LVL MID`, `LVL HIGH`)
- Win condition: score reaches `100`
- Lose condition: collision with wall or snake body
- Start selected difficulty with `Enter`
- Restart: `R`
- Quit/save flow: `Q` prompts for player name, saves score, then exits
- Win/save flow: on win, prompts for player name, saves score, then exits
- Right-side scoreboard displays only the chosen difficulty entries
- Attempts log shown below the game area with attempt number and score

Difficulty requirements:
- `ease`: 15% slower than base speed
- `mid`: current/base speed
- `high`: 20% faster than base speed

Scoreboard requirements:
- One file only: `SCORING_BOARD.md`
- Separate tables per difficulty section: `## EASE`, `## MID`, `## HIGH`
- Each table stores rank, score, player name, date

## Technical Requirements
- Python 3 (tested with Python 3.13 in this workspace)
- Terminal with `curses` support
- Minimum terminal size: `70 x 26`
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
- `WIN_SCORE = 100`
- `BOARD_WIDTH = GRID_SIZE * CELL_WIDTH + 2`
- `SCOREBOARD_LEFT = 2 + BOARD_WIDTH + 4`
- `SCOREBOARD_WIDTH = 20`
- `BASE_MIN_HEIGHT = GRID_SIZE + 6`
- `ATTEMPT_LOG_LINES = 5`
- `MIN_HEIGHT = BASE_MIN_HEIGHT + ATTEMPT_LOG_LINES + 1`
- `MIN_WIDTH = SCOREBOARD_LEFT + SCOREBOARD_WIDTH + 2`

Difficulty constants:
- `DIFFICULTY_CHOICES = (("ease", 161), ("mid", 140), ("high", 112))`

Scoreboard constants:
- `SCORING_BOARD_MD = Path(__file__).parent / "SCORING_BOARD.md"`
- `MAX_SCORES = 10`

Audio constants:
- `AFPLAY_PATH = shutil.which("afplay")`
- `SOUND_FILES["move"] = /System/Library/Sounds/Tink.aiff`
- `SOUND_FILES["pickup"] = /System/Library/Sounds/Pop.aiff`

## Architecture
### `SnakeGame` class
Responsibilities:
- Stores game state (`snake`, `direction`, `food`, `score`, `game_over`)
- Stores selected difficulty name and tick speed
- Stores scoreboard entries for selected difficulty
- Tracks attempts (`attempt number`, `score`) for on-screen history
- Handles reset and movement logic
- Validates collisions
- Draws the UI frame, board, entities, and overlays

Core methods:
- `reset()`: initializes a new game state
- `spawn_food()`: picks random free cell not occupied by snake
- `handle_key(key)`: processes controls, direction changes, and quit/save flow
- `update()`: advances game by one tick and applies rules
- `draw()`: full render cycle per frame
- `draw_frame()`, `draw_board()`, `draw_cell()`, `draw_overlay()`, `draw_scoreboard()`: rendering helpers
- `record_attempt()`: records current attempt result once
- `draw_attempt_log()`: renders recent attempts below the board

### Runtime functions
- `configure_screen(screen)`: configures `curses` modes and colors
- `set_tick_speed(screen, tick_ms)`: applies selected gameplay speed using `screen.timeout(...)`
- `choose_difficulty(screen)`: renders and handles the start menu
- `play_sound(event)`: plays macOS sound via `afplay`, else falls back to beep/flash
- `ensure_terminal_size(screen)`: enforces minimum terminal dimensions
- `ensure_scoring_board()`: initializes `SCORING_BOARD.md` if missing
- `load_all_scores()`: reads all difficulty tables from Markdown
- `load_scores(difficulty)`: returns entries only for selected difficulty
- `save_score(difficulty, score, name)`: appends score into selected table
- `write_scoring_board_md(scoreboards)`: writes full single-file scoreboard with separate sections
- `ask_player_name(screen, score, difficulty)`: in-terminal name input dialog
- `run(screen)`: main loop (`draw -> input -> update`)
- `main()`: entrypoint (`curses.wrapper(run)`)

## Start Screen Flow
1. Configure terminal rendering and input handling.
2. Validate minimum terminal size.
3. Show difficulty menu.
4. Let the user select `ease`, `mid`, or `high` using `Up` and `Down`.
5. Start the game after `Enter` is pressed.
6. Exit immediately if `Q` is pressed from the menu.

## Game Loop
Per iteration:
1. Draw current state
2. Read one key with non-blocking timeout
3. Handle control input
4. Advance one simulation tick

Timing uses the selected difficulty timeout so the loop updates regularly even without input.

## Collision And Rule Details
- Reverse-direction turns are rejected to prevent instant self-collision.
- Wall collision and self-collision set `game_over`.
- On pickup:
  - score increments
  - pickup sound is played
  - if score >= win score, game ends with win message and name prompt
  - otherwise spawn new food
- On non-pickup movement:
  - tail segment is removed
  - movement sound is played

## Scoreboard Data Model
- Storage format is Markdown, not plain text/CSV.
- File structure:
  - `# Scoring Board`
  - `## EASE` table
  - `## MID` table
  - `## HIGH` table
- Each record contains: rank (derived), score, player name, date/time.
- In-game panel shows only current difficulty table entries.

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
