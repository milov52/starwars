import curses
import random

from physics.curses_tools import go_to_sleep
from settings import BORDER_WIDTH, STAR_COUNTS


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


def get_stars_coroutine(canvas):
    canvas_height, canvas_width = canvas.getmaxyx()
    stars_coroutine = []
    for _ in range(STAR_COUNTS):
        row, column = (random.randint(0, canvas_height - BORDER_WIDTH),
                       random.randint(0, canvas_width - BORDER_WIDTH))

        symbol = random.choice('+*.:')
        offset_tics = random.randint(0, 3)
        stars_coroutine.append(blink(canvas, row, column, offset_tics, symbol))
    return stars_coroutine