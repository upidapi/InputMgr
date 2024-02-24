# import unicodedata
import unicodedata
from typing import Iterator, Type


class KeyData:
    def __init__(
            self,
            vk: int,
            char: str = None,
            # data: dict = None,
    ):

        # no actual data
        if all(thing is None for thing in [vk, char]):
            raise ValueError("no data provided, you must provide vk or data")

        if char is not None:
            if vk is None:
                raise ValueError("please also provide the vk when you provide char")

        self.vk: int = vk
        self.char: char = char
        # self.data = data and {}

        self.is_dead = False

        # can't be dead of it isn't a char
        if self.char:
            self.is_dead = self._calc_is_dead()

    def get_resulting_char(self) -> str:
        if self.is_dead:
            u_name = unicodedata.name(self.char)
            if u_name.startswith("COMBINING "):
                base_name = u_name[len("COMBINING "):]
                return unicodedata.lookup(base_name)

            return self.char

        return self.char

    def _calc_is_dead(self):
        """
        calculates if character is dead

        if you want it to be able to detect dead keys
        then you should overwrite this function
        """
        return False

    def __repr__(self):
        # todo maybe change to something more descriptive
        if self.is_dead:
            return f"[{self.char}]"
        if self.char is not None:
            return repr(self.char)
        return f"<{self.vk}>"

    def _get_important_vars(self):
        return tuple(
            x
            for x in vars(self)
            if not x.startswith("__") and not x.endswith("__")
        )

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False

        return all(
            getattr(self, x) == getattr(other, x)
            if hasattr(other, x) else False
            for x in self._get_important_vars()
        )

    def __hash__(self):
        return hash(self._get_important_vars())

    def join(self, key):
        """
        joins self (a dead char)
        with another
        """
        raise NotImplementedError

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


class MetaVkEnum(type):
    _ignore = {
        "_ignore",
        "_keyname_to_v_code_map",
        "_v_code_to_keyname_map",
        "_enum_item_type",
    }
    _keyname_to_v_code_map = {}
    _v_code_to_keyname_map = {}
    _enum_item_type: Type[KeyData]

    def __iter__(cls):
        itr: Iterator[cls._enum_item_type] = \
            iter(cls._keyname_to_v_code_map.values())
        return itr


class VkEnum(metaclass=MetaVkEnum):
    """
    exposes the attributes of a vk enum
    also uses those attributes to a few helper funcs
    """

    def __init_subclass__(cls, enum_item_type=None):
        """
        some trickery to get the (sub) class __dict__
        then find all manually added attributes (vk(s))
        and add them to a dict
        """
        if enum_item_type is None:
            raise TypeError("missing enum_item_type")

        cls._enum_item_type = enum_item_type

        cls._keyname_to_v_code_map = {
            key: getattr(cls, key)
            for key in vars(cls)
            if not key.startswith("__")
            and not key.endswith("__")
            and key not in cls._ignore
        }

        cls._v_code_to_keyname_map = {
            val: key for key, val in cls._keyname_to_v_code_map.items()
        }

    @classmethod
    def keyname_to_v_code(cls, keyname):
        """ convert a keyname to a vk """
        return cls._keyname_to_v_code_map[keyname]

    @classmethod
    def v_code_to_keyname(cls, v_code):
        """ convert a vk to a keyname """
        return cls._v_code_to_keyname_map[v_code]