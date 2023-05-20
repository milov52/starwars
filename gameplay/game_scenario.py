import asyncio

from gameplay.core import year
from physics.curses_tools import draw_frame, go_to_sleep


PHRASES = {
    # Только на английском, Repl.it ломается на кириллице
    1957: "First Sputnik",
    1961: "Gagarin flew!",
    1969: "Armstrong got on the moon!",
    1971: "First orbital space station Salute-1",
    1981: "Flight of the Shuttle Columbia",
    1998: 'ISS start building',
    2011: 'Messenger launch to Mercury',
    2020: "Take the plasma gun! Shoot the garbage!",
}

def get_garbage_delay_tics(year):
    if year < 1961:
        return None
    elif year < 1969:
        return 20
    elif year < 1981:
        return 14
    elif year < 1995:
        return 10
    elif year < 2010:
        return 8
    elif year < 2020:
        return 6
    else:
        return 2

async def show_message(canvas):
    while True:
        phrase = PHRASES.get(year[0])

        canvas.border()
        if phrase is None:
            frame = f"Year: {year[0]}"
        else:
            frame = f"Year: {year[0]}\n{phrase}"
        draw_frame(canvas, 1, 1, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, 1, 1, frame, negative=True)