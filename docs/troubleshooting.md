# Troubleshooting

Find your symptom below. Most fixes need SSH: from a computer on the same Wi-Fi, run `ssh dietpi@scoreboard` (or
`ssh dietpi@<address>`; the address is in quick settings, by pressing and holding the screen).

**Still stuck?** Open an [issue](https://github.com/Bombsurace/{{REPO}}/issues/new/choose) and include the output of
the [log commands](#collecting-logs).

- [Power](#power)
- [First boot and setup](#first-boot-and-setup)
- [Screen and touch](#screen-and-touch)
- [Wi-Fi and network](#wi-fi-and-network)
- [Data and display](#data-and-display)
- [Printing](#printing)
- [Collecting logs](#collecting-logs)

---

## Power

### No power

**With the 2-wire snap-in USB-C socket, it only works from a USB-A charger with an A-to-C cable.** A USB-C to USB-C
charger won't turn on: chargers wait for two 5.1 kΩ resistors (on the CC pins) before sending power, and this socket
doesn't have them.

Fixes:
- Use a USB-A charger and an A-to-C cable, or
- Use a USB-C breakout board **with 5.1 kΩ resistors**. Fits the customizer back with `power = "usbc_board"`, or
- If your breakout has bare **CC1** and **CC2** pads, solder one 5.1 kΩ resistor from CC1 to GND and one from CC2 to
  GND.

Also check:
- The switch is on, and only the **+** wire goes through it.
- The pigtail is in the Orange Pi's **power** USB-C port (it's marked on the board).
- The charger gives at least 5 V 2 A (3 A recommended). Weak chargers cause random restarts.

### It restarts by itself, or the screen flickers

Usually a weak charger or a thin pigtail. Use a 5 V 3 A charger and a short, thick cable.

---

## First boot and setup

### It's been 20 minutes and it shows a text login prompt

Unplug it and plug it back in once. The setup finished, but the scoreboard starts on the next boot.

### It never gets on the network (can't find it, setup doesn't run)

- Check the Wi-Fi name and password in `dietpi-wifi.txt`. They're case-sensitive and go inside the single quotes.
- Check `AUTO_SETUP_NET_WIFI_ENABLED=1` and your country code in `dietpi.txt`.
- Re-write the card and start over. DietPi reads those files only on the very first boot.

### The scoreboard page doesn't load after setup

```bash
sudo systemctl status scoreboard        # should say "active (running)"
sudo systemctl start scoreboard         # start it if not
cat /var/tmp/dietpi/logs/scoreboard-setup.log | tail -40
```

If the setup log shows a failed `apt-get` or `pip install`, the network dropped during setup. Re-write the card and run
it again, or run the [manual install](software-setup.md#b-manual-install) steps over SSH.

### SSH says "REMOTE HOST IDENTIFICATION HAS CHANGED"

This is normal after re-writing the card: the board has a new identity. Remove the old entry, then connect again:

```bash
ssh-keygen -R scoreboard
ssh-keygen -R <board address>
```

### Pasted commands fail with odd errors

Paste each command as **one line**. Some terminals split long lines when pasting. Also, run `scp` (copying files) from
your computer, not from inside an SSH session on the board: type `exit` first.

---

## Screen and touch

### Every tap lands in a corner (top-left or bottom-right)

Some touchscreens are *multi-touch* panels, and this board's kernel has no driver for them, so taps land at the edge.
The `touchfix` service fixes it (the SD card installs it):

```bash
sudo systemctl status touchfix          # should be active
sudo systemctl restart touchfix
```

If it's missing, see the touch fix in the [manual install](software-setup.md#b-manual-install).

### Touch doesn't work at all

- The screen's **Touch** micro-USB port must connect to the Orange Pi with a **data** (OTG) cable. Charge-only cables
  power the screen but carry no touch.
- Check the screen is seen: `ls /dev/input/by-id/`.

### A mouse cursor shows on the screen

The kiosk installs an invisible cursor theme. Reboot once; if it persists:
```bash
ls -la ~/.icons/default/cursors         # should point to ~/.icons/blank/cursors
```

### Black screen, but the board is on

- Check the FPC ribbon is fully seated at both ends, contacts the right way up.
- Power the screen through the Orange Pi's second USB-C port (or its own charger), not just HDMI.
- Over SSH: `cat /tmp/kiosk.log` shows browser errors.

### The picture is upside down or sideways

Settings → Display → Rotation (or *Upside down* in quick settings).

### The lit area isn't centered in the front's window

Screens vary a little. The 7" front is tuned for the tested Hosyond (`mount_shift` in `frame/field_frame.py`). Print
`frame/stl/tests/screen_center_test_7in.stl`, measure how much black shows on each side, and adjust `mount_shift`
(x, y in mm).

---

## Wi-Fi and network

### I can't find the board's address

Press and hold the screen: quick settings show it. Or look in your router's app for a device named `scoreboard`.

### The address changes after a power cut

Reserve it in your router (*address reservation* or *static DHCP*), using the board's address and the name
`scoreboard`.

### The board drops off the network after a while

The setup turns off Wi-Fi power saving, which causes this. Check it:
```bash
/usr/sbin/iw dev wlan0 get power_save    # should say "Power save: off"
sudo systemctl status wifi-powersave-off
```

### My phone can't open the settings page

- The phone must be on the same Wi-Fi (not mobile data or a guest network).
- Some mesh and guest networks block devices from reaching each other. Use the main network, or add Tailscale (see
  [software setup](software-setup.md#2-add-the-setup-script)).

### Changing Wi-Fi from the screen fails

- It goes back to the old network after about 30 seconds if the new one doesn't connect: check the password.
- Over SSH: `sudo cat /etc/wpa_supplicant/wpa_supplicant.conf` shows the saved networks.

---

## Data and display

### Logos show as colored circles with letters

The board downloads logos from ESPN on first start. Circles show until a download works; they fill in by themselves
once the board is online.

### Scores are behind or ahead of the TV

Ahead (spoilers): set Settings → Behavior → **TV sync delay** to 30–60 seconds. Behind: lower it to 0.

### Game times are wrong by a few hours

The board's time zone is wrong. Set `AUTO_SETUP_TIMEZONE` before first boot, or later with `sudo dietpi-config` →
Language/Regional Options → Timezone, then `sudo systemctl restart scoreboard`.

### Scores stop updating

ESPN's feed is unofficial and occasionally changes. Check
[Issues](https://github.com/Bombsurace/{{REPO}}/issues) for a fix, then [update](software-setup.md#updating).

---

## Printing

### The kickstand hinge is fused

Push the leg open firmly once: the first push breaks it free. If it won't move, print the hinge tests in
`frame/stl/tests/` and use `back_tray_medium.stl` or `back_tray_loose.stl`.

### The kickstand is floppy

Print the tight version (`back_tray.stl`, 0.30 mm). The click-shut catch holds it folded either way.

### The switch or USB-C socket won't snap in

The wall around each hole is thinned to 1.8 mm for the clips. If a clip still won't catch, sand the inside of the wall
around the hole. Print `wall_fit_test_switch_usbc.stl` first to check.

### End zones are loose or won't click in

PETG clips grip better than PLA. If they're too tight, sand the clip hooks lightly. If they're loose, check your
printer's dimensional accuracy (a 20 mm test cube should measure 20.0 ± 0.1 mm).

### The yard lines or letters are the wrong color

In the slicer, set the *lines* or *letters* part to the second filament (see
[printing guide](printing.md#two-color-prints-in-bambu-studio)).

---

## Collecting logs

Run these and paste the output into your issue:

```bash
cat /etc/os-release | head -3
sudo systemctl status scoreboard touchfix --no-pager
sudo journalctl -u scoreboard -n 80 --no-pager
tail -40 /var/tmp/dietpi/logs/scoreboard-setup.log
cat /tmp/kiosk.log | tail -20
```

They don't contain passwords. Remove your network name if you'd rather not share it.
