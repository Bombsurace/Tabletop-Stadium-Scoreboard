# FAQ

**How much does it cost?**
Roughly $100–130 in parts, plus under 400 g of filament. The screen and the Orange Pi are most of it. See the
[parts list](parts.md).

**Can I use a Raspberry Pi instead of an Orange Pi?**
A Raspberry Pi Zero 2 W has the same size and mounting holes, and the back tray customizer has a preset for it. The
software runs on any Debian-based system with Python and Chromium. It's *untested* on the Pi so far; reports are welcome.

**What size SD card do I need?**
16 or 32 GB, A1-rated or faster (any well-known brand). The whole system with the scoreboard uses only a few GB, and
future sports add almost nothing, because each one is a little code, not a separate install. 8 GB works but leaves little
room for updates, and it's barely cheaper. A bigger card doesn't make it faster. A "high endurance" card lasts longest
for something that runs all day.

**Can I use a different screen?**
The software adapts to any screen shape. It has layouts for 1024×600, 800×480, 1280×400 bars and more, picked
automatically. The frame currently has fronts for the Hosyond 7" (tested) and Waveshare 7.9" bar (untested). A front
customizer for other screens is planned.

**Why won't it turn on with my USB-C charger?**
The tested build uses a 2-wire USB-C socket without the resistors a USB-C to USB-C charger looks for, so those
chargers never turn on. Use a USB-A charger and a USB-A to USB-C cable. See
[troubleshooting](troubleshooting.md#no-power).

**Does it need a subscription or an account?**
No. It reads ESPN's free public scoreboard feed. No account, no API key, and nothing is sent anywhere.

**Is ESPN's feed official?**
No. It's public but undocumented, and widely used by hobby projects. It can change without notice. If it does, the fix
goes in one file (`espn.py`), and you update with `git pull` or a new SD card.

**Will it spoil plays before I see them on TV?**
ESPN's data often runs 30–60 seconds ahead of the broadcast. Set a TV sync delay in Settings → Behavior.

**Does it do other sports?**
Football (NFL) for now. Baseball, hockey, basketball and college are planned, using the same board and back tray with
new fronts. Watch or star the repository to hear about them.

**Can I put my team's name on the end zones?**
Yes. Use the [end zone customizer](../frame/openscad/README.md) (on MakerWorld or in desktop OpenSCAD) to make any text
with flush two-color lettering.

**Can I sell prints?**
The 3D models are licensed [CC BY-NC-SA 4.0](../frame/LICENSE): non-commercial. Printing for yourself and friends is
fine. The code is MIT.

**Does it work without Wi-Fi?**
It needs internet for live scores. If Wi-Fi drops, it shows a *No Wi-Fi* screen with a button to set up a network.

**Can I hang it on the wall?**
Yes. Two keyholes 200 mm apart are built into the back, and the kickstand folds flat and clicks shut. The back tray
customizer can also make a version with no kickstand.

**Why is my phone's settings page empty or unreachable?**
See [troubleshooting](troubleshooting.md#my-phone-cant-open-the-settings-page).

**Can I control it with buttons or a knob?**
There's an HTTP API for next, previous, auto and locking a game. See [development](development.md#api). A rotary
knob add-on is on the idea list.
