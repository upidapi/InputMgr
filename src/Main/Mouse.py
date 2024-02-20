from src.OsAbstractions import get_backend
from src.OsAbstractions.Abstract import AbsMouse

_mouse = get_backend().Mouse


class Mouse:
    @staticmethod
    def move(dx, dy):
        """ move the mouse relative to its current pos """
        cx, cy = _mouse.get_pos()
        _mouse.set_pos(cx + dx, cy + dy)

    @staticmethod
    def set_pos(x, y):
        """ move the mouse relative to its current pos """
        _mouse.set_pos(x, y)

    @staticmethod
    def get_pos():
        """ move the mouse relative to its current pos """
        return _mouse.get_pos()

    @staticmethod
    def scroll(dx: int, dy: int):
        return _mouse.scroll(dx, dy)

    @staticmethod
    def press_button(button: AbsMouse.buttons, down: bool):
        """
        on most os the mouse buttons are "just" keys,
        so you can press them with the keyboard class
        """
        return _mouse.press_button(button, down)

    @staticmethod
    def is_pressed(button: AbsMouse.buttons):
        return _mouse.is_pressed(button)
