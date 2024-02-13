from Mine.OsAbstractions.Linux.common import LinuxKeyEnum

testing = "print"

if testing == "type":
    import time
    from Mine.Main.Keyboard import Keyboard

    print("2 sec")
    time.sleep(2)

    # Keyboard.type(2, 3, "1¨^¨~1aASẼ")
    Keyboard.type(LinuxKeyEnum.f1)

elif testing == "print":
    from Mine.Main.EventStack import print_events

    print_events()

elif testing == "init":
    import cProfile
    cProfile.run(
        """from Mine.Main.Keyboard import Keyboard""",
        "stats"
    )
    import pstats

    p = pstats.Stats('restats')
    p.sort_stats("time").print_stats()
