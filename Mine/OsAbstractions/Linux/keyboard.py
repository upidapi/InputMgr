import Xlib


from Mine.OsAbstractions.Abstract import AbsKeyboard
from Mine.ViritallKeys.VkEnum import KeyData


class LinuxKeyboard(AbsKeyboard):
    @staticmethod
    def press(vk_code: int, down: bool) -> None:
        raise NotImplementedError

    @staticmethod
    def update_mapping() -> None:
        raise NotImplementedError

    @staticmethod
    def key_data_to_vk_code(key_data: KeyData) -> int:
        raise NotImplementedError


class Masks:
    def __init__(self, display: Xlib.display.Display):
        self._display = display

        #: The shift mask for :attr:`Key.ctrl`
        self.CTRL_MASK = Xlib.X.ControlMask

        #: The shift mask for :attr:`Key.shift`
        self.SHIFT_MASK = Xlib.X.ShiftMask

        self.ALT_MASK = self._find_mask('Alt_L')
        self.ALT_GR_MASK = self._find_mask('Mode_switch')
        self.NUM_LOCK_MASK = self._find_mask('Num_Lock')

    def _find_mask(self, symbol):
        """Returns the mode flags to use for a modifier symbol.

        :param Xlib.display.Display display: The *X* display.

        :param str symbol: The name of the symbol.

        :return: the modifier mask
        """
        # Get the key code for the symbol
        modifier_keycode = self._display.keysym_to_keycode(
            Xlib.XK.string_to_keysym(symbol))

        for index, keycodes in enumerate(self._display.get_modifier_mapping()):
            for keycode in keycodes:
                if keycode == modifier_keycode:
                    return 1 << index

        return 0


class Controller(NotifierMixin, _base.Controller):
    _KeyCode = KeyCode
    _Key = Key

    #: The shift mask for :attr:`Key.ctrl`
    CTRL_MASK = Xlib.X.ControlMask

    #: The shift mask for :attr:`Key.shift`
    SHIFT_MASK = Xlib.X.ShiftMask

    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)
        self._display = Xlib.display.Display()
        self._keyboard_mapping = None
        self._borrows = {}
        self._borrow_lock = threading.RLock()

        # pylint: disable=C0103; this is treated as a class scope constant, but
        # we cannot set it in the class scope, as it requires a Display instance
        self.ALT_MASK = alt_mask(self._display)
        self.ALT_GR_MASK = alt_gr_mask(self._display)
        # pylint: enable=C0103

    def __del__(self):
        if hasattr(self, '_display'):
            self._display.close()

    @property
    def keyboard_mapping(self):
        """A mapping from *keysyms* to *key codes*.

        Each value is the tuple ``(key_code, shift_state)``. By sending an
        event with the specified *key code* and shift state, the specified
        *keysym* will be touched.
        """
        if not self._keyboard_mapping:
            self._update_keyboard_mapping()
        return self._keyboard_mapping

    def _handle(self, key, is_press):
        """Resolves a key identifier and sends a keyboard event.

        :param int key: The key to handle.
        :param bool is_press: Whether this is a press.
        """
        event = Xlib.display.event.KeyPress if is_press \
            else Xlib.display.event.KeyRelease
        keysym = self._keysym(key)

        # Make sure to verify that the key was resolved
        if keysym is None:
            raise self.InvalidKeyException(key)

        # If the key has a virtual key code, use that immediately with
        # fake_input; fake input,being an X server extension, has access to
        # more internal state that we do
        if key.vk is not None:
            with display_manager(self._display) as dm:
                Xlib.ext.xtest.fake_input(
                    dm,
                    Xlib.X.KeyPress if is_press else Xlib.X.KeyRelease,
                    dm.keysym_to_keycode(key.vk))

        # Otherwise use XSendEvent; we need to use this in the general case to
        # work around problems with keyboard layouts
        else:
            try:
                keycode, shift_state = self.keyboard_mapping[keysym]
                self._send_key(event, keycode, shift_state)

            except KeyError:
                with self._borrow_lock:
                    keycode, index, count = self._borrows[keysym]
                    self._send_key(
                        event,
                        keycode,
                        index_to_shift(self._display, index))
                    count += 1 if is_press else -1
                    self._borrows[keysym] = (keycode, index, count)

        # Notify any running listeners
        self._emit('_on_fake_event', key, is_press)

    def _keysym(self, key):
        """Converts a key to a *keysym*.

        :param KeyCode key: The key code to convert.
        """
        return self._resolve_dead(key) if key.is_dead else None \
            or self._resolve_special(key) \
            or self._resolve_normal(key) \
            or self._resolve_borrowed(key) \
            or self._resolve_borrowing(key)

    def _send_key(self, event, keycode, shift_state):
        """Sends a single keyboard event.

        :param event: The *X* keyboard event.

        :param int keycode: The calculated keycode.

        :param int shift_state: The shift state. The actual value used is
            :attr:`shift_state` or'd with this value.
        """
        with display_manager(self._display) as dm, self.modifiers as modifiers:
            # Under certain cimcumstances, such as when running under Xephyr,
            # the value returned by dm.get_input_focus is an int
            window = dm.get_input_focus().focus
            send_event = getattr(
                window,
                'send_event',
                lambda event: dm.send_event(window, event))
            send_event(event(
                detail=keycode,
                state=shift_state | self._shift_mask(modifiers),
                time=0,
                root=dm.screen().root,
                window=window,
                same_screen=0,
                child=Xlib.X.NONE,
                root_x=0, root_y=0, event_x=0, event_y=0))

    def _resolve_dead(self, key):
        """Tries to resolve a dead key.

        :param str identifier: The identifier to resolve.
        """
        # pylint: disable=W0702; we want to ignore errors
        try:
            keysym, _ = SYMBOLS[CHARS[key.combining]]
        except:
            return None
        # pylint: enable=W0702

        if keysym not in self.keyboard_mapping:
            return None

        return keysym

    def _resolve_special(self, key):
        """Tries to resolve a special key.

        A special key has the :attr:`~KeyCode.vk` attribute set.

        :param KeyCode key: The key to resolve.
        """
        if not key.vk:
            return None

        return key.vk

    def _resolve_normal(self, key):
        """Tries to resolve a normal key.

        A normal key exists on the keyboard, and is typed by pressing
        and releasing a simple key, possibly in combination with a modifier.

        :param KeyCode key: The key to resolve.
        """
        keysym = self._key_to_keysym(key)
        if keysym is None:
            return None

        if keysym not in self.keyboard_mapping:
            return None

        return keysym

    def _resolve_borrowed(self, key):
        """Tries to resolve a key by looking up the already borrowed *keysyms*.

        A borrowed *keysym* does not exist on the keyboard, but has been
        temporarily added to the layout.

        :param KeyCode key: The key to resolve.
        """
        keysym = self._key_to_keysym(key)
        if keysym is None:
            return None

        with self._borrow_lock:
            if keysym not in self._borrows:
                return None

        return keysym

    def _resolve_borrowing(self, key):
        """Tries to resolve a key by modifying the layout temporarily.

        A borrowed *keysym* does not exist on the keyboard, but is temporarily
        added to the layout.

        :param KeyCode key: The key to resolve.
        """
        keysym = self._key_to_keysym(key)
        if keysym is None:
            return None

        mapping = self._display.get_keyboard_mapping(8, 255 - 8)

        def i2kc(index):
            return index + 8

        def kc2i(keycode):
            return keycode - 8

        #: Finds a keycode and index by looking at already used keycodes
        def reuse():
            for _, (keycode, _, _) in self._borrows.items():
                keycodes = mapping[kc2i(keycode)]

                # Only the first four items are addressable by X
                for index in range(4):
                    if not keycodes[index]:
                        return keycode, index

        #: Finds a keycode and index by using a new keycode
        def borrow():
            for i, keycodes in enumerate(mapping):
                if not any(keycodes):
                    return i2kc(i), 0

        #: Finds a keycode and index by reusing an old, unused one
        def overwrite():
            for keysym, (keycode, index, count) in self._borrows.items():
                if count < 1:
                    del self._borrows[keysym]
                    return keycode, index

        #: Registers a keycode for a specific key and modifier state
        def register(dm, keycode, index):
            i = kc2i(keycode)

            # Check for use of empty mapping with a character that has upper
            # and lower forms
            lower = key.char.lower()
            upper = key.char.upper()
            if lower != upper and len(lower) == 1 and len(upper) == 1 and all(
                    m == Xlib.XK.NoSymbol
                    for m in mapping[i]):
                lower = self._key_to_keysym(KeyCode.from_char(lower))
                upper = self._key_to_keysym(KeyCode.from_char(upper))
                if lower:
                    mapping[i][0] = lower
                    self._borrows[lower] = (keycode, 0, 0)
                if upper:
                    mapping[i][1] = upper
                    self._borrows[upper] = (keycode, 1, 0)
            else:
                mapping[i][index] = keysym
                self._borrows[keysym] = (keycode, index, 0)
            dm.change_keyboard_mapping(keycode, mapping[i:i + 1])

        try:
            with display_manager(self._display) as dm, self._borrow_lock as _:
                # First try an already used keycode, then try a new one, and
                # fall back on reusing one that is not currently pressed
                register(dm, *(
                    reuse() or
                    borrow() or
                    overwrite()))
            return keysym

        except TypeError:
            return None

    def _key_to_keysym(self, key):
        """Converts a character key code to a *keysym*.

        :param KeyCode key: The key code.

        :return: a keysym if found
        :rtype: int or None
        """
        # If the key code already has a VK, simply return it
        if key.vk is not None:
            return key.vk

        # If the character has no associated symbol, we try to map the
        # character to a keysym
        symbol = CHARS.get(key.char, None)
        if symbol is None:
            return char_to_keysym(key.char)

        # Otherwise we attempt to convert the symbol to a keysym
        # pylint: disable=W0702; we want to ignore errors
        try:
            return symbol_to_keysym(symbol)
        except:
            try:
                return SYMBOLS[symbol][0]
            except:
                return None
        # pylint: enable=W0702

    def _shift_mask(self, modifiers):
        """The *X* modifier mask to apply for a set of modifiers.

        :param set modifiers: A set of active modifiers for which to get the
            shift mask.
        """
        return (
            0
            | (self.ALT_MASK
               if Key.alt in modifiers else 0)

            | (self.ALT_GR_MASK
               if Key.alt_gr in modifiers else 0)

            | (self.CTRL_MASK
               if Key.ctrl in modifiers else 0)

            | (self.SHIFT_MASK
               if Key.shift in modifiers else 0))

    def _update_keyboard_mapping(self):
        """Updates the keyboard mapping.
        """
        with display_manager(self._display) as dm:
            self._keyboard_mapping = keyboard_mapping(dm)



