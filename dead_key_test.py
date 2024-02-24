from src.OsAbstractions.Linux.LinuxVk.xorg_keysyms import name_to_unicode_char, \
    is_dead

dead_examples = (
    ("´", "dead_acute"),
    ("`", "dead_grave"),
    ("¨", "dead_diaeresis"),
    ("^", "asciicircum"),
    ("~", "asciitilde"),
)

non_dead_examples = (
    ("a", "a"),
    ("A", "A"),
    ("@", "quotedbl"),
    ("-", "minus"),
    ("_", "underscore"),
)


for (char, name) in dead_examples:
    if not is_dead(name_to_unicode_char(name)):
        print(f" {char} {name} failed")

print("--------")

for (char, name) in non_dead_examples:
    if is_dead(name_to_unicode_char(name)):
        print(f" {char} {name} failed")
