# Ficha del modelo StreamRemaster

[English version](MODEL.md)

StreamRemaster es el modelo de IA que trae la pestaña **Vídeo fluido** de la extensión StreamRemaster, y
comparte su nombre. Hace dos
cosas con el vídeo de la página: reescala cada fotograma al doble de resolución y genera fotogramas
intermedios para que el vídeo vaya a la frecuencia de tu pantalla. Funciona en el navegador, en tu propia
tarjeta gráfica, mediante WebGPU.

## Qué hay en el archivo

El modelo es un solo archivo, `extension/shared/models/streamremaster.stmodel`, con dos redes pequeñas
dentro:

- **Red de reescalado.** Una red recurrente que duplica la resolución de cada fotograma. Recurrente quiere
  decir que lo que saca de los fotogramas anteriores lo arrastra al siguiente. Tiene 4 bloques de `<…>`
  canales.
  <!-- TODO: confirmar el número de canales. El encargo dice 32, pero el streamremaster.stmodel que hay
  ahora en el worktree lleva una parte de reescalado llamada «StreamRemaster SR 24x4 (prueba)», con 24
  canales y 4 bloques. -->
- **Red de movimiento.** Una U-Net, una red que mira la imagen a varias escalas, que trabaja con el brillo
  de los fotogramas (la luminancia) a un cuarto de su resolución. Calcula el movimiento entre dos
  fotogramas en los dos sentidos y una máscara de oclusión: las partes de la imagen que se ven en un
  fotograma y en el otro no. Con eso, el fotograma intermedio se compone a partir de los dos fotogramas
  ya reescalados.

El archivo solo contiene pesos, nada de código. La extensión lo lee y comprueba cada parte con rigor antes
de usarlo.

## Cómo se entrenó

El autor entrenó las dos redes juntas, desde cero, en su propia tarjeta gráfica (una NVIDIA RTX 2060). Los
pesos son suyos: no se usaron pesos preentrenados de terceros ni otros modelos como maestros.

Para crear las entradas de baja resolución, los fotogramas se redujeron a la mitad y se comprimieron en
JPEG. La red de reescalado aprendió a recuperar los fotogramas originales a partir de esas entradas. Parte
del entrenamiento fue adversario: una segunda red, que solo se usa al entrenar, juzgaba si el resultado
parecía un fotograma real.

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

No se usaron vídeos de Twitch ni de juegos comerciales. Ninguno de los datos de entrenamiento está en el
repositorio ni en la extensión.

## Licencia

El modelo tiene la [licencia PolyForm Noncommercial 1.0.0](../LICENSE), la misma que el código: se
permite cualquier uso no comercial; el uso comercial necesita permiso del autor. Los créditos de los datos
de entrenamiento están en [NOTICE](../NOTICE), en inglés.

<!-- TODO: la licencia de un modelo entrenado con REDS (CC BY 4.0) y con partidas de Xonotic está
pendiente de la revisión del jurista. Cambiar este apartado si la revisión lo pide. -->

Los modelos que añadas tú en Ajustes → **Modelos de vídeo fluido** conservan su propia licencia.

## Límites

- **Detalle inventado.** Por el entrenamiento adversario, el reescalado dibuja detalle verosímil que no
  estaba en el vídeo original: textura, bordes más nítidos, trazos en el texto pequeño. Se ve mejor, pero
  no es más fiel. Para leer texto pequeño del que tengas que fiarte, quita el reescalado (**Original (sin
  reescalar)**).
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
