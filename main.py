import time
import curses
import asyncio
from random import randint, choice
from fire_animation import fire
from curses_tools import draw_frame, read_controls, get_frame_size
from os.path import abspath, dirname, join

TIC_TIMEOUT = 0.1
MIN_ROW = 0
MIN_COL = 0
MAX_ROW = 0
MAX_COL = 0
SYMBOLS = '+*.:'
DIR_FRAMES = join(dirname(abspath(__file__)), 'frames')


def get_space_ship_frames():
    names_of_the_frames = [
        'rocket_frame_1.txt',
        'rocket_frame_2.txt'
    ]
    for name in names_of_the_frames:
        with open(join(DIR_FRAMES, name), 'rt', encoding='utf8') as frame_file:
            yield frame_file.read()


async def blink(canvas, row, column, symbol='*', timeout=0):
    timeout = int(timeout)
    while True:
        for _ in range(timeout):
            await asyncio.sleep(0)
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(5):
            await asyncio.sleep(0)
        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)
        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)
        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)


async def animate_spaceship(canvas, row, column):
    while True:
        for frame in get_space_ship_frames():
            row_up, col_up, _ = read_controls(canvas)
            row_size, column_size = get_frame_size(frame)
            if row in range(MIN_ROW + 1, MAX_ROW - row_size + 1):
                row += row_up
            elif row_up > 0 and row == MIN_ROW:
                row += row_up
            elif row_up < 0 and row == MAX_ROW - row_size + 1:
                row += row_up

            if column in range(MIN_COL + 1, MAX_COL - column_size + 1):
                column += col_up
            elif col_up > 0 and column == MIN_COL:
                column += col_up
            elif col_up < 0 and column == MAX_COL - column_size + 1:
                column += col_up

            draw_frame(canvas, row, column, frame)
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, frame, True)


def draw(canvas):
    canvas.border()
    curses.curs_set(False)
    coroutines = []
    for i in range(100):
        col, row = randint(MIN_COL, MAX_COL), randint(MIN_ROW, MAX_ROW)
        simbol = choice(SYMBOLS)
        start_timeout = randint(1, 10)
        coroutines.append(blink(canvas, row, col, simbol, start_timeout))
    start_row = int((MAX_ROW - MIN_ROW) / 2 + MIN_ROW)
    start_column = int((MAX_COL - MIN_COL) / 2 + MIN_COL)
    coroutines.append(fire(canvas, start_row, start_column))
    coroutines.append(animate_spaceship(canvas, 4, 20))
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
