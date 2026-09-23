# bitrot-demo

One flipped bit, several image formats. Companion to a dev.to post.

The same picture is encoded as PNG, JPEG, GIF and BMP, then exactly one bit is
flipped in each file. The point is not that damage happens — it is that the
formats fail in completely different ways:

![the live demo](images/live-app.png)

PNG stops at the damage and paints half a picture. JPEG and GIF hand you a
complete image in which almost no pixel is the original colour.

## Run it

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

`/img?fmt=png&bits=1&seed=3` renders the corrupted file directly; change `bits`
and `seed` to get different damage.

One thing worth knowing if you deploy this: some Pillow builds ship without a
WebP *encoder* even though `features.check("webp")` returns True, because that
flag reports decode support. `Image.SAVE` is the registry that actually decides.

MIT licensed.
