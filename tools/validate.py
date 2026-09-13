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
    settings = json.loads((ROOT/'pack/release.json').read_text())
    for size in (64, 128):
        path = ROOT / 'dist' / f'Lumina-Beauties-{settings["version"]}-Java-{settings["minecraft"]}-{size}x.zip'
        prefix = 'assets/minecraft/textures/block/'
        expected = {'pack.mcmeta', 'pack.png', 'LICENSE', *(prefix+n for n in [m+suffix+'.png' for m in settings['materials'] for suffix in ('','_n','_s')])}
        with zipfile.ZipFile(path) as z:
            require(set(z.namelist()) == expected and len(z.namelist()) == len(expected), 'Wrong ZIP structure')
            require(z.testzip() is None, 'ZIP CRC failure')
            require(z.read('LICENSE') == (ROOT/'LICENSE').read_bytes(), 'Pack license mismatch')
            meta = json.loads(z.read('pack.mcmeta'))['pack']
            require(meta['min_format'] == [75,0] == meta['max_format'], 'Wrong target format')
            require('supported_formats' not in meta and '{resolution}' not in meta['description'], 'Invalid metadata')
            require(str(size)+'x' in meta['description'] and settings['version'] in meta['description'], 'Wrong edition description')
            maps = {}
            for name, mode in [(m+suffix+'.png', 'RGB' if not suffix else 'RGBA') for m in settings['materials'] for suffix in ('','_n','_s')]:
                data = z.read(prefix+name)
                with Image.open(io.BytesIO(data)) as im:
                    im.verify()
                with Image.open(io.BytesIO(data)) as im:
                    require(im.size == (size,size) and im.mode == mode, f'Invalid PNG {name}')
                    maps[name] = np.array(im)
            with Image.open(io.BytesIO(z.read('pack.png'))) as im:
                require(im.size == (128,128), 'Invalid pack icon')
        for material in settings['materials']:
            params = json.loads((ROOT/'sources'/material/'material.json').read_text())
            n, s = maps[material+'_n.png'], maps[material+'_s.png']
            xy = n[...,:2].astype(float)/127.5 - 1
            require(np.all(np.sum(xy*xy,axis=-1) < 1), 'Normals cannot reconstruct Z')
            require(n[...,3].min() >= max(1,params['height_min']) and n[...,3].max() <= params['height_max'] and np.ptp(n[...,3]) > 0, 'Invalid height')
            require(n[...,2].min() >= round(255*(1-params['ao_strength'])), 'Excessive AO')
            require(np.all(s[...,1] == 10), 'Material F0 must be dielectric ~4%')
            require(np.all(s[...,2] <= 64) and np.all(s[...,3] == 255), 'Material must not have SSS/emission')
            require(s[...,0].min() >= round(params['smoothness_min']*255) and s[...,0].max() <= round(params['smoothness_max']*255), 'Smoothness out of range')
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
