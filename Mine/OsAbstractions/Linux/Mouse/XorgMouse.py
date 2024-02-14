import contextlib

from Mine.OsAbstractions.Abstract import AbsMouse

import Xlib.display
import Xlib.ext
import Xlib.ext.xtest
import Xlib.X
import Xlib.protocol


class X11Error(Exception):
    """An error that is thrown at the end of a code block managed by a
    :func:`display_manager` if an *X11* error occurred.
    """
    pass


@contextlib.contextmanager
def display_manager(display):
    """Traps *X* errors and raises an :class:``X11Error`` at the end if any
    error occurred.

    This handler also ensures that the :class:`Xlib.display.Display` being
    managed is sync'd.

    :param Xlib.display.Display display: The *X* display.

    :return: the display
    :rtype: Xlib.display.Display
    """
    errors = []

    def handler(*args):
        """The *Xlib* error handler.
        """
        errors.append(args)

    old_handler = display.set_error_handler(handler)
    try:
        yield display
        display.sync()
    finally:
        display.set_error_handler(old_handler)
    if errors:
        raise X11Error(errors)


class ButtonEnum:
    unknown = None

    left = 1
    middle = 2
    right = 3

    scroll_up = 4
    scroll_down = 5
    scroll_left = 6
    scroll_right = 7


class LinuxXLibMouse(AbsMouse):
    # todo possibly move this to an init
    _display = Xlib.display.Display()

    def __del__(self):
        # todo possibly move this to a set close meth
        if hasattr(self, '_display'):
            self._display.close()

    @classmethod
    def _check_bounds(cls, *args):
        """Checks the arguments and makes sure they are within the bounds of a
        short integer.

        :param args: The values to verify.
        """
        if not all(
                (-0x7fff - 1) <= number <= 0x7fff
                for number in args):
            raise ValueError(args)
        else:
            return tuple(int(p) for p in args)

    @classmethod
    def set_pos(cls, x: int, y: int):
        px, py = cls._check_bounds(x, y)
        with display_manager(cls._display) as dm:
            Xlib.ext.xtest.fake_input(
                dm,
                Xlib.X.MotionNotify,
                x=px,
                y=py
            )

    @classmethod
    def get_pos(cls) -> (int, int):
        with display_manager(cls._display) as dm:
            qp = dm.screen().root.query_pointer()
            return qp.root_x, qp.root_y

    @classmethod
    def _press_button(cls, button: int, down: bool):
        """
        on most os the mouse buttons are "just" keys,
        so you can press them with the keyboard class
        """
        with display_manager(cls._display) as dm:
            Xlib.ext.xtest.fake_input(
                dm,
                Xlib.X.ButtonPress if down else Xlib.X.ButtonRelease,
                button
            )

    @classmethod
    def press_button(cls, button: AbsMouse.buttons, down: bool):
        btn_id = {
            "left": ButtonEnum.left,
            "middle": ButtonEnum.middle,
            "right": ButtonEnum.right,
        }[button]

        cls._press_button(btn_id, down)

    @classmethod
    def _click_button(cls, button: int, count: int = 1):
        for _ in range(count):
            cls._press_button(button, True)
            cls._press_button(button, False)

    @classmethod
    def scroll(cls, dx: int, dy: int):
        cls._click_button(
            button=ButtonEnum.scroll_up if dy > 0 else ButtonEnum.scroll_down,
            count=abs(dy)
        )

        cls._click_button(
            button=ButtonEnum.scroll_right if dx > 0 else ButtonEnum.scroll_left,
            count=abs(dx))

    @staticmethod
    def is_pressed(button: AbsMouse.buttons):
        raise NotImplementedError
