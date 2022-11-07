#!/usr/bin/python

import os
import sys
import grp

try:
    import evdev
    from evdev import ecodes as e
except Exception as ex:
    print("Unable to import evdev python module", ex)
    sys.exit(1)

class uinput_keyboard():
    """
    
    """
    #keys = e.keys
    inv_map = {}
    char_map = {
        "/":"KEY_SLASH", "'":"KEY_APOSTROPHE", ",":"KEY_COMMA", ".":"KEY_DOT", ";":"KEY_SEMICOLON",
        "[":"KEY_LEFTBRACE", "]":"KEY_RIGHTBRACE", "\\":"KEY_BACKSLASH", "=":"KEY_EQUAL", "-":"KEY_MINUS", "`": "KEY_GRAVE",
        " ":"KEY_SPACE", "\t": "KEY_TAB","\n": "KEY_ENTER"
    }
    #define as the left versions
    shift_key = 42
    ctrl_key = 29
    alt_key = 56
    meta_key = 125
    #TODO other modifiers
    #altgr_key
    #TODO should this be raw scan code or evdev equivalent? evdev makes more sense to me here
    #string.printable;
    #0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r\x0b\x0c
    #
    shifted_chars = {
        "!":"KEY_1", "@":"KEY_2", "#":"KEY_3", "$":"KEY_4", "%":"KEY_5", "^":"KEY_6", "&": "KEY_7", "*": "KEY_8", "(":"KEY_9", ")":"KEY_0",
        "\"":"KEY_APOSTROPHE", ">": "KEY_DOT", "<": "KEY_COMMA", ":":"KEY_SEMICOLON", "{": "KEY_LEFTBRACE", "}": "KEY_RIGHTBRACE",
        "?": "KEY_SLASH", "+": "KEY_EQUAL", "_":"KEY_MINUS", "~":"KEY_GRAVE", "|":"KEY_BACKSLASH"
    }

    def __init__(self, shift_key=42, ctrl_key=29, alt_key=56, meta_key=125, dev_name="UInput Keyboard", clone=False):
        """
        
        @param shift_key: Evdev keycode for shift key. Defaults to left shift (42)
        @param ctrl_key: Evdev keycode for ctrl key. Defaults to left ctrl (29)
        @param alt_key: Evdev keycode for alt key. Defaults to left alt (56)
        @param meta_key: Evdev keycode for meta (windows) key. Defaults to left meta (125)
        @param dev_name: Used when creating uinput device.
        """
        self.validate()
        try:
            if clone:
                dev = self.grab_device(self.get_devices(), dev_name)
                self.ui = evdev.UInput.from_device(dev, name="Autokey Keyboard")
            else:
                self.ui = evdev.UInput(name=dev_name)
        except Exception as ex:
            print("Unable to grab /dev/uinput", ex)
            print("Check out how to resolve this issue: https://github.com/philipl/evdevremapkeys/issues/24")
            sys.exit(1)
        self.reverse_mapping(e.keys)
        #print(self.inv_map)
        self.shift_key = shift_key
        self.ctrl_key = ctrl_key
        self.alt_key = alt_key
        self.meta_key = meta_key
        #print("####",self.inv_map)


    def validate(self):
        #TODO run checks that uinput will work as expected.
        user = os.getlogin()
        input_group = grp.getgrnam("input")
        if user in input_group.gr_mem or os.geteuid()==0:
            print("User membership good!")
        else:
            print("User not in input group add yourself or run program as root")
            print(f"sudo usermod -a -G input {user}")
            sys.exit(1)

    def reverse_mapping(self, d):
        for item in d.items():
            #print(item)
            #print(type(item[1]))
            if type(item[1]) == list:
                continue
            else:
                self.inv_map[item[1]] = item[0]
        #return mapping
    
    def translate_to_evdev(self, key) -> int:
        """
        Takes an input and tries to convert it to a evdev key code, primarily for internal use

        Determination of type is based primarily on the key type in order;
        if key is type str and the first 4 letters have "KEY_" we assume it is an evdev keycode and return from the inverted mapping of the ecodes.keys
        
        elif the key is type int we will assume if is a raw evdev value and return it

        elif len(key) == 1, assume that this is an ascii char, check if "KEY_"+key exists in any of the character maps and process accordingly

        return (0, false)
        """
        if type(key)==str and "KEY_" in key[:4]: #if it is a "KEY_A" type value return evdev int from map
            #print("Type str")
            return self.inv_map[key], False
        elif type(key)==int: #if it is type int it should be a evdev raw value
            #print("Type int")
            return key, False
        elif len(key)==1:
            #print("Type single char", key)
            evdev_key = "KEY_"+key.upper()
            if key in self.shifted_chars:
                return self.inv_map[self.shifted_chars[key]], True
            elif key in self.char_map:
                return self.inv_map[self.char_map[key]], False
            elif evdev_key in self.inv_map:
                return self.inv_map[evdev_key], key.isupper()
            elif evdev_key in self.char_map:
                return self.inv_map[self.char_map[evdev_key]], key.isupper()
        return (0, False)


    def send_key(self, key, repeat=1, shifted=False, syn=True):
        """
        Send a keyboard event

        Usage: C{ukeyboard.send_key(key, repeat=1, syn=True)}

        @param key: The key to be sent (like "e" or "E" or "<enter>" or "KEY_ENTER")
                    Should be type int if you are sending raw keycodes!
        @param repeat: The number of times to send the key
        @param shifted: Should the shift button be held when key is sent
        @param syn: Send UInput sync event after. 
        """
        for _ in range(repeat):
            self._send_key(key, shifted, syn)

    def _send_key(self, key, shifted=False, syn=True):
        #print(f"Writing {key}")
        evdev_keycode, shifted_ = self.translate_to_evdev(key)
        #print(key, evdev_keycode, shifted_)
        evdev_key = e.keys[evdev_keycode]
        if shifted_:
            shifted=True

        #print(f"Keycode: {evdev_keycode}, Key: {evdev_key}", shifted_, shifted)

        if shifted:
            self.ui.write(e.EV_KEY, self.shift_key, 1)
        self.ui.write(e.EV_KEY, self.inv_map[evdev_key], 1)
        self.ui.write(e.EV_KEY, self.inv_map[evdev_key], 0)
        if shifted:
            self.ui.write(e.EV_KEY, self.shift_key, 0)
        if syn:
            self.ui.write(e.EV_SYN, 0, 0)



    def send_keys(self, keys):
        """
        Send a string of characters to be sent via the keyboard

        Usage: C{ukeyboard.send_keys("This is a test string")}

        @param keys: str or list, use list if you want to send characters like KEY_LEFTCTRL
        """
        #print(keys)
        if type(keys) == list:
            for subset in keys:
                self.send_keys(subset)
            return
        if type(keys) == str and "KEY_" in keys[:4]:
            self.send_key(keys)
            return
        if type(keys) == int:
            self._send_key(keys)
            return
        
        for key in keys:
            self.send_key(key)


    def _press_key(self, key, syn=False):
        self.ui.write(e.EV_KEY, self.inv_map[key], 1)
        if syn:
            self.ui.write(e.EV_SYN, 0, 0)

    def press_key(self, key, syn=False):
        """
        Send a key down event. A major caveat to be aware of is that I think this will only be sending as long as the ui exists. When the script exits the keyboard dies and input from it is reset

        Usage: C{ukeyboard.press_key(key)}

        The key will be "down" until a matching release_key() is sent!
        @param key: The key to be pressed ()
        """
        evdev_keycode, _ = self.translate_to_evdev(key)
        evdev_key = e.keys[evdev_keycode]
        self._press_key(evdev_key, syn)

    def _release_key(self, key, syn=False):
        self.ui.write(e.EV_KEY, self.inv_map[key], 0)
        if syn:
            self.ui.write(e.EV_SYN, 0, 0)

    def release_key(self, key, syn=False):
        """
        Send a key up event

        Usage: C{ukeyboard.release_key(key)}

        The key will be released


        """
        evdev_keycode, _ = self.translate_to_evdev(key)
        evdev_key = e.keys[evdev_keycode]
        self._release_key(evdev_key, syn)


    def get_devices(self):
        return [evdev.InputDevice(path) for path in evdev.list_devices()]

    def grab_device(self, devices, descriptor):
        #determine if descriptor is a path or a name
        return_device = None
        if len(descriptor) <= 2: #assume that people don't have more than 99 input devices
            descriptor = "/dev/input/event"+descriptor
        if "/dev/" in descriptor: #assume function was passed a path
            for device in devices:
                if descriptor==device.path:
                    device.close()
                    return_device = evdev.InputDevice(device.path)
                else:
                    device.close()
        else: #assume that function was passed a plain text name
            for device in devices:
                if descriptor==device.name:
                    device.close()
                    return_device = evdev.InputDevice(device.path)
                else:
                    device.close()

        return return_device


    # def wait_for_keyevent(self, dev_name, key, modifiers, timeout=30):
    #     """
    #     TODO
    #     Returns true if key event is heard from the device within the timeout, false other wise

    #     @param dev_name: Device name to watch for keyevents
    #     @param timeout: Timeout value in seconds
    #     @param key: Key to listen for.
    #     @param modifiers: list of keys to check if they are held
    #     @return True if key event heard, false other wise
    #     """
    #     return False
    #     start_time = time.time()
    #     #TODO create and implement check
    #     #self.validate_listen()
    #     devices = self.get_devices()
    #     dev = self.grab_device(devices, dev_name)
    #     evdev_key, shifted = self.translate_to_evdev(key)
    #     if dev is not None:
    #         for ev in dev.read_loop():
    #             print(f"Event - TYPE:{ev.type} CODE:{ev.code} VALUE:{ev.value}")
    #             if ev.code == evdev_key:
    #                 return True
                
    #             if time.time() >= start_time+timeout:
    #                 return False



    # def wait_for_keypress(self):
    #     return False
    #     self.validate_listen()
    #     pass

    # def device_selection(self):
    #     #TODO create popup that lists input devices and allows user to select one
    #     # use zenity
    #     pass