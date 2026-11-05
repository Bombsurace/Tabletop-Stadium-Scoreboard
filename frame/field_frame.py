"""Football-field scoreboard frame: hangs on a wall or stands on a desk.

    pip install cadquery
    python field_frame.py                          # everything
    python field_frame.py --left JAGUARS --right JACKSONVILLE
    python field_frame.py --check                  # overlap / cutout report only

Parts (all print with no supports)
  back_tray.stl          shared by every screen. Printed flat side (the back) down. A labeled spot for
                         every part, wall-hanging keyholes and a print-in-place kickstand.
  front_<screen>.stl     the field. Printed face down. Screws to the tray from behind.
  front_<screen>_lines.stl  optional second-color inlay for the yard lines and numbers
  screen_tab.stl         print 4: they clamp the screen to the front
  pi_clamp.stl           print 2: swivel clamps that hold the Orange Pi down (M3 x 8)
  endzone_*.stl          swappable end zone inserts (fit every front). Translucent filament glows
                         if LEDs are added behind them later.

EVERY SIZE IS A NAMED NUMBER BELOW. If a part measures differently, change one number and re-run.
Numbers marked UNVERIFIED are from spec sheets: measure your part before printing the tray.
"""
import argparse
import math
import os

import cadquery as cq

# =============================================================================
# FRAME
# =============================================================================
FW, FH = 280.0, 150.0      # outside width and height (Bambu H2C bed: 330 x 320)
CORNER_R = 4.0             # outside corner radius
WALL = 2.4                 # tray side walls
FLOOR = 3.0                # tray floor (the back panel)
ELEC_H = 16.0              # electronics layer: tallest part (with plugs) must fit under this
SCREEN_ZONE = 20.0         # space for the screen; fits screens up to this thick
FACE_T = 3.0               # front (field) thickness
CLR = 0.3                  # clearance per side for parts in holders
FIT = 0.3                  # clearance between printed parts

Z_ELEC = FLOOR + ELEC_H            # top of the electronics layer (19)
Z_FACE = Z_ELEC + SCREEN_ZONE      # back of the field / top of the tray walls (39)
DEPTH = Z_FACE + FACE_T            # total thickness (42)
IN_X = FW / 2 - WALL               # inside half-width of the tray
IN_Y = FH / 2 - WALL

# =============================================================================
# FIELD
# =============================================================================
BORDER = 5.0               # sideline border around the field
EZ_IN = 109.0              # goal line (x): just past the 7.9" screen body, so both fronts get full LED windows
EZ_OUT = FW / 2 - BORDER   # back of the end zone
EZ_HALF_H = FH / 2 - BORDER
EZ_DEPTH = 2.0             # end zone insert pocket depth (= insert thickness)
EZ_LEDGE = 3.0             # ledge around the LED window that the insert rests on
EZ_FIT = 0.2               # insert clearance per side
EZ_TEXT_D = 0.6            # flush two-color letters: how deep they sink into the insert face
# Snap clips: 4 flexing arms on the back of each insert hook under short walls behind the field.
# Push in to click; pry at the notch to pop out. Strain stays ~1.3% so they survive many swaps (PETG best).
SNAP = dict(RIM_DEPTH=12.0,   # walls reach this far behind the field face
            RIM_T=2.0,        # wall thickness
            ARM_T=1.0, ARM_W=12.0, ARM_Y=40.0,  # arm thickness, width, and +/- position along the end zone
            ROOT=1.2,         # gusset where the arm meets the insert (where a clip would crack)
            HOOK=0.9, HOOK_H=0.7, LEAD=2.0,     # hook reach, catch height, lead-in ramp length
            GAP=0.25)         # arm to wall clearance
# Screen cradle: one frame that screws on behind the screen and holds it evenly against the field.
CRADLE = dict(T=2.0,          # thickness
              LIP=7.0)        # how far it covers the screen's back edge (keep clear of the screen's connectors)
LINE_W, LINE_D = 1.0, 0.6  # yard line groove width and depth
NUM_H = 7.0                # yard number height

# =============================================================================
# SCREENS  (outer w x h x t, active area aw x ah, active-area offset ax/ay from center)
# =============================================================================
SCREENS = {
    # UNVERIFIED: from the Amazon listing. Measure thickness at the driver board and the bezel widths.
    # MEASURED (Oct 20): "7inch LCD Display-C". Mounts by its 4 ears, screwed to posts on the back of the field.
    "standard7": dict(label='7in 1024x600 (Hosyond, LCD Display-C)', mount="ears",
                      w=164.9, h=100.0,        # glass: height measured 99.5-100; width from the listing
                      t=7.0,                   # glass front to the board's front face (measured ~7)
                      pcb_h=107.0, pcb_t=1.6,  # board height (measured ~107, the 4 mm lip), thickness
                      back_parts=4.5,          # tallest parts on the back of the board
                      ear_holes=(156.9, 115.0),  # hole centers. up/down: 112 inner edges + 3 hole. across: UNVERIFIED
                      ear_hole_d=3.0, overall_h=124.3,
                      ports_end=1,             # HDMI + micro-USB on one short end: +1 = right (near the Pi), -1 = left
                      port_reach=25.0,         # how far the plugs stick out past that end
                      aw=154.21, ah=85.92, ax=0.0, ay=0.0,
                      # TEST FIT (Oct 22): with the screen centered, the lit area showed 3 mm black at the bottom and
                      # 1 mm at the right (clipped top/left). Shift the whole screen (its posts) so the lit area is centered.
                      mount_shift=(1.5, -3.5)),   # (right, up) in mm, facing the front. 2nd fit: +0.5 right, +0.5 down
    # UNVERIFIED: from a retailer listing (211 x 73 x 20, active 191 x 60.4).
    "wide79": dict(label='7.9in 1280x400 (Waveshare)', w=211.0, h=73.0, t=20.0, aw=191.0, ah=60.4, ax=0.0, ay=0.0),
}
GUIDE_LEG, GUIDE_T = 10.0, 2.0     # screen corner L-guides
M3_PILOT = 2.5             # M3 self-tapping screws straight into plastic (swap to heat-set inserts later)
M3_CLEAR = 3.4             # M3 passes freely
M3_HEAD = 6.4              # pan head counterbore
EAR_POST = dict(D=7.0, PILOT=M3_PILOT, SHORT=0.2)  # posts for screens with mounting ears (M3 screws);
                                               # SHORT: posts stop just shy so the screws pull the glass snug
TAB_X = 20.0                       # screen clamp tabs sit at x = +/-TAB_X above and below the screen
TAB_OVERLAP = 4.0                  # how far a tab reaches over the screen edge
TAB_BOSS = 4.5                     # boss center distance outside the screen edge
TAB = (16.0, TAB_OVERLAP + TAB_BOSS + 4.0, 3.0)   # clamp tab (x, y, thickness)

# =============================================================================
# PARTS IN THE BACK TRAY (all UNVERIFIED until measured)
# =============================================================================
# Orange Pi Zero 2W: 65 x 30 board, M2.5 holes 58 x 23 apart, 3.5 mm in from the edges.
PI = dict(L=65.0, W=30.0, T=1.6, HOLES=(58.0, 23.0), PEDESTAL=5.0, TOP=7.0,  # TOP = tallest part/plug above board
          PEG_D=2.4, PEG_H=1.4)   # its holes are ~2.75 mm (M2.5): printed pegs locate it, kept below the board top
# Two swivel clamps hold the Pi down (M3 x 8 each). They sit at the two corners with nothing next to them:
# GPIO/ribbon-connector corner (+x,+y) and HDMI corner (-x,-y); the microSD and antenna-plug corners stay clear.
PI_CLAMP = dict(CORNERS=((1, 1), (-1, -1)), POST_D=7.0, OFFSET=4.5, TIP_IN=2.2, W=6.0, T=3.0, PRELOAD=0.3)
# Rocker switch: KCD11 2-pin snap-in (measured hole 14 x 9). Body behind the panel, 2 terminals.
SWITCH = dict(CUT_W=14.0, CUT_H=9.0,       # panel hole (long side runs along the wall)
              BODY_W=13.6, BODY_H=8.6, BODY_D=11.0, TERM_D=7.0, TERM_GAP=8.0,
              PANEL_T=1.8)                # snap-in clips catch on a wall this thick
# USB-C power jack on a small breakout board: board, connector opening in the wall.
JACK = dict(BOARD_L=20.0, BOARD_W=14.0, BOARD_T=1.6, PORT_W=8.94, PORT_H=3.26, WIRE_GAP=6.0)  # 20 x 14 board (listing); connector centered at the wall edge
JACK_STYLE = "panel"       # "panel" = 2-wire snap-in USB-C socket (in use); "board" = USB-C breakout in a pocket
JACK_PANEL_CUT = (14.5, 6.4)   # measured: rounded-end hole for the 2-wire 5 V USB-C socket
JACK_PANEL = dict(BODY_W=13.0, BODY_H=6.0, BODY_D=14.0, PANEL_T=1.8)   # body behind the wall (estimate) + wall thickness its clips catch
# Wi-Fi antenna (flat stick in heat-shrink): 63 long, 5 wide, 3 thick, ~40 mm of cable to the Orange Pi.
ANT = dict(L=63.0, D=5.0, CABLE=40.0, CLIP_LEN=6.0, CLIP_WALL=1.8, FIT=0.2, MOUTH=4.0)  # round, 5 mm at its thick ends; clips grip the thick ends
# Wi-Fi antenna (round stick in heat-shrink): 63 long, 5 mm thick at the ends, ~40 mm of cable. Snaps down into two C-clips.

# where things go (x, y = center); controls are all on the RIGHT edge
POS = dict(
    pi=(68.0, 12.0),
    switch_y=-31.0,            # switch and USB-C side by side, low on the right wall (short wires, nothing crossed)
    jack_y=-50.0,
    keyhole=(100.0, 50.0),     # 200 mm apart
    antenna=(60.5, 40.0),       # center; lies along x above the Orange Pi, either end can face the Pi's antenna plug
    antenna_loops=(37.0, 84.0), # x of the two clips, over the antenna's thick ends
    post=(FW / 2 - 8.0, FH / 2 - 8.0),
)
JACK_Z = FLOOR + 3.0           # jack board bottom height (seat)
SWITCH_ZC = FLOOR + 1.5 + SWITCH["BODY_H"] / 2   # switch center height

# kickstand (print-in-place, folds flush into the back)
KS = dict(W=46.0, HINGE_Y=40.0, FOOT_Y=-68.0, TAIL=10.0, KNUCKLE_D=9.0, PIN_D=4.0, PIN_GAP=0.30,
          KNUCKLE_W=29.2, GAP=0.5, END_GAP=0.45, PIN_RELIEF=1.2, STOP_REACH=3.5,
          CATCH=True, PULL_W=26.0, PULL_H=14.0, PULL_FROM_FOOT=18.0, CATCH_LEN=30.0, CATCH_T=1.2, CATCH_SLOT=1.5, CATCH_RIDGE=1.4, CATCH_CLR=0.4, OPEN_DEG=32.0)   # PIN_GAP/END_GAP: print-in-place clearances
# keyhole for wall hanging: screw head and shank sizes
KEY = dict(HEAD_D=8.5, SHANK_W=4.2, SLIDE=10.0, CAVITY_H=4.0)
LABEL_H, LABEL_RAISE = 3.2, 0.4
SCREW_POST_D = 9.0
SCREW_LEN = 20.0           # longest M3 in the kit: the field's corner posts reach down to meet it
SCREW_BITE = 8.0           # how much thread grips the post
Z_JOIN = 2.6 + SCREW_LEN - SCREW_BITE - 0.6   # where the tray post ends and the field's post begins (~14)

# =============================================================================
# helpers
# =============================================================================
class Font:
    path = None
    name = "Arial"


def box(x0, y0, z0, x1, y1, z1):
    return cq.Solid.makeBox(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0),
                            cq.Vector(min(x0, x1), min(y0, y1), min(z0, z1)))


def cbox(cx, cy, z0, sx, sy, h):
    return box(cx - sx / 2, cy - sy / 2, z0, cx + sx / 2, cy + sy / 2, z0 + h)


def cyl(x, y, z, d, h):
    return cq.Solid.makeCylinder(d / 2, h, cq.Vector(x, y, z))


def xcyl(x0, x1, y, z, d):
    return cq.Solid.makeCylinder(d / 2, x1 - x0, cq.Vector(x0, y, z), cq.Vector(1, 0, 0))


def rounded_plate(w, h, r, z0, t):
    return cq.Workplane("XY").workplane(offset=z0).rect(w, h).extrude(t).edges("|Z").fillet(r).val()


def text_solid(txt, size, height, x=0.0, y=0.0, z=0.0, angle=0.0):
    kw = dict(halign="center", valign="center", kind="bold")
    if Font.path:
        kw["fontPath"] = Font.path
    else:
        kw["font"] = Font.name
    t = cq.Workplane("XY").text(txt, size, height, **kw).val()
    if angle:
        t = t.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), angle)
    return t.translate(cq.Vector(x, y, z))


def fuse(a, *more):
    for m in more:
        a = a.fuse(m)
    return a


# A registry of floor footprints so the layout can be checked for overlaps.
class Layout:
    def __init__(self):
        self.items = []  # (name, kind, x0, y0, x1, y1)

    def add(self, name, kind, x0, y0, x1, y1):
        self.items.append((name, kind, min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)))

    def overlaps(self):
        bad = []
        for i, a in enumerate(self.items):
            for b in self.items[i + 1:]:
                if a[1] == b[1] and a[1] in ("kickstand", "pi"):
                    continue  # pieces of one mechanism, designed to touch
                if a[2] < b[4] and b[2] < a[4] and a[3] < b[5] and b[3] < a[5]:
                    bad.append((a[0], b[0]))
        return bad

    def inside(self):
        return [a[0] for a in self.items if a[2] < -IN_X or a[4] > IN_X or a[3] < -IN_Y or a[5] > IN_Y]


def label(lay, tray, txt, x, y, angle=0.0):
    size = LABEL_H
    w = 0.66 * size * len(txt) + 1.0
    h = size + 1.0
    if angle in (90, -90):
        lay.add("label " + txt, "label", x - h / 2, y - w / 2, x + h / 2, y + w / 2)
    else:
        lay.add("label " + txt, "label", x - w / 2, y - h / 2, x + w / 2, y + h / 2)
    return tray.fuse(text_solid(txt, size, LABEL_RAISE, x, y, FLOOR, angle))


# =============================================================================
# BACK TRAY
# =============================================================================
def corner_guides(cx, cy, L, W, h, z0, leg=6.0, t=1.6, corners=((-1, -1), (-1, 1), (1, -1), (1, 1))):
    """L-shaped corner pieces around an L x W part (clearance included)."""
    hx, hy = L / 2 + CLR, W / 2 + CLR
    out = None
    for sx, sy in corners:
        if True:
            x, y = cx + sx * hx, cy + sy * hy
            a = cbox(x + sx * t / 2 - sx * leg / 2 + sx * t / 2, y + sy * t / 2, z0, leg, t, h)
            b = cbox(x + sx * t / 2, y + sy * t / 2 - sy * leg / 2 + sy * t / 2, z0, t, leg, h)
            g = a.fuse(b)
            out = g if out is None else out.fuse(g)
    return out


def pi_clamp_posts():
    cx, cy = POS["pi"]
    pc = PI_CLAMP
    return [(cx + sx * (PI["L"] / 2 + pc["OFFSET"]), cy + sy * (PI["W"] / 2 + pc["OFFSET"])) for sx, sy in pc["CORNERS"]]


def make_pi_clamp():
    """Swivel clamp: screw through the round end into the post, the other end presses on the board's corner pad.
    Loosen the screw and swing it aside to lift the Pi out."""
    pc = PI_CLAMP
    reach = (pc["OFFSET"] + pc["TIP_IN"]) * math.sqrt(2)
    c = (cq.Workplane("XY").center(reach / 2, 0).slot2D(reach + pc["W"], pc["W"], 0).extrude(pc["T"])
         .faces(">Z").workplane().center(-reach / 2, 0).hole(M3_CLEAR)).val()
    return c


# hinge test clearances: (name, gap around the pin, gap at the knuckle ends) in mm
HINGE_TESTS = (("loose", 0.60, 0.80), ("medium", 0.45, 0.60), ("tight", 0.30, 0.45))


def make_cutter(kind, length=12.0):
    """A solid the shape of a wall hole, centered on the origin, long axis = Z. Used as a negative part in the slicer."""
    if kind == "usb":
        w, h = JACK_PANEL_CUT
        return cq.Workplane("XY").slot2D(w, h, 0).extrude(length).val()
    return cbox(0, 0, 0, SWITCH["CUT_W"], SWITCH["CUT_H"], length)


def hinge_test(pin_gap, end_gap, name):
    """The kickstand hinge area of the tray at a given clearance, with the clearance name raised on the base."""
    saved = dict(KS)
    KS["PIN_GAP"], KS["END_GAP"] = pin_gap, end_gap
    try:
        t, _ = make_tray(include_leg=True)
    finally:
        KS.clear(); KS.update(saved)
    piece = t.intersect(box(-32, 22, -1, 32, 58, 30))
    tag = text_solid(f"{name.upper()} {pin_gap:.2f}", 3.2, 0.6, 0, 26.5, FLOOR - 0.01)
    return piece.fuse(tag.intersect(box(-23, 23, 0, 23, 30, FLOOR + 1)))


def make_tray(include_leg=True, controls=True):
    """controls=False: no switch or USB-C holes/pockets (cut your own with the cutter STLs)."""
    lay = Layout()
    tray = rounded_plate(FW, FH, CORNER_R, 0, Z_FACE)
    tray = tray.cut(rounded_plate(FW - 2 * WALL, FH - 2 * WALL, max(CORNER_R - WALL, 0.5), FLOOR, Z_FACE))

    # --- corner screw posts (front screws on from behind) ---------------------
    px, py = POS["post"]
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * px, sy * py
            tray = tray.fuse(cyl(x, y, 0, SCREW_POST_D, Z_JOIN - 0.2))
            tray = tray.cut(cyl(x, y, -1, M3_CLEAR, Z_FACE))
            tray = tray.cut(cyl(x, y, -0.01, M3_HEAD, 2.6))       # counterbore for the screw head
            lay.add(f"screw post {x:+.0f},{y:+.0f}", "post", x - 5.5, y - 5.5, x + 5.5, y + 5.5)

    # --- Orange Pi: pedestal posts at its holes + corner guides -----------------
    cx, cy = POS["pi"]
    zb = FLOOR + PI["PEDESTAL"]
    for dx in (-PI["HOLES"][0] / 2, PI["HOLES"][0] / 2):
        for dy in (-PI["HOLES"][1] / 2, PI["HOLES"][1] / 2):
            tray = tray.fuse(cyl(cx + dx, cy + dy, FLOOR, 5.5, PI["PEDESTAL"]))
            tray = tray.fuse(cyl(cx + dx, cy + dy, FLOOR + PI["PEDESTAL"] - 0.01, PI["PEG_D"], PI["PEG_H"]))
    free = tuple(c for c in ((-1, -1), (-1, 1), (1, -1), (1, 1)) if c not in PI_CLAMP["CORNERS"])
    tray = tray.fuse(corner_guides(cx, cy, PI["L"], PI["W"], PI["PEDESTAL"] + PI["T"] + 1.5, FLOOR, corners=free))
    pc = PI_CLAMP
    for (px_, py_), (sx, sy) in zip(pi_clamp_posts(), pc["CORNERS"]):   # clamp posts, a hair below the board top
        h = PI["PEDESTAL"] + PI["T"] - pc["PRELOAD"]
        tray = tray.fuse(cyl(px_, py_, FLOOR - 0.01, pc["POST_D"], h + 0.01)).cut(cyl(px_, py_, FLOOR + 0.6, M3_PILOT, h))
        lay.add(f"PI clamp post {sx:+d},{sy:+d}", "pi", px_ - pc["POST_D"] / 2, py_ - pc["POST_D"] / 2, px_ + pc["POST_D"] / 2, py_ + pc["POST_D"] / 2)
    lay.add("ORANGE PI holder", "pi", cx - PI["L"] / 2 - 2, cy - PI["W"] / 2 - 2, cx + PI["L"] / 2 + 2, cy + PI["W"] / 2 + 2)
    tray = label(lay, tray, "ORANGE PI", cx, cy + PI["W"] / 2 + 5.5)
    tray = label(lay, tray, "PORTS THIS EDGE", cx, cy - PI["W"] / 2 - 6.0)   # plugs face the open space below


    if controls:
        # --- rocker switch pocket in the right wall --------------------------------
        sy = POS["switch_y"]
        s = SWITCH
        xw = IN_X                                   # inner face of the right wall
        zc = SWITCH_ZC
        tray = tray.cut(box(xw - 1, sy - s["CUT_W"] / 2, zc - s["CUT_H"] / 2, FW / 2 + 1, sy + s["CUT_W"] / 2, zc + s["CUT_H"] / 2))
        # thin the wall around the cut-out so the snap-in clips catch
        thin = WALL - s["PANEL_T"]
        tray = tray.cut(box(xw - 0.01, sy - s["CUT_W"] / 2 - 2, zc - s["CUT_H"] / 2 - 2, xw + thin, sy + s["CUT_W"] / 2 + 2, zc + s["CUT_H"] / 2 + 2))
        wy = s["BODY_W"] / 2 + CLR
        depth = s["BODY_D"] + s["TERM_D"]
        for side in (-1, 1):   # side walls
            tray = tray.fuse(box(xw - depth, sy + side * wy, FLOOR, xw, sy + side * (wy + 2.0), zc + s["BODY_H"] / 2))
        tray = tray.fuse(box(xw - s["BODY_D"], sy - wy, FLOOR, xw, sy + wy, zc - s["BODY_H"] / 2 - CLR))   # seat
        # no back stops: the switch's own snap clips hold it, and the pins need the room (test fit)
        lay.add("ON/OFF pocket", "holder", xw - depth, sy - wy - 2, xw, sy + wy + 2)
        tray = label(lay, tray, "ON/OFF", xw - depth - 9.0, sy, angle=90)

        # --- USB-C power input in the right wall -----------------------------------
        jy = POS["jack_y"]
        j = JACK
        port_zc = JACK_Z + j["BOARD_T"] + j["PORT_H"] / 2
        if JACK_STYLE == "panel":
            # 2-wire snap-in USB-C socket: rounded-end hole, wall thinned around it so the clips catch
            cw, ch = JACK_PANEL_CUT
            jp = JACK_PANEL
            tray = tray.cut(cq.Workplane("YZ").workplane(offset=xw - 1).center(jy, port_zc)
                            .slot2D(cw, ch, 0).extrude(WALL + 2).val())
            thin = WALL - jp["PANEL_T"]
            tray = tray.cut(box(xw - 0.01, jy - cw / 2 - 2, port_zc - ch / 2 - 2, xw + thin, jy + cw / 2 + 2, port_zc + ch / 2 + 2))
            lay.add("USB-C socket", "holder", xw - jp["BODY_D"], jy - cw / 2 - 2, xw, jy + cw / 2 + 2)
            # label in line with the ON/OFF label, so it clears the switch pocket right above it
            tray = label(lay, tray, "USB-C PWR", xw - SWITCH["BODY_D"] - SWITCH["TERM_D"] - 9.0, jy, angle=90)
        else:
            tray = tray.cut(cq.Workplane("YZ").workplane(offset=xw - 1).center(jy, port_zc)
                            .slot2D(j["PORT_W"] + 0.6, j["PORT_H"] + 0.6, 0).extrude(WALL + 2).val())
            wy = j["BOARD_W"] / 2 + CLR
            for side in (-1, 1):
                tray = tray.fuse(box(xw - j["BOARD_L"] - 1, jy + side * wy, FLOOR, xw, jy + side * (wy + 2.0), port_zc + 3.0))
            tray = tray.fuse(box(xw - j["BOARD_L"], jy - wy, FLOOR, xw, jy + wy, JACK_Z))                   # seat
            bx = xw - j["BOARD_L"] - CLR
            for side in (-1, 1):   # back stop with a wire gap in the middle
                tray = tray.fuse(box(bx - 2.0, jy + side * j["WIRE_GAP"] / 2, FLOOR, bx, jy + side * (wy + 2.0), port_zc + 3.0))
            lay.add("USB-C pocket", "holder", xw - j["BOARD_L"] - 3, jy - wy - 2, xw, jy + wy + 2)
            tray = label(lay, tray, "USB-C POWER", xw - j["BOARD_L"] - 9.0, jy, angle=90)


    # --- Wi-Fi antenna: two C-clips it presses down into, away from the Pi and the screen's metal ---
    ax, ay = POS["antenna"]
    a = ANT
    r = a["D"] / 2 + a["FIT"]
    zc = FLOOR + r                               # antenna rests on the floor
    top = zc + math.sqrt(max(r * r - (a["MOUTH"] / 2) ** 2, 0.0))   # clip top: leaves a MOUTH-wide opening
    ow = 2 * (r + a["CLIP_WALL"])
    for lx in POS["antenna_loops"]:
        clip = box(lx - a["CLIP_LEN"] / 2, ay - ow / 2, FLOOR - 0.01, lx + a["CLIP_LEN"] / 2, ay + ow / 2, top)
        clip = clip.cut(xcyl(lx - a["CLIP_LEN"], lx + a["CLIP_LEN"], ay, zc, 2 * r))
        tray = tray.fuse(clip)
    lay.add("ANTENNA spot", "holder", ax - a["L"] / 2, ay - ow / 2, ax + a["L"] / 2, ay + ow / 2)
    tray = label(lay, tray, "ANTENNA", ax - 6.0, ay + ow / 2 + 4.5)

    # --- keyholes for wall hanging ---------------------------------------------
    kx, ky = POS["keyhole"]
    k = KEY
    for sx in (-1, 1):
        x = sx * kx
        slot = (cq.Workplane("XY").workplane(offset=-1).center(x, ky).circle(k["HEAD_D"] / 2).extrude(FLOOR + 2)
                .union(cq.Workplane("XY").workplane(offset=-1).center(x, ky + k["SLIDE"] / 2)
                       .slot2D(k["SLIDE"] + k["SHANK_W"], k["SHANK_W"], 90).extrude(FLOOR + 2))).val()
        cav = (cq.Workplane("XY").workplane(offset=FLOOR).center(x, ky + k["SLIDE"] / 2)
               .slot2D(k["SLIDE"] + k["HEAD_D"] + 1.0, k["HEAD_D"] + 1.0, 90).extrude(k["CAVITY_H"])).val()
        house = (cq.Workplane("XY").workplane(offset=FLOOR).center(x, ky + k["SLIDE"] / 2)
                 .slot2D(k["SLIDE"] + k["HEAD_D"] + 5.0, k["HEAD_D"] + 5.0, 90).extrude(k["CAVITY_H"] + 2.0)).val()
        tray = tray.fuse(house).cut(cav).cut(slot)
        hw = (k["HEAD_D"] + 5.0) / 2
        lay.add(f"keyhole {x:+.0f}", "keyhole", x - hw, ky - hw, x + hw, ky + k["SLIDE"] + hw)

    # --- vents (top and bottom walls, in the electronics layer) ------------------
    for yw in (FH / 2, -FH / 2):
        for i in range(9):
            x = -48 + i * 12
            tray = tray.cut(cbox(x, yw, FLOOR + 3.0, 2.5, WALL * 3, ELEC_H - 6.0))

    tray = make_kickstand(tray, lay, include_leg)
    return tray.clean(), lay


def make_kickstand(tray, lay, include_leg=True):
    """Print-in-place leg in a cut-out in the back. Hinge pin belongs to the tray, the leg pivots on it.
    A bridge inside stops it at OPEN_DEG; a small bar over the foot stops it folding inward."""
    k = KS
    hw = k["W"] / 2
    kw = k["KNUCKLE_W"] / 2
    yh, zh = k["HINGE_Y"], k["KNUCKLE_D"] / 2
    g = k["GAP"]
    y_tail = yh + k["TAIL"]
    # cut-out in the floor: wide leg below the hinge, narrow (knuckle width) at the hinge and tail
    cut = box(-hw - g, k["FOOT_Y"] - g, -1, hw + g, yh - k["KNUCKLE_D"] / 2 - 1.0 + g, FLOOR + 0.01)   # +g: gap at the leg's top corners too
    # tail slot: long enough for the tail's bottom corner as it swings (radius from the hinge axis)
    cut = cut.fuse(box(-kw - g, yh - k["KNUCKLE_D"] / 2 - 1.5, -1, kw + g, yh + math.hypot(k["TAIL"], zh) + g, FLOOR + 0.01))
    # beside the knuckles: room for the leg's top corners to swing down through the floor (knuckles are added after)
    for sx in (-1, 1):
        cut = cut.fuse(box(sx * (kw + g), yh - k["KNUCKLE_D"] / 2 - 1.5, -1, sx * (hw + g), yh - 2.5, FLOOR + 0.01))
    tray = tray.cut(cut)
    # tray knuckles + the pin (the pin is part of the tray)
    for sx in (-1, 1):
        x0, x1 = (kw + k["END_GAP"], hw + 4.0) if sx > 0 else (-hw - 4.0, -kw - k["END_GAP"])
        tray = tray.fuse(xcyl(x0, x1, yh, zh, k["KNUCKLE_D"]))
    tray = tray.fuse(xcyl(-hw - 4.0, hw + 4.0, yh, zh, k["PIN_D"]))
    # the leg
    leg = box(-hw, k["FOOT_Y"], 0, hw, yh - k["KNUCKLE_D"] / 2 - 1.0, FLOOR)
    leg = leg.fuse(box(-kw, yh - k["KNUCKLE_D"] / 2 - 1.5, 0, kw, y_tail, FLOOR))
    leg = leg.fuse(xcyl(-kw, kw, yh, zh, k["KNUCKLE_D"]))
    leg = leg.cut(xcyl(-kw - 1, kw + 1, yh, zh, k["PIN_D"] + 2 * k["PIN_GAP"]))
    # relief under the pin: the pin's underside droops a little as it prints, so give it room to fall without fusing
    leg = leg.cut(box(-kw - 1, yh - k["PIN_D"] * 0.35, zh - k["PIN_D"] / 2 - k["PIN_GAP"] - k["PIN_RELIEF"], kw + 1, yh + k["PIN_D"] * 0.35, zh))
    leg = leg.cut(cbox(0, k["FOOT_Y"] + 6, -0.01, 30, 8, 0.8))     # recess for a rubber foot strip
    if k["CATCH"]:
        leg = leg.cut(catch_parts(k)[2])
        leg = leg.cut(box(-8, k["FOOT_Y"] - 0.1, -0.01, 8, k["FOOT_Y"] + 3.5, 1.2))   # fingernail notch to pry it open
        fy0 = k["FOOT_Y"] + k["PULL_FROM_FOOT"]                                          # finger hole to pull it open
        leg = leg.cut(cq.Workplane("XY").workplane(offset=-1).center(0, fy0).slot2D(k["PULL_W"], k["PULL_H"], 0)
                      .extrude(FLOOR + 2).val())
    if include_leg:
        tray = tray.fuse(leg)
    # open stop: the tail rises into this bridge at OPEN_DEG
    r = math.hypot(k["TAIL"], zh - FLOOR)
    a0 = -math.degrees(math.atan2(zh - FLOOR, k["TAIL"]))
    z_stop = zh + r * math.sin(math.radians(k["OPEN_DEG"] + a0))
    # two hooks, one each side: they lean in over the tail's outer edges with a 45-degree underside,
    # so they print without supports or bridging. The tail's corners hit the slope at OPEN_DEG.
    x_in = kw + g + 0.6                 # hook's inner face (clear of the tail sideways)
    x_out = kw + g + 6.0
    reach = k["STOP_REACH"]             # how far each hook leans in over the tail
    x_tip = kw - reach
    z0 = z_stop - (x_in - kw)           # 45 deg: the slope passes through the tail corner (x = kw) at z_stop
    z_top = z0 + (x_in - x_tip) + 2.0
    for sx in (-1, 1):
        pts = [(x_in, FLOOR - 0.01), (x_out, FLOOR - 0.01), (x_out, z_top), (x_tip, z_top), (x_tip, z0 + (x_in - x_tip)), (x_in, z0)]
        prof = cq.Workplane("XZ").polyline([(sx * x, z) for x, z in pts]).close().extrude(6.0).val()
        bb = prof.BoundingBox()
        tray = tray.fuse(prof.translate(cq.Vector(0, (y_tail - 4.0) - bb.ymin, 0)))
    # fold stop over the foot
    fy = k["FOOT_Y"] + 2.0
    tray = tray.fuse(box(-hw - g - 5.0, fy - 2.0, FLOOR + 0.6, hw + g + 5.0, fy + 2.0, FLOOR + 2.4))
    for sx in (-1, 1):
        tray = tray.fuse(box(sx * (hw + g + 0.5), fy - 2.0, FLOOR - 0.01, sx * (hw + g + 5.0), fy + 2.0, FLOOR + 2.4))
    if k["CATCH"]:                            # click-shut catch at the foot end
        ridge, slot, _ = catch_parts(k)
        tray = tray.cut(slot).fuse(ridge)
    lay.add("kickstand leg + cut-out", "kickstand", -hw - g, k["FOOT_Y"] - g, hw + g, yh - k["KNUCKLE_D"] / 2 - 1.0)
    lay.add("kickstand hinge", "kickstand", -hw - 4.0, yh - k["KNUCKLE_D"] / 2 - 1.5, hw + 4.0, yh + k["KNUCKLE_D"] / 2)
    lay.add("kickstand stop", "kickstand", -kw - g - 6.0, yh + k["KNUCKLE_D"] / 2 + 0.01, kw + g + 6.0, y_tail + 2.0)
    lay.add("kickstand fold stop", "kickstand", -hw - g - 5.0, fy - 2.0, hw + g + 5.0, fy + 2.0)
    return tray


def catch_parts(k):
    """Click-shut catch at the foot: a flexible strip of floor across the foot end with a ridge on it, and a matching
    groove in the leg's end. Returns (ridge to add to the tray, relief slot to cut from the tray, groove to cut from the leg)."""
    hl = k["CATCH_LEN"] / 2
    y0 = k["FOOT_Y"] - k["GAP"]                 # face of the strip (floor edge at the foot end)
    yl = k["FOOT_Y"]                            # leg end face
    r, c = k["CATCH_RIDGE"], k["CATCH_CLR"]
    def prism(pts, length):
        w = cq.Workplane("YZ").polyline(pts).close().extrude(length).val()
        return w.translate(cq.Vector(-length / 2, 0, 0))
    ridge = prism([(y0 - 0.3, 0.6), (y0, 0.6), (y0 + r, 1.5), (y0, 2.4), (y0 - 0.3, 2.4)], 2 * hl - 6.0)
    groove = prism([(yl - 0.01, 0.3), (y0 + r + c + 0.1, 1.5), (yl - 0.01, 2.7)], 2 * hl - 4.0)
    slot = box(-hl, y0 - k["CATCH_T"] - k["CATCH_SLOT"], -1, hl, y0 - k["CATCH_T"], FLOOR + 0.01)
    return ridge, slot, groove


def kickstand_leg_only():
    """The leg alone (for previews of the open position)."""
    k = KS
    hw, kw = k["W"] / 2, k["KNUCKLE_W"] / 2
    yh, zh = k["HINGE_Y"], k["KNUCKLE_D"] / 2
    leg = box(-hw, k["FOOT_Y"], 0, hw, yh - k["KNUCKLE_D"] / 2 - 1.0, FLOOR)
    leg = leg.fuse(box(-kw, yh - k["KNUCKLE_D"] / 2 - 1.5, 0, kw, yh + k["TAIL"], FLOOR))
    leg = leg.fuse(xcyl(-kw, kw, yh, zh, k["KNUCKLE_D"]))
    return leg.cut(xcyl(-kw - 1, kw + 1, yh, zh, k["PIN_D"] + 2 * k["PIN_GAP"]))


# =============================================================================
# FRONT (the field), one per screen
# =============================================================================
def yard_x(yd):
    return -EZ_IN + (2 * EZ_IN) * yd / 100.0


def field_marks(scr):
    """Groove volumes for the yard lines, sideline and numbers (cut into the face, or printed as an inlay)."""
    z0 = DEPTH - LINE_D
    marks = []
    # sideline / end line boundary
    ring = rounded_plate(FW - 2 * 3.0, FH - 2 * 3.0, 2.0, z0, LINE_D + 1).cut(
        rounded_plate(FW - 2 * 3.0 - 2 * LINE_W, FH - 2 * 3.0 - 2 * LINE_W, 1.0, z0 - 1, LINE_D + 3))
    marks.append(ring)
    # yard lines every 5 yards, between the sidelines
    for yd in range(5, 100, 5):
        x = yard_x(yd)
        marks.append(cbox(x, 0, z0, LINE_W if yd % 10 == 0 else LINE_W * 0.7, 2 * EZ_HALF_H, LINE_D + 1))
    # numbers
    yn = EZ_HALF_H - NUM_H / 2 - 4.0
    for yd in range(10, 100, 10):
        n = str(yd if yd <= 50 else 100 - yd)
        x = yard_x(yd)
        marks.append(text_solid(n, NUM_H, LINE_D + 1, x, -yn, z0))
        marks.append(text_solid(n, NUM_H, LINE_D + 1, x, yn, z0, angle=180))
    return marks


def opening_rect(scr):
    return (scr["ax"], scr["ay"], scr["aw"] + 0.6, scr["ah"] + 0.6)


def ez_window_x0(scr):
    """LED window starts past the screen body if the screen reaches under the end zone."""
    x0 = EZ_IN + EZ_LEDGE
    if scr["w"] / 2 + CLR + GUIDE_T > EZ_IN:
        x0 = max(x0, scr["w"] / 2 + CLR + GUIDE_T + 0.6)
    return x0


def make_front(scr):
    face = rounded_plate(FW, FH, CORNER_R, Z_FACE, FACE_T)
    # locating lip that drops inside the tray walls
    lip_o = (FW - 2 * WALL - 2 * FIT, FH - 2 * WALL - 2 * FIT)
    lip = rounded_plate(lip_o[0], lip_o[1], 1.5, Z_FACE - 3.0, 3.0).cut(
        rounded_plate(lip_o[0] - 4.0, lip_o[1] - 4.0, 1.0, Z_FACE - 4.0, 5.0))
    front = face.fuse(lip)
    # bosses for the 4 screws from the back
    px, py = POS["post"]
    for sx in (-1, 1):
        for sy in (-1, 1):
            front = front.fuse(cyl(sx * px, sy * py, Z_JOIN, 8.0, Z_FACE - Z_JOIN))
            front = front.cut(cyl(sx * px, sy * py, Z_JOIN - 1, M3_PILOT, SCREW_BITE + 2.5))
    # screen mounting
    w, h, t = scr["w"] + 2 * CLR, scr["h"] + 2 * CLR, scr["t"]
    if t > SCREEN_ZONE:
        raise SystemExit(f"{scr['label']} is {t} mm thick; SCREEN_ZONE is {SCREEN_ZONE}.")
    zb = Z_FACE - t
    if scr.get("mount") == "ears":
        # posts under the screen's 4 ears; screws go through the ears from behind
        ex, ey = scr["ear_holes"]
        hpost = t - EAR_POST["SHORT"]
        for sx in (-1, 1):
            for sy in (-1, 1):
                mx, my = scr.get("mount_shift", (0.0, 0.0))
                front = front.fuse(cyl(mx + sx * ex / 2, my + sy * ey / 2, Z_FACE - hpost, EAR_POST["D"], hpost))
                front = front.cut(cyl(mx + sx * ex / 2, my + sy * ey / 2, Z_FACE - hpost - 1, EAR_POST["PILOT"], hpost + 0.5))
        sx_list = []
    else:
        sx_list = (-1, 1)
    for sx in sx_list:
        for sy in (-1, 1):
            x, y = sx * w / 2, sy * h / 2
            front = front.fuse(box(x, y, zb, x - sx * GUIDE_LEG, y + sy * GUIDE_T, Z_FACE))
            front = front.fuse(box(x, y + sy * GUIDE_T, zb, x + sx * GUIDE_T, y - sy * GUIDE_LEG, Z_FACE))
    by = h / 2 + TAB_BOSS
    for sx in sx_list:
        for sy in (-1, 1):
            front = front.fuse(cyl(sx * TAB_X, sy * by, zb, 7.0, t)).cut(cyl(sx * TAB_X, sy * by, zb - 1, 2.5, 8.0))
    # the screen opening
    ox, oy, ow, oh = opening_rect(scr)
    front = front.cut(cq.Workplane("XY").workplane(offset=Z_FACE - 30).center(ox, oy).rect(ow, oh)
                      .extrude(40).edges("|Z").fillet(1.0).val())
    # end zone pockets + LED windows + pry notches
    wx0 = ez_window_x0(scr)
    for sx in (-1, 1):
        front = front.cut(box(sx * EZ_IN, -EZ_HALF_H, DEPTH - EZ_DEPTH, sx * EZ_OUT, EZ_HALF_H, DEPTH + 1))
        front = front.cut(box(sx * wx0, -(EZ_HALF_H - EZ_LEDGE), Z_FACE - 5, sx * (EZ_OUT - EZ_LEDGE), EZ_HALF_H - EZ_LEDGE, DEPTH + 1))
        front = front.cut(cyl(sx * EZ_OUT, 0, DEPTH - EZ_DEPTH, 8.0, EZ_DEPTH + 1))
        # short walls along the window's long edges: the insert's clips hook under their far edge
        hy = SNAP["ARM_Y"] + SNAP["ARM_W"] / 2 + 6.0      # only as long as the clips need (clears the screw posts)
        for xe, d in ((wx0, -1), (EZ_OUT - EZ_LEDGE, 1)):
            front = front.fuse(box(sx * xe, -hy, DEPTH - SNAP["RIM_DEPTH"], sx * (xe + d * SNAP["RIM_T"]), hy, Z_FACE + 0.01))
    # yard lines and numbers: grooves where there is still field face
    marks = field_marks(scr)
    keep = box(-EZ_IN + 0.01, -FH, DEPTH - LINE_D - 0.01, EZ_IN - 0.01, FH, DEPTH + 2)  # not inside the end zones
    inlay = None
    for m in marks:
        front = front.cut(m)
    # inlay = what was removed, limited to the face
    face_only = rounded_plate(FW, FH, CORNER_R, DEPTH - LINE_D, LINE_D)
    face_only = face_only.cut(cq.Workplane("XY").workplane(offset=Z_FACE).center(ox, oy).rect(ow, oh).extrude(10).val())
    for sx in (-1, 1):
        face_only = face_only.cut(box(sx * EZ_IN, -EZ_HALF_H, DEPTH - EZ_DEPTH, sx * EZ_OUT, EZ_HALF_H, DEPTH + 1))
        face_only = face_only.cut(cyl(sx * EZ_OUT, 0, DEPTH - EZ_DEPTH, 8.0, EZ_DEPTH + 1))
    for m in marks:
        piece = m.intersect(face_only)
        inlay = piece if inlay is None else inlay.fuse(piece)
    return front.clean(), inlay.clean()


def tab_center_offset():
    """Tab center measured from the screen edge (positive = outward)."""
    return -TAB_OVERLAP + TAB[1] / 2


def make_tab():
    """Clamp tab: inner edge reaches TAB_OVERLAP over the screen, the hole sits on the boss."""
    t = cbox(0, 0, 0, TAB[0], TAB[1], TAB[2])
    hole_y = TAB_BOSS - tab_center_offset()
    return t.cut(cyl(0, hole_y, -1, 3.4, TAB[2] + 2)).clean()


def ez_window_half():
    return ((EZ_OUT - EZ_LEDGE) - (EZ_IN + EZ_LEDGE)) / 2


def make_endzone(txt, side):
    """End zone insert as installed: face at z = EZ_DEPTH, back at z = 0, clips reaching down (-z).
    Returns (body, letters). Letters are a flush inlay for a second color (None if no text)."""
    w = EZ_OUT - EZ_IN - 2 * EZ_FIT
    h = 2 * EZ_HALF_H - 2 * EZ_FIT
    s = SNAP
    plate = cbox(0, 0, 0, w, h, EZ_DEPTH)
    body = plate
    half = ez_window_half()
    drop = s["RIM_DEPTH"] - EZ_DEPTH           # insert back to the wall's far edge
    zc = -(drop + 0.15)                        # top of the hook's catch
    ztip = zc - s["HOOK_H"] - 0.3 - s["LEAD"]
    for sx in (-1, 1):
        xo = sx * (half - s["GAP"])            # arm outer face
        xi = sx * (half - s["GAP"] - s["ARM_T"])
        for sy in (-1, 1):
            y0 = sy * s["ARM_Y"]
            body = body.fuse(box(xi, y0 - s["ARM_W"] / 2, ztip, xo, y0 + s["ARM_W"] / 2, 0.01))
            gp = cq.Plane(origin=(0, y0 + s["ARM_W"] / 2, 0), xDir=(1, 0, 0), normal=(0, -1, 0))
            body = body.fuse(cq.Workplane(gp).polyline([(xi, 0.01), (xi - sx * s["ROOT"], 0.01), (xi, -s["ROOT"])]).close()
                             .extrude(s["ARM_W"]).val())
            pl = cq.Plane(origin=(0, y0 + s["ARM_W"] / 2, 0), xDir=(1, 0, 0), normal=(0, -1, 0))
            hook = (cq.Workplane(pl).polyline([(xo, zc), (xo + sx * s["HOOK"], zc - s["HOOK_H"]),
                                               (xo + sx * s["HOOK"], zc - s["HOOK_H"] - 0.3), (xo, ztip),
                                               (xo - sx * 0.3, ztip), (xo - sx * 0.3, zc)]).close()
                    .extrude(s["ARM_W"]).val())
            body = body.fuse(hook)
    letters = None
    if txt:
        size = max(5.0, min(w - 7.0, (h - 12.0) / (0.68 * len(txt))))
        t = text_solid(txt, size, EZ_TEXT_D + 1, 0, 0, EZ_DEPTH - EZ_TEXT_D, angle=90 if side == "left" else -90)
        letters = t.intersect(plate).clean()
        body = body.cut(t)
    return body.clean(), letters


def make_cradle(scr):
    """Back frame that screws to the 4 bosses and holds the screen against the field (as printed, flat)."""
    w, h = scr["w"] + 2 * CLR, scr["h"] + 2 * CLR
    ox, oy = w / 2 + GUIDE_T, h / 2 + TAB_BOSS + 4.0
    lip = CRADLE["LIP"]
    ring = cq.Workplane("XY").rect(2 * ox, 2 * oy).extrude(CRADLE["T"]).edges("|Z").fillet(2.0).val()
    ring = ring.cut(cq.Workplane("XY").workplane(offset=-1).rect(w - 2 * lip, h - 2 * lip).extrude(CRADLE["T"] + 2)
                    .edges("|Z").fillet(2.0).val())
    by = h / 2 + TAB_BOSS
    for sx in (-1, 1):
        for sy in (-1, 1):
            ring = ring.cut(cyl(sx * TAB_X, sy * by, -1, 3.4, CRADLE["T"] + 2))
    for (x0, y0, x1, y1) in scr.get("cradle_notches", []):   # gaps for connectors that sit on the edge
        ring = ring.cut(box(x0, y0, -1, x1, y1, CRADLE["T"] + 2))
    return ring.clean()


# =============================================================================
# checks
# =============================================================================
def part_envelopes():
    """Rough solids for the real parts (with plugs), to check nothing in the model hits them."""
    env = {}
    cx, cy = POS["pi"]
    zb = FLOOR + PI["PEDESTAL"]
    pi = cbox(cx, cy, zb, PI["L"], PI["W"], PI["T"] + PI["TOP"])
    for dx in (-PI["HOLES"][0] / 2, PI["HOLES"][0] / 2):
        for dy in (-PI["HOLES"][1] / 2, PI["HOLES"][1] / 2):
            pi = pi.cut(cyl(cx + dx, cy + dy, zb - 1, 2.75, PI["T"] + 2))   # its mounting holes
    env["Orange Pi + plugs"] = pi
    s = SWITCH
    sy0 = POS["switch_y"]
    env["switch body"] = box(IN_X - s["BODY_D"], sy0 - s["BODY_W"] / 2, SWITCH_ZC - s["BODY_H"] / 2,
                             IN_X, sy0 + s["BODY_W"] / 2, SWITCH_ZC + s["BODY_H"] / 2).fuse(
        box(IN_X - s["BODY_D"] - s["TERM_D"], sy0 - s["TERM_GAP"] / 2 + 1.0, SWITCH_ZC - 4.0,
            IN_X - s["BODY_D"], sy0 + s["TERM_GAP"] / 2 - 1.0, SWITCH_ZC + 4.0))
    j = JACK
    if JACK_STYLE == "panel":
        jp, zc = JACK_PANEL, JACK_Z + j["BOARD_T"] + j["PORT_H"] / 2
        env["USB-C socket"] = cbox(IN_X - jp["BODY_D"] / 2, POS["jack_y"], zc - jp["BODY_H"] / 2, jp["BODY_D"], jp["BODY_W"], jp["BODY_H"])
    else:
        env["USB-C jack"] = box(IN_X - j["BOARD_L"], POS["jack_y"] - j["BOARD_W"] / 2, JACK_Z, IN_X, POS["jack_y"] + j["BOARD_W"] / 2,
                                JACK_Z + j["BOARD_T"] + j["PORT_H"])
    ax, ay = POS["antenna"]
    env["antenna"] = xcyl(ax - ANT["L"] / 2, ax + ANT["L"] / 2, ay, FLOOR + ANT["D"] / 2 + ANT["FIT"], ANT["D"] - 0.2)
    return env


def screen_body(scr):
    """Envelope of the real screen as mounted: glass, board, ears, parts on the back, and plugs."""
    if scr.get("mount") != "ears":
        return cbox(0, 0, Z_FACE - scr["t"], scr["w"], scr["h"], scr["t"])
    t, pt = scr["t"], scr["pcb_t"]
    zp = Z_FACE - t - pt
    body = cbox(0, 0, Z_FACE - t, scr["w"], scr["h"], t)                         # glass + LCD
    body = body.fuse(cbox(0, 0, zp, scr["w"], scr["pcb_h"], pt))                 # board
    ex, ey = scr["ear_holes"]
    ear_h = (scr["overall_h"] - scr["pcb_h"]) / 2
    for sx in (-1, 1):
        for sy in (-1, 1):
            ear = cbox(sx * ex / 2, sy * (scr["pcb_h"] / 2 + ear_h / 2), zp, 9.0, ear_h, pt)
            body = body.fuse(ear.cut(cyl(sx * ex / 2, sy * ey / 2, zp - 1, scr["ear_hole_d"], pt + 2)))
    body = body.fuse(cbox(0, 0, zp - scr["back_parts"], scr["w"] - 6, scr["pcb_h"] - 6, scr["back_parts"]))
    e = scr["ports_end"]
    x0 = e * scr["w"] / 2
    body = body.fuse(box(x0, -scr["pcb_h"] / 2 + 4, zp - 7.0, x0 + e * scr["port_reach"], scr["pcb_h"] / 2 - 4, zp + pt))
    mx, my = scr.get("mount_shift", (0.0, 0.0))
    return body.translate(cq.Vector(mx, my, 0))


def run_checks(tray, lay, fronts):
    ok = True
    print("\n== layout check (floor footprints) ==")
    bad = lay.overlaps()
    for a, b in bad:
        print("  OVERLAP:", a, "<->", b)
    for n in lay.inside():
        print("  OUTSIDE THE TRAY:", n)
    ok &= not bad and not lay.inside()
    print("  %d items, %s" % (len(lay.items), "no overlaps" if not bad else f"{len(bad)} overlaps"))

    print("== wall cut-outs go all the way through ==")
    for name, (y, z) in {"switch": (POS["switch_y"], SWITCH_ZC),
                         "USB-C": (POS["jack_y"], JACK_Z + JACK["BOARD_T"] + JACK["PORT_H"] / 2)}.items():
        probe = cbox(FW / 2 - WALL / 2, y, z - 0.5, WALL + 0.2, 1.0, 1.0)
        left = tray.intersect(probe).Volume()
        print(f"  {name:7s}: {'open' if left < 1e-6 else 'BLOCKED (%.2f mm3)' % left}")
        ok &= left < 1e-6

    print("== parts vs model ==")
    env = part_envelopes()
    for key, (front, _) in fronts.items():
        scr = SCREENS[key]
        screen = screen_body(scr)
        ears = scr.get("mount") == "ears"
        tabs = None
        edge = (scr["h"] + 2 * CLR) / 2
        for sx in (-1, 1):
            for sy in (-1, 1):
                tb = cbox(sx * TAB_X, sy * (edge + tab_center_offset()), Z_FACE - scr["t"] - TAB[2], TAB[0], TAB[1], TAB[2])
                tabs = tb if tabs is None else tabs.fuse(tb)
        cradle = make_cradle(scr).translate(cq.Vector(0, 0, Z_FACE - scr["t"] - CRADLE["T"]))
        ez, _ = make_endzone("", "left")
        inserts = None
        for sx in (-1, 1):
            e = ez.translate(cq.Vector(sx * (EZ_IN + EZ_OUT) / 2, 0, DEPTH - EZ_DEPTH))
            inserts = e if inserts is None else inserts.fuse(e)
        checks = [("front vs tray", front, tray), ("screen + plugs vs tray", screen, tray), ("screen + plugs vs front", screen, front),
                  ("end zone inserts vs front", inserts, front), ("end zone inserts vs tray", inserts, tray),
                  ("end zone inserts vs screen", inserts, screen)]
        if not ears:
            checks += [("clamp tabs vs tray", tabs, tray), ("cradle vs tray", cradle, tray), ("cradle vs front", cradle, front)]
        for pname, p in env.items():
            checks += [(f"{pname} vs front", p, front), (f"{pname} vs screen", p, screen)]
            if not ears:
                checks += [(f"{pname} vs clamp tabs", p, tabs), (f"{pname} vs cradle", p, cradle)]
        print(f"  [{key}]")
        for name, a, b in checks:
            v = a.intersect(b).Volume()
            flag = "ok" if v < 0.5 else "HIT %.1f mm3" % v
            if v >= 0.5:
                ok = False
            print(f"    {name:32s} {flag}")
    for pname, p in env.items():
        v = p.intersect(tray).Volume()
        print(f"  {pname:20s} vs tray: {'ok' if v < 0.5 else 'HIT %.1f mm3' % v}")
        ok &= v < 0.5
    print("== RESULT:", "ALL CLEAR" if ok else "PROBLEMS FOUND", "==\n")
    return ok


# =============================================================================
def export(shape, path, step=True):
    wp = cq.Workplane().add(shape)
    cq.exporters.export(wp, path + ".stl", tolerance=0.03, angularTolerance=0.15)
    if step:
        cq.exporters.export(wp, path + ".step")


def main():
    ap = argparse.ArgumentParser(description="Football field scoreboard frame")
    ap.add_argument("--left", default="JAGUARS", help="left end zone text (reads bottom to top)")
    ap.add_argument("--right", default="JACKSONVILLE", help="right end zone text (reads top to bottom)")
    ap.add_argument("--screen", default="all", choices=["all"] + list(SCREENS))
    ap.add_argument("--font-path", default="")
    ap.add_argument("--out", default="stl")
    ap.add_argument("--no-step", action="store_true")
    ap.add_argument("--check", action="store_true", help="only run the overlap / cut-out checks")
    a = ap.parse_args()
    Font.path = a.font_path or next((p for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                                                 "C:/Windows/Fonts/arialbd.ttf", "/Library/Fonts/Arial Bold.ttf")
                                     if os.path.exists(p)), None)
    step = not a.no_step
    tray, lay = make_tray()
    keys = list(SCREENS) if a.screen == "all" else [a.screen]
    fronts = {k: make_front(SCREENS[k]) for k in keys}
    ok = run_checks(tray, lay, fronts)
    if a.check:
        raise SystemExit(0 if ok else 1)
    os.makedirs(a.out, exist_ok=True)
    export(tray, os.path.join(a.out, "back_tray"), step)
    # same back with looser hinges, for printers where the tight one fuses
    for name, pin_gap, end_gap in HINGE_TESTS:
        if name == "tight":
            continue
        saved = dict(KS); KS["PIN_GAP"], KS["END_GAP"] = pin_gap, end_gap
        try:
            alt, _ = make_tray()
        finally:
            KS.clear(); KS.update(saved)
        export(alt, os.path.join(a.out, f"back_tray_{name}"), step)
    # blank back: no switch / USB-C holes, so you can put them anywhere with the cutters below
    blank, _ = make_tray(controls=False)
    export(blank, os.path.join(a.out, "back_tray_blank"), step)
    # cutters: add as a "negative part" in the slicer, scale to your part, and place it through any wall
    export(make_cutter("usb"), os.path.join(a.out, "cutter_usb_c_socket"), step)
    export(make_cutter("switch"), os.path.join(a.out, "cutter_switch"), step)
    # print-in-place hinge tests at three clearances (small pieces cut from the tray)
    for name, pin_gap, end_gap in HINGE_TESTS:
        export(hinge_test(pin_gap, end_gap, name), os.path.join(a.out, "tests", f"hinge_test_{name}"), False)
    for k, (front, inlay) in fronts.items():
        # export face-down, ready to print (the field face sits on the bed)
        flip = lambda sh: sh.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), 180).translate(cq.Vector(0, 0, DEPTH))
        export(flip(front), os.path.join(a.out, f"front_{k}"), step)
        export(flip(inlay), os.path.join(a.out, f"front_{k}_lines"), step)
    export(make_tab(), os.path.join(a.out, "screen_tab"), step)
    export(make_pi_clamp(), os.path.join(a.out, "pi_clamp"), step)
    for k in fronts:
        if SCREENS[k].get("mount") != "ears":   # screens with mounting ears screw straight to the field
            export(make_cradle(SCREENS[k]), os.path.join(a.out, f"screen_cradle_{k}"), step)
    # end zones print face down too, so the face is smooth and the letters are flush
    ezflip = lambda sh: sh.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), 180).translate(cq.Vector(0, 0, EZ_DEPTH))
    ez_parts = []
    for name, txt, side in (("endzone_left", a.left, "left"), ("endzone_right", a.right, "right"), ("endzone_blank", "", "left")):
        body, letters = make_endzone(txt, side)
        export(ezflip(body), os.path.join(a.out, name), step)
        if letters is not None:
            export(ezflip(letters), os.path.join(a.out, name + "_letters"), step)
            ez_parts.append(name)
    try:
        import make_3mf
        for k in fronts:
            make_3mf.write_3mf(os.path.join(a.out, f"front_{k}_2color.3mf"),
                               [("field", os.path.join(a.out, f"front_{k}.stl")),
                                ("lines (white)", os.path.join(a.out, f"front_{k}_lines.stl"))], f"front_{k}")
        for name in ez_parts:
            make_3mf.write_3mf(os.path.join(a.out, f"{name}_2color.3mf"),
                               [("end zone", os.path.join(a.out, f"{name}.stl")),
                                ("letters", os.path.join(a.out, f"{name}_letters.stl"))], name)
    except ImportError:
        print("(trimesh not installed: skipped the 2-color .3mf files; pip install trimesh)")
    print("written to", a.out)


if __name__ == "__main__":
    main()
