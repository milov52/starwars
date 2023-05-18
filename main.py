import curses
import time

from gameplay.core import event_loop
from objects.animations import draw_spaceship
from objects.space_garbage import fill_orbit_with_garbage
from objects.stars import get_stars_coroutine
from settings import TIC_TIMEOUT


def draw(canvas):
    curses.curs_set(False)
    canvas.nodelay(True)
    canvas.border()

    canvas_height, canvas_width = canvas.getmaxyx()

    coroutine_garbage = fill_orbit_with_garbage(canvas, canvas_width)
    coroutine_spaceship = draw_spaceship(canvas, canvas_width - 1, canvas_height - 1)

    event_loop.append(coroutine_garbage)
    event_loop.append(coroutine_spaceship)
    event_loop.extend(get_stars_coroutine(canvas))

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
