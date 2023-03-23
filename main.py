# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import terminalio
import displayio
import adafruit_imageload
from adafruit_display_text import label
from adafruit_magtag.magtag import MagTag
from adafruit_seesaw.seesaw import Seesaw

# ----------------------------
# Define various assets
# ----------------------------
BACKGROUND_BMP = "/bmps/weather_bg.bmp"
ICONS_LARGE_FILE = "/bmps/weather_icons_70px.bmp"

magtag = MagTag()
# ----------------------------
# Backgrounnd bitmap
# ----------------------------
# magtag.graphics.set_background(BACKGROUND_BMP)

# ----------------------------
# Weather icons sprite sheet
# ----------------------------
icons_large_bmp, icons_large_pal = adafruit_imageload.load(ICONS_LARGE_FILE)

# /////////////////////////////////////////////////////////////////////////

def go_to_sleep(current_time):
    """We want to wake up at 6am, 2pm and 10pm"""
    # compute current time offset in seconds
    hour, minutes, seconds = time.localtime(current_time)[3:6]
    seconds_since_midnight = 60 * (hour * 60 + minutes) + seconds
    six = (6 * 60) * 60
    # wake up at 6am
    seconds_to_sleep = (24 * 60 * 60 - seconds_since_midnight) + six
    print(
        "Sleeping for {} hours, {} minutes".format(
            seconds_to_sleep // 3600, (seconds_to_sleep // 60) % 60
        )
    )
    magtag.exit_and_deep_sleep(seconds_to_sleep)
    
def make_banner(x=0, y=0):
    """Make a single future forecast info banner group."""
    day_of_week = label.Label(terminalio.FONT, text="DAY", color=0x000000)
    day_of_week.anchor_point = (0, 0.5)
    day_of_week.anchored_position = (0, 10)

    icon = displayio.TileGrid(
        icons_small_bmp,
        pixel_shader=icons_small_pal,
        x=25,
        y=0,
        width=1,
        height=1,
        tile_width=20,
        tile_height=20,
    )

    day_temp = label.Label(terminalio.FONT, text="+100F", color=0x000000)
    day_temp.anchor_point = (0, 0.5)
    day_temp.anchored_position = (50, 10)

    group = displayio.Group(x=x, y=y)
    group.append(day_of_week)
    group.append(icon)
    group.append(day_temp)

    return group
    
def update_banner(banner, data):
    """Update supplied forecast banner with supplied data."""
    banner[0].text = DAYS[time.localtime(data["dt"]).tm_wday][:3].upper()
    banner[1][0] = ICON_MAP.index(data["weather"][0]["icon"][:2])
    banner[2].text = temperature_text(data["temp"]["day"])
    
def update_today(data):
    """Update today info banner."""
    date = time.localtime(data["dt"])
    sunrise = time.localtime(data["sunrise"])
    sunset = time.localtime(data["sunset"])

    today_date.text = "{} {} {}, {}".format(
        DAYS[date.tm_wday].upper(),
        MONTHS[date.tm_mon - 1].upper(),
        date.tm_mday,
        date.tm_year,
    )
    today_icon[0] = ICON_MAP.index(data["weather"][0]["icon"][:2])
    today_morn_temp.text = temperature_text(data["temp"]["morn"])
    today_day_temp.text = temperature_text(data["temp"]["day"])
    today_night_temp.text = temperature_text(data["temp"]["night"])
    today_humidity.text = "{:3d}%".format(data["humidity"])
    today_wind.text = wind_text(data["wind_speed"])
    today_sunrise.text = "{:2d}:{:02d} AM".format(sunrise.tm_hour, sunrise.tm_min)
    today_sunset.text = "{:2d}:{:02d} PM".format(sunset.tm_hour - 12, sunset.tm_min)

# uses board.SCL and board.SDA
i2c_bus = board.I2C()

# locate the moisture sensor
ss = Seesaw(i2c_bus, addr=0x36)

# read moisture level through capacitive touch pad
touch = ss.moisture_read()

# read temperature from the temperature sensor
temp = ss.get_temp()

magtag.add_text(
    text_position=(
        180,
        (magtag.graphics.display.height // 2) - 1,
    ),
    text_scale=3,
    text=touch
)

print("sleeping for one second to test screen refresh")
time.sleep(1)

magtag.add_text(
    text_position=(
        1,
        (magtag.graphics.display.height // 2) - 1,
    ),
    text_scale=2,
    text=temp
)

# TODO: Need to figure out how to refresh the screen all at once
# instead of waiting for each element to appear which takes a while
print("we should have two numbers")

time.sleep(10)

print("temp: " + str(temp) + "  moisture: " + str(touch))
    
magtag.exit_and_deep_sleep(10)
#  entire code will run again after deep sleep cycle
#  similar to hitting the reset button
