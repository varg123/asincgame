import time
import curses
import asyncio
from random import randint, choice
# from fire_animation import fire
from curses_tools import draw_frame, read_controls, get_frame_size
# from space_garbage import fly_garbage
from os.path import abspath, dirname, join
from itertools import cycle
from physics import update_speed
from obstacles import Obstacle, show_obstacles
from explosion import explode

TIC_TIMEOUT = 0.1
MIN_ROW = 0
MIN_COL = 0
MAX_ROW = 0
MAX_COL = 0
SYMBOLS = '+*.:'
DIR_FRAMES = join(dirname(abspath(__file__)), 'frames')


def get_frame(name):
    with open(join(DIR_FRAMES, f"{name}.txt"), 'rt', encoding='utf8') as frame_file:
        return frame_file.read()


def get_space_ship_frames():
    names_of_the_frames = [
        'rocket_frame_1',
        'rocket_frame_2'
    ]
    for name in names_of_the_frames:
        yield get_frame(name)


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol='*', timeout=0):
    timeout = int(timeout)
    while True:
        await sleep(timeout)
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(5)
        canvas.addstr(row, column, symbol)
        await sleep(3)
        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(5)
        canvas.addstr(row, column, symbol)
        await sleep(3)


async def run_spaceship(canvas):
    global spaceship_frame
    global coroutines
    row, column = 5, 8
    row_speed = column_speed = 0
    while True:
        last_spaceship_frame = spaceship_frame
        row_control, col_control, space_control = read_controls(canvas)

        row_size, column_size = get_frame_size(last_spaceship_frame)
        if space_control:
            coroutines.append(fire(canvas, row, column + column_size // 2))
        row_range = range(MIN_ROW + 1, MAX_ROW - row_size + 1)
        column_range = range(MIN_COL + 1, MAX_COL - column_size + 1)

        row_speed, column_speed = update_speed(row_speed, column_speed, row_control, col_control)
        row += row_speed
        column += column_speed

        # TODO: перестало работать ограничение корабля, поправить

        # if row+row_speed in range(MIN_ROW + 1, MAX_ROW - row_size + 1):
        #     row += row_speed
        # elif row_speed > 0 and row == MIN_ROW:
        #     row += row_speed
        # elif row_speed < 0 and row == MAX_ROW - row_size + 1:
        #     row += row_speed
        # if column+column_speed in range(MIN_COL + 1, MAX_COL - column_size + 1):
        #     column += column_speed
        # elif column_speed > 0 and column == MIN_COL:
        #     column += column_speed
        # elif column_speed < 0 and column == MAX_COL - column_size + 1:
        #     column += column_speed

        for obstacle in obstacles:
            if obstacle.has_collision(row, column, row_size, column_size):
                coroutines.append(show_gameover(canvas))
                return

        draw_frame(canvas, row, column, last_spaceship_frame)
        await sleep(1)
        draw_frame(canvas, row, column, last_spaceship_frame, True)


async def animate_spaceship(canvas):
    global spaceship_frame
    for frame in cycle(get_space_ship_frames()):
        spaceship_frame = frame
        await sleep()


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    global obstacles
    global obstacles_in_last_collisions
    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        garbage_height, garbage_length = get_frame_size(garbage_frame)
        obstacle = Obstacle(row, column, garbage_height, garbage_length)
        obstacles.append(obstacle)
        await asyncio.sleep(0)

        draw_frame(canvas, row, column, garbage_frame, negative=True)
        obstacles.remove(obstacle)
        if obstacle in obstacles_in_last_collisions:
            await explode(canvas, row + garbage_height // 2, column + garbage_length // 2)
            obstacles_in_last_collisions.remove(obstacle)
            return
        row += speed


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot. Direction and speed can be specified."""
    global obstacles
    row, column = start_row, start_column
    global obstacles_in_last_collisions

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                obstacles_in_last_collisions.append(obstacle)
                return
        # if any(map(lambda x: x.has_collision(row, column), obstacles)):
        #     return
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def fill_orbit_with_garbage(canvas):
    garbage = [
        'duck',
        'hubble',
        'lamp',
        'trash_large',
        'trash_small',
        'trash_xl'
    ]
    while True:
        garbage_name = choice(garbage)
        column = randint(MIN_COL, MAX_COL)
        coroutines.append(fly_garbage(canvas, column, get_frame(garbage_name)))
        await sleep(10)


async def show_gameover(canvas):
    game_over_frame = get_frame('game_over')
    game_over_height, game_over_length = get_frame_size(game_over_frame)
    row = (MAX_ROW - game_over_height) // 2
    column = (MAX_COL - game_over_length) // 2
    while True:
        draw_frame(canvas, row, column, game_over_frame)
        await sleep(1)
        draw_frame(canvas, row, column, game_over_frame, True)


async def show_footer_message(canvas):
    message = str(year)
    row = 1
    column = (MAX_COL_FOOTER - len(message)) // 2
    while True:
        window_footer.addstr(row, column, message)
        await asyncio.sleep(0)


def draw(canvas):
    canvas.border()
    curses.curs_set(False)
    global coroutines
    coroutines = []
    global obstacles_in_last_collisions
    obstacles_in_last_collisions = []
    global spaceship_frame
    spaceship_frame = list(get_space_ship_frames())[0]  # TODO: убрать индексное обращение
    global obstacles
    obstacles = []
    global year
    year = 1957
    for i in range(100):
        col, row = randint(MIN_COL, MAX_COL), randint(MIN_ROW, MAX_ROW)
        simbol = choice(SYMBOLS)
        start_timeout = randint(1, 10)
        coroutines.append(blink(canvas, row, col, simbol, start_timeout))
    start_row = int((MAX_ROW - MIN_ROW) / 2 + MIN_ROW)
    start_column = int((MAX_COL - MIN_COL) / 2 + MIN_COL)
    # coroutines.append(fire(canvas, start_row, start_column))
    coroutines.append(animate_spaceship(canvas))
    coroutines.append(run_spaceship(canvas))
    coroutines.append(show_obstacles(canvas, obstacles))
    # coroutines.append(fly_garbage(canvas, 10, get_frame('duck')))
    coroutines.append(fill_orbit_with_garbage(canvas))
    coroutines.append(show_footer_message(canvas))

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.border()
        canvas.refresh()
        window_footer.refresh()
        time.sleep(TIC_TIMEOUT)


def init_scope_range():
    global window
    window = curses.initscr()
    rows_count, cols_count = window.getmaxyx()
    global MAX_ROW, MAX_COL, MIN_ROW, MIN_COL
    MAX_ROW, MAX_COL = rows_count - 2, cols_count - 2
    MIN_ROW, MIN_COL = 1, 1
    window.nodelay(True)
    global window_footer
    window_footer = window.derwin(3, MAX_COL, MAX_ROW - 1, 1)
    rows_count, cols_count = window_footer.getmaxyx()
    global MAX_ROW_FOOTER, MAX_COL_FOOTER, MIN_ROW_FOOTER, MIN_COL_FOOTER
    MAX_ROW_FOOTER, MAX_COL_FOOTER = rows_count - 2, cols_count - 2
    MIN_ROW_FOOTER, MIN_COL_FOOTER = 1, 1
    window_footer.nodelay(True)


if __name__ == '__main__':
    init_scope_range()
    curses.update_lines_cols()
    curses.wrapper(draw)
