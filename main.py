import time
import curses
import asyncio
from random import randint, choice
import fire_animation

TIC_TIMEOUT = 0.1
MIN_ROW = 0
MIN_COL = 0
MAX_ROW = 0
MAX_COL = 0
SYMBOLS = '+*.:'


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
    coroutines.append(fire_animation.fire(canvas, start_row, start_column))
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


if __name__ == '__main__':
    init_scope_range()
    curses.update_lines_cols()
    curses.wrapper(draw)
