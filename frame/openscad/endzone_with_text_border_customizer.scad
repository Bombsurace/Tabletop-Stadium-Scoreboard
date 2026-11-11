// =============================================================================
// Football field scoreboard - END ZONE INSERT customizer
// Snap-in end zones with flush lettering and an optional outline. Prints face down, clips up,
// no supports. Fits every front (7" Hosyond, 7.9" Waveshare, custom).
//
// MakerWorld: set the colors, hit Generate, and print as one plate.
// Desktop OpenSCAD: set "Output" to "Insert only" and "Letters only" in turn and
// export each as STL. With an outline enabled, also export "Border only".
// Load the exported STLs into the slicer as one object with multiple parts.
// =============================================================================

/* [End zone text] */
// Left end zone (reads bottom to top). Leave empty for a blank insert.
left_text = "HOME";
// Optional second line for the left end zone
left_line_2 = "";
// Right end zone (reads top to bottom). Leave empty for a blank insert.
right_text = "AWAY";
// Optional second line for the right end zone
right_line_2 = "";
// Lettering font (bold fonts read best)
font = "Roboto Condensed:style=Bold"; // font
// Make the lettering bigger or smaller than the automatic fit
text_size_percent = 100; // [60:5:120]

// Outline width in mm, measured outward from the fitted text (0 disables it)
text_border_width = 0.5; // [0:0.1:2]

/* [What to make] */
// Which end zones to put on the plate
part = "both"; // [both:Both end zones, left:Left end zone only, right:Right end zone only, blank:Blank insert (for your own logo)]
// All parts together (MakerWorld), or one part at a time (desktop OpenSCAD export)
output = "all"; // [all:All parts, insert:Insert only, letters:Letters only, border:Border only]
// End zone color
insert_color = "#006778"; // color
// Letter color
letter_color = "#FFFFFF"; // color

// Outline color
border_color = "#000000"; // color

/* [Hidden] */
// ---- sizes: match frame/field_frame.py (the tested print) -------------------
W = 25.6;          // insert width  (end zone 26 mm minus 0.2 mm fit each side)
H = 139.6;         // insert length (140 mm minus fit)
T = 2.0;           // insert thickness = pocket depth
TEXT_D = 0.6;      // letters sink this deep into the face (flush inlay)
TEXT_EDGE = 8.0;   // margin across the width for the lettering
TEXT_END = 12.0;   // margin at the ends of the lettering
CHAR_W = 0.70;     // average letter width / height for the default font (automatic fit; the size slider covers other fonts)
// snap clips (field_frame.py SNAP)
HALF = 10.0;       // half the LED window width the clips sit in
GAP = 0.25; ARM_T = 1.0; ARM_W = 12.0; ARM_Y = 40.0; ROOT = 1.2;
HOOK = 0.9; HOOK_H = 0.7; LEAD = 2.0; RIM_DEPTH = 12.0;
DROP = RIM_DEPTH - T;
ZC = -(DROP + 0.15);                   // top of the hook's catch
ZTIP = ZC - HOOK_H - 0.3 - LEAD;       // clip tip
PLATE_GAP = 14.0;                      // space between two inserts on the plate
$fn = 24;

// ---- one snap clip (installed position: face up at z = T, clips reaching down) ----
module clip(sx, y0) {
    xo = sx * (HALF - GAP);            // arm outer face
    xi = sx * (HALF - GAP - ARM_T);    // arm inner face
    translate([min(xi, xo), y0 - ARM_W / 2, ZTIP]) cube([ARM_T, ARM_W, -ZTIP + 0.01]);
    // gusset at the root (where a clip would crack) and the hook, drawn across the clip width
    translate([0, y0 + ARM_W / 2, 0]) rotate([90, 0, 0]) linear_extrude(ARM_W) {
        polygon([[xi, 0.01], [xi - sx * ROOT, 0.01], [xi, -ROOT]]);
        polygon([[xo, ZC], [xo + sx * HOOK, ZC - HOOK_H], [xo + sx * HOOK, ZC - HOOK_H - 0.3],
                 [xo, ZTIP], [xo - sx * 0.3, ZTIP], [xo - sx * 0.3, ZC]]);
    }
}

// ---- lettering, flat, along X, auto-fitted to the insert ---------------------
function fit_len(t, hmax) = min(H - TEXT_END, hmax * CHAR_W * len(t)) * text_size_percent / 100;

module line2d(t, hmax) {
    if (len(t) > 0)
        resize([fit_len(t, hmax), 0], auto = true)
            text(t, font = font, halign = "center", valign = "center");
}

module lettering2d(t1, t2) {
    if (len(t2) == 0) {
        line2d(t1, W - TEXT_EDGE);
    } else {
        hmax = (W - TEXT_EDGE - 2) / 2;
        translate([0, (hmax + 2) / 2]) line2d(t1, hmax);
        translate([0, -(hmax + 2) / 2]) line2d(t2, hmax);
    }
}

// letters as installed: the top TEXT_D of the insert face (extra = how far above the face to reach, for cutting)
module letters_installed(side, t1, t2, extra = 0, outline = false) {
    translate([0, 0, T - TEXT_D])
        linear_extrude(TEXT_D + extra)
            rotate([0, 0, side == "left" ? 90 : -90]) {
                if (outline && text_border_width > 0)
                    offset(r = text_border_width) lettering2d(t1, t2);
                else
                    lettering2d(t1, t2);
            }
}

module plate() { translate([-W / 2, -H / 2, 0]) cube([W, H, T]); }

module insert_installed(side, t1, t2) {
    difference() {
        union() {
            plate();
            for (sx = [-1, 1]) for (sy = [-1, 1]) clip(sx, sy * ARM_Y);
        }
        if (len(t1) + len(t2) > 0) letters_installed(side, t1, t2, extra = 1, outline = true);
    }
}

module inlay_installed(side, t1, t2) {
    if (len(t1) + len(t2) > 0) intersection() { plate(); letters_installed(side, t1, t2); }
}

module border_installed(side, t1, t2) {
    if (text_border_width > 0 && len(t1) + len(t2) > 0)
        intersection() {
            plate();
            difference() {
                letters_installed(side, t1, t2, outline = true);
                translate([0, 0, -0.01]) letters_installed(side, t1, t2, extra = 0.02);
            }
        }
}

// installed -> printed: face down on the bed, clips up (text comes out mirrored, reads right once flipped)
module face_down() { translate([0, 0, T]) rotate([0, 180, 0]) children(); }

module end_zone(side) {
    t1 = side == "left" ? left_text : side == "right" ? right_text : "";
    t2 = side == "left" ? left_line_2 : side == "right" ? right_line_2 : "";
    face_down() {
        if (output == "all" || output == "insert") color(insert_color) insert_installed(side, t1, t2);
        if (output == "all" || output == "letters") color(letter_color) inlay_installed(side, t1, t2);
        if (output == "all" || output == "border") color(border_color) border_installed(side, t1, t2);
    }
}

sides = part == "both" ? ["left", "right"] : [part];
for (i = [0 : len(sides) - 1])
    translate([len(sides) == 2 ? (i == 0 ? -1 : 1) * (W + PLATE_GAP) / 2 : 0, 0, 0]) end_zone(sides[i]);
