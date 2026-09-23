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

## Contributing

Issues and pull requests are welcome, and especially so during Hacktoberfest.
The [good first issues](https://github.com/DimitrovK/bitrot-demo/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
are small and self-contained on purpose: a damage report next to each image, a
control for how many bits to flip, a hex view of the changed byte, a Dockerfile,
and some tests.
