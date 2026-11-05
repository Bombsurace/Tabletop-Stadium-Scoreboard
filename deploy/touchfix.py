#!/usr/bin/env python3
"""Touch fix for multi-touch panels the kernel drives as single-touch (e.g. QDTECH MPI7002 in the Hosyond 7").

Without the hid-multitouch driver, each touch frame from these panels carries several finger slots
(ABS_X/ABS_Y pairs) and the last one, an empty slot at the far corner, wins. Every tap then lands in
the bottom-right corner. This program takes the panel over (grab), keeps only the FIRST position in each
frame (the real finger) and passes clean single-touch events on through a virtual touchscreen.

Runs as a system service (touchfix.service). Needs: apt install python3-evdev
"""
import sys
import time

import evdev
from evdev import AbsInfo, UInput
from evdev import ecodes as e

PANELS = {(0x0484, 0x5750)}          # (vendor, product) of panels that need this
VIRTUAL_NAME = "scoreboard-touch"


def find_panel():
    for path in evdev.list_devices():
        try:
            d = evdev.InputDevice(path)
        except OSError:
            continue
        if (d.info.vendor, d.info.product) in PANELS and d.name != VIRTUAL_NAME:
            return d
        d.close()
    return None


def main():
    dev = None
    while dev is None:                    # the panel may show up a little after boot
        dev = find_panel()
        if dev is None:
            time.sleep(2)
    ax, ay = dev.absinfo(e.ABS_X), dev.absinfo(e.ABS_Y)
    caps = {
        e.EV_KEY: [e.BTN_TOUCH],
        e.EV_ABS: [(e.ABS_X, AbsInfo(0, ax.min, ax.max, 0, 0, 0)),
                   (e.ABS_Y, AbsInfo(0, ay.min, ay.max, 0, 0, 0))],
    }
    ui = UInput(caps, name=VIRTUAL_NAME, vendor=0x1d6b, product=0x0104, input_props=[e.INPUT_PROP_DIRECT])
    dev.grab()                            # nothing else sees the raw (broken) events
    print(f"touchfix: {dev.name} -> {VIRTUAL_NAME} (x 0-{ax.max}, y 0-{ay.max})", flush=True)

    down = False                          # finger currently on the glass (as we report it)
    frame_btn, fx, fy = None, None, None  # this frame: touch state, first x, first y
    for ev in dev.read_loop():
        if ev.type == e.EV_KEY and ev.code == e.BTN_TOUCH:
            frame_btn = bool(ev.value)
        elif ev.type == e.EV_ABS and ev.code == e.ABS_X and fx is None:
            fx = ev.value
        elif ev.type == e.EV_ABS and ev.code == e.ABS_Y and fy is None:
            fy = ev.value
        elif ev.type == e.EV_SYN and ev.code == e.SYN_REPORT:
            want = down if frame_btn is None else frame_btn
            corner = fx == ax.max and fy == ay.max          # an empty slot, not a finger
            if want and fx is not None and fy is not None and not corner:
                ui.write(e.EV_ABS, e.ABS_X, fx)
                ui.write(e.EV_ABS, e.ABS_Y, fy)
                if not down:
                    ui.write(e.EV_KEY, e.BTN_TOUCH, 1)
                    down = True
                ui.syn()
            elif not want and down:
                ui.write(e.EV_KEY, e.BTN_TOUCH, 0)
                down = False
                ui.syn()
            frame_btn, fx, fy = None, None, None


if __name__ == "__main__":
    try:
        main()
    except OSError as err:                # panel unplugged: exit, systemd restarts us
        print("touchfix:", err, file=sys.stderr)
        sys.exit(1)
