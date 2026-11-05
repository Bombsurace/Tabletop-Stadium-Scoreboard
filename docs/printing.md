# Printing guide

All the print files are in [`frame/stl/`](../frame/stl). Every file is already turned the right way to print, and
**nothing needs supports**. STEP files for Fusion 360 and other CAD apps sit next to every STL.

**Frame size:** 280 × 150 × 42 mm. The largest part (280 × 150) needs a bed of at least 290 × 160 mm.

## Settings

| Setting | Value |
|---|---|
| Material | PLA or PETG (PETG for the end zones makes their clips last longer) |
| Layer height | 0.2 mm |
| Walls | 3 |
| Infill | 15% |
| Supports | **off** for every part |
| Brim | not needed; use one on the back tray if your corners lift |

## What to print

| File | Qty | Notes |
|---|---|---|
| `back_tray.stl` | 1 | holds all the electronics. The kickstand prints **in place** with a tight hinge (0.30 mm) and clicks shut |
| `front_standard7_2color.3mf` | 1 | the field for the 7" screen, **two colors**: one object with two parts. Set the "lines" part to white |
| `endzone_left_2color.3mf`, `endzone_right_2color.3mf` | 1 each | snap-in end zones with flush lettering. Set the "letters" part to white. Make your own text with the [customizer](../frame/openscad/README.md) |
| `pi_clamp.stl` | 2 | swivel clamps that hold the Orange Pi down |

**Single-color printer?** Use `front_standard7.stl` instead of the 3MF: the yard lines come out as grooves, and you can
paint them or leave them. For the end zones, use `endzone_blank.stl` or print a 3MF in one color.

### Options

| File | When to use it |
|---|---|
| `back_tray_medium.stl`, `back_tray_loose.stl` | if the kickstand hinge fuses on your printer: same back, hinge gap 0.45 / 0.60 mm |
| `back_tray_blank.stl` + `cutter_usb_c_socket.stl`, `cutter_switch.stl` | a back with no power or switch holes, so you can place your own (see below) |
| `endzone_blank.stl` | plain end zone to decorate yourself |
| `front_wide79*.stl/3mf`, `screen_tab.stl` (×4), `screen_cradle_wide79.stl` | for the Waveshare 7.9" bar screen. *Untested* |

## Before the big parts: test prints

These small pieces are cut straight from the real parts, so a fit problem costs minutes instead of a whole back tray.
They're in [`frame/stl/tests/`](../frame/stl/tests).

| File | Checks |
|---|---|
| `hinge_test_tight.stl`, `_medium`, `_loose` | which kickstand hinge clearance works on your printer. Tight is the least floppy but can fuse. Pick the tightest one that swings freely after a firm first push, then print the matching back tray |
| `wall_fit_test_switch_usbc.stl` | the switch and USB-C socket snap into the wall |
| `screen_center_test_7in.stl` | the 7" screen's lit area is centered in the window (about 18 g) |
| `pi_antenna_fit_test.stl` | the Orange Pi on its pegs with both clamps, and the antenna clips |
| `kickstand_test_tight_catch.stl` | the full kickstand with its click-shut catch |

## Print order

1. **Test prints** above (optional, but the hinge test is worth it).
2. **Back tray.** Set the real parts in their labeled spots before printing the rest.
3. **Front**, then the **end zones** and **clamps**.

## After printing

- **Kickstand:** push the leg open firmly once to break it free. It stops at about 32°, which leans the frame back
  about 22°. To close, fold it flat until it clicks. To open, hook a finger in the slot near the foot and pull.
- **End zones:** press them in until they click. To swap one, pry at the notch on the outer edge.

## Two-color prints in Bambu Studio

The 3MF files already contain both parts. Open the file, then in the object list set the *lines* or *letters* part to
your second filament.

If you're using STL files instead, drag **both** files in together (for example `front_standard7.stl` and
`front_standard7_lines.stl`) and answer **Yes** to "load as a single object with multiple parts".

## Cutting your own holes (blank back)

Use `back_tray_blank.stl` and the two cutters to place the power socket and switch wherever you want, at your parts'
sizes. In Bambu Studio:

1. Load `back_tray_blank.stl`.
2. Right-click it, choose **Add negative part → Load…** and pick `cutter_usb_c_socket.stl` or `cutter_switch.stl`.
3. Scale the cutter to your part's hole, rotate it to go straight through a wall, and move it into place. It's 12 mm
   long, so it passes all the way through.
4. Repeat for the other hole.

Snap-in parts usually want a wall about 1.5–2 mm thick. The blank back's walls are 2.4 mm; if a clip won't catch, sand
the inside of the wall around the hole a little. The [back tray customizer](../frame/openscad/README.md) does this for
you, including thinning the wall.

## Print problems

See [Troubleshooting → Printing](troubleshooting.md#printing).
