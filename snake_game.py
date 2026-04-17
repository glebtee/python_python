import curses
import random
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


GRID_SIZE = 20
CELL_WIDTH = 2
TICK_MS = 140
WIN_SCORE = 100
BOARD_WIDTH = GRID_SIZE * CELL_WIDTH + 2
SCOREBOARD_LEFT = 2 + BOARD_WIDTH + 4
SCOREBOARD_WIDTH = 20
BASE_MIN_HEIGHT = GRID_SIZE + 6
ATTEMPT_LOG_LINES = 5
MIN_HEIGHT = BASE_MIN_HEIGHT + ATTEMPT_LOG_LINES + 1
MIN_WIDTH = SCOREBOARD_LEFT + SCOREBOARD_WIDTH + 2
SCORING_BOARD_MD = Path(__file__).parent / "SCORING_BOARD.md"
MAX_SCORES = 10
DIFFICULTY_CHOICES = (
    ("ease", int(TICK_MS * 1.15)),
    ("mid", TICK_MS),
    ("high", int(TICK_MS * 0.8)),
)
AFPLAY_PATH = shutil.which("afplay")
SOUND_FILES = {
    "move": Path("/System/Library/Sounds/Tink.aiff"),
    "pickup": Path("/System/Library/Sounds/Pop.aiff"),
}

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class SnakeGame:
    def __init__(self, screen: curses.window, difficulty_name: str, tick_ms: int, scores: list) -> None:
        self.screen = screen
        self.difficulty_name = difficulty_name
        self.tick_ms = tick_ms
        self.scores = scores
        self.current_attempt = 0
        self.attempt_finished = False
        self.attempt_history: list[tuple[int, int]] = []
        self.board_top = 2
        self.board_left = 2
        self.reset()

    def reset(self) -> None:
        if not self.attempt_finished and self.current_attempt > 0:
            self.record_attempt()

        self.current_attempt += 1
        self.attempt_finished = False
        mid = GRID_SIZE // 2
        self.snake = [(mid, mid), (mid - 1, mid), (mid - 2, mid)]
        self.direction = RIGHT
        self.pending_direction = RIGHT
        self.score = 0
        self.message = ""
        self.game_over = False
        self.food = self.spawn_food()

    def spawn_food(self) -> tuple[int, int]:
        free_cells = [
            (x, y)
            for x in range(GRID_SIZE)
            for y in range(GRID_SIZE)
            if (x, y) not in self.snake
        ]
        return random.choice(free_cells)

    def handle_key(self, key: int) -> bool:
        if key in (ord("q"), ord("Q")):
            self.record_attempt()
            name = ask_player_name(self.screen, self.score, self.difficulty_name)
            save_score(self.difficulty_name, self.score, name)
            self.scores = load_scores(self.difficulty_name)
            write_scoring_board_md(load_all_scores())
            return False

        direction_map = {
            curses.KEY_UP: UP,
            curses.KEY_DOWN: DOWN,
            curses.KEY_LEFT: LEFT,
            curses.KEY_RIGHT: RIGHT,
        }

        if key in direction_map and not self.game_over:
            new_direction = direction_map[key]
            if not self.is_reverse_direction(new_direction):
                self.pending_direction = new_direction

        if key in (ord("r"), ord("R")):
            self.reset()

        return True

    def is_reverse_direction(self, new_direction: tuple[int, int]) -> bool:
        return (
            self.direction[0] + new_direction[0] == 0
            and self.direction[1] + new_direction[1] == 0
        )

    def update(self) -> None:
        if self.game_over:
            return

        self.direction = self.pending_direction
        head_x, head_y = self.snake[0]
        step_x, step_y = self.direction
        new_head = (head_x + step_x, head_y + step_y)

        if self.hit_wall(new_head) or new_head in self.snake:
            self.game_over = True
            self.message = "GAME OVER, LOOSER!"
            self.record_attempt()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            play_sound("pickup")
            if self.score >= WIN_SCORE:
                self.game_over = True
                self.message = "YOU WIN!"
                self.record_attempt()
                self.draw()
                name = ask_player_name(self.screen, self.score, self.difficulty_name)
                save_score(self.difficulty_name, self.score, name)
                self.scores = load_scores(self.difficulty_name)
                write_scoring_board_md(load_all_scores())
                return
            self.food = self.spawn_food()
        else:
            self.snake.pop()
            play_sound("move")

    def record_attempt(self) -> None:
        if self.attempt_finished:
            return
        self.attempt_finished = True
        self.attempt_history.append((self.current_attempt, self.score))
        self.attempt_history = self.attempt_history[-ATTEMPT_LOG_LINES:]

    def hit_wall(self, position: tuple[int, int]) -> bool:
        x, y = position
        return x < 0 or x >= GRID_SIZE or y < 0 or y >= GRID_SIZE

    def draw(self) -> None:
        self.screen.erase()
        self.screen.addstr(0, 2, "PYTHON PYTHON", curses.A_BOLD)
        self.screen.addstr(0, MIN_WIDTH - 20, f"LVL {self.difficulty_name.upper()}", curses.A_BOLD)
        self.screen.addstr(0, MIN_WIDTH - 8, f"PTS {self.score:02d}", curses.A_BOLD)
        self.draw_frame()
        self.draw_board()
        self.draw_scoreboard()

        attempts_top = self.board_top + GRID_SIZE + 3
        if self.game_over:
            self.draw_overlay(self.message, "R TO RESTART OR Q TO QUIT AS LOOSERS DO!!1")
            self.screen.addstr(attempts_top, 2, "R TO RESTART  Q TO SAVE + QUIT")
        else:
            self.screen.addstr(attempts_top, 2, "ARROWS TO MOVE  Q TO SAVE + QUIT")

        self.draw_attempt_log(attempts_top + 1)

        self.screen.refresh()

    def draw_frame(self) -> None:
        board_height = GRID_SIZE + 2
        board_width = GRID_SIZE * CELL_WIDTH + 2
        self.screen.addstr(self.board_top, self.board_left, "+" + "-" * (board_width - 2) + "+")
        for row in range(1, board_height - 1):
            self.screen.addstr(self.board_top + row, self.board_left, "|")
            self.screen.addstr(self.board_top + row, self.board_left + board_width - 1, "|")
        self.screen.addstr(self.board_top + board_height - 1, self.board_left, "+" + "-" * (board_width - 2) + "+")

    def draw_board(self) -> None:
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                self.draw_cell((x, y), "  ", curses.color_pair(1))

        self.draw_cell(self.food, "[]", curses.color_pair(3) | curses.A_BOLD)

        for index, segment in enumerate(self.snake):
            cell_text = "<>" if index == 0 else "[]"
            self.draw_cell(segment, cell_text, curses.color_pair(2) | curses.A_BOLD)

    def draw_cell(self, position: tuple[int, int], text: str, style: int) -> None:
        x, y = position
        row = self.board_top + 1 + y
        col = self.board_left + 1 + x * CELL_WIDTH
        self.screen.addstr(row, col, text, style)

    def draw_overlay(self, title: str, subtitle: str) -> None:
        width = 24
        start_row = self.board_top + GRID_SIZE // 2 - 1
        start_col = self.board_left + (GRID_SIZE * CELL_WIDTH + 2 - width) // 2
        self.screen.addstr(start_row, start_col, "+" + "-" * (width - 2) + "+", curses.A_BOLD)
        self.screen.addstr(start_row + 1, start_col, "|" + " " * (width - 2) + "|", curses.A_BOLD)
        self.screen.addstr(start_row + 2, start_col, "|" + " " * (width - 2) + "|", curses.A_BOLD)
        self.screen.addstr(start_row + 3, start_col, "+" + "-" * (width - 2) + "+", curses.A_BOLD)
        self.screen.addstr(start_row + 1, start_col + (width - len(title)) // 2, title, curses.A_BOLD)
        self.screen.addstr(start_row + 2, start_col + (width - len(subtitle)) // 2, subtitle)

    def draw_scoreboard(self) -> None:
        col = SCOREBOARD_LEFT
        top = self.board_top
        inner = SCOREBOARD_WIDTH

        self.screen.addstr(top, col, "+" + "-" * inner + "+", curses.A_BOLD)
        title = f" {self.difficulty_name.upper()} SCORES "
        self.screen.addstr(top + 1, col, "|" + title.center(inner) + "|", curses.A_BOLD)
        self.screen.addstr(top + 2, col, "+" + "-" * inner + "+", curses.A_BOLD)

        for rank, (score, name, date) in enumerate(self.scores[:MAX_SCORES], start=1):
            line = f"{rank:>2}. {score:>4} {name[:11]}"
            self.screen.addstr(top + 2 + rank, col, "|" + line.ljust(inner) + "|")

        for blank in range(len(self.scores), MAX_SCORES):
            self.screen.addstr(top + 3 + blank, col, "|" + " " * inner + "|")

        self.screen.addstr(top + 3 + MAX_SCORES, col, "+" + "-" * inner + "+", curses.A_BOLD)

    def draw_attempt_log(self, start_row: int) -> None:
        self.screen.addstr(start_row, 2, "ATTEMPTS (number + score):", curses.A_BOLD)
        recent = list(reversed(self.attempt_history[-ATTEMPT_LOG_LINES:]))

        for idx in range(ATTEMPT_LOG_LINES):
            row = start_row + 1 + idx
            if idx < len(recent):
                attempt_number, score = recent[idx]
                line = f"#{attempt_number:>2}  SCORE {score:>3}"
            else:
                line = ""
            self.screen.addstr(row, 2, line.ljust(30))


def configure_screen(screen: curses.window) -> None:
    curses.curs_set(0)
    screen.nodelay(True)
    screen.keypad(True)

    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_BLACK)


def set_tick_speed(screen: curses.window, tick_ms: int) -> None:
    screen.timeout(tick_ms)


def play_sound(event: str) -> None:
    sound_file = SOUND_FILES.get(event)
    if AFPLAY_PATH and sound_file and sound_file.exists():
        subprocess.Popen(
            [AFPLAY_PATH, str(sound_file)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return

    try:
        curses.beep()
    except curses.error:
        curses.flash()


def ensure_terminal_size(screen: curses.window) -> None:
    height, width = screen.getmaxyx()
    if height < MIN_HEIGHT or width < MIN_WIDTH:
        raise RuntimeError(
            f"Terminal too small. Need at least {MIN_WIDTH}x{MIN_HEIGHT}, got {width}x{height}."
        )


def _empty_scoreboards() -> dict[str, list[tuple[int, str, str]]]:
    return {difficulty_name: [] for difficulty_name, _ in DIFFICULTY_CHOICES}


def _parse_difficulty_header(line: str, scoreboards: dict[str, list[tuple[int, str, str]]]) -> str | None:
    if not line.startswith("## "):
        return None
    section_name = line[3:].strip().lower()
    return section_name if section_name in scoreboards else None


def _parse_score_line(line: str) -> tuple[int, str, str] | None:
    if not line.startswith("|"):
        return None
    if "Rank" in line or "------" in line or "No scores recorded yet" in line:
        return None

    parts = [p.strip() for p in line.strip("|").split("|")]
    if len(parts) != 4:
        return None

    _, score_text, name, date = parts
    if score_text == "-":
        return None

    try:
        score = int(score_text)
    except ValueError:
        return None

    return score, (name or "ANON"), date


def load_all_scores() -> dict[str, list[tuple[int, str, str]]]:
    scoreboards = _empty_scoreboards()
    if not SCORING_BOARD_MD.exists():
        write_scoring_board_md(scoreboards)
        return scoreboards

    current_difficulty = None
    for raw_line in SCORING_BOARD_MD.read_text().splitlines():
        line = raw_line.strip()
        parsed_difficulty = _parse_difficulty_header(line, scoreboards)
        if parsed_difficulty is not None:
            current_difficulty = parsed_difficulty
            continue

        if current_difficulty is None:
            continue

        parsed_score = _parse_score_line(line)
        if parsed_score is None:
            continue

        scoreboards[current_difficulty].append(parsed_score)

    for difficulty_name in scoreboards:
        scoreboards[difficulty_name].sort(key=lambda e: e[0], reverse=True)

    return scoreboards


def load_scores(difficulty: str) -> list:
    return load_all_scores().get(difficulty, [])


def save_score(difficulty: str, score: int, name: str) -> None:
    scoreboards = load_all_scores()
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    scoreboards[difficulty].append((score, name, date))
    scoreboards[difficulty].sort(key=lambda e: e[0], reverse=True)
    write_scoring_board_md(scoreboards)


def write_scoring_board_md(scoreboards: dict[str, list[tuple[int, str, str]]]) -> None:
    lines = [
        "# Scoring Board",
        "",
    ]

    for difficulty_name, _ in DIFFICULTY_CHOICES:
        scores = scoreboards.get(difficulty_name, [])
        lines.extend(
            [
                f"## {difficulty_name.upper()}",
                "",
                "| Rank | Score | Name | Date |",
                "|------|-------|------|------|",
            ]
        )

        for rank, (score, name, date) in enumerate(scores[:MAX_SCORES], start=1):
            lines.append(f"| {rank} | {score} | {name} | {date} |")

        if not scores:
            lines.append("| - | - | - | No scores recorded yet |")

        lines.append("")

    SCORING_BOARD_MD.write_text("\n".join(lines))


def ensure_scoring_board() -> None:
    if not SCORING_BOARD_MD.exists():
        write_scoring_board_md(_empty_scoreboards())


def ask_player_name(screen: curses.window, score: int, difficulty: str) -> str:
    curses.curs_set(1)
    screen.nodelay(False)
    name = ""
    max_len = 12
    width = 28
    row = 8
    col = (GRID_SIZE * CELL_WIDTH + 4 - width) // 2

    while True:
        screen.addstr(row,     col, "+" + "-" * (width - 2) + "+", curses.A_BOLD)
        screen.addstr(row + 1, col, "|" + " ENTER YOUR NAME ".center(width - 2) + "|", curses.A_BOLD)
        screen.addstr(row + 2, col, "|" + f" Score: {score}  {difficulty.upper()} ".ljust(width - 2) + "|", curses.A_BOLD)
        screen.addstr(row + 3, col, "|" + " " * (width - 2) + "|")
        screen.addstr(row + 3, col + 2, (name + "_")[: width - 4])
        screen.addstr(row + 4, col, "|" + " ENTER to confirm ".center(width - 2) + "|")
        screen.addstr(row + 5, col, "+" + "-" * (width - 2) + "+", curses.A_BOLD)
        screen.refresh()

        key = screen.getch()
        if key in (10, 13, curses.KEY_ENTER):
            break
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            name = name[:-1]
        elif 32 <= key <= 126 and len(name) < max_len:
            name += chr(key)

    curses.curs_set(0)
    screen.nodelay(True)
    return name.strip() or "ANON"


def choose_difficulty(screen: curses.window) -> tuple[str, int] | None:
    selected = 1

    while True:
        screen.erase()
        screen.addstr(3, 10, "PYTHON PYTHON", curses.A_BOLD)
        screen.addstr(5, 8, "SELECT DIFFICULTY", curses.A_BOLD)
        screen.addstr(7, 6, "UP/DOWN TO CHOOSE  ENTER TO START")
        screen.addstr(8, 6, "Q TO QUIT")

        for index, (name, tick_ms) in enumerate(DIFFICULTY_CHOICES):
            marker = ">" if index == selected else " "
            speed_text = f"{tick_ms} MS"
            row = 11 + index * 2
            screen.addstr(row, 10, f"{marker} {name.upper():<4}  {speed_text}", curses.A_BOLD if index == selected else 0)

        screen.refresh()
        key = screen.getch()

        if key in (ord("q"), ord("Q")):
            return None
        if key == curses.KEY_UP:
            selected = (selected - 1) % len(DIFFICULTY_CHOICES)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(DIFFICULTY_CHOICES)
        elif key in (10, 13, curses.KEY_ENTER):
            return DIFFICULTY_CHOICES[selected]


def run(screen: curses.window) -> None:
    ensure_scoring_board()
    configure_screen(screen)
    ensure_terminal_size(screen)
    difficulty = choose_difficulty(screen)
    if difficulty is None:
        return

    difficulty_name, tick_ms = difficulty
    set_tick_speed(screen, tick_ms)
    scores = load_scores(difficulty_name)
    game = SnakeGame(screen, difficulty_name, tick_ms, scores)

    running = True
    while running:
        game.draw()
        key = screen.getch()
        running = game.handle_key(key)
        game.update()


def main() -> None:
    curses.wrapper(run)


if __name__ == "__main__":
    main()