# Switch V2 screen connector (mainboard side)

First pass (2026-11-18): Axel probed the **even side** (solder tails) of the ~54-pin ZIF, starting at the
triangle (pin 1) end, so pass position n is pin 2n. The odd row is still to measure.

Diode-mode readings, red probe on ground, black probe on the pin, battery and screen
unplugged. Measured by Axel on 2026-11-18 (pins 1-14; pin 6 read 0.279 on the second pass).

| Pass position | Pin (even row, from the triangle end) | Reading | Reading suggests |
|---|---|---|---|
| 1 | 2 | 0.278 | signal; same reading as the DSI pins, so probably half of a pair whose other half is off the measured range, or a lone DSI line |
| 2 | 4 | 0.000 | ground |
| 3 | 6 | 0.279 | DSI pair A (+/-) |
| 4 | 8 | 0.279 | DSI pair A |
| 5 | 10 | 0.000 | ground |
| 6 | 12 | 0.278 | DSI pair B |
| 7 | 14 | 0.278 | DSI pair B |
| 8 | 16 | 0.000 | ground |
| 9 | 18 | 0.322 | signal, different kind from the DSI pins (logic line or a different pad type) |
| 10 | 20 | 0.322 | same as 9 |
| 11 | 22 | 0.322 | same as 9 |
| 12 | 24 | 0.000 | ground |
| 13 | 26 | 0.630 | supply rail or control line (higher reading = fewer diode paths, typical for a power pin) |
| 14 | 28 | OL (confirmed on second pass) | not connected, or a pin isolated by an off switch (for example backlight or bias output) |
| 15-18 | 30-36 | OL | |
| 19 | 38 | 0.000 | ground |
| 20-21 | 40-42 | OL | |
| 22 | 44 | 0.840 | (count uncertain: the pass restarted at 21 right after this pin) |
| 23-24+ | 46-48+ | OL | "I think the rest are OL" |

**Update (2026-11-19):** the even row shows 5 DSI-like pins (2, 6, 8, 12, 14). A 4-lane link needs
10, so the other 5 are very likely on the odd side next to them (pins 1-15), with pin 2's partner
there too.

**Doubt (2026-11-18):** a 4-lane DSI link needs 10 DSI pins, and only 4 to 7 have shown up.
A long run of OL usually means the probe isn't touching the contact (FPC contacts sit recessed
inside the connector), or this is a different connector. Re-check a few OL pins with firm
pressure, and confirm the connector and its total pin count with a close-up photo.

The ground, pair, pair, ground pattern is the usual layout for MIPI DSI lanes. Identical
readings of about 0.28 V point to the same kind of pin on the SoC (DSI pads). Four data lanes
plus the clock need five pairs, so expect the pattern to continue for several more pins.

## Backlight connector (separate from the picture connector)

Confirmed 2026-11-18: the backlight has its own small white 4-pin ZIF connector just above the
speaker (narrow flex with yellow tape). With the picture board-to-board flex unplugged the
backlight still lights; with this one unplugged it does not.

Readings against ground, console on at the modchip's "no SD card" screen (brightness level
unknown):

| Pin | Volts | Continuity to ground (console off) | Role |
|---|---|---|---|
| 1 | 0 | beeps | ground on the board side only: no trace on the flex |
| 2 | 0 | no beep | LED cathode (return into the driver's current sink) |
| 3 | 16.4 | no beep | LED anode (boost output) |
| 4 | 0 | beeps | ground, carried on the flex (shield or return) |

The flex carries pins 2, 3 and 4 (3 traces), so the stock backlight is one anode and one cathode: a single
string, or parallel strings joined on the panel. 16.4 V at about 3.0-3.1 V per white LED means
about 5 LEDs in series (6 if the current was low), with the series groups possibly in parallel.

Consequence for the new panel: the Raystar WTIMV70E-01 is also one anode and one cathode, but
wants about 21 V (18 LEDs, likely 6 series x 3 parallel) at 60 mA. The wiring maps 1:1. Whether
the V2 driver works depends on its boost's overvoltage limit and its set current: identify the
backlight driver chip (near this connector) and read its datasheet.

### Backlight driver (unconfirmed)

A repair forum thread names the V1/V2 backlight driver as a TI TPS61163A (marking "8316"), on
the back side of the mainboard, opposite the backlight connector. That is a single-string WLED
boost driver with a 40 V switch and roughly 38 V overvoltage limit (up to about 10 LEDs in
series), so ~21 V for the Raystar panel is within range. LED current is set by the resistor on
its FB pin; read that resistor to know the stock current. To confirm: check the marking on the
back side. The small QFN next to the connector (marking roughly "T451 / 118 / AUSV") is not it.
Source: https://www.tronicsfixforum.com/t/switch-with-no-backlight-no-enable-signal-at-the-ic/8572

## Picture connector: type and pin count (corrected 2026-11-19)

The screen's picture flex ends in a **ZIF tail**: gold contact pads on one face (about 54,
staggered long/short), a brown stiffener on the other face printed with a triangle and "1" at one
end and "53" near the other. It goes into the long single-row ZIF connector on the mainboard,
beside the game-card area, with a triangle printed on the board at its pin 1 end. (An earlier
note called it a 2 x 27 board-to-board plug; that was wrong.) Shops sell a "Nintendo Switch LCD
FPC connector (56 pin)", so 54-56 contacts; to be confirmed when the odd side is probed.

At this fine pitch the connector's solder tails alternate sides: odd pins come out on one long
side, even pins on the other. Axel's first pass walked the side away from the triangle mark,
starting at the triangle end, which we take as the even pins (position n = pin 2n).

## Odd side, first readings (2026-11-19)

Same diode mode setup, solder tails on the triangle side, from the triangle end (position n =
pin 2n-1). "No trace" = the leg has no visible trace on the board and reads OL.

| Pass position | Pin | Reading |
|---|---|---|
| 1 | 1 | ground |
| 2 | 3 | no trace |
| 3 | 5 | no trace |
| 4 | 7 | ground |
| 5 | 9 | no trace |
| 6 | 11 | no trace |
| 7 | 13 | trace, OL |
| 8 | 15 | no trace |
| 9 | 17 | trace, OL |
| 10 | 19 | ground |
| 11 | 21 | trace, OL |

So far the odd side carries grounds and a few lines that read OL in diode mode. OL on a line
with a trace usually means a supply or switched output with no diode path to ground while the
console is off (for example the panel's +/-5.5 V bias outputs). These need a powered pass: DC
volts, flex plugged in, console on at the boot/no-SD screen, probing the solder tails.
