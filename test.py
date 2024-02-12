# import time
#
import time

from Mine.Main.Keyboard import Keyboard
from Mine.Main.EventStack import print_events
from Mine.OsAbstractions.Linux.xorg_keysyms import unicode_char_to_name, name_to_symbolic_key

# print_events()

# start = time.time_ns()

# key = _keyboard.get_key_data_from_char(char)
# vk, need_pressed, need_unpressed = _keyboard.calc_buttons_for_key(key)


# sd = Keyboard._compile_to_state_data("HELLO this IS @upidapi")
# print(sd)
# seq = Keyboard._state_to_press_seq(*sd)
# print(seq)

time.sleep(1)
print("2 sec")
time.sleep(2)

Keyboard.type("1¨^¨~1")


# import unicodedata
#
#
# for char in "aA3#£^¨":
#     try:
#         x = unicodedata.lookup(
#             'COMBINING ' + unicodedata.name(char)
#         )
#         print()
#         print(char, x, hex(ord(x)))
#
#         name = unicode_char_to_name(x)
#
#         print(f"{char} {x} {name}")
#
#         symbolic_key = name_to_symbolic_key(name)
#
#         print(f"{char} {x} {symbolic_key}")
#
#     except KeyError:
#         # not dead key
#         print("not", char)
