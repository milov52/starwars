import curses
import random
import time

import settings
from animations import blink, draw_spaceship, fly_garbage, go_to_sleep
from curses_tools import fire, get_frame_size
from settings import BORDER_WIDTH, STAR_COUNTS, TIC_TIMEOUT

event_loop = []


async def fill_orbit_with_garbage(canvas, canvas_width):
    while True:
        garbage_frame = random.choice(settings.GARBAGE_FRAMES)

        with open(f'{settings.ANIMATE_FRAME_PATH}/{garbage_frame}', "r") as garbage_file:
            frame = garbage_file.read()

        _, frame_width = get_frame_size(frame)
        column = random.randint(0, canvas_width - frame_width)

        garbage = fly_garbage(canvas, column=column, garbage_frame=frame)

        event_loop.append(garbage)
        await go_to_sleep(settings.GARBAGE_DELAY)


def draw(canvas):
    curses.curs_set(False)
    canvas_height, canvas_width = curses.window.getmaxyx(canvas)

    coroutine_garbage = fill_orbit_with_garbage(canvas, canvas_width)

    coroutine_spaceship = draw_spaceship(canvas, canvas_width - 1, canvas_height - 1)
    coroutine_fire = fire(canvas, canvas_height // 2, canvas_width // 2)

    for _ in range(STAR_COUNTS):
        row, column = (random.randint(0, canvas_height - BORDER_WIDTH),
                       random.randint(0, canvas_width - BORDER_WIDTH))

        symbol = random.choice('+*.:')
        offset_tics = random.randint(0, 3)
        event_loop.append(blink(canvas, row, column, offset_tics, symbol))

    event_loop.append(coroutine_garbage)
    event_loop.append(coroutine_fire)
    event_loop.append(coroutine_spaceship)

    canvas.border()
    while True:
        try:
            for coroutine in event_loop.copy():
                coroutine.send(None)
        except StopIteration:
            event_loop.remove(coroutine)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
