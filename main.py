"""Flip bits in an image, in the browser, and see which formats lie to you."""
import io, random
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from PIL import Image, features

app = FastAPI()
SRC = Image.open("source.png").convert("RGB")
_ALL = {"png": ("PNG", "image/png"), "jpeg": ("JPEG", "image/jpeg"),
        "webp": ("WEBP", "image/webp"), "gif": ("GIF", "image/gif"),
        "bmp": ("BMP", "image/bmp")}
# The Pillow build on some platforms has no WebP *encoder*, even though
# features.check("webp") reports True for decoding. Ask the save registry.
Image.init()
FORMATS = {k: v for k, v in _ALL.items() if v[0] in Image.SAVE}


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
        f'<figure data-format="{f}"><img src="/img?fmt={f}&bits=1&seed=3" alt="{f} with one bit flipped">'
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
 .controls{{margin-bottom:24px;display:flex;flex-wrap:wrap;align-items:center;gap:12px}}
 .controls[hidden]{{display:none}}
</style>
<h1>One flipped bit</h1>
<p>The same picture, encoded five ways, starting with one bit flipped in each file.
Some formats stop at the damage and show you half a picture. Others hand you a
complete image in which almost nothing is the original colour.</p>
<div class="controls" hidden>
 <label for="bits">Bits to flip: <output id="bit-count" for="bits">1</output></label>
 <input id="bits" type="range" min="0" max="50" value="1">
 <button id="reroll" type="button">Reroll damage</button>
 <span>Seed: <output id="seed">3</output></span>
</div>
<div class="row"><figure><img src="/img?fmt=png&bits=0"><figcaption>the original</figcaption></figure>{cards}</div>
<script>
 const bits = document.querySelector('#bits');
 let seed = 3;
 function updateImages() {{
   const count = Number(bits.value);
   document.querySelector('#bit-count').value = count;
   document.querySelector('#seed').value = seed;
   document.querySelectorAll('figure[data-format]').forEach(card => {{
     const format = card.dataset.format;
     const description = `${{count}} bit${{count === 1 ? '' : 's'}} flipped`;
     const image = card.querySelector('img');
     image.src = '/img?' + new URLSearchParams({{fmt: format, bits: count, seed}});
     image.alt = `${{format}} with ${{description}}`;
     card.querySelector('figcaption').textContent = `${{format.toUpperCase()}} — ${{description}}`;
   }});
 }}
 bits.addEventListener('input', updateImages);
 document.querySelector('#reroll').addEventListener('click', () => {{
   seed += 1;
   updateImages();
 }});
 document.querySelector('.controls').hidden = false;
</script>
"""
