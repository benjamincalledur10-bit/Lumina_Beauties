Piedra renovada y troncos de roble para **Minecraft Java 1.21.11**, en **64x y 128x**.

- Piedra con fracturas más definidas, detalle mineral y un rango de profundidad mayor.
- Corteza de roble con surcos verticales, más extremos cortados con anillos de crecimiento y relieve suave.
- Fuentes originales de color y altura separadas; mapas LabPBR de normales, altura, AO y propiedades por material.
- Herramienta única para generar ambas ediciones: `python tools/build.py` tras instalar `requirements.txt`.
- Validación de los 12 archivos de cada ZIP, metadatos 75.0, PNG, canales, normales/altura, continuidad de bordes, CRC y licencia. Cuatro pruebas de procesamiento aprobadas; ZIP reproducibles en el entorno usado.

**Instalación:** descarga un ZIP, colócalo sin descomprimir en `resourcepacks`, desactiva alpha.1 y activa alpha.2 con prioridad. Prueba cada resolución por separado.

**Para el relieve en Event Horizon 1.3.81:** selecciona **RP Support → labPBR (RP Required)** y activa **Parallax Occlusion Mapping**. Inicio sugerido: POM Depth 0.80, Quality 128, Distance 32 y Normal Map Strength 1.00. El modo predeterminado Integrated PBR+ no selecciona estos mapas externos. Opciones verificadas en el código del shader instalado; ejecución pendiente de prueba.

[Instrucciones completas](https://github.com/benjamincalledur10-bit/Lumina_Beauties/blob/v1a-alpha.2/docs/DEVELOPMENT.md) · [Piedra repetida 128x](https://github.com/benjamincalledur10-bit/Lumina_Beauties/blob/v1a-alpha.2/previews/stone-128x-3x3.png) · [Corteza repetida 128x](https://github.com/benjamincalledur10-bit/Lumina_Beauties/blob/v1a-alpha.2/previews/oak_log-128x-3x3.png) · [Diagnóstico de relieve fuera del juego](https://github.com/benjamincalledur10-bit/Lumina_Beauties/blob/v1a-alpha.2/previews/relief-128x.png)

Apariencia, rendimiento y compatibilidad con shaders **pendientes de la prueba de Benji en Minecraft**. POM no modifica geometría ni colisiones. La madera implementada es roble con corteza y extremos; tablones, troncos sin corteza y otras especies siguen pendientes.

Tag público: `v1a-alpha.2`. Versión interna de los ZIP: `0.0.1-alpha.2`. Publicado desde `luminabeautiesdev`; licencia existente conservada.
