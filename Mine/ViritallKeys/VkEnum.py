class KeyData:
    """
    a data class for marking a vk dynamic
    basically it takes some data and when used (for example when pressed)
    it then used that data to convert it to a vk
    """
    _os_options = (
        "linux",
        "windows",
        "darwin",
    )

    def __init__(self, key_data: str, os: str):
        if os not in KeyData._os_options:
            raise TypeError(f"invallid os \"{os}\"")

        self.key_data = key_data
        self.os = os


class VkEnum:
    """
    exposes the attributes of a vk enum
    also uses those attributes to a few helper funcs
    """

    _keyname_to_v_code_map = {}
    _v_code_to_keyname_map = {}

    def __init_subclass__(cls, os=None, *_, **__):
        """
        some trickery to get the (sub) class __dict__
        then find all manually added attributes (vk(s))
        and add them to a dict
        """
        if os is None:
            raise TypeError("os is required")

        cls._keyname_to_v_code_map = {
            key: KeyData(val, os)
            for key, val in cls.__dict__.items()
            if not (key.startswith("__") and key.endswith("__"))
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
