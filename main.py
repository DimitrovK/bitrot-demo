"""Flip bits in an image, in the browser, and see which formats lie to you."""
import io, random
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from PIL import Image

app = FastAPI()
SRC = Image.open("source.png").convert("RGB")
FORMATS = {"png": ("PNG", "image/png"), "jpeg": ("JPEG", "image/jpeg"),
           "webp": ("WEBP", "image/webp"), "gif": ("GIF", "image/gif"),
           "bmp": ("BMP", "image/bmp")}


def encode(fmt):
    pil, mime = FORMATS[fmt]
    buf = io.BytesIO()
    im = SRC.convert("P", palette=Image.ADAPTIVE) if fmt == "gif" else SRC
    im.save(buf, format=pil, **({"quality": 85} if pil in ("JPEG", "WEBP") else {}))
    return buf.getvalue(), mime


@app.get("/img")
def img(fmt: str = "png", bits: int = 1, seed: int = 0):
    raw, mime = encode(fmt)
    b = bytearray(raw)
    rng = random.Random(seed)
    for _ in range(max(0, bits)):
        i = rng.randrange(len(b))
        b[i] ^= 1 << rng.randrange(8)
    return Response(bytes(b), media_type=mime,
                    headers={"Cache-Control": "no-store", "X-Bytes": str(len(b))})


@app.get("/healthz")
def health():
    return {"ok": True}


@app.get("/", response_class=HTMLResponse)
def index():
    cards = "".join(
        f'<figure><img src="/img?fmt={f}&bits=1&seed=3" alt="{f} with one bit flipped">'
        f'<figcaption>{f.upper()} — 1 bit flipped</figcaption></figure>' for f in FORMATS)
    return f"""<!doctype html><meta charset=utf-8><title>One flipped bit</title>
<style>
 body{{font-family:system-ui;margin:0;padding:32px;background:#0f1115;color:#e6e8eb}}
 h1{{font-size:1.5rem;margin:0 0 4px}} p{{color:#9aa4b2;margin:0 0 24px;max-width:60ch}}
 .row{{display:flex;flex-wrap:wrap;gap:16px}}
 figure{{margin:0;background:#171a21;border:1px solid #232833;border-radius:10px;padding:10px}}
 img{{width:240px;height:240px;object-fit:contain;background:#fff;border-radius:6px;display:block}}
 figcaption{{font-size:.8rem;color:#9aa4b2;margin-top:8px;text-align:center}}
 a{{color:#6ea8fe}}
</style>
<h1>One flipped bit</h1>
<p>The same picture, encoded five ways, with exactly one bit flipped in each file.
Some formats stop at the damage and show you half a picture. Others hand you a
complete image in which almost nothing is the original colour.</p>
<div class="row"><figure><img src="/img?fmt=png&bits=0"><figcaption>the original</figcaption></figure>{cards}</div>
"""
