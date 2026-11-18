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
| 14 | OL | not connected, or a pin isolated by an off switch (for example backlight or bias output) |

The ground, pair, pair, ground pattern is the usual layout for MIPI DSI lanes. Identical
readings of about 0.28 V point to the same kind of pin on the SoC (DSI pads). Four data lanes
plus the clock need five pairs, so expect the pattern to continue for several more pins.
