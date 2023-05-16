import curses
import curses
import random
import time
from itertools import cycle

from animations import blink, draw_spaceship
from curses_tools import fire, get_frame_size
from settings import BORDER_WIDTH, STAR_COUNTS, TIC_TIMEOUT


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
        except StopIteration:
            coroutines.remove(coroutine)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
