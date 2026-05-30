from machine import Pin, PWM, I2C
import time
import ssd1306

# ── Hardware ──────────────────────────────────────────────
buzzer = PWM(Pin(2))
buzzer.freq(1000)

do_pin = Pin(1, Pin.IN, Pin.PULL_DOWN)

light_pin = Pin(4, Pin.OUT)
bump_pin = Pin(5, Pin.OUT)

i2c = I2C(1, scl=Pin(15), sda=Pin(14))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# ── Helpers ───────────────────────────────────────────────

def circle(cx, cy, r):
    """Midpoint circle algorithm — draws outline."""
    x, y, err = r, 0, 0
    while x >= y:
        for px, py in ((x, y), (y, x), (-y, x), (-x, y),
                       (-x, -y), (-y, -x), (y, -x), (x, -y)):
            oled.pixel(cx + px, cy + py, 1)
        y += 1
        err += 1 + 2 * y
        if 2 * (err - x) + 1 > 0:
            x -= 1
            err += 1 - 2 * x

def fill_circle(cx, cy, r):
    """Filled circle — draws concentric outlines inward."""
    for radius in range(r, -1, -1):
        circle(cx, cy, radius)

def draw_dry_face():
    """Hot / thirsty face with X eyes and wavy mouth."""
    oled.fill(0)

    # Round head
    circle(64, 28, 22)

    # X left eye  (center ~54, 22)
    oled.line(51, 19, 57, 25, 1)
    oled.line(57, 19, 51, 25, 1)

    # X right eye (center ~74, 22)
    oled.line(71, 19, 77, 25, 1)
    oled.line(77, 19, 71, 25, 1)

    # Wavy / worried mouth (~4 horizontal dashes)
    for i, (mx, my) in enumerate(((56, 34), (60, 36), (64, 34), (68, 36), (72, 34))):
        oled.hline(mx - 3, my, 6, 1)

    # Sweat drop on forehead
    oled.pixel(76, 8, 1)
    oled.pixel(77, 9, 1)
    oled.pixel(76, 10, 1)
    oled.pixel(75, 9, 1)

    # "DRY" label
    oled.text("DRY", 4, 54)

    oled.show()

def draw_wet_face():
    """Happy / hydrated face with arched eyes and big smile."""
    oled.fill(0)

    # Round head
    circle(64, 28, 22)

    # Happy arched eyes ( ^  ^ )
    for dx, dy in ((52, 20), (72, 20)):
        oled.pixel(dx, dy + 2, 1)
        oled.pixel(dx + 1, dy + 1, 1)
        oled.pixel(dx + 2, dy, 1)
        oled.pixel(dx + 3, dy + 1, 1)
        oled.pixel(dx + 4, dy + 2, 1)

    # Big smile (arc across bottom of face)
    smile_y = 38
    for sx in range(54, 75):
        # parabola-ish curve
        offset = ((sx - 64) ** 2) // 28
        oled.pixel(sx, smile_y - offset, 1)

    # Rosy cheeks (tiny filled circles)
    fill_circle(49, 30, 2)
    fill_circle(79, 30, 2)

    # "WET" label
    oled.text("WET", 4, 54)

    oled.show()

# ── Relay control ────────────────────────────────────────

def everything_on():
    buzzer.duty_u16(32768)
    light_pin.value(1)
    bump_pin.value(1)

def everything_off():
    buzzer.duty_u16(0)
    light_pin.value(0)
    bump_pin.value(0)

# ── Main loop ────────────────────────────────────────────

print("--- Humidity + Relay + Buzzer Control ---")
everything_off()
last_state = None

while True:
    is_dry = do_pin.value() == 1

    if is_dry == last_state:
        time.sleep(0.2)
        continue

    last_state = is_dry

    if is_dry:
        everything_on()
        draw_dry_face()
        print("Dry - watering")
    else:
        everything_off()
        draw_wet_face()
        print("Wet - idle")

    time.sleep(0.2)
