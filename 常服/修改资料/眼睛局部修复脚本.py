from pathlib import Path
from PIL import Image, ImageChops


ROOT = Path(__file__).parent
SOURCE = ROOT / "current-normalized.png"
GENERATED = ROOT / "generated-scaled.png"
OUTPUT = ROOT / "spritesheet-eye-corrected.png"

atlas = Image.open(SOURCE).convert("RGBA")
generated = Image.open(GENERATED).convert("RGBA")
frame_x, frame_y = 192, 1248  # waiting frame 01

# The reference edit supplies the iris colors. Limit compositing to the
# discolored iris; retain the original eyelashes, highlights and eye shape.
changed = []
for y in range(73, 90):
    for x in range(68, 81):
        original = atlas.getpixel((frame_x + x, frame_y + y))
        replacement = generated.getpixel((x, y))
        r, g, b, a = original
        rr, gg, bb, aa = replacement
        if a < 255 or aa < 180:
            continue
        if b <= r + 12 or b <= g + 3:
            continue
        if bb <= rr + 30 or bb <= gg + 8:
            continue
        # White glints remain from the source frame.
        if min(r, g, b) > 210 and max(r, g, b) - min(r, g, b) < 35:
            continue
        atlas.putpixel((frame_x + x, frame_y + y), (rr, gg, bb, a))
        changed.append((x, y))

atlas.save(OUTPUT, optimize=True)
original = Image.open(SOURCE).convert("RGBA")
diff = ImageChops.difference(original.convert("RGB"), atlas.convert("RGB"))
print(f"changed_pixels={len(changed)} bbox={diff.getbbox()}")

before = original.crop((frame_x, frame_y, frame_x + 192, frame_y + 208))
after = atlas.crop((frame_x, frame_y, frame_x + 192, frame_y + 208))
before.save(ROOT / "frame-before.png")
after.save(ROOT / "frame-after.png")
before.crop((64, 67, 119, 105)).resize((880, 608), Image.Resampling.NEAREST).save(ROOT / "eye-before-zoom.png")
after.crop((64, 67, 119, 105)).resize((880, 608), Image.Resampling.NEAREST).save(ROOT / "eye-after-zoom.png")
