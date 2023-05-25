import curses
import time

from gameplay.core import coroutins, year
from gameplay.game_scenario import show_message
from objects.animations import draw_spaceship
from objects.space_garbage import fill_orbit_with_garbage
from objects.stars import get_stars_coroutine
from settings import TIC_TIMEOUT



def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)

    canvas_height, canvas_width = canvas.getmaxyx()
    canvas.nodelay(True)
    info_place = canvas.derwin(4, 40, canvas_height - 4, canvas_width - 40)

    coroutine_garbage = fill_orbit_with_garbage(canvas)
    coroutine_spaceship = draw_spaceship(canvas)
    coroutines_message = show_message(info_place)

    coroutins.extend(get_stars_coroutine(canvas))
    coroutins.append(coroutine_garbage)
    coroutins.append(coroutine_spaceship)

    cnt = 0
    while True:
        try:
            for coroutine in coroutins.copy():
                coroutine.send(None)
            coroutines_message.send(None)
        except StopIteration:
            coroutins.remove(coroutine)

        canvas.refresh()
        info_place.refresh()
        time.sleep(TIC_TIMEOUT)
        if cnt % 15 == 0:
            year[0] += 1
        cnt += 1


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
