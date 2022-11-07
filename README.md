# uinput-keyboard-module


## Install
All of this is tested on 20.04 (XORG) and 22.04 (Wayland). Please open an issue if you're having issues and we'll try to figure it out :)

The module is dependent on the evdev python module.
`pip3 install evdev`

Make sure that your user is in the `input` group:

`sudo usermod -a -G input <user>`

REBOOT.

If it is still giving you trouble I have had to `chmod 660 /dev/input` before in some of my testing. Also reboot after you do this. Always reboot.

You can also just always run the program as root.

You may also need to follow the instructions outlined and add a permanent udev rule.
https://github.com/philipl/evdevremapkeys/issues/24


## Known issues
Note that if you are not seeing any output and are on Wayland/GNOME you will have to clone a keyboard already existing on your system.
See: https://gitlab.gnome.org/GNOME/mutter/-/issues/1869

In order to do so, get the devices currently attached to your system. In this example we're just grabbing the default keyboard and setting that as the device to clone.
On my virtualbox the output of `evtest`;
```
sam@ubuntuserver:~$ evtest
No device specified, trying to scan all of /dev/input/event*
Not running as root, no devices may be available.
Available devices:
/dev/input/event0:	Power Button
/dev/input/event1:	Sleep Button
/dev/input/event2:	AT Translated Set 2 keyboard
/dev/input/event3:	Video Bus
/dev/input/event4:	ImExPS/2 Generic Explorer Mouse
/dev/input/event5:	VirtualBox USB Tablet
/dev/input/event6:	VirtualBox mouse integration
```

```python
import ukeyboard
keyboard = ukeyboard.uinput_keyboard(dev_name="AT Translated Set 2 keyboard", clone=True)
keyboard.send_keys("The quick brown fox jumps over the lazy dog")
```

Essentially something about the way that a "default" uinput device is created causes the device to be ignored by something inbetween uinput and actually outputting things.