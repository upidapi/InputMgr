""" abstract representation for a keyboard """

from abc import ABC, abstractmethod

from Mine.ViritallKeys.VkEnum import KeyData


class AbsKeyboard(ABC):
    class InvalidKeyException(Exception):
        """The exception raised when an invalid ``key`` parameter is passed to
        :meth:`AbsKeyboard.press`

        Its first argument is the ``key`` parameter.
        """
        pass

    class InvalidCharacterException(Exception):
        """The exception raised when an invalid character is encountered in
        the string passed to :meth:`Controller.key_data_to_vk_code`.

        Its first argument is the index of the character in the string, and the
        second the character.
        """
        pass

    @classmethod
    @abstractmethod
    def is_pressed(cls, vk_code: int) -> bool:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def press(cls, vk_code: int, down: bool) -> None:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def update_mapping(cls) -> None:
        """
        updates the internal keyboard key to vk_code mapping
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def key_data_to_vk_code(cls, key_data: KeyData) -> int:
        """
        converts some data to a keycode e.g. "NP_0" to the keycode for numpad 0
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def key_to_vk_code(cls, key: str) -> int:
        """
        converts a key from the keyboard e.g. "a", "#", "^" to a keycode
        """
        raise NotImplementedError


class KeyCode(object):
    """
    A :class:`KeyCode` represents the description of a key code used by the
    operating system.
    """
    #: The names of attributes used as platform extensions.
    _PLATFORM_EXTENSIONS = []

    def __init__(self, vk=None, char=None, is_dead=False, **kwargs):
        self.vk = vk
        self.char = str(char) if char is not None else None
        self.is_dead = is_dead

        if self.is_dead:
            try:
                self.combining = unicodedata.lookup(
                    'COMBINING ' + unicodedata.name(self.char))
            except KeyError:
                self.is_dead = False
                self.combining = None
            if self.is_dead and not self.combining:
                raise KeyError(char)
        else:
            self.combining = None

        for key in self._PLATFORM_EXTENSIONS:
            setattr(self, key, kwargs.pop(key, None))
        if kwargs:
            raise ValueError(kwargs)


    def __repr__(self):
        if self.is_dead:
            return '[%s]' % repr(self.char)
        if self.char is not None:
            return repr(self.char)
        else:
            return '<%d>' % self.vk

    def __str__(self):
        return repr(self)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.char is not None and other.char is not None:
            return self.char == other.char and self.is_dead == other.is_dead
        else:
            return self.vk == other.vk and all(
                getattr(self, f) == getattr(other, f)
                for f in self._PLATFORM_EXTENSIONS)

    def __hash__(self):
        return hash(repr(self))

    def join(self, key):
        """Applies this dead key to another key and returns the result.

        Joining a dead key with space (``' '``) or itself yields the non-dead
        version of this key, if one exists; for example,
        ``KeyCode.from_dead('~').join(KeyCode.from_char(' '))`` equals
        ``KeyCode.from_char('~')`` and
        ``KeyCode.from_dead('~').join(KeyCode.from_dead('~'))``.

        :param KeyCode key: The key to join with this key.

        :return: a key code

        :raises ValueError: if the keys cannot be joined
        """
        # A non-dead key cannot be joined
        if not self.is_dead:
            raise ValueError(self)

        # Joining two of the same keycodes, or joining with space, yields the
        # non-dead version of the key
        if key.char == ' ' or self == key:
            return self.from_char(self.char)

        # Otherwise we combine the characters
        if key.char is not None:
            combined = unicodedata.normalize(
                'NFC',
                key.char + self.combining)
            if combined:
                return self.from_char(combined)

        raise ValueError(key)

    @classmethod
    def from_vk(cls, vk, **kwargs):
        """Creates a key from a virtual key code.

        :param vk: The virtual key code.

        :param kwargs: Any other parameters to pass.

        :return: a key code
        """
        return cls(vk=vk, **kwargs)

    @classmethod
    def from_char(cls, char, **kwargs):
        """Creates a key from a character.

        :param str char: The character.

        :return: a key code
        """
        return cls(char=char, **kwargs)

    @classmethod
    def from_dead(cls, char, **kwargs):
        """Creates a dead key.

        :param char: The dead key. This should be the unicode character
            representing the stand alone character, such as ``'~'`` for
            *COMBINING TILDE*.

        :return: a key code
        """
        return cls(char=char, is_dead=True, **kwargs)
