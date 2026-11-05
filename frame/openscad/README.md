# OpenSCAD customizers (3D parts only)

These files only make 3D parts. They don't touch the scoreboard software. License: [CC BY-NC-SA 4.0](../LICENSE). `frame/field_frame.py` is still where the tested
prints come from and is used to check that the OpenSCAD defaults match.

| File | Makes | Status |
|---|---|---|
| `endzone_customizer.scad` | snap-in end zone inserts with flush two-color lettering | tested on MakerWorld |
| `back_customizer.scad` | back tray: board presets and rotation, power/switch holes, kickstand on/off, hinge tightness | default matches the tested print |
| `front_customizer.scad` | field front: screen presets or custom screen | planned |

## End zones

**Settings:** left and right text (one or two lines each), font, a size tweak (60–120%), which inserts to make
(both, left, right, blank), and the two colors.

**Built like the tested inserts:** same size (25.6 × 139.6 × 2 mm), same four snap clips, letters 0.6 mm deep and
flush with the face. It prints face down with the clips up, no supports. The lettering is mirrored in the file so it
reads the right way once flipped and snapped in. Long names shrink to fit automatically.

**Default font:** Roboto Condensed Bold (a Google Font, available on MakerWorld). Other bold or condensed fonts work
too; use the size slider if a font comes out too big or small.

### Testing on a desktop
1. Install OpenSCAD (openscad.org, 2021.01 or newer).
2. Install the font: download *Roboto Condensed* from Google Fonts and install the Bold weight. Without it, OpenSCAD
   falls back to a default font; you can also type `Liberation Sans:style=Bold`, which comes with OpenSCAD.
3. Open `endzone_customizer.scad`, then **Window → Customizer** if the panel isn't showing.
4. Type your text. **F5** previews, **F6** builds.
5. For a two-color print, export two files: set **Output → Insert only**, press F6, then **File → Export → STL**.
   Then set **Output → Letters only**, press F6, and export again.
6. In Bambu Studio, drag **both files in together** and answer **Yes** to "load as one object with multiple parts". Set
   the letters part to your second color.

### Testing on MakerWorld (do this before publishing) 
1. Open MakerWorld's **Parametric Model Maker**, load `endzone_customizer.scad`, and try a few names.
2. Check that it generates quickly and that the downloaded 3MF has **two parts in two colors** (insert and letters).
3. If it comes out as one color, set Output to *Insert only* and *Letters only* in turn as a fallback, and note it in
   the listing.

## Back tray

**Settings:**
- **Board:** Orange Pi Zero 2W (tested), Raspberry Pi Zero 2 W (same footprint), or Custom (length, width, hole spacing
  both ways, hole size, tallest part). Held by pegs + 2 swivel clamps, or screw posts. The board can be moved, and turned 0/90/180/270° so its ports face
  down (tested), right, up or left. Its labels turn with it.
- **Power hole:** USB-C snap-in (tested), USB-C breakout pocket, Custom (rectangle, rounded slot or circle), or none.
- **Switch hole:** KCD11 (tested), Custom, or none.
- **Placement:** which wall, position along it, spacing between the two, and whether to thin the wall for snap-in parts.
- **Kickstand:** on or off (off = solid back for wall-only use, hangs on the keyholes); tight (tested), medium or
  loose hinge; click-shut catch on or off.
- **Extras:** keyholes, antenna clips and labels, each on or off. *What to make*
  also offers the Pi swivel clamp (print 2).

**Checks:** if a custom board or hole would run into the kickstand, keyholes, antenna clips, the board, a corner post
or the other hole, OpenSCAD stops with a message saying what it hits and what to change, instead of making a part
that won't work. Vents on the top and bottom walls are left out wherever a power or switch hole lands on them.

**Turned board positions that fit** (with the default holes on the right wall): turned 90° at `board_center_x = -95`,
`board_center_y = 0` (left of the kickstand); turned 180° at the default spot moved down 1 mm (`board_center_y = 11`).

**Matches the tested back:** with the default settings it differs from `stl/back_tray.stl` only in label font and
corner faceting (about 0.1% of the part). The kickstand clicks shut and swings free to the stops the same way.

**Speed:** about 5–7 seconds to generate (labels are most of it). If MakerWorld times out, turn **Raised labels** off
(about 4 seconds).
