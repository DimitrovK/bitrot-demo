from PIL import Image
import os
src = Image.open("source.png").convert("RGB")
targets = {
    "png":  dict(format="PNG", optimize=True),
    "jpeg": dict(format="JPEG", quality=85),
    "jpeg_rst": dict(format="JPEG", quality=85, restart_marker_blocks=4),
    "gif":  dict(format="GIF"),
    "webp": dict(format="WEBP", quality=85),
    "avif": dict(format="AVIF", quality=85),
    "bmp":  dict(format="BMP"),
}
for name, kw in targets.items():
    im = src.convert("P", palette=Image.ADAPTIVE) if name == "gif" else src
    ext = name.split("_")[0]
    im.save(f"img.{name}.{ext}", **kw)
    print(f"  {name:<9} {os.path.getsize(f'img.{name}.{ext}'):>8,} bytes")
