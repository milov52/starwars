import curses
import time

from gameplay.core import event_loop, year
from gameplay.game_scenario import show_message
from objects.animations import draw_spaceship
from objects.space_garbage import fill_orbit_with_garbage
from objects.stars import get_stars_coroutine
from settings import TIC_TIMEOUT



def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)

    # cnv = canvas.derwin(5, 40, max_y - 5, max_x - 40)
    canvas_height, canvas_width = canvas.getmaxyx()
    canvas.nodelay(True)
    info_place = canvas.derwin(4, 40, canvas_height - 4, canvas_width - 40)

    coroutine_garbage = fill_orbit_with_garbage(canvas)
    coroutine_spaceship = draw_spaceship(canvas)
    coroutines_message = show_message(info_place)

    event_loop.extend(get_stars_coroutine(canvas))
    event_loop.append(coroutine_garbage)
    event_loop.append(coroutine_spaceship)

    cnt = 0
    while True:
        try:
            for coroutine in event_loop.copy():
                coroutine.send(None)
            coroutines_message.send(None)
        except StopIteration:
            event_loop.remove(coroutine)

        canvas.refresh()
        info_place.refresh()
        time.sleep(TIC_TIMEOUT)
        if cnt % 15 == 0:
            year[0] += 1
        cnt += 1


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
