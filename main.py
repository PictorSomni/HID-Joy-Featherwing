import time
import usb_hid
import board
from micropython import const
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode as ccc
from adafruit_hid.mouse import Mouse
from adafruit_seesaw.seesaw import Seesaw

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

i2c_bus = board.I2C()
ss = Seesaw(i2c_bus)
ss.pin_mode_bulk(button_mask, ss.INPUT_PULLUP)

cc = ConsumerControl(usb_hid.devices)
mouse = Mouse(usb_hid.devices)

last_x = 0
last_y = 0

pot_min = 0
pot_max = 1024
step = (pot_max - pot_min) / 20


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
        cc.press(ccc.STOP)
        time.sleep(0.5)
        cc.release()
    if not buttons & (1 << BUTTON_DOWN):
        cc.press(ccc.SCAN_PREVIOUS_TRACK)
        time.sleep(0.5)
        cc.release()
    if not buttons & (1 << BUTTON_LEFT):
        cc.press(ccc.PLAY_PAUSE)
        time.sleep(0.5)
        cc.release()
    if not buttons & (1 << BUTTON_UP):
        cc.press(ccc.SCAN_NEXT_TRACK)
        time.sleep(0.5)
        cc.release()
    if not buttons & (1 << BUTTON_SEL):
        mouse.click(mouse.LEFT_BUTTON)
