# StreamRemaster model card

[Versión en español](MODEL.es.md)

StreamRemaster is the AI model built into the **Smooth video** tab of the StreamRemaster extension, and
shares its name. It does two
things to the video on the page: it upscales each frame ×2, and it generates in-between frames so that the
video plays at the frame rate of your screen. It runs in the browser, on your own graphics card, through
WebGPU.

## What is in the file

The model is a single file, `extension/shared/models/streamremaster.stmodel`, with two small networks
inside:

- **Upscaling network.** A recurrent network that doubles the resolution of each frame. Recurrent means
  that it carries what it learnt from the previous frames on to the next one. It has 4 blocks of
  `<…>` channels.
  <!-- TODO: confirm the number of channels. The brief says 32, but the streamremaster.stmodel now in the
  worktree carries an upscaling part named "StreamRemaster SR 24x4 (prueba)", with 24 channels and 4 blocks. -->
- **Motion network.** A U-Net, a network that looks at the picture at several scales, working on the
  brightness of the frames (luma) at a quarter of their resolution. It estimates the motion between two
  frames in both directions, and an occlusion mask: the parts of the picture that can be seen in one frame
  but not in the other. The in-between frame is then synthesised from the two upscaled frames.

The file holds weights only, no code. The extension reads it and checks every part strictly before using
it.

## How it was trained

The author trained both networks together, from scratch, on his own graphics card (an NVIDIA RTX 2060).
The weights are his own: no pretrained weights from third parties and no other models as teachers were
used.

To make the low-resolution inputs, the frames were halved in resolution and compressed as JPEG. The
upscaling network learnt to recover the original frames from those inputs. Part of the training was adversarial: a
second network, used only during training, judged whether the result looked like a real frame.

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

No Twitch footage and no footage of commercial games was used. None of the training data is included in
the repository or in the extension.

## Licence

The model is under the [PolyForm Noncommercial License 1.0.0](../LICENSE), the same as the code: any
noncommercial use is allowed; commercial use needs the author's permission. The credits for the training
data are in [NOTICE](../NOTICE).

<!-- TODO: the licence of a model trained on REDS (CC BY 4.0) and on footage of Xonotic is pending the
lawyer's review. Change this section if the review asks for it. -->

Models that you add yourself in Settings → **Smooth video models** stay under their own licence.

## Limits

- **Made-up detail.** Because of the adversarial training, the upscaling draws plausible detail that was
  not in the original video: texture, sharper edges, strokes in small text. It looks better, but it is not
  more faithful. To read small text that you need to trust, turn the upscaling off (**Original (no
  upscaling)**).
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
