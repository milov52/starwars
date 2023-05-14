import asyncio
import curses
import random
import time
from itertools import cycle

from curses_tools import draw_frame, fire, get_frame_size, read_controls

TIC_TIMEOUT = 0.1
STAR_COUNTS = 100
BORDER_WIDTH = 1
ANIMATE_FRAME_PATH = 'figures'


async def go_to_sleep(seconds):
    iteration_count = int(seconds * 10)
    for _ in range(iteration_count):
        await asyncio.sleep(0)


async def blink(canvas, row, column, offset_tics, symbol='*'):
    while True:
        await go_to_sleep(offset_tics)
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await go_to_sleep(2)
        canvas.addstr(row, column, symbol)
        await go_to_sleep(.3)
        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await go_to_sleep(.5)
        canvas.addstr(row, column, symbol)
        await go_to_sleep(.3)


async def animate_spaceship(canvas, row, column, frame_size, animation_frames):
    canvas.nodelay(True)

    canvas_height, canvas_width = curses.window.getmaxyx(canvas)
    frame_width, frame_height = frame_size

    for frame in animation_frames:
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        row += rows_direction
        column += columns_direction

        if row < BORDER_WIDTH or column < BORDER_WIDTH:
            row = max(BORDER_WIDTH, row)
            column = max(BORDER_WIDTH, column)
        else:
            row = min(row, canvas_height - BORDER_WIDTH - frame_height)
            column = min(column, canvas_width - BORDER_WIDTH - frame_width)

        draw_frame(canvas, row, column, frame)
        await go_to_sleep(.1)
        draw_frame(canvas, row, column, frame, negative=True)


def draw_spaceship(canvas, canvas_width, canvas_height):
    with open(f"{ANIMATE_FRAME_PATH}/rocket_frame_1.txt", "r") as rocket1_frame, \
            open(f"{ANIMATE_FRAME_PATH}/rocket_frame_2.txt", "r") as rocket2_frame:
        frame1 = rocket1_frame.read()
        frame2 = rocket2_frame.read()

    frame_height, frame_width = get_frame_size(frame1)

    row, column = canvas_height // 2, canvas_width // 2 - frame_width // 2

    animation_frames = cycle([frame1, frame2])
    return animate_spaceship(canvas, row, column, (frame_width, frame_height), animation_frames)


def draw(canvas):
    curses.curs_set(False)
    canvas_height, canvas_width = curses.window.getmaxyx(canvas)

    coroutine_spaceship = draw_spaceship(canvas, canvas_width - 1, canvas_height - 1)
    coroutine_fire = fire(canvas, canvas_height // 2, canvas_width // 2)

    coroutines = []
    for _ in range(STAR_COUNTS):
        row, column = (random.randint(0, canvas_height - BORDER_WIDTH),
                       random.randint(0, canvas_width - BORDER_WIDTH))

        symbol = random.choice('+*.:')
        offset_tics = random.randint(0, 3)
        coroutines.append(blink(canvas, row, column, offset_tics, symbol))

    coroutines.append(coroutine_fire)
    coroutines.append(coroutine_spaceship)
    canvas.border()
    while True:
        try:
            for coroutine in coroutines.copy():
                coroutine.send(None)

            canvas.refresh()
            time.sleep(TIC_TIMEOUT)
        except StopIteration:
            coroutines.remove(coroutine)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
