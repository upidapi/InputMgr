import evdev

from Mine.OsAbstractions.Abstract import AbsKeyboard
from Mine.OsAbstractions.Abstract.Keyboard import InvalidKeyException, StateData
from Mine.OsAbstractions.Linux.LinuxVk import LinuxKeyData, LinuxLayout, LinuxKeyEnum
from Mine.OsAbstractions.Linux.LinuxVk.LinuxKeyEnum import LINUX_MODIFIER_MAP


class LinuxKeyboard(AbsKeyboard):
    _pressed_keys = set()

    @classmethod
    def get_pressed_keys(cls) -> set[LinuxKeyData]:
        return cls._pressed_keys

    @classmethod
    def key_pressed(cls, key: LinuxKeyData) -> bool:
        return key in cls._pressed_keys

    @classmethod
    def add_pressed_keys(cls, *keys: LinuxKeyData):
        cls._pressed_keys.update(keys)

    @classmethod
    def remove_pressed_keys(cls, *keys: LinuxKeyData):
        cls._pressed_keys -= set(keys)

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
        vk, mod = LinuxLayout.for_char(char)
        # print(char, vk, mod, LinuxLayout.for_vk(vk, mod))
        # print(
        #     vk, mod,
        #     LinuxLayout._vk_table[vk],
        #     LinuxKeyEnum.alt_gr,
        #     LinuxLayout.for_vk(vk, {LinuxKeyEnum.alt_gr}),
        #     LinuxLayout.for_vk(vk, mod),
        # )

        return LinuxLayout.for_vk(vk, mod)

    @classmethod
    def get_vk_from_key_data(cls, key_data: LinuxKeyData) -> int:
        if key_data.vk is not None:
            return key_data.vk
        elif key_data.char is not None:
            return LinuxLayout.for_char(key_data.char)[0]
        else:
            raise InvalidKeyException(key_data)

    @classmethod
    def _get_req_mod_state(cls, raw_required_modifiers) \
            -> tuple[set[int], set[int]]:
        required_modifiers: set[int] = {x.vk for x in raw_required_modifiers}

        need_pressed = set()
        need_unpressed = set()

        # todo possibly move this to StateMgr
        rev_multidict: dict[int, set[int]] = {}
        for key, value in LINUX_MODIFIER_MAP.items():
            if value.vk in rev_multidict.keys():
                rev_multidict[value.vk].add(key.vk)
            else:
                rev_multidict[value.vk] = {key.vk}

        for generic_key, keys in rev_multidict.items():
            # this assumes the mod key is always the base form
            # so shift_l and not shift_r
            if generic_key in required_modifiers:
                need_pressed.add(generic_key)
            else:
                need_unpressed.update(keys)

        return need_pressed | required_modifiers, need_unpressed

    @classmethod
    def _calc_buttons_for_layout_char(cls, char: str) -> StateData:

        vk, raw_required_modifiers = LinuxLayout.for_char(char)

        key_data = LinuxLayout.for_vk(vk, raw_required_modifiers)

        need_pressed, need_unpressed = cls._get_req_mod_state(
            raw_required_modifiers
        )

        # if the char is a dead key then we have to press it
        # twice for it to show up
        return StateData(
            do=(vk, ) * (2 if key_data.is_dead else 1),
            need_pressed=need_pressed,
            need_unpressed=need_unpressed
        )

    @classmethod
    def _calc_buttons_for_unicode_char(cls, char: str) -> StateData:
        # consists of the chars: 0-9, a-f
        unicode_hex = hex(ord(char))[2:]

        do: list[int] = [
            LinuxLayout.for_char(char)[0]
            for char in f"u{unicode_hex}"
        ]
        do.append(LinuxKeyEnum.enter.vk)

        need_pressed, need_unpressed = cls._get_req_mod_state(
            {LinuxKeyEnum.shift, LinuxKeyEnum.ctrl}
        )

        return StateData(
            do=tuple(do),
            need_pressed=need_pressed,
            need_unpressed=need_unpressed,  # | {LinuxKeyEnum.ctrl},
        )

    @classmethod
    def calc_buttons_for_char(cls, char: str) -> StateData:
        """
        gets the buttons that needs to be pressed to get a specific char
        """
        if len(char) != 1:
            raise TypeError(f"len of char must be 1 {char=}")

        if LinuxLayout.char_in_layout(char):
            return cls._calc_buttons_for_layout_char(char)
        else:
            return cls._calc_buttons_for_unicode_char(char)
