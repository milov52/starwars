import curses

from physics.curses_tools import draw_frame, get_frame_size


def show_gameover(canvas):
    with open("gameplay/frames/gameover.txt", "r") as file:
        gameover_frame = file.read()

    canvas_height, canvas_width = curses.window.getmaxyx(canvas)
    frame_height, frame_width = get_frame_size(gameover_frame)
    row = (canvas_height - frame_height) // 2
    column = (canvas_width - frame_width) // 2
    draw_frame(canvas, row, column, gameover_frame)