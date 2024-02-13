from Mine.OsAbstractions import get_backend

_mouse = get_backend().Mouse


class Mouse:
    @classmethod
    def move(cls, dx, dy):
        """ move the mouse relative to its current pos """
        cx, cy = _mouse.get_pos()
        _mouse.set_pos(cx + dx, cy + dy)

    @classmethod
    def set_pos(cls, x, y):
        """ move the mouse relative to its current pos """
        _mouse.set_pos(x, y)

    @classmethod
    def get_pos(cls):
        """ move the mouse relative to its current pos """
        return _mouse.get_pos()

    # todo fully implement this
