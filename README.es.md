# StreamRemaster

**Subtítulos en directo y vídeo fluido para cualquier pestaña del navegador, con tu propio equipo.**

Mira un directo de Twitch, un vídeo de YouTube o una llamada en un idioma que no hablas y
léelo en el tuyo, en tiempo real. El audio no sale de tu red: solo va al servidor
[WhisperLive](https://github.com/collabora/WhisperLive) que tú montes. La pestaña **Vídeo fluido** sube
los fotogramas por segundo del vídeo y lo reescala con IA, en tu propia tarjeta gráfica.

StreamRemaster se llamaba Stream Transcription hasta la versión 2.2.0. Los subtítulos funcionan igual que
antes.

[English version](README.md)

![Subtítulos traducidos sobre un directo](store/screenshot-1-subtitles.png)

## Qué hace

- **Subtítulos encima de cualquier web**: Twitch, YouTube, Kick, cualquier `<video>`… Siguen
  en pantalla completa, se pueden arrastrar, y eliges de 1 a 4 líneas y el tamaño del texto.
- **Traducción**: la del propio Whisper al inglés, o a unos 100 idiomas con el traductor del
  servidor.
- **Cualquier modelo Whisper, desde la extensión**: pega el nombre o el enlace de un modelo de
  Hugging Face (`Systran/faster-whisper-large-v3`, uno ajustado para tu idioma, un `.zip`
  directo…) y el servidor lo descarga; los modelos normales (*transformers*) se convierten
  solos al formato de faster-whisper. Luego lo eliges de una lista. Sin rutas ni terminal.
- **Cabe en gráficas modestas**: la opción «int8» gasta la mitad de memoria con el mismo
  texto, el traductor puede ir en el procesador, y si el modelo no cabe sale un **aviso de
  VRAM** en vez de unos subtítulos que se congelan sin decir nada.
- **Guarda los subtítulos** en un `.srt` al parar.
- **Vídeo fluido**: fotogramas intermedios generados con IA suben los fotogramas por segundo del vídeo
  hasta los de tu pantalla, y el reescalado con IA duplica su resolución. En tu propia tarjeta gráfica y
  sin servidor. [Más abajo](#vídeo-fluido).
- **Busca actualizaciones** desde la extensión: dice si hay una versión más nueva, de la
  extensión y del servidor, y te lleva a ella. Solo cuando lo pides.
- Interfaz en castellano, catalán, gallego, euskera, inglés, portugués, francés, alemán, italiano,
  neerlandés, polaco, ruso, ucraniano, chino, japonés, coreano, tailandés e hindi; sigue al navegador o se elige en los ajustes.
- Sin cuentas, sin rastreo, sin estadísticas. Código fuente disponible (PolyForm Noncommercial).

| Ventana de la extensión | Ajustes · modelos |
|---|---|
| ![Ventana de la extensión](store/screenshot-2-popup.png) | ![Modelos](store/screenshot-3-models.png) |

## Vídeo fluido

La pestaña **Vídeo fluido**, junto a **Subtítulos** en la ventana de la extensión, hace que el vídeo de la
página se vea más fluido y más nítido. Hace dos cosas con IA:

- **Fotogramas intermedios.** Un directo a 30 o 60 fps en una pantalla de 144 Hz muestra cada fotograma
  varias veces. La extensión genera los fotogramas que faltan entre medias, y el vídeo va hasta a los
  fotogramas por segundo de tu pantalla.
- **Reescalado.** Duplica la resolución del vídeo; por ejemplo, de 720p a 1440p.

Todo funciona en el navegador, en tu propia tarjeta gráfica, mediante WebGPU. Esta pestaña no necesita
servidor: funciona sin el servidor WhisperLive, y el vídeo no sale de tu ordenador. Va en Firefox, Zen y
los navegadores Chromium (probado en Brave).

<!-- TODO: captura de la pestaña Vídeo fluido -->

Los controles:

- **El botón grande** lo activa y lo quita en la pestaña actual.
- **FPS objetivo**: **Igual que la pantalla** o un valor fijo: 60, 75, 90, 100, 120, 144, 165, 180 o
  240 fps.
- **Modelo de IA**: **StreamRemaster**, el modelo que trae la extensión; cualquier modelo que hayas
  añadido; o **Ninguno (sin IA)**, que usa un fundido simple entre fotogramas y un escalado simple.
- **Resolución objetivo del reescalado**: **Original (sin reescalar)**, **Igual que la pantalla**, 1080p,
  1440p o 4K.

Mientras está activo, un contador en la página muestra los fotogramas por segundo del vídeo y los que
consigues.

**Modelos.** En Ajustes → **Modelos de vídeo fluido** puedes añadir archivos de modelo (`.stmodel`, y los
antiguos `.srmodel` y `.fimodel`) y elegir uno. El modelo que trae la extensión aparece como **Incluido** y
no se puede borrar. Un archivo de modelo solo contiene pesos, nada de código, y la extensión lo comprueba
con rigor antes de usarlo. Cómo se hizo StreamRemaster, con qué datos y qué límites tiene:
[ficha del modelo](docs/MODEL.es.md).

**Límites.** Necesitas una tarjeta gráfica y un navegador con WebGPU. El reescalado dibuja detalle
verosímil que no estaba en el original, así que no sirve para leer texto pequeño del que tengas que
fiarte. El vídeo protegido (DRM) se ve negro para cualquier extensión y no se puede procesar.

## Instalar la extensión

<!-- TODO: el enlace de AMO, si StreamRemaster tiene una ficha o un ID nuevos; y cómo comprarla en
Chromium, cuando se decida el sistema de pago y licencias. -->
- **Firefox** (y Zen, LibreWolf, Floorp…), gratis: [addons.mozilla.org](https://addons.mozilla.org/firefox/addon/stream-transcription/)
- **Chromium** (Chrome, Brave, Edge, Opera, Vivaldi…): descarga
  `streamremaster-chromium-<versión>.zip` de la
  [última versión](https://github.com/javimentallab/StreamRemaster/releases/latest),
  descomprímelo, abre `chrome://extensions`, activa el **Modo de desarrollador** y pulsa
  **Cargar descomprimida** sobre la carpeta.

**Actualizaciones.** Firefox actualiza solo el complemento desde AMO. En los dos navegadores,
**Buscar actualizaciones** (al pie de la ventana de la extensión o en Ajustes → Acerca de)
pregunta a GitHub cuál es la última versión y, si hay una más nueva, abre la página para
conseguirla: la del complemento en AMO en Firefox, o la de la versión en GitHub en Chromium,
donde se descomprime el zip nuevo encima de la carpeta antigua y se pulsa el icono de recargar
en `chrome://extensions` (los ajustes se conservan). La extensión nunca descarga código ni se
sustituye sola.

Después pulsa el icono de la extensión, escribe la dirección de tu servidor (p. ej.
`192.168.1.10:9090`) y **Conectar**.

## Servidor

Necesitas un servidor WhisperLive, mejor en un ordenador con tarjeta gráfica NVIDIA (los
modelos pequeños también van solo con el procesador). Dos opciones:

### Opción A — servidor de StreamRemaster (recomendada)

WhisperLive más los parches que hacen funcionar todo lo de la extensión (gestión de modelos,
cambio de modelo, int8, traductor en el procesador, avisos de VRAM). Con Docker y el
[NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html):

```sh
git clone https://github.com/javimentallab/StreamRemaster.git
cd StreamRemaster/server
docker compose up -d --build
```

El primer arranque descarga el modelo por defecto (`Systran/faster-whisper-small`, ~0,5 GB).
El servidor escucha en el puerto **9090**, funciona con un usuario sin privilegios y guarda
los modelos en el volumen de Docker `models` (la antigua carpeta `server/models/` ya no se usa
y se puede borrar; los modelos se vuelven a descargar). Opciones en `docker-compose.yml`:

| Variable | Por defecto | Qué hace |
|---|---|---|
| `ST_DEFAULT_MODEL` | `Systran/faster-whisper-small` | Modelo que se descarga y se usa por defecto |
| `ST_ALLOW_MANAGEMENT` | `1` | `0` = la extensión puede ver los modelos pero no descargarlos ni borrarlos |
| `ST_MAX_CLIENTS` | `4` | Transcripciones a la vez |
| `HF_TOKEN` | — | Para modelos de Hugging Face restringidos o privados |

Quien llegue al puerto puede usar el servidor (y, con la gestión activada, descargar o borrar
modelos): déjalo dentro de tu red o detrás de un cortafuegos.

### Actualizar el servidor

El servidor nunca se actualiza solo. En la extensión, **Ajustes → Acerca de → Buscar
actualizaciones** dice si hay una versión más nueva (los servidores a partir de esta versión
dicen la suya). Para actualizar, ejecuta esto desde la carpeta donde clonaste el repositorio:

```sh
cd StreamRemaster
git pull
cd server
docker compose up -d --build
```

Los modelos se quedan en el volumen `models` y no se vuelven a descargar. Si has cambiado
`docker-compose.yml` y `git pull` se niega, ejecuta `git stash` antes y `git stash pop`
después.

### Opción B — WhisperLive tal cual

La extensión también funciona con un WhisperLive sin modificar. En ese caso escribes un
tamaño de modelo (`tiny`, `small`, `medium`, `large-v3`…) en vez de elegirlo de una lista, y
no hay gestión de modelos ni opciones de rendimiento.

## ¿Cuánta memoria gráfica?

| Modelo | VRAM (float16) | Con «Ahorrar memoria (int8)» |
|---|---|---|
| small | ~1 GB | ~0,6 GB |
| medium | ~2 GB | ~1,2 GB |
| large-v3 / turbo | ~4 GB | ~2,3 GB |

El traductor suma ~0,7 GB en la gráfica (o nada, si lo pones en el procesador).

## Privacidad

La extensión envía el audio de la pestaña **solo** a la dirección de servidor que escribas, y
nada a ningún otro sitio. **Vídeo fluido** no envía nada: el vídeo se procesa en tu propia tarjeta
gráfica. Solo cuando pulsas **Buscar actualizaciones** pregunta a GitHub el
número de la última versión. Guarda sus ajustes en tu navegador. Ver [PRIVACY.md](PRIVACY.md).

## Compilar

```sh
python -m pip install -r tools/requirements.txt
python tools/build.py
```

Genera `dist/chromium`, `dist/firefox` y sus zips a partir de `extension/shared` más la
carpeta de cada navegador. Los textos en inglés y castellano están juntos en
`tools/i18n-messages.py`, y los demás idiomas en `tools/i18n-more.py`; el script comprueba cada clave y
hueco contra el inglés.

## Contribuir

Qué cambia en cada versión: [CHANGELOG](CHANGELOG.md), en inglés. Consulta [CONTRIBUTING](CONTRIBUTING.md), en inglés. Para avisar en privado de un problema de seguridad, consulta [SECURITY](SECURITY.md).

## Créditos y licencia

[PolyForm Noncommercial 1.0.0](LICENSE): se permite cualquier uso no comercial; el uso comercial necesita permiso del autor. Las versiones hasta la 2.2.0 se publicaron con licencia MIT. Hecho sobre [WhisperLive](https://github.com/collabora/WhisperLive), de Collabora (MIT, ver
[NOTICE](NOTICE)), y
[faster-whisper](https://github.com/SYSTRAN/faster-whisper). La traducción usa
[SMALL100](https://huggingface.co/alirezamsh/small100). El modelo de vídeo fluido, que también se llama StreamRemaster, lo
entrenó el autor desde cero con el conjunto [REDS](https://seungjunnah.github.io/Datasets/reds.html)
(CC BY 4.0) y con partidas de [Xonotic](https://xonotic.org); los detalles, en la
[ficha del modelo](docs/MODEL.es.md) y en [NOTICE](NOTICE).
