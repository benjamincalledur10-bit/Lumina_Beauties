"""Bootstrap editable masters once. Build does not overwrite artist edits."""
from pathlib import Path
import argparse
import numpy as np
from PIL import Image, ImageFilter
from material import periodic, u8

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--overwrite', action='store_true')
args = p.parse_args()
source = ROOT / 'sources/stone'
if not args.overwrite and any((source / n).exists() for n in ('albedo.png', 'height.png')):
    p.error('Masters exist; use --overwrite only to discard edits and reauthor them.')
a = np.asarray(Image.open(source / 'generated-original.png').convert('RGB').resize((1024, 1024), Image.Resampling.LANCZOS)) / 255.
a = np.stack([periodic(a[..., c]) for c in range(3)], -1)
# Compress photographic contrast to limit residual baked shading.
a = np.clip(.52 + (a - a.mean()) * .68, 0, 1)
Image.fromarray(u8(a)).save(source / 'albedo.png')
# Initial artistic height approximation, NOT a measured scan. Dark cracks recede.
lum = np.sum(a * np.array([.2126, .7152, .0722]), axis=-1)
blur = Image.fromarray(u8(np.tile(lum, (3, 3)))).filter(ImageFilter.GaussianBlur(2))
h = np.asarray(blur, dtype=float)[1024:2048, 1024:2048] / 255
lo, hi = np.percentile(h, [1, 99])
h = np.clip((h - lo) / (hi - lo), 0, 1)
Image.fromarray(np.rint(h * 65535).astype(np.uint16)).save(source / 'height.png')
print('Editable 1024x sources authored.')
