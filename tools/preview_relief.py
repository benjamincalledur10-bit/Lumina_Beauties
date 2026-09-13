"""Offline diffuse-light diagnostic of exported normals, not a Minecraft/POM render."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw
from material import linear, srgb, u8

ROOT = Path(__file__).resolve().parents[1]

def preview():
    release = json.loads((ROOT/'pack/release.json').read_text())
    for size in (64,128):
        folder = ROOT/'build'/f'Lumina-Beauties-{release["version"]}-Java-{release["minecraft"]}-{size}x'/'assets/minecraft/textures/block'
        board = Image.new('RGB',(1152,1280),'#20252b')
        draw = ImageDraw.Draw(board)
        draw.text((16,12),f'Lumina Beauties {release["tag"]} | {size}x | OFFLINE NORMAL TEST - NOT MINECRAFT / NO POM',fill='white')
        for row,name in enumerate(release['materials']):
            color = np.asarray(Image.open(folder/f'{name}.png'))/255.
            n = np.asarray(Image.open(folder/f'{name}_n.png'))/255.
            xy = n[...,:2]*2-1
            normal = np.dstack((xy,np.sqrt(np.maximum(0,1-np.sum(xy*xy,axis=-1)))))
            variants = [color]
            for direction in ((-.8,-.3,.5),(.8,.3,.5)):
                light = np.asarray(direction); light /= np.linalg.norm(light)
                diffuse = np.maximum(0,np.sum(normal*light,axis=-1))
                variants.append(srgb(linear(color)*(.30+.95*diffuse[...,None])*n[...,2,None]))
            for col,(pixels,label) in enumerate(zip(variants,['Albedo 3x3','Light from left','Light from right'])):
                y=44+row*410
                draw.text((col*384+12,y),f'{name} | {label}',fill='white')
                tile=Image.fromarray(u8(np.tile(pixels,(3,3,1))))
                board.paste(tile.resize((384,384),Image.Resampling.NEAREST),(col*384,y+16))
        board.save(ROOT/f'previews/relief-{size}x.png')

if __name__=='__main__':
    preview()
