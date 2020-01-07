import time
import curses
import asyncio


# документация curses  https://docs.python.org/3/library/curses.html#curses.resizeterm

def draw(canvas):  # холст в качестве параметра
    row, column = (5, 20)  # строка столбец (координаты, точка) начала текста
    curses.curs_set(False)  # отключение мигания курсора
    canvas.border()  # добавление рамки
    canvas.addstr(row, column, 'Hello, World!' + str(curses.COLS))  # добавление строки
    # canvas.addstr(row, column, 'PRESS START', curses.A_BOLD)
    # canvas.addstr(row, column, 'PRESS START', curses.A_REVERSE | curses.A_BOLD)
    char = canvas.getch()
    print(f"Вы ввели {char}")
    key = canvas.getkey()
    print(f"Вы ввели {key}")

    # Если вы введёте g, то canvas.getch() вернёт код буквы — 103. canvas.getkey() вернёт сам символ — g.
    # Если вы нажмёте клавишу "вверх", canvas.getch() вернёт код клавиши — 259. canvas.getkey() вернёт KEY_UP.
    # Если ввода пользователя ждать не хочется, можно вызвать функцию canvas.nodelay(True).

    canvas.refresh()  # обновление холста
    time.sleep(1)


def draw_star(canvas):
    row, column = (5, 20)
    curses.curs_set(False)
    star_char = "*"
    while True:
        canvas.addstr(row, column, star_char, curses.A_DIM)
        time.sleep(2)
        canvas.refresh()
        canvas.addstr(row, column, star_char)
        time.sleep(2)
        canvas.refresh()
        canvas.addstr(row, column, star_char, curses.A_BOLD)
        time.sleep(2)
        canvas.refresh()
        canvas.addstr(row, column, star_char)
        time.sleep(2)
        canvas.refresh()


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)


def draw_asinc_star(canvas):
    row, column = (5, 20)
    curses.curs_set(False)
    star_char = "*"
    corutine_star = blink(canvas, row, column, star_char)
    while True:
        corutine_star.send(None)
        canvas.refresh()
        time.sleep(1)


def draw_5_stars(canvas):
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
        time.sleep(1)


if __name__ == '__main__':
    curses.update_lines_cols()  # иницализирует терминал ( записывает canvas.LINES и canvas.COLS)
    # curses.wrapper(draw)
    # curses.wrapper(draw_star)
    # curses.wrapper(draw_asinc_star)
    curses.wrapper(draw_5_stars)
