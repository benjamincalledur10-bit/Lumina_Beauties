"""Shared linear-light, periodic material operations. Image y points downward."""
import numpy as np
from PIL import Image


def u8(a):
    return np.rint(np.clip(a, 0, 1) * 255).astype(np.uint8)


def linear(a):
    return np.where(a <= .04045, a / 12.92, ((a + .055) / 1.055) ** 2.4)


def srgb(a):
    a = np.clip(a, 0, 1)
    return np.where(a <= .0031308, a * 12.92, 1.055 * a ** (1 / 2.4) - .055)


def periodic(a):
    """Periodic-plus-smooth decomposition; remove boundary mismatch without mirroring."""
    h, w = a.shape
    v = np.zeros_like(a)
    v[0] = a[-1] - a[0]
    v[-1] = -v[0]
    v[:, 0] += a[:, -1] - a[:, 0]
    v[:, -1] -= a[:, -1] - a[:, 0]
    yy, xx = np.meshgrid(np.arange(h), np.arange(w), indexing='ij')
    denom = 2 * np.cos(2 * np.pi * xx / w) + 2 * np.cos(2 * np.pi * yy / h) - 4
    denom[0, 0] = 1
    spectrum = np.fft.fft2(v) / denom
    spectrum[0, 0] = 0
    return a - np.fft.ifft2(spectrum).real


def resize_wrap(a, size):
    """Filter a repeated 3x3 field, keeping its central tile (no edge clamping)."""
    if a.ndim == 3:
        return np.stack([resize_wrap(a[..., c], size) for c in range(a.shape[2])], -1)
    tiled = Image.fromarray(np.tile(a, (3, 3)).astype(np.float32))
    return np.asarray(tiled.resize((size * 3, size * 3), Image.Resampling.LANCZOS))[size:2*size, size:2*size]


def normals(height):
    # LabPBR height spans 0.25 blocks. Derivatives use block units, not pixel units.
    scale = height.shape[0] * .25 / 2
    dx = (np.roll(height, -1, 1) - np.roll(height, 1, 1)) * scale
    dy = (np.roll(height, -1, 0) - np.roll(height, 1, 0)) * scale
    n = np.stack((-dx, -dy, np.ones_like(dx)), -1)
    return n / np.linalg.norm(n, axis=-1, keepdims=True)


def export_maps(color, height, settings, size, name="stone"):
    albedo = u8(srgb(resize_wrap(linear(color), size)))
    h = np.clip(resize_wrap(height, size), 0, 1)
    # Quantize height first: normal field agrees with the actual shipped alpha.
    encoded = np.rint(settings['height_min'] + h * (settings['height_max'] - settings['height_min'])).astype(np.uint8)
    n = normals(encoded.astype(float) / 255)
    ao = u8(1 - settings['ao_strength'] * (1 - h))
    normal = np.dstack((u8(n[..., :2] * .5 + .5), ao, encoded))
    smooth = settings['smoothness_min'] + h * (settings['smoothness_max'] - settings['smoothness_min'])
    spec = np.dstack((u8(smooth), np.full(h.shape, round(settings['f0'] * 255), np.uint8),
                     np.full(h.shape, round(settings['porosity'] * 64), np.uint8),
                     np.full(h.shape, 255, np.uint8)))
    return {f'{name}.png': albedo, f'{name}_n.png': normal, f'{name}_s.png': spec}
