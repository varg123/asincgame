import time
import curses
import asyncio
from random import randint, choice
from fire_animation import fire
from curses_tools import draw_frame, read_controls, get_frame_size
from space_garbage import fly_garbage
from os.path import abspath, dirname, join
from itertools import cycle
from physics import update_speed

TIC_TIMEOUT = 0.1
MIN_ROW = 0
MIN_COL = 0
MAX_ROW = 0
MAX_COL = 0
SYMBOLS = '+*.:'
DIR_FRAMES = join(dirname(abspath(__file__)), 'frames')


def get_garbage_frame(name):
    with open(join(DIR_FRAMES, f"{name}.txt"), 'rt', encoding='utf8') as frame_file:
        return frame_file.read()


def get_space_ship_frames():
    names_of_the_frames = [
        'rocket_frame_1.txt',
        'rocket_frame_2.txt'
    ]
    for name in names_of_the_frames:
        with open(join(DIR_FRAMES, name), 'rt', encoding='utf8') as frame_file:
            yield frame_file.read()


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
    row, column = 5, 8
    row_speed = column_speed = 0
    while True:
        last_spaceship_frame = spaceship_frame
        row_control, col_control, space_control = read_controls(canvas)
        row_size, column_size = get_frame_size(last_spaceship_frame)
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

        draw_frame(canvas, row, column, last_spaceship_frame)
        await sleep(1)
        draw_frame(canvas, row, column, last_spaceship_frame, True)


async def animate_spaceship(canvas):
    global spaceship_frame
    for frame in cycle(get_space_ship_frames()):
        spaceship_frame = frame
        await sleep()


async def fill_orbit_with_garbage(canvas):
    garbage = [
        'duck',
        'hubble',
        'lamp',
        'trash_large',
        'trash_small',
        'trash_xl'
    ]
    loop = asyncio.get_event_loop()
    while True:
        garbage_name = choice(garbage)
        column = randint(MIN_COL, MAX_COL)
        coroutines.append(fly_garbage(canvas, column, get_garbage_frame(garbage_name)))
        await sleep(10)


def draw(canvas):
    canvas.border()
    curses.curs_set(False)
    global coroutines
    coroutines = []
    global spaceship_frame
    spaceship_frame = list(get_space_ship_frames())[0]  # TODO: убрать индексное обращение
    for i in range(100):
        col, row = randint(MIN_COL, MAX_COL), randint(MIN_ROW, MAX_ROW)
        simbol = choice(SYMBOLS)
        start_timeout = randint(1, 10)
        coroutines.append(blink(canvas, row, col, simbol, start_timeout))
    start_row = int((MAX_ROW - MIN_ROW) / 2 + MIN_ROW)
    start_column = int((MAX_COL - MIN_COL) / 2 + MIN_COL)
    coroutines.append(fire(canvas, start_row, start_column))
    coroutines.append(animate_spaceship(canvas))
    coroutines.append(run_spaceship(canvas))
    # coroutines.append(fly_garbage(canvas, 10, get_garbage_frame('duck')))
    coroutines.append(fill_orbit_with_garbage(canvas))

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


def init_scope_range():
    global window
    window = curses.initscr()
    rows_count, cols_count = window.getmaxyx()
    global MAX_ROW, MAX_COL, MIN_ROW, MIN_COL
    MAX_ROW, MAX_COL = rows_count - 2, cols_count - 2
    MIN_ROW, MIN_COL = 1, 1
    window.nodelay(True)


if __name__ == '__main__':
    init_scope_range()
    curses.update_lines_cols()
    curses.wrapper(draw)
