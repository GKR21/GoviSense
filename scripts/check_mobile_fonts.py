"""Check bundled Sinhala/Tamil fonts cover the characters used by the app."""
from pathlib import Path
import struct


ROOT = Path(__file__).resolve().parents[1]


def has_glyph(data, codepoint):
    tables = struct.unpack_from(">H", data, 4)[0]
    cmap = next(struct.unpack_from(">I", data, 12 + index * 16 + 8)[0]
                for index in range(tables)
                if data[12 + index * 16:16 + index * 16] == b"cmap")
    count = struct.unpack_from(">H", data, cmap + 2)[0]
    for index in range(count):
        offset = cmap + struct.unpack_from(">I", data, cmap + 4 + index * 8 + 4)[0]
        format_id = struct.unpack_from(">H", data, offset)[0]
        if format_id == 12:
            groups = struct.unpack_from(">I", data, offset + 12)[0]
            for group in range(groups):
                start, end, glyph = struct.unpack_from(">III", data, offset + 16 + group * 12)
                if start <= codepoint <= end and glyph + codepoint - start:
                    return True
        elif format_id == 4:
            segments = struct.unpack_from(">H", data, offset + 6)[0] // 2
            ends = offset + 14
            starts = ends + segments * 2 + 2
            deltas = starts + segments * 2
            ranges = deltas + segments * 2
            for segment in range(segments):
                start = struct.unpack_from(">H", data, starts + segment * 2)[0]
                end = struct.unpack_from(">H", data, ends + segment * 2)[0]
                if not start <= codepoint <= end:
                    continue
                delta = struct.unpack_from(">h", data, deltas + segment * 2)[0]
                range_offset = struct.unpack_from(">H", data, ranges + segment * 2)[0]
                if range_offset:
                    glyph = struct.unpack_from(">H", data,
                        ranges + segment * 2 + range_offset + (codepoint - start) * 2)[0]
                    if not glyph:
                        continue
                    glyph = (glyph + delta) & 0xFFFF
                else:
                    glyph = (codepoint + delta) & 0xFFFF
                if glyph:
                    return True
    return False


if __name__ == "__main__":
    text = "".join(path.read_text(encoding="utf-8")
                   for path in (ROOT / "mobile/lib").rglob("*.dart"))
    for name, lower, upper in [("NotoSansSinhala", 0x0D80, 0x0DFF),
                               ("NotoSansTamil", 0x0B80, 0x0BFF)]:
        characters = {ord(char) for char in text if lower <= ord(char) <= upper}
        font = (ROOT / f"mobile/assets/fonts/{name}.ttf").read_bytes()
        missing = [f"U+{code:04X}" for code in sorted(characters)
                   if not has_glyph(font, code)]
        if missing:
            raise SystemExit(f"{name} missing: {', '.join(missing)}")
        print(f"{name}: all {len(characters)} used characters covered")
