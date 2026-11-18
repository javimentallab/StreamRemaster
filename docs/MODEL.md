# StreamRemaster model card

[Versión en español](MODEL.es.md)

StreamRemaster is the AI model built into the **Smooth video** tab of the StreamRemaster extension, and
shares its name. It does two things to the video on the page: it upscales each frame ×2, and it generates
in-between frames so that the video plays at the frame rate of your screen. It runs in the browser, on your
own graphics card, through WebGPU.

## What is in the file

The model is a single file, `extension/shared/models/streamremaster.stmodel`, with two small networks
inside:

- **Upscaling network.** A recurrent network that doubles the resolution of each frame. Recurrent means
  that it carries what it learnt from the previous frames on to the next one: it uses the motion network's
  estimate to move the previous upscaled frame onto the current one. It has 4 blocks of 32 channels.
- **Motion network.** A U-Net, a network that looks at the picture at several scales, working on the
  brightness of the frames (luma) at a quarter of their resolution. It estimates the motion between two
  frames in both directions, and an occlusion mask: the parts of the picture that can be seen in one frame
  but not in the other. The in-between frame is then synthesised from the two upscaled frames.

The file holds weights only, no code. The extension reads it and checks every part strictly before using
it.

## How it was trained

The author trained both networks together, from scratch, on their own graphics card (an NVIDIA RTX 2060).
The weights are the author's own: the model contains no pretrained weights from third parties.

To make the training inputs, the frames were halved in resolution and degraded the way a live stream
degrades them: video compression at several strengths, noise and sensor grain, and synthetic rain, snow
and screen effects. Both networks learnt to recover the original frames and the real in-between frames
from those inputs, measured pixel by pixel.

In the last stage of the training, the motion network also learnt from **RIFE 4.25**, an open-source frame
interpolation model (MIT License), used as a teacher: for each pair of training frames, RIFE gave its own
estimate of the motion and of the in-between frame, and the motion network was trained to come close to
them as well as to the real frames. RIFE ran only on the author's computer during training. None of its
code or weights is in the model or in the extension.

## Training data

- **REDS**, a dataset of real-world video, in its 120 fps originals. Licensed under
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Seungjun Nah, Sungyong Baik, Seokil Hong,
  Gyeongsik Moon, Sanghyun Son, Radu Timofte and Kyoung Mu Lee, *NTIRE 2019 Challenge on Video Deblurring
  and Super-Resolution: Dataset and Study*, CVPR Workshops 2019.
  [Dataset page](https://seungjunnah.github.io/Datasets/reds.html).
- **Gameplay footage of [Xonotic](https://xonotic.org)**, an open-source game, recorded by the author at
  120 fps.
- **Synthetic stream overlays**: fixed text, scrolling chat, a camera box and logos, drawn with the DejaVu
  and Liberation fonts and made-up text. The fonts were used only to make training images and are not
  included in the extension.
- **Synthetic rain, snow and grain**, drawn by program by the author.

No Twitch footage and no footage of commercial games was used. None of the training data is included in
the repository or in the extension.

## Licence

The model is under the [PolyForm Noncommercial License 1.0.0](../LICENSE), the same as the code: any
noncommercial use is allowed; commercial use needs the author's permission. The credits for the training
data and for RIFE are in [NOTICE](../NOTICE).

<!-- TODO: the licence of a model trained on REDS (CC BY 4.0) and on footage of Xonotic, with RIFE (MIT) as
a teacher, is pending the lawyer's review. Change this section if the review asks for it. -->

Models that you add yourself in Settings → **Smooth video models** stay under their own licence.

## Limits

- **Fast motion.** Where the picture changes a lot between two frames (fast turns, flashes, many small
  particles), the in-between frames can show blur or noise. The extension lowers the sharpening there.
- **It needs a graphics card with WebGPU.** The browser must be able to use WebGPU on your graphics card.
  If it cannot, the tab says so.
- **Protected video cannot be read.** Video with DRM shows as black to any extension, so there is nothing
  to process. The same happens with some video served from another site.

## Citation

If you use REDS, cite it as its authors ask:

```bibtex
@InProceedings{Nah_2019_CVPR_Workshops_REDS,
  author = {Nah, Seungjun and Baik, Sungyong and Hong, Seokil and Moon, Gyeongsik and Son, Sanghyun and Timofte, Radu and Lee, Kyoung Mu},
  title = {NTIRE 2019 Challenge on Video Deblurring and Super-Resolution: Dataset and Study},
  booktitle = {CVPR Workshops},
  month = {June},
  year = {2019}
}
```
