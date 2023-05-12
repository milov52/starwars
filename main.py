import asyncio
import curses
import random
import time

from curses_tools import draw_frame, fire, get_frame_size, read_controls

TIC_TIMEOUT = 0.1
STAR_COUNTS = 100


async def go_to_sleep(seconds):
    iteration_count = int(seconds * 10)
    for _ in range(iteration_count):
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol='*'):
    while True:
        await go_to_sleep(random.randint(0, 3))
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await go_to_sleep(2)
        canvas.addstr(row, column, symbol)
        await go_to_sleep(.3)
        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await go_to_sleep(.5)
        canvas.addstr(row, column, symbol)
        await go_to_sleep(.3)


async def animate_spaceship(canvas, row, column, frame1, frame2):
    canvas.nodelay(True)
    frame_row, frame_column = get_frame_size(frame1)
    max_y, max_x = curses.window.getmaxyx(canvas)

    while True:
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        row += rows_direction
        column += columns_direction

        row = max(0, row) and min(row, max_y - frame_row)
        column = max(0, column) and min(column, max_x - frame_column)

        draw_frame(canvas, row, column, frame1),
        canvas.refresh()
        await go_to_sleep(.1)
        draw_frame(canvas, row, column, frame1, negative=True),

        draw_frame(canvas, row, column, frame2),
        canvas.refresh()
        await go_to_sleep(.1)
        draw_frame(canvas, row, column, frame2, negative=True)


def draw_spaceship(canvas, max_x, max_y):
    with open("figures/rocket_frame_1.txt", "r") as rocket1_frame, \
            open("figures/rocket_frame_2.txt", "r") as rocket2_frame:
        frame1 = rocket1_frame.read()
        frame2 = rocket2_frame.read()

    return animate_spaceship(canvas, max_y // 2, max_x // 2 - 2, frame1, frame2)


def draw(canvas):

    curses.curs_set(False)
    max_y, max_x = curses.window.getmaxyx(canvas)

    coroutine_spaceship = draw_spaceship(canvas, max_x, max_y)
    coroutine_fire = fire(canvas, max_y // 2, max_x // 2)

    coroutines = []
    for _ in range(STAR_COUNTS):
        row, column = (random.randint(0, max_y - 1), random.randint(0, max_x - 1))
        symbol = random.choice('+*.:')
        coroutines.append(blink(canvas, row, column, symbol))

    coroutines.append(coroutine_fire)
    coroutines.append(coroutine_spaceship)
    while True:
        try:
            canvas.border()
            for coroutine in coroutines.copy():
                coroutine.send(None)

            canvas.refresh()
            time.sleep(TIC_TIMEOUT)
        except StopIteration:
            coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
