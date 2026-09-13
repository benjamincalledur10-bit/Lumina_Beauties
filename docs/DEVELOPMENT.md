# v1a-alpha.2 — piedra y troncos de roble

Minecraft Java **1.21.11**, formato de recursos **75.0**, ediciones **64x y 128x**. Tag público `v1a-alpha.2`; versión interna `0.0.1-alpha.2`, siguiendo la convención de alpha.1. Se reemplazan `stone`, `oak_log` y `oak_log_top`. Los modelos vanilla reutilizan la corteza también en `oak_wood`. Tablones, madera sin corteza y otras especies siguen pendientes.

## Generar ambos ZIP

Python 3.10+:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python tools/build.py
```

En Windows utiliza `.venv\Scripts\python.exe`. El build exporta, valida y genera vistas previas:

- `dist/Lumina-Beauties-0.0.1-alpha.2-Java-1.21.11-64x.zip`
- `dist/Lumina-Beauties-0.0.1-alpha.2-Java-1.21.11-128x.zip`
- `dist/SHA256SUMS`
- `build/Lumina-Beauties-…-{64,128}x/`: carpetas instalables.
- `previews/{stone,oak_log,oak_log_top}-{64,128}x-3x3.png`: repetición sin iluminación añadida.
- `previews/{stone,oak_log,oak_log_top}-{64,128}x-maps.png`: canales separados.
- `previews/relief-{64,128}x.png`: diagnóstico de normales con dos luces opuestas, **fuera de Minecraft y sin parallax**.
- `previews/validation.json`: resultados y hashes.

Validar sin exportar: `.venv/bin/python tools/validate.py`.
Pruebas: `.venv/bin/python -m unittest discover -s tests -v`.
Los ZIP usan una lista explícita de archivos, orden y fechas fijas. Son reproducibles con las mismas fuentes y entorno; no se garantiza identidad entre versiones de Python/zlib o plataformas. Dependencias fijadas en `requirements.txt`; salidas y entorno excluidos de Git.

## Fuentes editables y cambios de alpha.2

Cada carpeta `sources/<material>/` conserva:

- `generated-original.png`: color original creado con la herramienta integrada imagegen.
- `generated-height.png`: edición generada usando ese color como referencia para describir las alturas, sin convertir simplemente su luminancia.
- `prompt.txt`: ambos encargos exactos y procedencia.
- `albedo.png`: maestro RGB 1024².
- `height.png`: maestro gris de 16 bits, 1024², editable independientemente.
- `material.json`: profundidad, AO, reflectancia, porosidad y suavidad.

Son materiales originales inspirados en las referencias de Benji; la fotografía de los troncos no se incorpora al pack. Las alturas son interpretaciones artísticas, no escaneos medidos: la alineación de las formas principales se revisa visualmente y los detalles finos pueden necesitar correcciones tras probarlos. Convertir la fuente generada a 16 bits conserva el formato de edición; no inventa precisión adicional.

La piedra cambia de manchas de poco contraste a placas fracturadas con grietas legibles. Se elimina la compresión global de contraste de alpha.1. La corteza tiene surcos verticales y escamas; el corte transversal tiene anillos y fisuras finas, con relieve mucho menor que la corteza.

`tools/author_sources.py` normaliza tamaño y corrige el salto de borde mediante descomposición periódica. Reconstrucción explícita, **descarta ediciones de maestros**: `.venv/bin/python tools/author_sources.py --overwrite`. El build normal nunca sobrescribe fuentes. Ambos tamaños se reducen directamente desde los maestros; el color se filtra en luz lineal y todos los canales usan filtrado periódico. Las texturas pueden conservar algo de sombreado aparente de la generación; revisarlo con luz opuesta en juego.

## Material y validación

Asignación [LabPBR 1.3](https://shaderlabs.org/wiki/LabPBR_Material_Standard): `_n` guarda normal X/Y DirectX, AO en B y altura en A; `_s` guarda suavidad perceptual, F0, porosidad y 255 para ausencia de emisión. Normales calculadas por resolución desde la altura cuantizada, con derivadas periódicas. Sin metales ni SSS.

| Material | Altura codificada (rango permitido) | Profundidad máxima teórica | AO | Suavidad |
| --- | --- | --- | --- | --- |
| Piedra | 155–255 | 0.098 bloques | 0.72–1 | 0.10–0.22 |
| Corteza | 135–255 | 0.118 bloques | 0.66–1 | 0.08–0.18 |
| Corte transversal | 230–255 | 0.025 bloques | 0.88–1 | 0.14–0.25 |

Son límites; los píxeles exportados no necesariamente alcanzan ambos extremos. F0 es 10/255; porosidad 18/64 para piedra y 12/64 para madera. La profundidad efectiva depende de la escala del shader. POM simula relieve; no cambia la geometría ni la colisión del bloque.

Cada ZIP contiene exactamente **12 archivos**: `pack.mcmeta`, `pack.png`, `LICENSE` y los tres PNG de cada material en `assets/minecraft/textures/block/`. Usa los modelos originales. La licencia se conserva byte por byte; README solo actualiza el estado del desarrollo.

[Mojang especifica recursos 75.0 para Java 1.21.11](https://www.minecraft.net/en-us/article/minecraft-java-edition-1-21-11); metadatos `min_format`/`max_format` `[75,0]`. No se declara compatibilidad con 26.2.

La validación comprueba dimensiones/modos PNG, canales, reconstrucción Z, correspondencia altura/normal, saltos de borde, metadatos, CRC, contenido exacto y licencia. El salto medio del borde debe ser menor que dos veces las diferencias interiores. Este criterio no certifica la estética: una única textura repetida conserva motivos reconocibles.

## Prueba en Minecraft — pendiente de Benji

1. Copia **un solo ZIP** de alpha.2 sin descomprimir en `resourcepacks` de Java 1.21.11. Desactiva alpha.1 y coloca alpha.2 encima de otros packs que cambien piedra o roble. Recarga con F3+T.
2. Comprueba nombre, resolución, ausencia de aviso de incompatibilidad y ausencia de texturas moradas/negras. Sin shader revisa color y repetición en pared/suelo de piedra 8×8 y columnas de roble.
3. Prueba troncos orientados en X, Y y Z, extremos cortados y bloques `oak_wood`. Revisa que la corteza siga el eje del tronco y no haya cortes duros entre bloques.
4. En **Event Horizon 1.3.81**, selecciona **RP Support → labPBR (RP Required)** (`RP_MODE=3`). Su código tiene **Integrated PBR+** (`RP_MODE=1`) como valor predeterminado; activar el shader por sí solo no selecciona los mapas externos.
5. En los ajustes de materiales/PBR personalizados activa **Parallax Occlusion Mapping**. Empieza con **POM Depth 0.80**, **POM Quality 128**, **POM Distance 32** y **Normal Map Strength 1.00**. Estos nombres y opciones se verificaron leyendo el ZIP instalado; no se comprobó su ejecución ni tu configuración activa. Otras versiones pueden cambiar el menú.
6. Compara POM apagado/encendido a 1–4 bloques y con cámara rasante. Las grietas y surcos deben hundirse; el corte transversal debe ser mucho más plano. Cambia hora del día y orientación de luz; busca relieve invertido, ruido brillante, grietas demasiado profundas o bordes abiertos. Prueba también lluvia.
7. Repite con la otra resolución, misma escena y ajustes. Registra versión de Iris/shader, PBR/POM, capturas, FPS y `logs/latest.log` si falla. Lumina Lite requiere su propia comprobación; no se asume soporte idéntico.

La inspección estática de Event Horizon confirma código para LabPBR y POM, **no compatibilidad probada en juego**. Apariencia final, rendimiento y compatibilidad quedan pendientes de tu prueba.
