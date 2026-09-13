"""Rebuild editable masters from preserved generated color and separate relief sources."""
from pathlib import Path
import argparse
import json
import numpy as np
from PIL import Image
from material import periodic, u8

ROOT = Path(__file__).resolve().parents[1]

def author(overwrite=False):
    materials = json.loads((ROOT/'pack/release.json').read_text())['materials']
    for name in materials:
        source = ROOT/'sources'/name
        if not overwrite and any((source/n).exists() for n in ('albedo.png','height.png')):
            raise ValueError('Masters exist; --overwrite discards artist edits.')
    for name in materials:
        source = ROOT/'sources'/name
        a = np.asarray(Image.open(source/'generated-original.png').convert('RGB').resize((1024,1024), Image.Resampling.LANCZOS))/255.
        a = np.stack([periodic(a[...,c]) for c in range(3)], -1)
        # Preserve material contrast: alpha.1's global contrast compression is removed.
        Image.fromarray(u8(a)).save(source/'albedo.png')
        h = np.asarray(Image.open(source/'generated-height.png').convert('L').resize((1024,1024), Image.Resampling.LANCZOS))/255.
        h = np.clip(periodic(h),0,1)
        Image.fromarray(np.rint(h*65535).astype(np.uint16)).save(source/'height.png')
    print('Authored separate editable color and 16-bit height masters.')

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--overwrite', action='store_true')
    author(p.parse_args().overwrite)
