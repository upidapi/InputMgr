import  re


with open("data.txt") as f:
    raw_data = f.read()


KEYCODE_RE = re.compile(
    r"keycode\s+(\d+)\s+=(.*)")
key_data = KEYCODE_RE.findall(raw_data)

print(key_data)
