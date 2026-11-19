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

Groups found (same sequences as Atmosphère's `boot_display.cpp`). Each group ends with a delay
entry whose byte +0x19 is 1:

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

## How nvservices picks a table (FUN_0003ADB0, panel power-on)

1. Sends DCS read 0x04 and keeps the 3 reply bytes: `vendor`, `model`, `board`.
2. If the read fails, it uses a fallback ID: Samsung OLED on an Aula console, else InnoLux
   (`board` 0x10 on Hoag, else 0x0F).
3. Turns `vendor` into a variant number:

| `vendor` byte | `board` | Variant | Init entries used (index into the 0x20-byte array at 0xED0D0) |
|---|---|---|---|
| 0x20 (InnoLux) | not 0x10 | 1 | 0-8: InnoLux 6.2" sequence |
| 0x30 (AUO) | not 0x10 | 2 | 8-16: AUO 6.2" sequence |
| 0x20 (InnoLux) | 0x10 | 3 | 16-20: **default** (11, wait 120, 29) |
| 0x30 (AUO) | 0x10 | 4 | 16-20: default |
| 0x40 (Sharp) | any | 5 | 16-20: default |
| 0x50 (Samsung) | any | 6 | 20-28: Samsung OLED sequence |
| anything else (JDI 0x10, unknown) | any | 0 | 28-42: **JDI sequence** |

   The start and end indexes come from two arrays in rodata: start at 0xBE680 = {0, 8, 16, 16,
   16, 20}, end at 0xBE668 = {8, 16, 20, 20, 20, 28}, for variants 1 to 6. Variant 0 is
   hardcoded as 0x1C to 0x2A. The walk also stops at a delay entry whose byte +0x19 is 1.
4. The variant is kept (0x5B51FF) and picks the shutdown sequence later (FUN_0003B940).

Atmosphère's boot module agrees: vendor 0x40 and unknown IDs go to its `default` case.

## What this means for a new panel

* **An unknown panel ID gets the JDI sequence, not the default one.** JDI's sequence is Himax
  HX8394 commands (B9, BD, D8, D9) followed by sleep out and display on. On a panel with a
  different driver chip those writes may be ignored or may set wrong registers.
* **No-patch route:** a panel whose init code is in its driver chip's OTP **and** whose ID
  bytes read back as vendor **0x40** (board 0x0F) gets only sleep out + display on, in both
  boot and nvservices. Many driver chips let the factory program the ID bytes along with
  the OTP init.
* **Patch route (data only):** for an unknown ID, rewrite the JDI group (entries 28-41 at
  0xED450, 14 entries) with the new panel's sequence and point its long writes at new
  parameter bytes. A sequence longer than 14 entries needs the variant-0 indexes (hardcoded
  in FUN_0003ADB0) changed too. Atmosphère applies exefs patches to the decompressed image,
  so IPS offsets are these offsets + 0x100 (NSO header).
