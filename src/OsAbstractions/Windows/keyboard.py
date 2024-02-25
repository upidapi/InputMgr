import ctypes

from src.AbsVkEnum import KeyData
from src.OsAbstractions.Abstract import AbsKeyboard
from src.OsAbstractions.Windows.Base import SendInput, INPUT, INPUT_union, \
    KEYBDINPUT, MapVirtualKey, VkKeyScan
from src.OsAbstractions.Windows.WinKeyData import WinKeyData


# class WindowsKeyboard(AbsKeyboard):
#     @staticmethod
#     def press(vk_code: int, down: bool) -> None:
#         raise NotImplementedError
#
#     @classmethod
#     def update_mapping(cls) -> None:
#         raise NotImplementedError
#
#     @staticmethod
#     def key_data_to_vk_code(key_data: KeyData) -> int:
#         raise NotImplementedError


# def send_key(key, is_press):
#     """
#     The parameters to pass to ``SendInput`` to generate this key.
#
#     :param bool is_press: Whether to generate a press event.
#
#     :return: all arguments to pass to ``SendInput`` for this key
#
#     :rtype: dict
#
#     :raise ValueError: if this key is a unicode character that cannot be
#     represented by a single UTF-16 value
#     """
#     if key.vk:
#         vk = key.vk
#         scan = key.scan or MapVirtualKey(
#             vk,
#             MapVirtualKey.MAPVK_VK_TO_VSC
#         )
#         flags = 0
#     elif ord(key.char) > 0xFFFF:
#         # If key._parameters raises ValueError, the key is a unicode
#         # characters outside the range of a single UTF-16 value, and we
#         # must break it up into its surrogates
#         byte_data = bytearray(key.char.encode('utf-16le'))
#         surrogates = [
#             byte_data[i] | (byte_data[i + 1] << 8)
#             for i in range(0, len(byte_data), 2)
#         ]
#
#         state_flags = KEYBDINPUT.UNICODE \
#             | (KEYBDINPUT.KEYUP if not is_press else 0)
#
#         SendInput(
#             len(surrogates),
#             (INPUT * len(surrogates))(*(
#                 INPUT(
#                     INPUT.KEYBOARD,
#                     INPUT_union(
#                         ki=KEYBDINPUT(
#                             dwFlags=state_flags,
#                             wScan=scan
#                         )
#                     )
#                 )
#                 for scan in surrogates)),
#             ctypes.sizeof(INPUT)
#         )
#         return
#     else:
#         res = VkKeyScan(key.char)
#
#         # can it be represented by a scancode?
#         if (res >> 8) & 0xFF == 0:
#             # send scancode
#             vk = res & 0xFF
#             scan = key.scan or MapVirtualKey(
#                 vk,
#                 MapVirtualKey.MAPVK_VK_TO_VSC
#             )
#             flags = 0
#
#         else:
#             # send unicode
#             vk = 0
#             scan = ord(key.char)
#             flags = KEYBDINPUT.UNICODE
#
#     state_flags = (
#         KEYBDINPUT.KEYUP
#         if not is_press else
#         0
#     )
#
#     SendInput(
#         1,
#         ctypes.byref(INPUT(
#             type=INPUT.KEYBOARD,
#             value=INPUT_union(
#                 ki=KEYBDINPUT(
#                     dwFlags=(key.flags or 0) | flags | state_flags,
#                     wVk=vk,
#                     wScan=scan
#                 )
#             )
#         )),
#         ctypes.sizeof(INPUT))


def send_key_surrogates(key, is_press):
    # If key._parameters raises ValueError, the key is a unicode
    # characters outside the range of a single UTF-16 value, and we
    # must break it up into its surrogates
    byte_data = bytearray(key.char.encode('utf-16le'))
    surrogates = [
        byte_data[i] | (byte_data[i + 1] << 8)
        for i in range(0, len(byte_data), 2)
    ]

    state_flags = KEYBDINPUT.UNICODE | (
        KEYBDINPUT.KEYUP if not is_press else 0
    )

    SendInput(
        len(surrogates),
        (INPUT * len(surrogates))(*(
            INPUT(
                INPUT.KEYBOARD,
                INPUT_union(
                    ki=KEYBDINPUT(
                        dwFlags=state_flags,
                        wScan=scan
                    )
                )
            )
            for scan in surrogates)),
        ctypes.sizeof(INPUT)
    )


def send_key(key: WinKeyData, is_press: bool):
    if key.vk:
        vk = key.vk
        scan = key.scan or MapVirtualKey(
            vk,
            MapVirtualKey.MAPVK_VK_TO_VSC
        )
        flags = 0
    elif ord(key.char) > 0xFFFF:
        send_key_surrogates(key, is_press)
        return
    else:
        res = VkKeyScan(key.char)

        # can it be represented by a scancode?
        if (res >> 8) & 0xFF == 0:
            # send scancode
            vk = res & 0xFF
            scan = key.scan or MapVirtualKey(
                vk,
                MapVirtualKey.MAPVK_VK_TO_VSC
            )
            flags = 0

        else:
            # send unicode
            vk = 0
            scan = ord(key.char)
            flags = KEYBDINPUT.UNICODE

    state_flags = (
        KEYBDINPUT.KEYUP
        if not is_press else
        0
    )

    SendInput(
        1,
        ctypes.byref(INPUT(
            type=INPUT.KEYBOARD,
            value=INPUT_union(
                ki=KEYBDINPUT(
                    dwFlags=(key.flags or 0) | flags | state_flags,
                    wVk=vk,
                    wScan=scan
                )
            )
        )),
        ctypes.sizeof(INPUT))
