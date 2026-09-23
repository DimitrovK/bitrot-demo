"""Flip exactly one bit in an image file and see what the decoder makes of it."""
import glob, io, os, random, sys
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

REF = np.array(Image.open("source.png").convert("RGB"), np.int16)

def decode(raw):
    try:
        im = Image.open(io.BytesIO(raw))
        im.load()
        return np.array(im.convert("RGB"), np.int16)
    except Exception as e:
        return type(e).__name__

def trial(raw, rng):
    b = bytearray(raw)
    i = rng.randrange(len(b))
    b[i] ^= 1 << rng.randrange(8)
    out = decode(bytes(b))
    if isinstance(out, str):
        return "dead", 0.0, out, i / len(b)
    if out.shape != REF.shape:
        return "wrong size", 100.0, "", i / len(b)
    diff = np.abs(out - REF).max(axis=2)
    changed = float((diff > 2).mean() * 100)
    if changed == 0:
        return "identical", 0.0, "", i / len(b)
    return "changed", changed, "", i / len(b)

def main(trials=400):
    files = sorted(glob.glob("img.*"))
    print(f"{'format':<10}{'bytes':>9}{'dead':>7}{'changed':>9}{'identical':>11}"
          f"{'median % of image damaged':>27}")
    for f in files:
        raw = open(f, "rb").read()
        rng = random.Random(9)
        kinds, dmg, errs = [], [], {}
        for _ in range(trials):
            k, d, e, pos = trial(raw, rng)
            kinds.append(k)
            if k == "changed":
                dmg.append(d)
            if e:
                errs[e] = errs.get(e, 0) + 1
        n = len(kinds)
        name = f.split(".")[1]
        med = f"{np.median(dmg):.1f}%" if dmg else "-"
        print(f"  {name:<8}{len(raw):>9,}{100*kinds.count('dead')/n:>6.0f}%"
              f"{100*kinds.count('changed')/n:>8.0f}%{100*kinds.count('identical')/n:>10.0f}%"
              f"{med:>27}")
    print("\n(a bit flip is 'identical' when it lands in metadata or padding the decoder ignores)")

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 400)
