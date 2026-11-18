# Switch V2 7" screen (Route A)

Goal: put a 7" 16:9 panel in a Switch V2 (HAC-001(-01), Mariko, "Iowa") that runs CFW
(hardware modchip), and teach the system software to drive it. No bridge or FPGA board.
Started 2026-11-18.

Target console: firmware **22.5.0**, Atmosphère **1.11.2**. The boot patch applies cleanly to
the Atmosphère `1.11.2` tag; nvservices patches must match the 22.5.0 nvservices build ID.

## What fits

* A 7.0" 16:9 module is about 89 x 161 mm. That is the Switch OLED's screen size, in about
  the same body (V2 console without Joy-Con: roughly 102 x 173 mm, estimated, to be measured).
* 16:10 panels (1200x1920, about 99 mm on the short side) and anything over 7" do not fit.
* A new front shell and mid-frame are needed (the Super7 kit ships both).
* Keep the panel at **720x1280**. HOS drives the internal screen at 720x1280 portrait; a
  1080x1920 panel would also need display mode changes in nvservices and vi.

## What the V2 sends to the screen (from Atmosphère's boot code)

Source: `stratosphere/boot/source/boot_display.cpp` and `boot_display_config.inc`
(Atmosphère master, 2026-11-18).

| Item | Value |
|---|---|
| Link | MIPI DSI, 4 lanes (`DSI_CONTROL_LANES(3)`), RGB888 (`FORMAT(3)`), video mode |
| Active | 720 x 1280 (`DC_DISP_ACTIVE 0x050002D0`) |
| Horizontal | sync 72, back porch 72, front porch 136, total 1000 |
| Vertical | sync 1, back porch 9, front porch 10, total 1300 |
| Pixel clock | about 78 MHz for 60 Hz, so about 470 Mbit/s per lane |
| Panel ID | DCS read 0x04 at boot; vendor byte + board byte (0x0F = 6.2" V1/V2) |
| Backlight | PWM on `LCD_BL_PWM` (period 33898 ns, about 29.5 kHz) + `LCD_BL_EN`; LED driver is on the mainboard |
| Panel power (V1/V2) | two GPIOs (port I bits 0 and 1) switched 10 ms apart: very likely the + and - LCD bias rails; then `LCD_RST` |

All stock V1/V2 panels (JDI, InnoLux, AUO) use the same Himax HX8394 family of driver
chip: every init starts with `B9 FF 83 94` (HX8394 "set extension command").

The new panel's driver chip must accept these timings, or the timings must be patched in
both places below.

## Where the system software sets up the screen

1. **boot sysmodule** (open source, replaced by Atmosphère). It powers the panel, reads the
   panel ID, sends a per-vendor init, shows the boot logo, then **switches the panel fully
   off** (`FinalizeDisplay`: sleep in, rails off).
   An unknown panel ID falls into the `default` case, which only sends sleep out (0x11)
   and display on (0x29).
2. **nvservices** (closed source, sysmodule 0100000000000019; notes for 22.5.0 in
   [docs/nvservices-22.5.0.md](docs/nvservices-22.5.0.md)) powers the panel up again for
   HOS, and handles sleep, wake and brightness. Because boot turns the panel off, nvservices
   must hold its own init code, so **this is the part that matters most**. It needs IPS
   patches per firmware build ID. Not reverse-engineered yet.
   Known so far (FW 21.2 nvservices, from the earlier 1440p work): it reads the setting
   `nvservices!internal_display_vddpn_control` (default 1), which looks like the switch
   for the internal panel's bias rails.

### Shortcut worth checking first

If nvservices also sends only 0x11 + 0x29 to unknown panel IDs, then a panel whose init
code is **burned into the driver chip's OTP** at the factory would light up with **no
software patch**. Many panel vendors do this on request. The stock "second revision"
panels (0x1020, 0x1030) already work this way in boot.

## Panel candidates (7", 720x1280, MIPI DSI, 4 lanes)

| Panel | Driver | Size (mm) | Backlight | Notes |
|---|---|---|---|---|
| Raystar WTIMV70E-01 | Jadard JD9365 + JD5001 (makes its own bias rails) | 95.0 x 163.3 x 2.6 | 18 LEDs, 21 V, 60 mA | 250-300 nits, no touch. 95 mm is tight for the shell. [Datasheet](https://botland.cz/img/art/inne/13970_datasheet.pdf) |
| A 7" 720x1280 panel with a Himax HX8394 | same family as stock | to find | to find | Best fit for the software: the stock init is nearly right |
| Switch OLED Samsung AMS699VC01 | Samsung, ID 0x2050 | 7.0" | OLED (no LED driver) | Boot and nvservices already know it, but only on OLED hardware; needs OLED power rails the V2 doesn't have |

Still to find: a brighter (400+ nit) IPS 720x1280 module at or under about 92 mm wide,
ideally with an HX8394, ideally with OTP init.

## Files here

* `atmosphere/boot-custom7-panel.patch`: adds an `AMS_CUSTOM7_PANEL_ID` case to the boot
  sysmodule with its own init table, so the boot logo works on the new panel. Untested,
  not built yet.
* `tools/init2ams.py`: turns a vendor init list (`B9 FF 83 94`, `delay 120`...) into
  Atmosphère table rows. Checked against Atmosphère's stock InnoLux values.
* Datasheets are kept out of the repo (vendor copyright). Links:
  [Raystar WTIMV70E-01](https://botland.cz/img/art/inne/13970_datasheet.pdf),
  [Panox PO070FMTO (7" AMOLED 1080x1920)](https://www.panoxdisplay.com/uploadfile/datasheet/PO070FMTO_1.pdf).

## What needs Axel's hands

1. ~~The brother's firmware version~~: 22.5.0, Atmosphère 1.11.2.
2. nvservices' ExeFS (`main`, title 0100000000000019) from 22.5.0. The 21.2 dump from the
   OLED is the wrong build. Dump it on the brother's console: Lockpick_RCM (from hekate)
   for 22.5.0 keys, then extract it as in the 1440p work, or dump the system title's ExeFS
   with nxdumptool.
3. With the stock screen unplugged: measure the V2 screen connector against ground with a
   multimeter, console on, for each pin (V2 connector is the mainboard side of the LCD FPC).
   Mark which pins carry ~1.8 V, ~+5.5 V, ~-5.5 V, the backlight anode voltage, and which
   are the DSI pairs (they read ~0.2-1.2 V while the screen is on).
4. Count the stock panel's backlight LEDs or read its datasheet, so the V2 LED driver's
   range can be compared with the new panel's (for example 21 V, 60 mA).

## Next steps

1. Reverse-engineer nvservices' internal panel path: find the panel ID read, the per-vendor
   init tables, and what it does for an unknown ID.
2. Pick the panel; ask the vendor for its init code and whether they can burn it to OTP.
3. Design the adapter flex: V2 connector to the panel's connector (DSI pairs as 100 ohm
   differential, power, backlight, reset).
4. Fill in the boot table, then the nvservices patch, then test.
