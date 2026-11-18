# nvservices on 22.5.0: internal panel notes

Firmware 22.5.0, nvservices (0100000000000019) build ID
`795BFA3EE49A448E0BF9A55C3371F78BEB030369`. Offsets are in the decompressed NSO image
(text at 0x0, rodata at 0xBA000, data at 0xE6000). No Nintendo code or data is stored in this
repository; dump your own copy (see the README).

## Panel command tables (data, around 0xED0D0)

nvservices keeps its own copies of the panel init sequences that Atmosphère's boot module
sends. They are arrays of 0x40-byte entries. What each entry holds, as far as we can tell:

| Offset in entry | Meaning |
|---|---|
| +0x00 | DSI data type: 0x05 (short, no parameter), 0x15 (short, one parameter), 0x39 (long) |
| +0x04 | DCS command byte (0xB9, 0x11, 0x29...) |
| +0x08 | parameter count |
| +0x10 | pointer to the parameter bytes (in data), or to a zero buffer in bss |
| +0x18 | 1 for packets with a parameter list |
| +0x24 | 0xFFFFFFFF marks a delay |
| +0x28 | delay after the packet, in ms |

Tables found (same sequences as Atmosphère's `boot_display.cpp`):

| Start | Sequence | Matches |
|---|---|---|
| 0xED0D0 | 11, wait 180, B9 FF 83 94, wait 5, B1 48 15 75 09 32 14, wait 5, 29, wait 15 | InnoLux 0x0F20 |
| 0xED1D0 | same, with B1 48 11 71 09 32 14 | AUO 0x0F30 |
| 0xED2D0 | 11, wait 120, 29, wait 15 | the default (rev2 panels, unknown IDs in boot) |
| 0xED350 | 11, wait 180, A0, 53 20, 51 ..., wait 5, 29, wait 15 | Samsung 0x2050 (OLED) |
| 0xED450 | B9 FF 83 94, BD/D8 gamma pages, D9, B9 00 00 00, 11, wait 180, 29, wait 15 | JDI 0x10 |
| 0xED690 | 10 (sleep in) ... | shutdown tables follow |

Parameter bytes live just before the tables, at 0xED070 (B9 FF 83 94, then the B1 sets)
and 0xED610 onward (D5/D6 gamma, B1 shutdown sets).

## Panel timing descriptor (data, 0xECEC0)

One descriptor for the internal panel, pointed to from the GOT at 0xEB578:
720 x 1280, h sync 72 / back porch 72 / front porch 136, v sync 1 / back porch 9 /
front porch 10, pixel clock 78000 kHz. It is identical to what boot programs, so a new panel
must accept these timings, or this descriptor is patched too.

The structure just before it (0xECEA0) points to the first init table (0xED0D0) and the first
shutdown table (0xED690).

## Why this matters

* The default table (sleep out, display on) exists in nvservices as well as in boot. A panel
  whose init code is burned into its driver chip's OTP is likely to work with **no patch**,
  if nvservices picks the default table for an unknown panel ID the way boot does.
  Not confirmed yet: the code that picks a table by panel ID hasn't been found.
* The tables are plain data. A custom panel can probably be supported with an IPS patch that
  rewrites one table's entries (and points them at new parameter bytes), without changing code.
  Atmosphère applies exefs patches to the decompressed image, so these offsets apply directly
  (IPS offsets add the 0x100 NSO header).

## Still to do

* Find the code that reads the panel ID and picks a table (and what it does for an unknown ID).
* Check how many entries each table may hold (the count the code passes with the pointer).
