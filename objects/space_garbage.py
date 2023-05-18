import asyncio
import random

from settings import BORDER_WIDTH, ANIMATE_FRAME_PATH, GARBAGE_DELAY
from gameplay.core import obstacles, obstacles_in_last_collisions, event_loop
from physics.curses_tools import draw_frame, get_frame_size, go_to_sleep
from physics.explosion import explode
from physics.obstacles import Obstacle


async def fill_orbit_with_garbage(canvas, canvas_width):
    while True:
        garbage_frame = 'duck.txt'  # random.choice(settings.GARBAGE_FRAMES)

        with open(f'{ANIMATE_FRAME_PATH}/{garbage_frame}', "r") as garbage_file:
            frame = garbage_file.read()

        frame_height, frame_width = get_frame_size(frame)
        column = random.randint(0, canvas_width - frame_width)
        garbage = fly_garbage(canvas, column=column, garbage_frame=frame)
        event_loop.append(garbage)

        await go_to_sleep(GARBAGE_DELAY)


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()
    column = max(column, 0)
    column = min(column, columns_number - 1)

    frame_height, frame_width = get_frame_size(garbage_frame)
    obstacle = Obstacle(0, column, frame_height, frame_width)
    obstacles.append(obstacle)
    # obstacles_coroutine = show_obstacles(canvas, obstacles)
    # event_loop.append(obstacles_coroutine)

    row = BORDER_WIDTH

    try:
        while row < rows_number - BORDER_WIDTH:
            draw_frame(canvas, row, column, garbage_frame)
            obstacle.row = row
            obstacle.column = column
            if obstacle in obstacles_in_last_collisions:
                await explode(canvas, row, column)
                draw_frame(canvas, row, column, garbage_frame, negative=True)
                return

            await asyncio.sleep(0)
            draw_frame(canvas, row, column, garbage_frame, negative=True)
            row += speed
    finally:
        obstacles.remove(obstacle)