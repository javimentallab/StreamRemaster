# Ficha del modelo StreamRemaster

[English version](MODEL.md)

StreamRemaster es el modelo de IA que trae la pestaña **Vídeo fluido** de la extensión StreamRemaster, y
comparte su nombre. Hace dos cosas con el vídeo de la página: reescala cada fotograma al doble de
resolución y genera fotogramas intermedios para que el vídeo vaya a la frecuencia de tu pantalla. Funciona
en el navegador, en tu propia tarjeta gráfica, mediante WebGPU.

## Qué hay en el archivo

El modelo es un solo archivo, `extension/shared/models/streamremaster.stmodel`, con dos redes pequeñas
dentro:

- **Red de reescalado.** Una red recurrente que duplica la resolución de cada fotograma. Recurrente quiere
  decir que lo que saca de los fotogramas anteriores lo arrastra al siguiente: usa el movimiento que
  calcula la otra red para llevar el fotograma reescalado anterior encima del actual. Tiene 4 bloques de
  32 canales.
- **Red de movimiento.** Una U-Net, una red que mira la imagen a varias escalas, que trabaja con el brillo
  de los fotogramas (la luminancia) a un cuarto de su resolución. Calcula el movimiento entre dos
  fotogramas en los dos sentidos y una máscara de oclusión: las partes de la imagen que se ven en un
  fotograma y en el otro no. Con eso, el fotograma intermedio se compone a partir de los dos fotogramas
  ya reescalados.

El archivo solo contiene pesos, nada de código. La extensión lo lee y comprueba cada parte con rigor antes
de usarlo.

## Cómo se entrenó

El autor entrenó las dos redes juntas, desde cero, en su propia tarjeta gráfica (una NVIDIA RTX 2060). Los
pesos son del autor: el modelo no contiene pesos preentrenados de terceros.

Para crear las entradas de entrenamiento, los fotogramas se redujeron a la mitad y se estropearon como los
estropea un directo: compresión de vídeo de distinta intensidad, ruido y grano de sensor, y lluvia, nieve
y efectos de pantalla sintéticos. Las dos redes aprendieron a recuperar, a partir de esas entradas, los
fotogramas originales y los fotogramas intermedios reales, comparándolos píxel a píxel.

En la última fase del entrenamiento, la red de movimiento aprendió también de **RIFE 4.25**, un modelo de
interpolación de fotogramas de código abierto (licencia MIT), usado como profesor: para cada pareja de
fotogramas de entrenamiento, RIFE daba su propio cálculo del movimiento y del fotograma intermedio, y la
red de movimiento se entrenó para acercarse a ellos además de a los fotogramas reales. RIFE solo funcionó
en el ordenador del autor durante el entrenamiento. Ni su código ni sus pesos están en el modelo ni en la
extensión.

## Datos de entrenamiento

- **REDS**, un conjunto de vídeos reales, en sus originales a 120 fps. Licencia
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es). Seungjun Nah, Sungyong Baik, Seokil
  Hong, Gyeongsik Moon, Sanghyun Son, Radu Timofte y Kyoung Mu Lee, *NTIRE 2019 Challenge on Video
  Deblurring and Super-Resolution: Dataset and Study*, CVPR Workshops 2019.
  [Página del conjunto](https://seungjunnah.github.io/Datasets/reds.html).
- **Partidas de [Xonotic](https://xonotic.org)**, un juego de código abierto, grabadas por el autor a
  120 fps.
- **Rótulos de directo sintéticos**: texto fijo, chat que se desplaza, un recuadro de cámara y logotipos,
  dibujados con las fuentes DejaVu y Liberation y con texto inventado. Las fuentes solo se usaron para
  crear las imágenes de entrenamiento y no van en la extensión.
- **Lluvia, nieve y grano sintéticos**, dibujados por programa por el autor.

No se usaron vídeos de Twitch ni de juegos comerciales. Ninguno de los datos de entrenamiento está en el
repositorio ni en la extensión.

## Licencia

El modelo tiene la [licencia PolyForm Noncommercial 1.0.0](../LICENSE), la misma que el código: se
permite cualquier uso no comercial; el uso comercial necesita permiso del autor. Los créditos de los datos
de entrenamiento y de RIFE están en [NOTICE](../NOTICE), en inglés.

<!-- TODO: la licencia de un modelo entrenado con REDS (CC BY 4.0) y con partidas de Xonotic, con RIFE (MIT)
de profesor, está pendiente de la revisión del jurista. Cambiar este apartado si la revisión lo pide. -->

Los modelos que añadas tú en Ajustes → **Modelos de vídeo fluido** conservan su propia licencia.

## Límites

- **Movimiento rápido.** Donde la imagen cambia mucho entre dos fotogramas (giros rápidos, destellos,
  muchas partículas pequeñas), los fotogramas intermedios pueden verse borrosos o con ruido. La extensión
  baja ahí el enfoque.
- **Necesita una tarjeta gráfica con WebGPU.** El navegador tiene que poder usar WebGPU en tu gráfica. Si
  no puede, la pestaña lo dice.
- **El vídeo protegido no se puede leer.** El vídeo con DRM se ve negro para cualquier extensión, así que
  no hay nada que procesar. Lo mismo pasa con algunos vídeos servidos desde otro sitio.

## Cita

Si usas REDS, cítalo como piden sus autores:

```bibtex
@InProceedings{Nah_2019_CVPR_Workshops_REDS,
  author = {Nah, Seungjun and Baik, Sungyong and Hong, Seokil and Moon, Gyeongsik and Son, Sanghyun and Timofte, Radu and Lee, Kyoung Mu},
  title = {NTIRE 2019 Challenge on Video Deblurring and Super-Resolution: Dataset and Study},
  booktitle = {CVPR Workshops},
  month = {June},
  year = {2019}
}
```
