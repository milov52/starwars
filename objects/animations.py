import asyncio
import curses
from itertools import cycle

from gameplay.core import event_loop, obstacles, obstacles_in_last_collisions
from gameplay.messages import show_gameover
from physics.curses_tools import draw_frame, get_frame_size, go_to_sleep, read_controls
from physics.physics import update_speed
from settings import ANIMATE_FRAME_PATH, BORDER_WIDTH


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                obstacles_in_last_collisions.append(obstacle)
                return

        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def run_spaceship(canvas, row, column, frame_size, animation_frames):
    canvas_height, canvas_width = canvas.getmaxyx()
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

        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                show_gameover(canvas)
                return

        draw_frame(canvas, row, column, frame)
        await go_to_sleep(.1)
        draw_frame(canvas, row, column, frame, negative=True)


def draw_spaceship(canvas):
    canvas_height, canvas_width = canvas.getmaxyx()

    with open(f"{ANIMATE_FRAME_PATH}/rocket_frame_1.txt", "r") as rocket1_frame, \
            open(f"{ANIMATE_FRAME_PATH}/rocket_frame_2.txt", "r") as rocket2_frame:
        frame1 = rocket1_frame.read()
        frame2 = rocket2_frame.read()

    frame_height, frame_width = get_frame_size(frame1)
    row, column = canvas_height // 2, canvas_width // 2 - frame_width // 2

    animation_frames = cycle([frame1, frame1, frame2, frame2])
    return run_spaceship(canvas, row, column, (frame_width, frame_height), animation_frames)
