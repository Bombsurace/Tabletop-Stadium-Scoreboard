# Parts list

Everything for one scoreboard. **Tested** means it's in the build these guides were written from. *Untested* parts
should work but nobody has confirmed it yet; if you try one, please say how it went in an
[issue](https://github.com/Bombsurace/Tabletop-Stadium-Scoreboard/issues).

> Some links are Amazon affiliate links: as an Amazon Associate I earn from qualifying purchases, at no extra cost to
> you. Prices change; the totals are rough.

## Electronics

| Qty | Part | Notes | Status | Link |
|---|---|---|---|---|
| 1 | **Orange Pi Zero 2W**, 1 GB or more | the computer. 65 × 30 mm | Tested | [Amazon](https://link.amazon/B09s5Ofy1) |
| — | *or* Raspberry Pi Zero 2 W | same footprint and holes; there's a back tray preset for it | *Untested* | [Amazon](https://www.amazon.com/s?k=raspberry+pi+zero+2+w&tag=bombsurace0c-20) |
| 1 | **Hosyond 7" 1024×600 IPS touchscreen, HDMI** | the screen. Screws to the front by its 4 ears | Tested | [Amazon](https://link.amazon/B0eExN99E) |
| 1 | microSD card, 16–32 GB, A1 or faster | holds the operating system. Uses a few GB; 8 GB works but is tight. A "high endurance" card lasts longest | Tested | [Amazon](https://link.amazon/B0j6sqmAZ) |
| 1 | **90° mini-HDMI to HDMI FPC ribbon, 20 cm** (JSER CYFPV or similar) | flat ribbon; the angled end goes on the Orange Pi | Tested | [Amazon](https://link.amazon/B0eOeYVWk) |
| 1 | **USB-C to micro-USB OTG data cable** | powers the screen and carries touch. It must be a *data* (OTG) cable | Tested | [Amazon](https://link.amazon/B05G2uN7v) |
| 1 | Wi-Fi antenna | comes with the Orange Pi | Tested | — |

## Power

Pick **one** power input. Both fit the same back tray.

| Qty | Part | Notes | Status | Link |
|---|---|---|---|---|
| 1 | **2-wire 5 V snap-in USB-C socket** (14.5 × 6.4 mm hole) | ⚠️ only powers on from a **USB-A charger with an A-to-C cable**. A USB-C to USB-C charger gives no power, because the socket has no 5.1 kΩ resistors | Tested | [Amazon](https://link.amazon/B0bjHbrCO) |
| — | *or* USB-C breakout board **with 5.1 kΩ resistors** | works with any USB-C charger. Fits the back tray's breakout pocket (`power = "usbc_board"` in the customizer) | *Untested* | [Amazon](https://www.amazon.com/s?k=usb+c+breakout+board+5.1k+resistor&tag=bombsurace0c-20) |
| 1 | **KCD11 2-pin rocker switch** (14 × 9 mm hole) | snaps into the side wall | Tested | [Amazon](https://link.amazon/B0aT9bRm1) |
| 1 | USB-C male to 2-wire pigtail (or a cut USB-C cable) | carries power from the switch to the Orange Pi | Tested | [Amazon](https://www.amazon.com/s?k=usb+c+male+pigtail+2+wire&tag=bombsurace0c-20) |
| 1 | 5 V 3 A USB charger | with the snap-in socket: a USB-A charger and an A-to-C cable | Tested | [Amazon](https://www.amazon.com/s?k=5v+3a+usb+wall+charger&tag=bombsurace0c-20) |

## Hardware

| Qty | Part | Used for | Link |
|---|---|---|---|
| 4 | M3 × 20 mm self-tapping screws | back tray to front, from behind | [M3 self-tapping assortment](https://link.amazon/B0dwFPG6M) |
| 4 | M3 × 8–10 mm self-tapping screws | the 7" screen's ears | same assortment |
| 2 | M3 × 8 mm self-tapping screws | the two swivel clamps holding the Orange Pi | same assortment |
| 1 | thin rubber strip | kickstand foot (there's a recess for it) | [Amazon](https://www.amazon.com/s?k=adhesive+rubber+strip+thin&tag=bombsurace0c-20) |
| 2 | wall screws, head 8.5 mm or less | only for wall hanging (keyholes 200 mm apart) | — |

Also: short lengths of wire, solder or wire connectors for the switch, and heat-shrink.

## Filament

Under 400 g in total (the back tray is most of it; your slicer gives the exact amount). PLA works; PETG makes the snap-in end zone clips last longer.

| Color | For |
|---|---|
| Green | field front |
| White | yard lines and lettering (two-color print), or print the lines as grooves in one color |
| Your team's color | end zones |
| Any | back tray, Pi clamps |

## Tools

- 3D printer with a bed of at least 290 × 160 mm. A multi-color printer is optional.
- A Phillips screwdriver, a soldering iron (or crimp connectors), and a computer to write the SD card.

## Other screens

The software adapts its layout to any screen shape. The frame has fronts for:

| Screen | Front | Status |
|---|---|---|
| Hosyond 7" 1024×600 HDMI | `front_standard7` | Tested |
| Waveshare 7.9" 1280×400 HDMI bar | `front_wide79` | *Untested*: designed from the spec sheet |

A front customizer for other screens is planned.
