"""Build and validate both installable editions from preserved editable masters."""
from pathlib import Path
import hashlib
import json
import zipfile
import numpy as np
from PIL import Image, ImageDraw
from material import export_maps

ROOT = Path(__file__).resolve().parents[1]
TEXTURES = 'assets/minecraft/textures/block'


def build():
    source = ROOT / 'sources/stone'
    settings = json.loads((source / 'material.json').read_text())
    color = np.asarray(Image.open(source / 'albedo.png').convert('RGB')) / 255.
    height = np.asarray(Image.open(source / 'height.png'), dtype=float) / 65535
    if color.shape != (1024, 1024, 3) or height.shape != (1024, 1024):
        raise ValueError('Editable masters must be 1024x1024')
    dist = ROOT / 'dist'
    dist.mkdir(exist_ok=True)
    (ROOT / 'previews').mkdir(exist_ok=True)
    checksums = []
    for size in (64, 128):
        name = f'Lumina-Beauties-{settings["version"]}-Java-{settings["minecraft"]}-{size}x'
        folder = ROOT / 'build' / name
        textures = folder / TEXTURES
        textures.mkdir(parents=True, exist_ok=True)
        maps = export_maps(color, height, settings, size)
        for filename, pixels in maps.items():
            Image.fromarray(pixels).save(textures / filename)
        meta = (ROOT / 'pack/pack.mcmeta').read_text().replace('{resolution}', str(size))
        (folder / 'pack.mcmeta').write_text(meta)
        (folder / 'LICENSE').write_bytes((ROOT / 'LICENSE').read_bytes())
        Image.fromarray(maps['stone.png']).resize((128, 128), Image.Resampling.NEAREST).save(folder / 'pack.png')
        # Explicit allowlist prevents stale or private files leaking into packages.
        entries = ['pack.mcmeta', 'pack.png', 'LICENSE'] + [f'{TEXTURES}/{n}' for n in maps]
        archive = dist / f'{name}.zip'
        with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for entry in sorted(entries):
                info = zipfile.ZipInfo(entry, date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                z.writestr(info, (folder / entry).read_bytes())
        checksums.append(f'{hashlib.sha256(archive.read_bytes()).hexdigest()}  {archive.name}')
        tile = Image.fromarray(np.tile(maps['stone.png'], (3, 3, 1)))
        tile.resize((768, 768), Image.Resampling.NEAREST).save(ROOT / f'previews/stone-{size}x-3x3.png')
        # Channels are displayed separately; packed alpha is material data, not opacity.
        n, s = maps['stone_n.png'], maps['stone_s.png']
        panels = [maps['stone.png'], np.dstack((n[..., :2], np.full((size,size),255,np.uint8))), n[...,3], n[...,2], s[...,0]]
        board = Image.new('RGB', (1280, 292), '#20252b')
        draw = ImageDraw.Draw(board)
        for i, (pixels, label) in enumerate(zip(panels, ['Albedo', 'Normal XY (DX)', 'Height', 'AO', 'Smoothness'])):
            board.paste(Image.fromarray(pixels).convert('RGB').resize((256,256), Image.Resampling.NEAREST), (i*256,36))
            draw.text((i*256+10,10), f'{size}x | {label}', fill='white')
        board.save(ROOT / f'previews/stone-{size}x-maps.png')
        print(archive.relative_to(ROOT))
    (dist / 'SHA256SUMS').write_text('\n'.join(checksums) + '\n')
    from validate import validate
    validate()


if __name__ == '__main__':
    build()
