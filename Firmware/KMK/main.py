import board
import busio

import asyncio
from kmk.kmk_keyboard import KMKKeyboard
from kmk.scanners.keypad import KeysScanner
from kmk.scanners import DiodeOrientation
from kmk.keys import KC
from kmk.modules.macros import Macros
from kmk.extensions.display import Display, TextEntry, BitmapEntry
from kmk.handlers.sequences import simple_key_sequence, send_string
from kmk.extensions.display.ssd1306 import SSD1306
from kmk.modules.encoder import EncoderHandler
import time

last_encoder_event_time = 0
display_timeout = 2

COL1 = board.GP26
COL2 = board.GP27
COL3 = board.GP28
COL4 = board.GP29
ROW1 = board.GP3
ROW2 = board.GP4
ROW3 = board.GP2

bus = busio.I2C(board.GP_SCL, board.GP_SDA)
driver = SSD1306(i2c=bus, device_address=0x3C)

display = Display(
    display=driver,
    flip=True,
    width=128,
    height=32,
    dim_time=10,
    dim_target=0.2,
    off_time=1200,
    brightness=0.8
)
default_display = [
    TextEntry(text='BajajPad', x=64, y=12, x_anchor="M"),
]
display.entries = default_display

keyboard = KMKKeyboard()
encoder_handler = EncoderHandler()

macros = Macros()
keyboard.modules.append(macros)
keyboard.modules.append(encoder_handler)
keyboard.extensions.append(display)

keyboard.col_pins = (COL1, COL2, COL3, COL4)
keyboard.row_pins = (ROW1, ROW2, ROW3)
keyboard.diode_orientation = DiodeOrientation.COL2ROW

encoder_handler.pins =((board.GP0,board.GP1),)
encoder_handler.map = [(KC.VOLD, KC.VOLU)]

rick_art = [
    0b0000011110000000,
    0b0001111111100000,
    0b0011111111110000,
    0b0111101111011000,
    0b0111111111111000,
    0b0111111111111000,
    0b0011011110110000,
    0b0000111111000000,
    0b0000111111000000,
    0b0000111111000000,
    0b0000110111000000,
    0b0000010010000000,
    0b0000010010000000,
    0b0000110111000000,
    0b0000011110000000,
    0b0000000000000000,
]
def show_rickroll_animation():
    display.display_image([
        BitmapEntry(bitmap=rick_art, width=16, height=16, x=56, y=8),
    ])
async def rickroll_action(*args, **kwargs):
    show_rickroll_animation()
    keyboard.tap_key([KC.LGUI, KC.R])
    keyboard.send_string("https://www.youtube.com/watch?v=dQw4w9WgXcQ\n")
    await asyncio.sleep(3)
    display.entries = default_display

def show_volume_change(text):
    display.entries = [
        TextEntry(text=text, x=64, y=12, x_anchor="M")
    ]
def handle_encoder(index, direction):
    global last_encoder_event_time

    if direction > 0:
        keyboard.send(KC.VOLU)
        show_volume_change("Volume UP ↑")
    elif direction < 0:
        keyboard.send(KC.VOLD)
        show_volume_change("Volume DOWN ↓")

    last_encoder_event_time = time.monotonic()

encoder_handler.handlers = [handle_encoder]

rickroll_macro = rickroll_action
ss_macro = simple_key_sequence((KC.LGUI, KC.LSHIFT, KC.S))
keyboard.keymap = [
    [[KC.LALT, KC.TAB], KC.W,               ss_macro,           KC.MUTE],
    [KC.A,              KC.S,               KC.D,               [KC.LGUI, KC.L]],
    [[KC.LCTRL, KC.C],  [KC.LCTRL, KC.V],   [KC.LCTRL, KC.X],   rickroll_macro],
]
idle_display = [TextEntry(text='BajajPad', x=64, y=12, x_anchor="M")]
display.entries = idle_display

if __name__ == '__main__':
    keyboard.go()
    if (time.monotonic() - last_encoder_event_time > display_timeout and display.entries != idle_display):
            display.entries = idle_display