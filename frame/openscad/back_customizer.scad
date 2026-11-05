// =============================================================================
// Football field scoreboard - BACK TRAY customizer
// The back that holds the electronics, hangs on the wall (keyholes) or stands on
// a desk (print-in-place kickstand that clicks shut). Prints flat back down, no
// supports. The frame size is fixed (280 x 150 mm) so every front fits.
// Defaults = the tested build: Orange Pi Zero 2W, KCD11 switch, 2-wire USB-C.
// =============================================================================

/* [Board] */
// Single-board computer
board = "opi_zero2w"; // [opi_zero2w:Orange Pi Zero 2W (tested), rpi_zero2w:Raspberry Pi Zero 2 W (same size as the Orange Pi), custom:Custom board]
// How the board is held
board_hold = "pegs_clamps"; // [pegs_clamps:Pegs + 2 swivel clamps (M3 x 8 screws), screws:Screw posts at its 4 holes]
// Custom board: length (long side, mm)
custom_board_length = 65.0;
// Custom board: width (mm)
custom_board_width = 30.0;
// Custom board: mounting holes, center to center along the length (mm)
custom_hole_spacing_length = 58.0;
// Custom board: mounting holes, center to center along the width (mm)
custom_hole_spacing_width = 23.0;
// Custom board: mounting hole diameter (mm)
custom_hole_diameter = 2.75;
// Custom board: tallest part or plug above the board (mm, must fit under the screen)
custom_tallest_part = 7.0;
// Screw posts: pilot hole for self-tapping screws (2.1 = M2.5, 2.5 = M3)
screw_pilot = 2.1;
// Text printed beside the board (empty = automatic)
board_label = "";
// Board center, left/right (mm from the middle of the back; tested: 68)
board_center_x = 68.0;
// Board center, up/down (mm from the middle of the back; tested: 12)
board_center_y = 12.0;
// Turn the board: which way its ports (HDMI/USB) face
board_rotation = 0; // [0:Ports face down (tested), 90:Ports face right, 180:Ports face up, 270:Ports face left]

/* [Power and switch] */
// Power input hole
power = "usbc_snap"; // [usbc_snap:USB-C snap-in socket 14.5 x 6.4 (tested), usbc_board:USB-C breakout board 20 x 14 (pocket), custom:Custom hole, none:No power hole]
// On/off switch hole
switch_type = "kcd11"; // [kcd11:KCD11 rocker 14 x 9 (tested), custom:Custom hole, none:No switch hole]
// Wall for the power input and switch
controls_wall = "right"; // [right:Right (tested), left:Left, top:Top, bottom:Bottom (not for desk use: the stand sits on this edge)]
// Middle of the pair along the wall (mm from the wall's center; right/left walls: + = up, top/bottom: + = right, seen from the front)
controls_position = -40.5;
// Distance between the switch and the power input, center to center (mm)
controls_spacing = 19.0;
// Which one is first along the wall (higher, or further right)
switch_first = true;
// Custom power hole: shape
custom_power_shape = "rounded"; // [rect:Rectangle, rounded:Rounded slot, circle:Circle]
// Custom power hole: width or diameter (mm)
custom_power_w = 14.5;
// Custom power hole: height (mm, rectangle and slot)
custom_power_h = 6.4;
// Custom switch hole: shape
custom_switch_shape = "rect"; // [rect:Rectangle, rounded:Rounded slot, circle:Circle]
// Custom switch hole: width or diameter (mm)
custom_switch_w = 14.0;
// Custom switch hole: height (mm, rectangle and slot)
custom_switch_h = 9.0;
// Custom holes: center height above the inside floor (mm)
custom_hole_height = 6.0;
// Thin the wall around custom holes so snap-in parts can clip in
thin_wall_for_snap_in = true;

/* [Kickstand and hanging] */
// Fold-out desk stand (turn off for wall-only: solid back)
kickstand = true;
// Print-in-place hinge clearance (loosen it if the hinge fuses on your printer)
hinge = "tight"; // [tight:Tight 0.30 mm (tested), medium:Medium 0.45 mm, loose:Loose 0.60 mm]
// Click-shut catch at the foot + finger hole to pull it open
kickstand_catch = true;
// Keyholes for hanging on the wall
keyholes = true;

/* [Extras] */
// Clips for the Wi-Fi antenna
antenna_clips = true;
// Raised labels beside each part's spot (turn off if it takes too long to generate)
part_labels = true;
// What to make
part = "back"; // [back:Back tray, clamp:Pi swivel clamp (print 2)]

/* [Hidden] */
$fn = 24;   // 24 segments: round parts stay within ~0.02 mm (hinge clearance is 0.30), and it renders much faster
FW = 280; FH = 150; CORNER_R = 4; WALL = 2.4; FLOOR = 3; ELEC_H = 16; SCREEN_ZONE = 20;
CLR = 0.3;
Z_FACE = FLOOR + ELEC_H + SCREEN_ZONE;      // 39: top of the walls
IN_X = FW / 2 - WALL; IN_Y = FH / 2 - WALL;
M3_PILOT = 2.5; M3_CLEAR = 3.4; M3_HEAD = 6.4;
SCREW_POST_D = 9; Z_JOIN = 2.6 + 20 - 8 - 0.6;
LABEL_H = 3.2; LABEL_RAISE = 0.4; LABEL_FONT = "Liberation Sans:style=Bold";

// board
BOARD = board == "custom"
    ? [custom_board_length, custom_board_width, custom_hole_spacing_length, custom_hole_spacing_width, custom_hole_diameter, custom_tallest_part]
    : [65.0, 30.0, 58.0, 23.0, 2.75, 7.0];
B_L = BOARD[0]; B_W = BOARD[1]; H_L = BOARD[2]; H_W = BOARD[3]; H_D = BOARD[4]; B_TOP = BOARD[5];
B_T = 1.6; PEDESTAL = 5.0; PEG_D = min(2.4, H_D - 0.35); PEG_H = 1.4;
BOARD_POS = [board_center_x, board_center_y];
CLAMP = [7.0, 4.5, 2.2, 6.0, 3.0, 0.3];     // post d, offset, tip in, width, thickness, preload
CLAMP_CORNERS = [[1, 1], [-1, -1]];
LABEL_TEXT = board_label != "" ? board_label : board == "opi_zero2w" ? "ORANGE PI" : board == "rpi_zero2w" ? "PI ZERO 2 W" : "BOARD";
// antenna, keyholes
ANT = [63.0, 5.0, 6.0, 1.8, 0.2, 4.0]; ANT_POS = [60.5, 40.0]; ANT_CLIPS = [37.0, 84.0];
KEY = [8.5, 4.2, 10.0, 4.0]; KEY_POS = [100.0, 50.0];
POST_POS = [FW / 2 - 8, FH / 2 - 8];
// switch / power presets
SW_BODY = [13.6, 8.6, 11.0, 7.0]; SW_PANEL_T = 1.8; SW_ZC = FLOOR + 1.5 + SW_BODY[1] / 2;
JACK = [20.0, 14.0, 1.6, 8.94, 3.26, 6.0]; JACK_Z = FLOOR + 3.0; JACK_ZC = JACK_Z + JACK[2] + JACK[4] / 2;
USB_PANEL_T = 1.8; USB_BODY_D = 14.0;
// kickstand
PIN_GAP = hinge == "loose" ? 0.60 : hinge == "medium" ? 0.45 : 0.30;
END_GAP = hinge == "loose" ? 0.80 : hinge == "medium" ? 0.60 : 0.45;
KS_W = 46; HINGE_Y = 40; FOOT_Y = -68; TAIL = 10; KNUCKLE_D = 9; PIN_D = 4; KNUCKLE_W = 29.2; KS_GAP = 0.5;
PIN_RELIEF = 1.2; STOP_REACH = 3.5; OPEN_DEG = 32;
PULL = [26, 14, 18]; CATCH_LEN = 30; CATCH_T = 1.2; CATCH_SLOT = 1.5; CATCH_RIDGE = 1.4; CATCH_CLR = 0.4;

// ---- checks: a clear message instead of a broken part ----
assert(H_L < B_L && H_W < B_W, "Hole spacing must be smaller than the board.");
assert(PEDESTAL + B_T + B_TOP <= ELEC_H + 2, "The board's tallest part would hit the screen. Max about 11 mm above the board.");
// footprint of the board with its clamps/guides and labels, and the things it must not touch: [[x0, y0], [x1, y1]]
B_REACH = board_hold == "pegs_clamps" ? 8.0 : 2.5;
function rot2(p, a) = [cos(a) * p[0] - sin(a) * p[1], sin(a) * p[0] + cos(a) * p[1]];
BOARD_CORNERS = [for (x = [-B_L / 2 - B_REACH, B_L / 2 + B_REACH]) for (y = [-B_W / 2 - 9, B_W / 2 + 8]) rot2([x, y], board_rotation) + BOARD_POS];
BOARD_RECT = [[min([for (p = BOARD_CORNERS) p[0]]), min([for (p = BOARD_CORNERS) p[1]])], [max([for (p = BOARD_CORNERS) p[0]]), max([for (p = BOARD_CORNERS) p[1]])]];
function hits(a, b) = a[0][0] < b[1][0] && b[0][0] < a[1][0] && a[0][1] < b[1][1] && b[0][1] < a[1][1];
KS_ZONES = [[[-24, -71], [24, 35]], [[-27.5, 35], [27.5, 52]], [[-29, -71], [29, -63]]];   // leg, hinge + stops, fold stop
assert(!kickstand || len([for (z = KS_ZONES) if (hits(BOARD_RECT, z)) 1]) == 0, "The board overlaps the kickstand. Move it right (board_center_x), turn it, or use a smaller board.");
assert(!antenna_clips || !hits(BOARD_RECT, [[28, 35.6], [93, 51]]), "The board overlaps the antenna clips. Move it down, or turn off antenna_clips.");
assert(!keyholes || !hits(BOARD_RECT, [[93, 43], [107, 67]]), "The board overlaps the right keyhole. Move it down, or turn off keyholes.");
assert(BOARD_RECT[0][1] > -IN_Y && BOARD_RECT[1][1] < IN_Y && BOARD_RECT[1][0] < IN_X && BOARD_RECT[0][0] > -IN_X, "The board doesn't fit inside the back there.");

// ---- helpers ----
module box(p0, p1) { translate(p0) cube([p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]]); }
module cbox(c, s, z0, h) { translate([c[0] - s[0] / 2, c[1] - s[1] / 2, z0]) cube([s[0], s[1], h]); }
module cyl(c, z, d, h) { translate([c[0], c[1], z]) cylinder(d = d, h = h); }
module xcyl(x0, x1, y, z, d) { translate([x0, y, z]) rotate([0, 90, 0]) cylinder(d = d, h = x1 - x0); }
module slot2d(len, wid) { hull() for (s = [-1, 1]) translate([s * (len - wid) / 2, 0]) circle(d = wid); }
module rounded_plate(w, h, r, z0, t) { translate([0, 0, z0]) linear_extrude(t) offset(r) square([w - 2 * r, h - 2 * r], center = true); }
module label(txt, c, ang = 0) {
    if (part_labels)
    translate([c[0], c[1], FLOOR - 0.01]) linear_extrude(LABEL_RAISE + 0.01)
        rotate(ang) text(txt, size = LABEL_H, font = LABEL_FONT, halign = "center", valign = "center", $fn = 6);   // small text: few curve segments renders much faster
}
module corner_guides(c, L, W, h, z0, leg = 6, t = 1.6, corners = [[-1, -1], [-1, 1], [1, -1], [1, 1]]) {
    hx = L / 2 + CLR; hy = W / 2 + CLR;
    for (k = corners) {
        sx = k[0]; sy = k[1]; x = c[0] + sx * hx; y = c[1] + sy * hy;
        cbox([x + sx * t / 2 - sx * leg / 2 + sx * t / 2, y + sy * t / 2], [leg, t], z0, h);
        cbox([x + sx * t / 2, y + sy * t / 2 - sy * leg / 2 + sy * t / 2], [t, leg], z0, h);
    }
}
function clamp_posts() = [for (k = CLAMP_CORNERS) [k[0] * (B_L / 2 + CLAMP[1]), k[1] * (B_W / 2 + CLAMP[1])]];   // in the board's own frame
function free_corners() = [for (k = [[-1, -1], [-1, 1], [1, -1], [1, 1]]) if (len([for (c = CLAMP_CORNERS) if (c == k) 1]) == 0) k];

// ---- wall holes: built against a right-hand wall (inner face at local x = 0, outward = +x), then placed ----
function wall_rot() = controls_wall == "right" ? 0 : controls_wall == "top" ? 90 : controls_wall == "left" ? 180 : 270;
function wall_off() = controls_wall == "right" || controls_wall == "left" ? IN_X : IN_Y;
// local "along the wall" so that + means up (left/right walls) or right (top/bottom walls), seen from the front
function along(u) = controls_wall == "top" || controls_wall == "left" ? -u : u;
module on_wall() { rotate(wall_rot()) translate([wall_off(), 0, 0]) children(); }
SW_U = controls_position + (switch_first ? 1 : -1) * controls_spacing / 2;
PW_U = controls_position - (switch_first ? 1 : -1) * controls_spacing / 2;

// ---- checks for the holes: each hole (with its pocket) and its label must stay clear of everything else ----
LBL_X = -(SW_BODY[2] + SW_BODY[3] + 9);                          // the labels' line, in from the wall
function lbl_half(t) = (0.75 * LABEL_H * len(t) + 1) / 2;
function hole_local(u, half, depth) = [[-depth, along(u) - half], [WALL + 0.1, along(u) + half]];
function lbl_local(u, half) = [[LBL_X - 2.6, along(u) - half], [LBL_X + 2.6, along(u) + half]];
function rot_pt(p) = let(a = wall_rot(), x = p[0] + wall_off(), y = p[1]) [cos(a) * x - sin(a) * y, sin(a) * x + cos(a) * y];
function to_world(r) = let(a = rot_pt(r[0]), b = rot_pt(r[1])) [[min(a[0], b[0]), min(a[1], b[1])], [max(a[0], b[0]), max(a[1], b[1])]];
SW_HOLE = switch_type == "kcd11" ? [SW_BODY[0] / 2 + CLR + 2, SW_BODY[2] + SW_BODY[3]] : [custom_switch_w / 2 + (thin_wall_for_snap_in ? 2 : 0.5), 12];
PW_HOLE = power == "usbc_board" ? [JACK[1] / 2 + CLR + 2, JACK[0] + 3] : power == "usbc_snap" ? [14.5 / 2 + 2, USB_BODY_D]
        : [custom_power_w / 2 + (thin_wall_for_snap_in ? 2 : 0.5), 12];
PW_TEXT = "POWER";
CTL = concat(
    switch_type != "none" ? [["switch", to_world(hole_local(SW_U, SW_HOLE[0], SW_HOLE[1])), to_world(lbl_local(SW_U, lbl_half("ON/OFF")))]] : [],
    power != "none" ? [["power input", to_world(hole_local(PW_U, PW_HOLE[0], PW_HOLE[1])), to_world(lbl_local(PW_U, lbl_half(PW_TEXT)))]] : []);
OTHER_ZONES = concat(
    kickstand ? [for (z = KS_ZONES) ["kickstand", z]] : [],
    [["board", BOARD_RECT]],
    [for (sx = [-1, 1]) for (sy = [-1, 1]) ["corner screw post", [[sx * (FW / 2 - 8) - 6, sy * (FH / 2 - 8) - 6], [sx * (FW / 2 - 8) + 6, sy * (FH / 2 - 8) + 6]]]],
    keyholes ? [["keyhole", [[93, 43], [107, 67]]], ["keyhole", [[-107, 43], [-93, 67]]]] : [],
    antenna_clips ? [["antenna clips", [[28, 35.6], [93, 51]]]] : []);
CTL_FAILS = [for (c = CTL) for (z = OTHER_ZONES) for (k = [1, 2]) if (hits(c[k], z[1]))
    str("The ", c[0], (k == 1 ? " hole" : " label"), " runs into the ", z[0], ". Change controls_position (or controls_wall).")];
assert(len(CTL_FAILS) == 0, len(CTL_FAILS) > 0 ? CTL_FAILS[0] : "");
assert(len(CTL) < 2 || (!hits(CTL[0][1], CTL[1][1]) && !hits(CTL[0][2], CTL[1][2])), "The switch and power holes are too close. Increase controls_spacing.");
assert(abs(controls_position) + controls_spacing / 2 + 10 < (controls_wall == "right" || controls_wall == "left" ? IN_Y : IN_X),
       "The holes run past the end of the wall. Move controls_position toward the middle.");

module hole2d(shape, w, h) {
    if (shape == "circle") circle(d = w);
    else if (shape == "rounded") slot2d(w, h);
    else square([w, h], center = true);
}
// through-hole in the wall at along-position u, center height zc
module wall_hole(u, zc, shape, w, h) {
    translate([-1, along(u), zc]) rotate([0, 90, 0]) rotate([0, 0, 90]) linear_extrude(WALL + 2) hole2d(shape, w, h);
}
module wall_thin(u, zc, w, h, panel_t) {
    translate([-0.01, along(u) - w / 2 - 2, zc - h / 2 - 2]) cube([WALL - panel_t + 0.01, w + 4, h + 4]);
}
module controls_cuts() {
    on_wall() {
        if (switch_type == "kcd11") { wall_hole(SW_U, SW_ZC, "rect", 14, 9); wall_thin(SW_U, SW_ZC, 14, 9, SW_PANEL_T); }
        if (switch_type == "custom") {
            wall_hole(SW_U, FLOOR + custom_hole_height, custom_switch_shape, custom_switch_w, custom_switch_h);
            if (thin_wall_for_snap_in) wall_thin(SW_U, FLOOR + custom_hole_height, custom_switch_w,
                                                 custom_switch_shape == "circle" ? custom_switch_w : custom_switch_h, 1.8);
        }
        if (power == "usbc_snap") { wall_hole(PW_U, JACK_ZC, "rounded", 14.5, 6.4); wall_thin(PW_U, JACK_ZC, 14.5, 6.4, USB_PANEL_T); }
        if (power == "usbc_board") wall_hole(PW_U, JACK_ZC, "rounded", JACK[3] + 0.6, JACK[4] + 0.6);
        if (power == "custom") {
            wall_hole(PW_U, FLOOR + custom_hole_height, custom_power_shape, custom_power_w, custom_power_h);
            if (thin_wall_for_snap_in) wall_thin(PW_U, FLOOR + custom_hole_height, custom_power_w,
                                                 custom_power_shape == "circle" ? custom_power_w : custom_power_h, 1.8);
        }
    }
}
module controls_solids() {
    on_wall() {
        if (switch_type == "kcd11") {
            y = along(SW_U); wy = SW_BODY[0] / 2 + CLR; depth = SW_BODY[2] + SW_BODY[3];
            // (pocket pieces reach 0.5 mm into the wall so they fuse solidly with it)
            for (s = [-1, 1]) box([-depth, y + s * wy - (s < 0 ? 2 : 0), FLOOR], [0.5, y + s * wy + (s > 0 ? 2 : 0), SW_ZC + SW_BODY[1] / 2]);
            box([-SW_BODY[2], y - wy, FLOOR], [0.5, y + wy, SW_ZC - SW_BODY[1] / 2 - CLR]);   // seat
        }
        if (power == "usbc_board") {
            y = along(PW_U); wy = JACK[1] / 2 + CLR;
            for (s = [-1, 1]) box([-JACK[0] - 1, min(y + s * wy, y + s * (wy + 2)), FLOOR], [0.5, max(y + s * wy, y + s * (wy + 2)), JACK_ZC + 3]);
            box([-JACK[0], y - wy, FLOOR], [0.5, y + wy, JACK_Z]);                              // seat
            bx = -JACK[0] - CLR;
            for (s = [-1, 1]) box([bx - 2, min(y + s * JACK[5] / 2, y + s * (wy + 2)), FLOOR], [bx, max(y + s * JACK[5] / 2, y + s * (wy + 2)), JACK_ZC + 3]);
        }
    }
}
module controls_labels() {
    lx = -(SW_BODY[2] + SW_BODY[3] + 9);         // in line with each other, inside the pockets
    if (switch_type != "none") placed_label("ON/OFF", lx, along(SW_U));
    if (power != "none") placed_label(PW_TEXT, lx, along(PW_U));
}
module placed_label(txt, lx, ly) {
    a = wall_rot();
    p = [cos(a) * (wall_off() + lx) - sin(a) * ly, sin(a) * (wall_off() + lx) + cos(a) * ly];
    label(txt, p, controls_wall == "right" || controls_wall == "left" ? 90 : 0);   // always readable from the front
}

// ---- kickstand (print in place) ----
HW = KS_W / 2; KW = KNUCKLE_W / 2; ZH = KNUCKLE_D / 2; Y_TAIL = HINGE_Y + TAIL;
module ks_floor_cut() {
    box([-HW - KS_GAP, FOOT_Y - KS_GAP, -1], [HW + KS_GAP, HINGE_Y - ZH - 1 + KS_GAP, FLOOR + 0.01]);
    box([-KW - KS_GAP, HINGE_Y - ZH - 1.5, -1], [KW + KS_GAP, HINGE_Y + sqrt(TAIL * TAIL + ZH * ZH) + KS_GAP, FLOOR + 0.01]);
    for (s = [-1, 1]) box([min(s * (KW + KS_GAP), s * (HW + KS_GAP)), HINGE_Y - ZH - 1.5, -1],
                          [max(s * (KW + KS_GAP), s * (HW + KS_GAP)), HINGE_Y - 2.5, FLOOR + 0.01]);
    if (kickstand_catch) box([-CATCH_LEN / 2, FOOT_Y - KS_GAP - CATCH_T - CATCH_SLOT, -1], [CATCH_LEN / 2, FOOT_Y - KS_GAP - CATCH_T, FLOOR + 0.01]);
}
module prism_yz(pts, length) { translate([-length / 2, 0, 0]) rotate([90, 0, 90]) linear_extrude(length) polygon(pts); }
module catch_ridge() {
    y0 = FOOT_Y - KS_GAP;
    prism_yz([[y0 - 0.3, 0.6], [y0, 0.6], [y0 + CATCH_RIDGE, 1.5], [y0, 2.4], [y0 - 0.3, 2.4]], CATCH_LEN - 6);
}
module ks_leg() {
    difference() {
        union() {
            box([-HW, FOOT_Y, 0], [HW, HINGE_Y - ZH - 1, FLOOR]);
            box([-KW, HINGE_Y - ZH - 1.5, 0], [KW, Y_TAIL, FLOOR]);
            xcyl(-KW, KW, HINGE_Y, ZH, KNUCKLE_D);
        }
        xcyl(-KW - 1, KW + 1, HINGE_Y, ZH, PIN_D + 2 * PIN_GAP);
        box([-KW - 1, HINGE_Y - PIN_D * 0.35, ZH - PIN_D / 2 - PIN_GAP - PIN_RELIEF], [KW + 1, HINGE_Y + PIN_D * 0.35, ZH]);  // relief under the pin
        cbox([0, FOOT_Y + 6], [30, 8], -0.01, 0.8);                    // rubber foot strip recess
        if (kickstand_catch) {
            y0 = FOOT_Y - KS_GAP;
            prism_yz([[FOOT_Y - 0.01, 0.3], [y0 + CATCH_RIDGE + CATCH_CLR + 0.1, 1.5], [FOOT_Y - 0.01, 2.7]], CATCH_LEN - 4);
            box([-8, FOOT_Y - 0.1, -0.01], [8, FOOT_Y + 3.5, 1.2]);    // fingernail notch
            translate([0, FOOT_Y + PULL[2], -1]) linear_extrude(FLOOR + 2) slot2d(PULL[0], PULL[1]);   // finger hole
        }
    }
}
module ks_hinge_parts() {
    for (s = [-1, 1]) xcyl(s > 0 ? KW + END_GAP : -HW - 4, s > 0 ? HW + 4 : -KW - END_GAP, HINGE_Y, ZH, KNUCKLE_D);
    xcyl(-HW - 4, HW + 4, HINGE_Y, ZH, PIN_D);
}
module ks_stops() {
    r = sqrt(TAIL * TAIL + (ZH - FLOOR) * (ZH - FLOOR));
    a0 = -atan2(ZH - FLOOR, TAIL);
    z_stop = ZH + r * sin(OPEN_DEG + a0);
    x_in = KW + KS_GAP + 0.6; x_out = KW + KS_GAP + 6; x_tip = KW - STOP_REACH;
    z0 = z_stop - (x_in - KW); z_top = z0 + (x_in - x_tip) + 2;
    for (s = [-1, 1])     // two hooks with 45-degree undersides: the tail's corners hit them at OPEN_DEG
        translate([0, Y_TAIL + 2, 0]) rotate([90, 0, 0]) linear_extrude(6)
            polygon([for (p = [[x_in, FLOOR - 0.01], [x_out, FLOOR - 0.01], [x_out, z_top], [x_tip, z_top], [x_tip, z0 + (x_in - x_tip)], [x_in, z0]]) [s * p[0], p[1]]]);
    fy = FOOT_Y + 2;      // fold stop over the foot
    box([-HW - KS_GAP - 5, fy - 2, FLOOR + 0.6], [HW + KS_GAP + 5, fy + 2, FLOOR + 2.4]);
    for (s = [-1, 1]) box([min(s * (HW + KS_GAP + 0.5), s * (HW + KS_GAP + 5)), fy - 2, FLOOR - 0.01], [max(s * (HW + KS_GAP + 0.5), s * (HW + KS_GAP + 5)), fy + 2, FLOOR + 2.4]);
}

// ---- the board's holder, drawn unrotated around its center (ports edge toward -y), then turned and placed ----
module board_place() { translate([BOARD_POS[0], BOARD_POS[1], 0]) rotate(board_rotation) children(); }
TEXT_FLIP = board_rotation >= 180 ? 180 : 0;      // keep its labels readable when the board is turned
module board_solids() {
    for (dx = [-H_L / 2, H_L / 2]) for (dy = [-H_W / 2, H_W / 2]) {
        cyl([dx, dy], FLOOR, 5.5, PEDESTAL);
        if (board_hold == "pegs_clamps") cyl([dx, dy], FLOOR + PEDESTAL - 0.01, PEG_D, PEG_H);
    }
    if (board_hold == "pegs_clamps") {
        corner_guides([0, 0], B_L, B_W, PEDESTAL + B_T + 1.5, FLOOR, corners = free_corners());
        for (p = clamp_posts()) cyl(p, FLOOR - 0.01, CLAMP[0], PEDESTAL + B_T - CLAMP[5] + 0.01);
    } else corner_guides([0, 0], B_L, B_W, PEDESTAL + B_T + 1.5, FLOOR);
    label(LABEL_TEXT, [0, B_W / 2 + 5.5], TEXT_FLIP);
    label("PORTS THIS EDGE", [0, -B_W / 2 - 6], TEXT_FLIP);
}
module board_cuts() {
    if (board_hold == "pegs_clamps") for (p = clamp_posts()) cyl(p, FLOOR + 0.6, M3_PILOT, PEDESTAL + B_T);
    else for (dx = [-H_L / 2, H_L / 2]) for (dy = [-H_W / 2, H_W / 2]) cyl([dx, dy], FLOOR + 0.6, screw_pilot, PEDESTAL + 1);
}
// vents along the top and bottom walls, minus any that would land on a power/switch hole
function vent_blocked(x, yw) = len([for (c = CTL) if (x > c[1][0][0] - 3 && x < c[1][1][0] + 3 &&
                                     (yw > 0 ? c[1][1][1] > IN_Y - 1 : c[1][0][1] < -IN_Y + 1)) 1]) > 0;

// ---- the tray ----
module tray_solids() {
    difference() { rounded_plate(FW, FH, CORNER_R, 0, Z_FACE); rounded_plate(FW - 2 * WALL, FH - 2 * WALL, max(CORNER_R - WALL, 0.5), FLOOR, Z_FACE); }
    for (sx = [-1, 1]) for (sy = [-1, 1]) cyl([sx * POST_POS[0], sy * POST_POS[1]], 0, SCREW_POST_D, Z_JOIN - 0.2);
    board_place() board_solids();
    controls_solids();
    controls_labels();
    if (antenna_clips) {
        r = ANT[1] / 2 + ANT[4]; zc = FLOOR + r; top = zc + sqrt(max(r * r - (ANT[5] / 2) * (ANT[5] / 2), 0)); ow = 2 * (r + ANT[3]);
        for (lx = ANT_CLIPS) difference() {
            box([lx - ANT[2] / 2, ANT_POS[1] - ow / 2, FLOOR - 0.01], [lx + ANT[2] / 2, ANT_POS[1] + ow / 2, top]);
            xcyl(lx - ANT[2], lx + ANT[2], ANT_POS[1], zc, 2 * r);
        }
        label("ANTENNA", [ANT_POS[0] - 6, ANT_POS[1] + ow / 2 + 4.5]);
    }
    if (keyholes) for (sx = [-1, 1])
        translate([sx * KEY_POS[0], KEY_POS[1] + KEY[2] / 2, FLOOR]) linear_extrude(KEY[3] + 2) rotate(90) slot2d(KEY[2] + KEY[0] + 5, KEY[0] + 5);
    if (kickstand) ks_stops();
}
module tray_cuts() {
    for (sx = [-1, 1]) for (sy = [-1, 1]) {
        c = [sx * POST_POS[0], sy * POST_POS[1]];
        cyl(c, -1, M3_CLEAR, Z_FACE + 2); cyl(c, -0.01, M3_HEAD, 2.6);
    }
    board_place() board_cuts();
    controls_cuts();
    if (keyholes) for (sx = [-1, 1]) {
        x = sx * KEY_POS[0]; ky = KEY_POS[1];
        translate([x, ky + KEY[2] / 2, FLOOR]) linear_extrude(KEY[3]) rotate(90) slot2d(KEY[2] + KEY[0] + 1, KEY[0] + 1);
        translate([x, ky, -1]) cylinder(d = KEY[0], h = FLOOR + 2);
        translate([x, ky + KEY[2] / 2, -1]) linear_extrude(FLOOR + 2) rotate(90) slot2d(KEY[2] + KEY[1], KEY[1]);
    }
    for (yw = [FH / 2, -FH / 2]) for (i = [0 : 8]) if (!vent_blocked(-48 + i * 12, yw))
        cbox([-48 + i * 12, yw], [2.5, WALL * 3], FLOOR + 3, ELEC_H - 6);   // vents
    if (kickstand) ks_floor_cut();
}
module back_tray() {
    difference() { tray_solids(); tray_cuts(); }
    if (kickstand) {
        ks_hinge_parts();
        if (kickstand_catch) catch_ridge();
        ks_leg();
    }
}

// swivel clamp for the board (as printed, flat)
module clamp() {
    reach = (CLAMP[1] + CLAMP[2]) * sqrt(2);
    difference() {
        translate([reach / 2, 0, 0]) linear_extrude(CLAMP[4]) slot2d(reach + CLAMP[3], CLAMP[3]);
        translate([0, 0, -1]) cylinder(d = M3_CLEAR, h = CLAMP[4] + 2);
    }
}

if (part == "clamp") clamp(); else back_tray();
