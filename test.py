import ukeyboard
import time
import pprint
import string
import sys

from evdev import ecodes as e

#time.sleep(2)
pp = pprint.PrettyPrinter(indent=4)

# pp.pprint(e.keys)

#keyboard = ukeyboard.uinput_keyboard()
keyboard = ukeyboard.uinput_keyboard(dev_name="AT Translated Set 2 keyboard", clone=True)
print(keyboard.get_devices())
input()

#v = keyboard.wait_for_keyevent("OLKB Preonic", "KEY_SPACE", None, 2)
#print(v)
#sys.exit()

keyboard.send_key("A") 
keyboard.press_key("KEY_LEFTSHIFT", True)
keyboard.send_key("a")
keyboard.release_key("KEY_LEFTSHIFT", True)
keyboard.send_key("a")
# keyboard.release_key("KEY_LEFTSHIFT", True)



#keyboard.send_keys("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
#print(string.printable)
for char in string.printable:
    #print(char)
    keyboard.send_key(char)

keyboard.send_key("\t")
keyboard.send_key(15)
keyboard.send_key("KEY_ENTER")
keyboard.send_keys("This is a test of the typing on the UInput module")
keyboard.send_keys(["THis is ", "KEY_ENTER", "testing", [2,3]])


keyboard.send_key("a")
keyboard.send_key("KEY_A", shifted=True)
keyboard.send_key("KEY_A")
keyboard.send_key(2, shifted=True)
keyboard.send_key("!")
keyboard.send_key("KEY_ENTER", True)
#keyboard.send_key("KEY_COLON", True)
#keyboard.send_keys("ABCDEFGHIJKLMNOPQRSTUVWXYZ".lower())

keyboard.send_key("c")


# ukeyboard.send_keys("Aa")

#vals = keyboard.translate_string("This is a Test of")
#pp.pprint(vals)
#keyboard._send_keys(vals)
# ukeyboard._send_keys([{"kaaaaaTHIS IS A TEST OFey":54, "status":1},{"key":30, "status":1},{"key":30, "status":0},{"key":54, "status":0}])aTHIS IS A TEST OFaTHIS IS A TEST OF
"""

"""