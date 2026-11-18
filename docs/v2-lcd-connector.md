# Switch V2 screen connector (mainboard side)

Diode-mode readings, red probe on ground, black probe on the pin, battery and screen
unplugged. Measured by Axel on 2026-11-18 (pins 1-14; pin 6 read 0.279 on the second pass). Pin 1 position still to confirm with a close-up.

| Pin | Reading | Reading suggests |
|---|---|---|
| 1 | 0.278 | signal; same reading as the DSI pins, so probably half of a pair whose other half is off the measured range, or a lone DSI line |
| 2 | 0.000 | ground |
| 3 | 0.279 | DSI pair A (+/-) |
| 4 | 0.279 | DSI pair A |
| 5 | 0.000 | ground |
| 6 | 0.278 | DSI pair B |
| 7 | 0.278 | DSI pair B |
| 8 | 0.000 | ground |
| 9 | 0.322 | signal, different kind from the DSI pins (logic line or a different pad type) |
| 10 | 0.322 | same as 9 |
| 11 | 0.322 | same as 9 |
| 12 | 0.000 | ground |
| 13 | 0.630 | supply rail or control line (higher reading = fewer diode paths, typical for a power pin) |
| 14 | OL (confirmed on second pass) | not connected, or a pin isolated by an off switch (for example backlight or bias output) |
| 15-18 | OL | |
| 19 | 0.000 | ground |
| 20-21 | OL | |
| 22 | 0.840 | (count uncertain: the pass restarted at 21 right after this pin) |
| 23-24+ | OL | "I think the rest are OL" |

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

| Pin | Volts | Likely |
|---|---|---|
| 1 | 0 | LED cathode (string return to the driver) or ground: check continuity to ground, console off |
| 2 | 0 | same |
| 3 | 16.4 | LED anode (boost output) |
| 4 | 0 | same as 1 |

16.4 V / about 3.0-3.1 V per white LED gives about 5 LEDs in series per string (6 if the current
was low). Re-measure at full brightness in HOS to firm this up. If pins 1, 2 and 4 are separate
cathodes (not tied to ground), the stock driver runs 3 strings, each with its own current sink.

Consequence for the new panel: the Raystar WTIMV70E-01 wants about 21 V across its LED strings
(18 LEDs). Whether the V2 boost can reach 21 V, and how its per-string sinks map onto the new
panel's LED pins, decides if the stock driver can be reused.
