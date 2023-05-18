import asyncio
import curses
import random
import time
from itertools import cycle

import settings
from obstacles import Obstacle, show_obstacles
from curses_tools import draw_frame, fire, get_frame_size, go_to_sleep, read_controls
from physics import update_speed
from settings import BORDER_WIDTH, STAR_COUNTS, TIC_TIMEOUT

event_loop = []
obstacles = []


async def run_spaceship(canvas, row, column, frame_size, animation_frames):
    canvas.nodelay(True)

    canvas_height, canvas_width = curses.window.getmaxyx(canvas)
    frame_width, frame_height = frame_size
    row_speed = column_speed = 0

    for frame in animation_frames:
        rows_direction, columns_direction, space_pressed = read_controls(canvas)

        row_speed, column_speed = update_speed(row_speed, column_speed, rows_direction, columns_direction)
        row += row_speed
        column += column_speed

        if row < BORDER_WIDTH or column < BORDER_WIDTH:
            row = max(BORDER_WIDTH, row)
            column = max(BORDER_WIDTH, column)
        else:
            row = min(row, canvas_height - BORDER_WIDTH - frame_height)
            column = min(column, canvas_width - BORDER_WIDTH - frame_width)

        if space_pressed:
            coroutine_fire = fire(canvas, row, column + frame_width // 2)
            event_loop.append(coroutine_fire)

        draw_frame(canvas, row, column, frame)
        await go_to_sleep(.1)
        draw_frame(canvas, row, column, frame, negative=True)


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


def draw_spaceship(canvas, canvas_width, canvas_height):
    with open(f"{settings.ANIMATE_FRAME_PATH}/rocket_frame_1.txt", "r") as rocket1_frame, \
            open(f"{settings.ANIMATE_FRAME_PATH}/rocket_frame_2.txt", "r") as rocket2_frame:
        frame1 = rocket1_frame.read()
        frame2 = rocket2_frame.read()

    frame_height, frame_width = get_frame_size(frame1)

    row, column = canvas_height // 2, canvas_width // 2 - frame_width // 2

    animation_frames = cycle([frame1, frame1, frame2, frame2])
    return run_spaceship(canvas, row, column, (frame_width, frame_height), animation_frames)


async def fill_orbit_with_garbage(canvas, canvas_width):
    garbage_id = 0
    while True:
        garbage_frame = 'duck.txt'  # random.choice(settings.GARBAGE_FRAMES)

        with open(f'{settings.ANIMATE_FRAME_PATH}/{garbage_frame}', "r") as garbage_file:
            frame = garbage_file.read()

        frame_height, frame_width = get_frame_size(frame)
        column = random.randint(0, canvas_width - frame_width)


        garbage = fly_garbage(canvas, column=column, garbage_frame=frame)

        event_loop.append(garbage)

        await go_to_sleep(settings.GARBAGE_DELAY)


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()
    column = max(column, 0)
    column = min(column, columns_number - 1)

    frame_height, frame_width = get_frame_size(garbage_frame)
    obstacle = Obstacle(0, column, frame_height, frame_width)
    obstacles.append(obstacle)
    obstacles_coroutine = show_obstacles(canvas, obstacles)
    event_loop.append(obstacles_coroutine)

    row = settings.BORDER_WIDTH

    try:
        while row < rows_number - settings.BORDER_WIDTH:
            draw_frame(canvas, row, column, garbage_frame)
            obstacle.row = row
            obstacle.column = column

            await asyncio.sleep(0)
            draw_frame(canvas, row, column, garbage_frame, negative=True)
            row += speed
    finally:
        obstacles.remove(obstacle)

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


def draw(canvas):
    curses.curs_set(False)
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
        canvas.addstr(3, 10, f'{len(obstacles)}', curses.A_BOLD)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
