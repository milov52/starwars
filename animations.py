import asyncio
import curses
from itertools import cycle
from physics import update_speed

import settings
from curses_tools import draw_frame, get_frame_size, read_controls
from settings import ANIMATE_FRAME_PATH, BORDER_WIDTH

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


def draw_spaceship(canvas, canvas_width, canvas_height):
    with open(f"{ANIMATE_FRAME_PATH}/rocket_frame_1.txt", "r") as rocket1_frame, \
            open(f"{ANIMATE_FRAME_PATH}/rocket_frame_2.txt", "r") as rocket2_frame:
        frame1 = rocket1_frame.read()
        frame2 = rocket2_frame.read()

    frame_height, frame_width = get_frame_size(frame1)

    row, column = canvas_height // 2, canvas_width // 2 - frame_width // 2

    animation_frames = cycle([frame1, frame1, frame2, frame2])
    return animate_spaceship(canvas, row, column, (frame_width, frame_height), animation_frames)


async def animate_spaceship(canvas, row, column, frame_size, animation_frames):
    canvas.nodelay(True)

    canvas_height, canvas_width = curses.window.getmaxyx(canvas)
    frame_width, frame_height = frame_size
    row_speed = column_speed = 0

    for frame in animation_frames:
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        if space_pressed:
            pass

        row_speed, column_speed = update_speed(row_speed, column_speed, rows_direction, columns_direction)
        row += row_speed
        column += column_speed

        if row < BORDER_WIDTH or column < BORDER_WIDTH:
            row = max(BORDER_WIDTH, row)
            column = max(BORDER_WIDTH, column)
        else:
            row = min(row, canvas_height - BORDER_WIDTH - frame_height)
            column = min(column, canvas_width - BORDER_WIDTH - frame_width)

        draw_frame(canvas, row, column, frame)
        await go_to_sleep(.1)
        draw_frame(canvas, row, column, frame, negative=True)


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = settings.BORDER_WIDTH

    while row < rows_number-settings.BORDER_WIDTH:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed
