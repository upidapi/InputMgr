# import unicodedata as ud
#
#
# # chars = "^¨~`aâ'a1.:aͣͣ"
# # # chars = "â"
# # for char in chars:
# #     name = unicodedata.name(char)
# #     group = unicodedata.category(char)
# #
# #     try:
# #         comb = unicodedata.lookup(f"COMBINING {name}")
# #         c_group = unicodedata.category(comb)
# #     except KeyError:
# #         comb = None
# #         c_group = None
# #
# #     # https://www.compart.com/en/unicode/category
# #     # Mark, nonspacing
# #
# #     # Sk => Modifier symbol
# #     print(f"\"{char}\" {name:<40} {group} \" {comb}\" {c_group}")
#
# o1 = 'ö'  # '\xf6'
# o2 = 'ö'  # 'o\u0308'
#
# combining_a = ud.lookup(f"COMBINING {ud.name("^")}")
# wierd_a = " " + combining_a
#
#
# def print_uc(chars: str):
#     for char in chars:
#         print(f'U+{ord(char):04X} {ud.name(char)}')
#     print()
#
#
# print_uc(wierd_a)
# print_uc(ud.normalize('NFC', wierd_a))
# print_uc(ud.normalize('NFD', wierd_a))
import asyncio
import time

from src import LinuxKeyEnum, EventQueue, KeyboardEvent
from src.Events import KeyboardEvents
from src.Main import EventHandler
from src.Main.EventHandler import print_event
from src.Main.Keyboard import Keyboard
from src.OsAbstractions.Abstract.Keyboard import StateData

# time.sleep(3)
#
# # Keyboard.typewrite(StateData(("\n", ), {LinuxKeyEnum.shift.vk}))
#
# data = r"""_^¨"""
#
# for line in data.split("\n"):
#     Keyboard.typewrite(line, delta_press=0.01)
#     Keyboard.typewrite(StateData(("\n", ), {LinuxKeyEnum.shift.vk}))
#


async def main():
    with EventQueue() as eq:
        async for event in eq:
            if isinstance(event, KeyboardEvent.KeySend):
                print_event(event, mouse_scroll=False, mouse_click=False, mouse_unclick=False)


if __name__ == '__main__':
    asyncio.run(main())

r"""
\u2d9 ˙ DOT ABOVE
\u2da ˚ RING ABOVE
\ub4 ´ ACUTE ACCENT
\u2d8 ˘ BREVE
\u2c7 ˇ CARON
\ub8 ¸ CEDILLA
\u5e ^ CIRCUMFLEX ACCENT
\ua8 ¨ DIAERESIS
\u2dd ˝ DOUBLE ACUTE ACCENT
\u60 ` GRAVE ACCENT
\u37a ͺ GREEK YPOGEGRAMMENI
\u5f _ LOW LINE
\uaf ¯ MACRON
\u2db ˛ OGONEK
\u7e ~ TILDE
"""