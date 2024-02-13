from Mine.OsAbstractions.Abstract import AbsMouse
# pylint: disable=W0611
try:
    import pynput._util.xorg
except Exception as e:
    raise ImportError('failed to acquire X connection: {}'.format(str(e)), e)
# pylint: enable=W0611

import enum
import Xlib.display
import Xlib.ext
import Xlib.ext.xtest
import Xlib.X
import Xlib.protocol

from pynput._util.xorg import (
    display_manager,
    ListenerMixin)


# pylint: disable=C0103
Button = enum.Enum(
    'Button',
    module=__name__,
    names=[
        ('unknown', None),
        ('left', 1),
        ('middle', 2),
        ('right', 3),
        ('scroll_up', 4),
        ('scroll_down', 5),
        ('scroll_left', 6),
        ('scroll_right', 7)] + [
            ('button%d' % i, i)
            for i in range(8, 31)])


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

    @staticmethod
    def scroll(dx: float, dy: float):
        # might be int, int and not float, float
        raise NotImplementedError

    @staticmethod
    def press_button(button: AbsMouse._buttons, down: bool):
        """
        on most os the mouse buttons are "just" keys,
        so you can press them with the keyboard class
        """
        raise NotImplementedError

    @staticmethod
    def is_pressed(button: AbsMouse._buttons):
        raise NotImplementedError
