#!/usr/bin/env python3
"""Turn a panel vendor's init code into Atmosphère boot_display table rows.

Input: one command per line, as vendors usually ship it:
    B9 FF 83 94          # DCS/generic long write: first byte is the command
    11                   # short write, no parameter
    delay 120            # sleep in milliseconds (also "sleep 120" or "ms 120")
Bytes may be written as 0xB9, B9 or b9, separated by spaces or commas.
Lines starting with # or // are ignored.

Output: rows for a `constexpr const SleepOrRegisterWrite Name[] = { ... };`
table, in the same packing Atmosphère uses for the stock panels:
  * 1 byte   -> DCS short write, no parameter   (data type 0x05)
  * 2 bytes  -> DCS short write, one parameter  (data type 0x15)
  * 3+ bytes -> DCS long write                  (data type 0x39), header word
                0x39 | (byte count << 8), then the payload packed little-endian
                into 32-bit words.
Every packet ends with a DSI_TRIGGER_HOST write, as in DisplayConfigJdiSpecificInit01.

Check: "B9 FF 83 94" must give 0x439 then 0x9483FFB9, which is what Atmosphère
sends to the stock InnoLux and AUO panels.
"""
import re
import sys


def parse(lines):
    for raw in lines:
        line = re.split(r"#|//", raw, maxsplit=1)[0].strip()
        if not line:
            continue
        m = re.match(r"(?i)(delay|sleep|ms)\s+(\d+)", line)
        if m:
            yield ("sleep", int(m.group(2)))
            continue
        data = [int(t, 16) for t in re.split(r"[\s,]+", line) if t]
        if any(b > 0xFF for b in data):
            raise ValueError(f"not a byte list: {raw!r}")
        yield ("cmd", data)


def rows(items):
    out = []
    w = lambda reg, val: out.append(f"    {{SleepOrRegisterWriteKind_Write, {reg}, 0x{val:X}}},")
    for kind, val in items:
        if kind == "sleep":
            out.append(f"    {{SleepOrRegisterWriteKind_Sleep, {val}, 0}},")
            continue
        data = val
        if len(data) == 1:
            w("DSI_WR_DATA", 0x05 | data[0] << 8)
        elif len(data) == 2:
            w("DSI_WR_DATA", 0x15 | data[0] << 8 | data[1] << 16)
        else:
            w("DSI_WR_DATA", 0x39 | len(data) << 8)
            for i in range(0, len(data), 4):
                chunk = data[i:i + 4]
                w("DSI_WR_DATA", sum(b << (8 * j) for j, b in enumerate(chunk)))
        out.append("    {SleepOrRegisterWriteKind_Write, DSI_TRIGGER, DSI_TRIGGER_HOST},")
    return out


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "DisplayConfigCustom7SpecificInit01"
    src = open(sys.argv[2]) if len(sys.argv) > 2 else sys.stdin
    body = rows(parse(src))
    print(f"constexpr const SleepOrRegisterWrite {name}[] = {{")
    print("\n".join(body))
    print("};")


if __name__ == "__main__":
    main()
