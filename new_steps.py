import time
import curses
import asyncio
from random import randint, choice

TIC_TIMEOUT = 0.1


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
    for i in range(4):
        coroutines_stars.append(blink(canvas, 1, i + 1, '*'))
    while True:
        for coroutine in coroutines_stars.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines_stars.remove(coroutine)
        canvas.refresh()
        # time.sleep(1)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
