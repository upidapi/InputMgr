import asyncio
import time

from src.Events import KeyboardEvent, any_event, MouseEvent
from src.Main.EventQueue import EventQueue
from src.Main.Keyboard import Keyboard, Hotkey
from src.Main.Mouse import Mouse
from src.OsAbstractions.Abstract.Keyboard import Down, LiteralVk


class Recorder:
    """
    records user inputs

    --------example--------
    # records until "a" is typed
    # then waits for 1 sec before playing the recording
    async def main():
        Recorder.record()

        await EventHelper.wait_for_text_typed("a")

        recording = Recorder.stop_recording()

        await asyncio.sleep(1)

        await Recorder.play(recording)

    asyncio.run(main())
    """

    # int corresponds to seconds sleep
    data: list[dict] = []

    eq: EventQueue | None = None

    @classmethod
    def _handle_event(cls, event):
        # we ignore key-send events sice they're not really
        # user inputs and only a helper for handling them
        if isinstance(event, KeyboardEvent.KeySend):
            return

        cls.data.append(event)
        return

    @classmethod
    def record(cls):
        """
        starts recording user inputs
        """
        cls.eq = EventQueue()

        async def record():
            with cls.eq:
                async for event in cls.eq:
                    cls._handle_event(event)

        # will finish eventually
        asyncio.create_task(record())

    @classmethod
    async def record_hotkey(
            cls,
            exclusive: bool = True,
            ignore_mouse: bool = True,
    ) -> Hotkey:
        pressed: set[int] = set()
        last_pressed: int = -1

        with cls.eq:
            async for event in cls.eq:
                if isinstance(event, KeyboardEvent.KeyUp):
                    return Hotkey(
                        press=last_pressed,
                        along_with=pressed,
                        exclusive=exclusive,
                        ignore_mouse=ignore_mouse,
                    )

                if isinstance(event, KeyboardEvent.KeyDown):
                    last_pressed = event.key_data.vk
                    pressed.add(last_pressed)

    @classmethod
    def stop_recording(cls):
        """
        stops the current recording and returns the recording

        can be replayed with Recorder.play(recording)
        """
        if cls.eq is None:
            raise TypeError("cant stop it since recorder not running")

        cls.eq.stop()

        data = cls.data
        cls.data = []
        return data

    @classmethod
    async def play(cls, data: [any_event]):
        """
        replays a recording (returned from stop_recording)
        with the timings preserved
        """
        if not data:
            return

        start = time.time_ns() / 10 ** 6
        initial_time = data[0].time_ms
        start_delta = start + initial_time

        for event in data:
            event: any_event
            to_exec = event.time_ms + start_delta - time.time_ns() / 10 ** 6

            if to_exec > 0:
                await asyncio.sleep(to_exec * 1000)

            if isinstance(event, KeyboardEvent.KeyDown | KeyboardEvent.KeyUp):
                dc = Down if isinstance(event, KeyboardEvent.KeyDown) else Down
                Keyboard.typewrite(
                    dc(
                        LiteralVk(
                            event.key_data
                        )
                    )
                )

            elif isinstance(event, MouseEvent.Move):
                Mouse.set_pos(*event.pos)

            elif isinstance(event, MouseEvent.Click | MouseEvent.UnClick):
                down = isinstance(event, MouseEvent.Click)

                Mouse.press_button(event.button, down)

            elif isinstance(event, MouseEvent.Scroll):
                # todo make sure that the scroll(dx, dy)
                #  == event for it (.dx, .dy)
                Mouse.scroll(event.dx, event.dy)

            else:
                raise TypeError(f"invalid event type for playback: {event}")
