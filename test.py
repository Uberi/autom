#!/usr/bin/env python3

import sys

import autom as a

print(a.keyboard_get_toggles())
sys.exit()

a.keyboard_press(["CapsLock"])
a.keyboard_press(["Win", "Left"])
a.keyboard_type("ech")
a.keyboard_press(["\t"])
a.keyboard_down(["Alt", "\t"])
import time; time.sleep(1)
a.keyboard_up(["Alt", "\t"])

print(a.sound_get_volume(), "muted" if a.sound_get_mute() else "not muted")
a.sound_set_mute()
a.sound_set_volume(20)
a.sound_set_mute(False)
print(a.sound_get_volume(), "muted" if a.sound_get_mute() else "not muted")

print(a.msgbox("hi", buttons=["Yes", "No"]))

a.click(50, 50)
a.type_string('Hello, World!')
