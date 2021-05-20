import asyncio
from contextlib import suppress


async def paint_window_for(window, time: float = 2):
    """
    Paint a window for a number of seconds

    Args:
        window: The window to paint
        time: How long to paint the window
    """

    async def _paint_task():
        with suppress(asyncio.CancelledError):
            while True:
                await window.debug_paint()

    paint_task = asyncio.create_task(_paint_task())
    await asyncio.sleep(time)
    paint_task.cancel()
