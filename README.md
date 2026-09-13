# ✨ Lumina Beauties

**Natural materials. Rich detail. A world worth exploring.**

Lumina Beauties is an original resource pack in development for **Minecraft: Java Edition**, with planned **64x** and **128x** editions. Its goal is to bring natural surfaces, convincing material depth, and a consistent visual identity to Minecraft while keeping its blocks recognizable.

Designed with **Lumina Event Horizon** and **Lumina Lite** in mind, Lumina Beauties will be the material and texture companion to the **Lumina Realism** modpack.

> **Project status: initial development.** Both editions, their material maps, and shader compatibility are development goals. No playable release or completed texture coverage is announced yet.

## 🌿 The visual direction

Stone should feel weathered, soil should feel earthy, and wood should show grain, wear, and character. Lumina Beauties aims to make those differences visible through carefully authored textures and material properties.

- **Natural color:** a coherent palette that works across landscapes and builds.
- **Believable surfaces:** detail shaped around each material rather than a uniform layer of noise.
- **Clean repetition:** textures that join naturally across larger walls, floors, and terrain.
- **Responsive lighting:** surface color without painted directional shadows or highlights, so the shader can provide the lighting.
- **Recognizable blocks:** enough continuity with Minecraft to keep building and exploration intuitive.

## 🖼️ Planned editions

| Edition | Texture resolution | Intended role | Status |
| --- | --- | --- | --- |
| **Lumina Beauties 64x** | 64 × 64 per block texture | Base edition with a smaller texture memory footprint | Planned |
| **Lumina Beauties 128x** | 128 × 128 per block texture | Higher-resolution edition for additional surface detail | Planned |

Both editions will share the same art direction and material sources. The 128x edition is intended to preserve additional source detail, rather than simply enlarge the 64x images.

Actual performance will depend on the shader, enabled effects, hardware, and other installed content. Performance comparisons will be published once playable builds have been tested.

## 💡 Material design

The planned material workflow follows the LabPBR material standard:

- **Base color** for the visible surface texture.
- **Normal and height information** for surface relief and shader-supported parallax effects.
- **Material properties** for appropriate reflectance, smoothness, and other supported effects.

Each material will receive properties that suit its surface. Features such as emission, metal response, or subsurface scattering will be used only where appropriate.

The final appearance depends on the shader's implementation and settings. PBR and parallax support will be verified in-game before being listed as tested compatibility.

## 🌌 Part of the Lumina ecosystem

| Project | Role |
| --- | --- |
| **Lumina Beauties** | Original textures and material maps |
| Lumina Event Horizon | Shader project and intended visual testing target |
| Lumina Lite | Shader project focused on a lighter rendering experience |
| Lumina Engine | Performance measurements, diagnostics, and manual tuning guidance |
| **Lumina Realism** | The planned modpack bringing the experience together |

Automatic texture-resolution selection through Lumina Engine is not implemented.

## 🧱 First prototype

The proposed first milestone is **0.0.1-alpha.1**, initially targeting **Minecraft Java 1.21.11** with three materials:

| Material | Initial focus |
| --- | --- |
| **Stone** | Natural variation and restrained surface relief |
| **Dirt** | Earthy color, granularity, and a matte finish |
| **Oak planks** | Wood grain, plank definition, and subtle wear |

The prototype will be used to assess repetition, material consistency, and appearance at different viewing distances in both resolutions. Testing with Event Horizon and Lumina Lite will guide further adjustments.

Minecraft **26.2** is a later compatibility target; support will be documented after validation.

## 🛠️ Development

- **`luminabeautiesdev`** — planned working branch for textures, tooling, and experiments.
- **`main`** — intended home for reviewed release milestones.

Editable material sources will be preserved so both editions can be exported consistently. Packaging tools and their exact commands will be documented as they are implemented.

Before a prototype is considered ready, its metadata, texture dimensions, material maps, ZIP structure, and in-game appearance must be checked.

## 📦 Downloads

There is no playable download announced yet. Installation instructions and tested configurations will accompany the first available build.

## 📄 License

Lumina Beauties is distributed under the [Lumina Beauties Resource Pack License, Version 1.0](LICENSE). See the license for the full terms covering both the 64x and 128x editions.

---

Created by **Benji** · Part of the **Lumina** ecosystem.

*Not an official Minecraft product. Not approved by or associated with Mojang or Microsoft.*
