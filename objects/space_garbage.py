import asyncio
import random

from gameplay.core import event_loop, obstacles, obstacles_in_last_collisions, year
from gameplay.game_scenario import get_garbage_delay_tics
from physics.curses_tools import draw_frame, get_frame_size, go_to_sleep
from physics.explosion import explode
from physics.obstacles import Obstacle
from settings import ANIMATE_FRAME_PATH, BORDER_WIDTH, GARBAGE_FRAMES


async def fill_orbit_with_garbage(canvas):
    while True:
        garbage_frame = random.choice(GARBAGE_FRAMES)
        canvas_height, canvas_width = canvas.getmaxyx()

        with open(f'{ANIMATE_FRAME_PATH}/{garbage_frame}', "r") as garbage_file:
            frame = garbage_file.read()

        frame_height, frame_width = get_frame_size(frame)
        column = random.randint(0, canvas_width - frame_width)
        garbage = fly_garbage(canvas, column=column, garbage_frame=frame)
        garbage_delay = get_garbage_delay_tics(year[0])
        if garbage_delay:
            event_loop.append(garbage)
            await go_to_sleep(garbage_delay)
        else:
            await asyncio.sleep(0)


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()
    column = max(column, 0)
    column = min(column, columns_number - 1)

    frame_height, frame_width = get_frame_size(garbage_frame)
    obstacle = Obstacle(0, column, frame_height, frame_width)
    obstacles.append(obstacle)

    row = BORDER_WIDTH

    try:
        while row < rows_number - BORDER_WIDTH:

            obstacle.row = row
            obstacle.column = column
            if obstacle in obstacles_in_last_collisions:
                center_row, center_column = (row + (row + frame_height)) // 2, \
                                            (column + (column + frame_width)) // 2
                await explode(canvas, center_row, center_column)
                draw_frame(canvas, row, column, garbage_frame, negative=True)
                return

            draw_frame(canvas, row, column, garbage_frame)
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, garbage_frame, negative=True)
            row += speed
    finally:
        obstacles.remove(obstacle)
