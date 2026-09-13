"""Independent archive and material checks; no Minecraft/shader runtime claims."""
from pathlib import Path
import hashlib
import io
import json
import zipfile
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
LICENSE_SHA = '325d9e0370a09d811da619461bd7c8d0f3dfe6a898721b02f6092642b806278c'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate():
    require(hashlib.sha256((ROOT/'LICENSE').read_bytes()).hexdigest() == LICENSE_SHA, 'Existing license changed')
    report = {'status': 'PASS', 'runtime': 'Minecraft and shaders NOT tested', 'editions': {}}
    settings = json.loads((ROOT/'sources/stone/material.json').read_text())
    for size in (64, 128):
        path = ROOT / 'dist' / f'Lumina-Beauties-{settings["version"]}-Java-{settings["minecraft"]}-{size}x.zip'
        prefix = 'assets/minecraft/textures/block/'
        expected = {'pack.mcmeta', 'pack.png', 'LICENSE', *(prefix+n for n in ['stone.png','stone_n.png','stone_s.png'])}
        with zipfile.ZipFile(path) as z:
            require(set(z.namelist()) == expected and len(z.namelist()) == len(expected), 'Wrong ZIP structure')
            require(z.testzip() is None, 'ZIP CRC failure')
            require(z.read('LICENSE') == (ROOT/'LICENSE').read_bytes(), 'Pack license mismatch')
            meta = json.loads(z.read('pack.mcmeta'))['pack']
            require(meta['min_format'] == [75,0] == meta['max_format'], 'Wrong target format')
            require('supported_formats' not in meta and '{resolution}' not in meta['description'], 'Invalid metadata')
            require(str(size)+'x' in meta['description'] and settings['version'] in meta['description'], 'Wrong edition description')
            maps = {}
            for name, mode in [('stone.png','RGB'), ('stone_n.png','RGBA'), ('stone_s.png','RGBA')]:
                data = z.read(prefix+name)
                with Image.open(io.BytesIO(data)) as im:
                    im.verify()
                with Image.open(io.BytesIO(data)) as im:
                    require(im.size == (size,size) and im.mode == mode, f'Invalid PNG {name}')
                    maps[name] = np.array(im)
            with Image.open(io.BytesIO(z.read('pack.png'))) as im:
                require(im.size == (128,128), 'Invalid pack icon')
        n, s = maps['stone_n.png'], maps['stone_s.png']
        xy = n[...,:2].astype(float)/127.5 - 1
        require(np.all(np.sum(xy*xy,axis=-1) < 1), 'Normals cannot reconstruct Z')
        require(n[...,3].min() >= 1 and n[...,3].max() > n[...,3].min(), 'Invalid height')
        require(n[...,2].min() >= 220, 'Excessive AO')
        require(np.all(s[...,1] == 10), 'Stone F0 must be dielectric ~4%')
        require(np.all(s[...,2] <= 64) and np.all(s[...,3] == 255), 'Stone must not have SSS/emission')
        require(s[...,0].min() >= 30 and s[...,0].max() <= 52, 'Stone too glossy')
        # Independent finite-difference check of signs and relief scale, including wrap.
        h = n[...,3].astype(float)/255
        dx = (np.roll(h,-1,1)-np.roll(h,1,1))*size*.125
        dy = (np.roll(h,-1,0)-np.roll(h,1,0))*size*.125
        length = np.sqrt(1+dx*dx+dy*dy)
        require(np.max(np.abs(xy - np.stack((-dx/length,-dy/length),-1))) <= 1/255 + 1e-6, 'Normal/height mismatch')
        seams = {}
        for name, a in maps.items():
            a = a.astype(float)
            ratios = []
            for axis in (0,1):
                inside = np.abs(np.diff(a,axis=axis)).mean()
                edge = np.abs(np.take(a,0,axis=axis)-np.take(a,-1,axis=axis)).mean()
                ratio = edge/max(inside,.01)
                require(ratio < 2, f'Boundary discontinuity: {size} {name} axis {axis}: {ratio:.2f}')
                ratios.append(round(ratio,3))
            seams[name] = {'wrap_to_internal_mean_y_x': ratios}
        report['editions'][str(size)] = {'files':len(expected), 'seams':seams, 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    (ROOT/'previews/validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: metadata, PNGs, LabPBR channels, wrap gradients, ZIP contents/CRC and license. Runtime pending.')


if __name__ == '__main__':
    validate()
