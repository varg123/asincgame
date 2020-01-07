import time
import curses
import asyncio
from random import randint, choice

TIC_TIMEOUT = 0.1
MIN_ROW = 0
MIN_COL = 0
MAX_ROW = 0
MAX_COL = 0
SYMBOLS = '+*.:'


async def blink(canvas, row, column, symbol='*', timeout=TIC_TIMEOUT):
    timeout *= 10000
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(int(5 * timeout)):
            await asyncio.sleep(0)
        canvas.addstr(row, column, symbol)
        for _ in range(int(3 * timeout)):
            await asyncio.sleep(0)
        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(int(5 * timeout)):
            await asyncio.sleep(0)
        canvas.addstr(row, column, symbol)
        for _ in range(int(3 * timeout)):
            await asyncio.sleep(0)


def draw(canvas):
    canvas.border()
    curses.curs_set(False)
    coroutines_stars = []
    for i in range(500):
        col, row = randint(MIN_COL, MAX_COL), randint(MIN_ROW, MAX_ROW)
        simbol = choice(SYMBOLS)
        coroutines_stars.append(blink(canvas, row, col, simbol))
    while True:
        for coroutine in coroutines_stars.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines_stars.remove(coroutine)
        canvas.refresh()


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
