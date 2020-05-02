import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse
import busio
from micropython import const
from board import SCL, SDA
from adafruit_seesaw.seesaw import Seesaw
from time import sleep

COUNT = 1
MOUSE_MAX = 20
BUTTON_RIGHT = const(6)
BUTTON_DOWN = const(7)
BUTTON_LEFT = const(9)
BUTTON_UP = const(10)
BUTTON_SEL = const(14)

button_mask = const(
    (1 << BUTTON_RIGHT)
    | (1 << BUTTON_DOWN)
    | (1 << BUTTON_LEFT)
    | (1 << BUTTON_UP)
    | (1 << BUTTON_SEL)
)

i2c_bus = busio.I2C(SCL, SDA)
ss = Seesaw(i2c_bus)
ss.pin_mode_bulk(button_mask, ss.INPUT_PULLUP)

sleep(1)
keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)

mouse = Mouse(usb_hid.devices)
pot_min = 0
pot_max = 1024
step = (pot_max - pot_min) / 20
last_x = 0
last_y = 0

def counter() :
    global COUNT
    COUNTER_SEQUENCE = [Keycode.F2, "g_{:02}\n".format(COUNT)]
    for key in COUNTER_SEQUENCE :
        if isinstance(key, str):
            keyboard_layout.write(key)
        else:
            keyboard.press(key)
            keyboard.release_all()
        sleep(0.1)
    COUNT+=1

def normalize(value, min, max, new_min, new_max):
    if value > max:
        value = max
    if value < min:
        value = min
    newvalue = int((new_max - new_min) / (max - min) * (value-max) + new_max)
    return newvalue

def steps(axis):
    """ Maps the potentiometer voltage range to 0-20 """
    return round((axis - pot_min) / step)

while True:
    x = ss.analog_read(2)
    y = ss.analog_read(3)
    buttons = ss.digital_read_bulk(button_mask)
    if steps(x) > 11:
        mouse.move(x=-normalize(x, 600, 1023, 0, MOUSE_MAX))
    if steps(x) < 9:
        mouse.move(x=normalize(x, 0, 400, MOUSE_MAX, 0))
    if steps(y) > 11:
        mouse.move(y=normalize(y, 600, 1023, 0, MOUSE_MAX))
    if steps(y) < 9:
        mouse.move(y=-normalize(y, 0, 400, MOUSE_MAX, 0))
    if not buttons & (1 << BUTTON_RIGHT):
        keyboard_layout.write("PASSWORD 1")
        sleep(0.5)
    if not buttons & (1 << BUTTON_DOWN):
        keyboard_layout.write("PASSWORD 2")
        sleep(0.5)
    if not buttons & (1 << BUTTON_LEFT):
        counter()
        sleep(0.5)
    if not buttons & (1 << BUTTON_UP):
        keyboard_layout.write("PASSWORD 3")
        sleep(0.5)
    if not buttons & (1 << BUTTON_SEL):
        mouse.click(Mouse.LEFT_BUTTON)
        sleep(0.5)