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
import time

from src import LinuxKeyEnum
from src.Main.Keyboard import Keyboard
from src.OsAbstractions.Abstract.Keyboard import StateData

time.sleep(3)

# Keyboard.typewrite(StateData(("\n", ), {LinuxKeyEnum.shift.vk}))

data = r"""
"""

for line in data.split("\n"):
    Keyboard.typewrite(line, delta_press=0.01)
    Keyboard.typewrite(StateData(("\n", ), {LinuxKeyEnum.shift.vk}))


