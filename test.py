from evdev import InputDevice

from Mine.Main.EventStack import EventStack

for _ in EventStack.get_conveyor():
    continue
# from select import select
#
# import evdev
# from evdev import InputDevice
#
# devices = map(InputDevice, evdev.list_devices())
# devices = {dev.fd: dev for dev in devices}
#
# for dev in devices.values(): print(dev)
#
# print(type(devices))
# while True:
#     r, w, x = select(devices, [], [])
#
#     for fd in r:
#         for event in devices[fd].read():
#             pass
#             # print(event)


