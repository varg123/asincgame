import time
import curses
import asyncio
from random import randint, choice
import curses_tools

TIC_TIMEOUT = 0.1
SYMBOLS = '+*.:'


async def animate_spaceship(canvas, start_row, start_column, frames):
    row, column = start_row, start_column
    first_frame, second_frame = frames
    while True:
        curses_tools.draw_frame(canvas, round(row), round(column), first_frame)
        await asyncio.sleep(0)
        curses_tools.draw_frame(
            canvas,
            round(row),
            round(column),
            first_frame,
            negative=True
        )
        curses_tools.draw_frame(
            canvas,
            round(row),
            round(column),
            second_frame
        )
        await asyncio.sleep(0)
        row_difference, column_difference, _ = curses_tools.read_controls(canvas)
        rcount, ccount = curses_tools.get_frame_size(second_frame)
        mrcount, mccount = canvas.getmaxyx()
        curses_tools.draw_frame(
            canvas,
            round(row),
            round(column),
            second_frame,
            negative=True
        )
        if row > 1 and row_difference < 0:
            row += row_difference
        if row_difference > 0 and row < mrcount-rcount-1:
            row += row_difference
        if column < mccount-ccount-1 and column_difference > 0:
            column += column_difference
        if column_difference < 0 and column > 1:
            column += column_difference


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot. Direction and speed can be specified."""
    row, column = start_row, start_column
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
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def blink(canvas, row, column, symbol='*', timeout=0):
    while True:
        for _ in range(timeout):
            await asyncio.sleep(0)
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(20):
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
    max_column, max_row = window.getmaxyx()
    frames = []
    for frame_index in range(2):
        frame_index += 1
        with open(
            f'frames/rocket_frame_{frame_index}.txt',
            'rt',
            encoding='utf8'
        ) as file:
            frames.append(file.read())
    coroutines = [
        blink(
            canvas,
            randint(2, max_column-2),
            randint(2, max_row-2),
            symbol=choice(SYMBOLS),
            timeout=randint(10, 30)
        ) for i in range(100)]
    coroutinefire = fire(canvas, max_column//2, max_row//2)
    coroutineship = animate_spaceship(
        canvas,
        max_column//2,
        max_row//2,
        frames
    )
    coroutines.extend([coroutinefire, coroutineship])
    canvas.nodelay(True)
    while True:
        for cor in coroutines:
            try:
                cor.send(None)
            except StopIteration:
                coroutines.remove(cor)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


def main():
    global window
    window = curses.initscr()
    curses.update_lines_cols()
    curses.curs_set(False)
    curses.wrapper(draw)

if __name__ == '__main__':
    main()
