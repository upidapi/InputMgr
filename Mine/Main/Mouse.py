from Mine.OsAbstractions import get_backend

_mouse = get_backend().mouse_controller


class Mouse:
    @classmethod
    def move(cls, dx, dy):
        """ move the mouse relative to its current pos """
        cx, cy = _mouse.get_pos()
        _mouse.set_pos(cx + dx, cy + dy)

    @classmethod
    def set_pos(cls, dx, dy):
        """ move the mouse relative to its current pos """
        cx, cy = _mouse.get_pos()
        _mouse.set_pos(cx + dx, cy + dy)

    # todo fully implement this
