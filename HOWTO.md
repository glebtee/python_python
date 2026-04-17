# HOWTO: Play Snake

## Start The Game
Run from the workspace root:

```bash
/opt/homebrew/bin/python3 python-python/snake_game.py
```

Or if `python3` is on your PATH:

```bash
python3 python-python/snake_game.py
```

## Controls
- Start screen:
  - `Up` / `Down`: select difficulty
  - `Enter`: start game with selected difficulty
  - `Q`: quit from the menu
- Arrow keys: move the snake (`Up`, `Down`, `Left`, `Right`)
- `R`: restart the game after game over or win
- `Q`: open name prompt, save score, quit

## Difficulty Levels
- `ease`: 15% slower than the base speed (`161 ms` per tick)
- `mid`: current default speed (`140 ms` per tick)
- `high`: 20% faster than the base speed (`112 ms` per tick)

When the game starts, a menu is shown before gameplay begins. The selected difficulty is also displayed during the game as `LVL EASE`, `LVL MID`, or `LVL HIGH`.

## Objective
- Eat the black square food blocks (`[]`).
- Each food pickup gives 1 point.
- The score is shown in the upper-right as `PTS XX`.
- Reach 100 points to win.

On win, the game asks for player name, saves score, and updates the scoring board.

## Lose Conditions
The game ends with game over if the snake:
- Hits a wall
- Hits its own body

## Sounds
- Movement sound: played on normal movement steps
- Pickup sound: played when food is eaten

On macOS, the game uses built-in system sounds via `afplay` when available.

## Terminal Requirements
- Use a terminal window with minimum size `70 x 26` (width x height).
- If your terminal is too small, the game exits and prints the minimum required size.

## Scoreboard
- The right-side panel shows scores for the currently selected difficulty only.
- Scores are stored in one Markdown file: `SCORING_BOARD.md`.
- `SCORING_BOARD.md` contains three separate tables:
	- `## EASE`
	- `## MID`
	- `## HIGH`

## Attempts Log
- Below the game screen, the game shows recent attempts.
- Each line shows both the attempt number and score (example: `#3  SCORE 42`).
- The newest attempt is shown first.
- Attempts are recorded when you lose, win, restart mid-game, or quit.

## Notes
- The game is real-time with a fixed tick speed.
- The selected difficulty changes the game tick speed.
- Turning directly into the opposite direction is blocked (for example, `Left` to `Right` instantly is not allowed).
