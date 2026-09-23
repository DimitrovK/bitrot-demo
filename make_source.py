"""A deterministic, photograph-like source image, so anyone can reproduce this."""
import numpy as np
from PIL import Image

rng = np.random.default_rng(42)
H = W = 512
yy, xx = np.mgrid[0:H, 0:W]

# smooth sky-to-ground gradient
img = np.zeros((H, W, 3), np.float64)
img[..., 0] = 60 + 150 * (yy / H)
img[..., 1] = 90 + 120 * (1 - (yy / H)) + 30 * np.sin(xx / 40)
img[..., 2] = 200 - 120 * (yy / H)

# a few hard edges, which is what compressors struggle with
for cx, cy, r in [(120, 150, 60), (380, 200, 90), (250, 400, 110)]:
    m = (xx - cx) ** 2 + (yy - cy) ** 2 < r * r
    img[m] = img[m] * 0.35 + np.array([230, 180, 60]) * 0.65

# fine texture, so the file is not trivially compressible
img += rng.normal(0, 6, img.shape)
img = np.clip(img, 0, 255).astype(np.uint8)
Image.fromarray(img).save("source.png")
print("source.png written", img.shape)
