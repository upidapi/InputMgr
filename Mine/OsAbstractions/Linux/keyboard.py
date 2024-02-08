import evdev

from Mine.OsAbstractions.Abstract import AbsKeyboard
from Mine.OsAbstractions.Abstract.Keyboard import InvalidKeyException
from Mine.OsAbstractions.Linux.StateMgr import StateMgr
from Mine.OsAbstractions.Linux.common import LinuxKeyData, LinuxLayout
from common import LinuxKeyEnum


class LinuxKeyboard(AbsKeyboard):
    _dev = evdev.UInput()

    @classmethod
    def queue_press(cls, vk: int, is_press: bool) -> None:
        """Queues a virtual key event.

        This method does not perform ``SYN``.

        :param int vk: The virtual key.

        :param bool is_press: Whether this is a press event.
        """
        cls._dev.write(evdev.ecodes.EV_KEY, vk, int(is_press))

    @classmethod
    def send_queued_presses(cls):
        cls._dev.syn()

    @classmethod
    def update_mapping(cls) -> None:
        """
        updates the internal keyboard key to vk_code mapping
        """
        raise NotImplementedError

    @classmethod
    def get_key_data_from_vk(cls, vk: int):
        return LinuxKeyData.from_vk(vk)

    @classmethod
    def get_key_data_from_char(cls, char: str) -> LinuxKeyData:
        return LinuxLayout.for_char(char)

    @classmethod
    def calc_buttons_for_key(cls, key: LinuxKeyData)\
            -> (int, set[int], set[int]):
        """
        gets the buttons that needs to be pressed to get a specific char
        """
        required_modifiers: set[LinuxKeyData] = set()
        vk: int
        if key.vk is not None:
            vk = key.vk
        elif key.char is not None:
            required_modifiers, vk = \
                LinuxLayout.for_char(key.char)
        else:
            raise InvalidKeyException(key)

        # pressed_keys = LinuxEventApi.get_pressed_keys()
        need_pressed = set()
        need_unpressed = set()

        rev_multidict = {}
        for key, value in StateMgr.MODIFIER_MAP.items():
            rev_multidict.setdefault(value, set()).add(key)

        for keys, generic_key in rev_multidict:
            # this assumes the mod key is always the base form
            # so shift_l and not shift_r
            if generic_key in required_modifiers:
                need_pressed.add(generic_key)
            else:
                need_unpressed += keys

        def conv_to_vk(x: set[LinuxKeyData]) -> set[int]:
            return set(
                getattr(evdev.ecodes, key_data.kernel_name)
                for key_data in x
            )

        return vk, conv_to_vk(need_pressed), conv_to_vk(need_unpressed)


class ListenerMixin(object):
    """A mixin for *uinput* event listeners.

    Subclasses should set a value for :attr:`_EVENTS` and implement
    :meth:`_handle`.
    """
    #: The events for which to listen
    _EVENTS = tuple()

    def __init__(self):
        self._dev = self._device(
            DEVICE_PATHS or evdev.list_devices()
        )
        if SUPPRESS:
            self._dev.grab()

        self._layout = LAYOUT
        self._modifiers = set()

    def _run(self):
        for event in self._dev.read_loop():
            if event.type in self._EVENTS:
                self._handle(event)

    def _stop_platform(self):
        self._dev.close()

    def _device(self, paths):
        """Attempts to load a readable keyboard device.

        :param paths: A list of paths.

        :return: a compatible device
        """
        dev, count = None, 0
        for path in paths:
            # Open the device
            try:
                next_dev = evdev.InputDevice(path)
            except OSError:
                continue

            # Does this device provide more handled event codes?
            capabilities = next_dev.capabilities()
            next_count = sum(
                len(codes)
                for event, codes in capabilities.items()
                if event in self._EVENTS)
            if next_count > count:
                dev = next_dev
                count = next_count
            else:
                next_dev.close()

        if dev is None:
            raise OSError('no keyboard device available')
        else:
            return dev

    _EVENTS = (
        evdev.ecodes.EV_KEY,)

    #: A
    _MODIFIERS = {
        LinuxKeyEnum.alt.value.vk: LinuxKeyEnum.alt,
        LinuxKeyEnum.alt_l.value.vk: LinuxKeyEnum.alt,
        LinuxKeyEnum.alt_r.value.vk: LinuxKeyEnum.alt,
        LinuxKeyEnum.alt_gr.value.vk: LinuxKeyEnum.alt_gr,
        LinuxKeyEnum.shift.value.vk: LinuxKeyEnum.shift,
        LinuxKeyEnum.shift_l.value.vk: LinuxKeyEnum.shift,
        LinuxKeyEnum.shift_r.value.vk: LinuxKeyEnum.shift}

    def _handle(self, event):
        """
        Handles a single event.

        This method should call one of the registered event callbacks.

        :param event: The event.
        """
        is_press = event.value in (KeyEvent.key_down, KeyEvent.key_hold)
        vk = event.code

        # Update the modifier state
        if vk in self._MODIFIERS:
            modifier = self._MODIFIERS[vk]
            if is_press:
                self._modifiers.add(modifier)
            elif modifier in self._modifiers:
                self._modifiers.remove(modifier)

        # Attempt to map the virtual key code to a key
        try:
            key = self._layout.for_vk(vk, self._modifiers)
        except KeyError:
            try:
                key = next(
                    key
                    for key in LinuxKeyEnum
                    if key.value.vk == vk)
            except StopIteration:
                key = KeyCode.from_vk(vk)

        if is_press:
            self.on_press(key)
        else:
            self.on_release(key)
