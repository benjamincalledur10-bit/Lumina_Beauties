# 0.0.1-alpha.1 — prototipo local de piedra

Objetivo: Minecraft Java 1.21.11, ediciones 64x y 128x. Solo se reemplaza `minecraft:block/stone`; dirt y oak planks siguen pendientes. No hay publicación ni compatibilidad con shaders certificada.

## Generar y validar

Requiere Python 3.10 o posterior. Desde la raíz del repositorio:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python tools/build.py
```

El último comando exporta ambas ediciones y valida los archivos. En Windows, sustituye `.venv/bin/python` por `.venv\Scripts\python.exe`.

Salidas:

- `dist/Lumina-Beauties-0.0.1-alpha.1-Java-1.21.11-64x.zip`
- `dist/Lumina-Beauties-0.0.1-alpha.1-Java-1.21.11-128x.zip`
- `dist/SHA256SUMS`
- `build/Lumina-Beauties-…-{64,128}x/`: carpetas instalables exportadas.
- `previews/stone-{64,128}x-3x3.png`: repetición 3 × 3, ampliada con vecino más cercano.
- `previews/stone-{64,128}x-maps.png`: canales separados para inspección.
- `previews/validation.json`: resultado técnico, métricas de bordes y hashes.

Validación sin regenerar: `.venv/bin/python tools/validate.py`.
Pruebas del procesamiento: `.venv/bin/python -m unittest discover -s tests -v`.
Los ZIP tienen rutas explícitas, orden y fechas fijas. Dos ejecuciones con las mismas fuentes y entorno deben producir los mismos bytes. Las dependencias están fijadas; no se garantiza identidad binaria entre distintas versiones de Python/zlib o plataformas. `build/`, `dist/` y `.venv/` se excluyen de Git.

## Fuentes y estructura

`sources/stone/generated-original.png` conserva la salida original de la herramienta integrada imagegen; `prompt.txt` conserva el encargo exacto. Se generó una composición nueva de roca gris estratificada, inspirada visualmente en la referencia aportada por Benji. No se incorporaron píxeles de esa fotografía ni de Minecraft a las texturas.

`sources/stone/albedo.png` (RGB, 1024²) y `height.png` (gris de 16 bits, 1024²) son los maestros editables en cualquier editor que conserve esos formatos. `material.json` contiene los parámetros del material. El build lee esos maestros y nunca los sobrescribe. Ambos tamaños se filtran directamente desde 1024², con filtrado periódico; el albedo se reduce en luz lineal.

`tools/author_sources.py` documenta la transformación inicial: descomposición periódica para suavizar el salto entre bordes, compresión de contraste y estimación de altura desde luminancia suavizada. La altura es una aproximación artística, no una medición física; puede interpretar alguna variación mineral como relieve. Se conserva separada para corregirla a mano. La fuente generada puede retener indicios de iluminación, cuyo impacto debe evaluarse en juego. Para descartar ediciones y reconstruir los maestros explícitamente: `.venv/bin/python tools/author_sources.py --overwrite`.

Cada ZIP contiene exactamente:

```text
pack.mcmeta
pack.png
LICENSE
assets/minecraft/textures/block/stone.png
assets/minecraft/textures/block/stone_n.png
assets/minecraft/textures/block/stone_s.png
```

No necesita modelos personalizados: usa los modelos originales del juego. El icono es un recorte representativo de la propia textura. La licencia incluida es una copia byte por byte de la existente.

## Convenciones del material

Se siguen las asignaciones de [LabPBR 1.3, shaderLABS](https://shaderlabs.org/wiki/LabPBR_Material_Standard):

| Archivo | R | G | B | A |
| --- | --- | --- | --- | --- |
| `stone.png` | Color sRGB | Color sRGB | Color sRGB | Sin alfa; opaco |
| `stone_n.png` | Normal X | Normal Y, DirectX | AO | Altura |
| `stone_s.png` | Suavidad perceptual | F0 | Porosidad | 255, sin emisión |

Los datos PBR se empaquetan sin corrección gamma. Las normales se recalculan por resolución desde la altura ya cuantizada, con derivadas que atraviesan los bordes y escala constante en unidades de bloque. El signo usa X hacia la derecha e Y hacia abajo. Z se reconstruye en el shader.

Valores iniciales: altura 218–255 (profundidad máxima aproximada de 0.036 bloques bajo la escala LabPBR); AO 0.88–1; suavidad 0.12–0.20; F0 10/255; porosidad 18/64. Sin metales, SSS ni emisión. Son elecciones artísticas conservadoras, ajustables tras la prueba.

[Mojang indica formato de recursos 75.0 para 1.21.11](https://www.minecraft.net/en-us/article/minecraft-java-edition-1-21-11). `pack/pack.mcmeta` declara `min_format` y `max_format` como `[75, 0]`, según el [esquema introducido en 1.21.9](https://www.minecraft.net/en-us/article/minecraft-java-edition-1-21-9). No se declara soporte 26.2.

La validación revisa PNG, dimensiones, canales, reconstrucción de normales, correspondencia altura/normal, gradientes de borde, estructura y CRC de ZIP, y licencia. El promedio del salto de borde debe ser menor que dos veces el promedio de diferencias interiores. Es una detección de discontinuidades, no una garantía estética: un motivo puede seguir siendo reconocible al repetirse.

## Prueba manual en Minecraft — pendiente de Benji

1. Abre la instancia **Java 1.21.11**. En Opciones → Paquetes de recursos → Abrir carpeta, copia uno de los ZIP sin descomprimir. Actívalo con prioridad sobre otros packs que modifiquen stone. Prueba cada resolución por separado.
2. Comprueba que aparece el nombre y tamaño correctos, que no hay aviso de versión incompatible y que stone no muestra cuadros morados/negros. Empieza sin shader para revisar color y repetición.
3. En un mundo creativo de prueba, construye pared y suelo de piedra de al menos 8 × 8 bloques, una esquina y varios bloques aislados. Inspecciona caras superiores/laterales, a 1, 4 y 16 bloques, y con distintos niveles de mipmaps. Busca líneas de unión, repetición demasiado evidente y pérdida de detalle.
4. Activa Event Horizon y después Lumina Lite, si tienes versiones que funcionen en esa instancia. Anota versión exacta del shader y cargador. Habilita LabPBR y, si existe, parallax/POM; los nombres de las opciones dependen del shader.
5. Compara PBR desactivado/activado, iluminación frontal/rasante, mañana/mediodía/noche y seco/lluvia. Las grietas deberían hundirse; la piedra debe permanecer mate, sin brillo metálico ni emisión. Revisa relieve invertido, bordes que se abren con POM y reflejos excesivos.
6. Cambia al otro ZIP, recarga recursos (F3+T) y repite con la misma escena y ajustes. Si hay problemas, guarda captura y `logs/latest.log`, con resolución, shader, ajustes PBR/POM y pasos para reproducirlos.

Estado: archivos y previsualizaciones revisados fuera del juego. Carga real, apariencia, rendimiento y compatibilidad de ambos shaders **pendientes de prueba en Minecraft**.

## Verificación de esta preparación

Se ejecutaron las cuatro pruebas de procesamiento y el build completo con Python 3.12, NumPy 2.2.6 y Pillow 11.3.0. Dos builds consecutivos produjeron los mismos SHA-256. Se inspeccionaron las vistas 3 × 3 y los canales de ambas resoluciones. No se observaron cortes duros en los bordes; el motivo sigue siendo reconocible como repetición de una sola textura.
