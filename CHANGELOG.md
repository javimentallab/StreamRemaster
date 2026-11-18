# Changelog

All notable changes to StreamRemaster, called Stream Transcription up to version 2.2.0. Versions follow [semantic versioning](https://semver.org/).

## 3.0.0 — 2026-11-18

### Added
- **Start automatically**: two separate boxes, one in each tab of the popup and in Settings, turn on the
  smooth video or the subtitles by themselves when a video starts playing on the page. Both are off by
  default. If you stop either by hand, it stays off until the page reloads or you go to another page.
  In Chromium browsers the subtitles can only start by themselves on tabs where you have pressed the
  extension's button, because only then can the extension capture a tab. The smooth video can start on
  any website if you allow it: the permission is asked for when you tick its box.
- **Smooth video**, a new tab in the popup next to **Subtitles**. It raises the frame rate of the video on
  the page up to your screen's by generating in-between frames with AI, and upscales it ×2 with AI. It
  runs in the browser, on your own graphics card, through WebGPU: no server is needed for it. For Firefox,
  Zen and Chromium browsers (tested in Brave).
- The tab's controls: a large on/off button; **Target frame rate** (Match the screen, or 60, 75, 90, 100,
  120, 144, 165, 180 or 240); **AI model**; and **Upscaling target resolution** (Original (no upscaling),
  Match the screen, 1080p, 1440p or 4K). **Match the screen** follows the size the picture takes on
  screen, so a video in a small player is not upscaled to 4K. While it is on, a meter on the page shows
  the frame rate.
- A built-in model, **StreamRemaster**: two small networks, one for upscaling and one for motion, trained
  from scratch by the author, with no third-party weights. How it was made and on what data:
  [docs/MODEL.md](docs/MODEL.md).
- Settings → **Smooth video models**: add model files (`.stmodel`, and the older `.srmodel` and
  `.fimodel`) and pick one. The built-in model is marked **Built-in** and cannot be deleted. **None** in
  the **AI model** list uses a plain cross-fade and plain scaling instead. Model files contain weights
  only, and the extension reads and checks them strictly before using them.
- **Transcribe on this computer**, with no server. Whisper runs in the browser, on your graphics card,
  through WebGPU. In Settings → **Transcription models**, download a model once (tiny, base, small,
  medium or large-v3-turbo, from Hugging Face); it stays in the browser and can be deleted there. The
  audio never leaves your computer. On this computer the subtitles can only be translated into English.
- Smooth video models can also be kept on your StreamRemaster server: the chosen model is downloaded from
  it and runs on this computer's graphics card.
- The interface in Catalan, Galician and Basque: 18 languages in all.

### Changed
- **New name: StreamRemaster.** Stream Transcription is now called StreamRemaster. The numbering carries on
  from 2.2.0, so that Firefox updates the add-on by itself. The subtitles work as before.
- Licence: from this version on, the code and the models are under the
  [PolyForm Noncommercial License 1.0.0](LICENSE). Versions up to 2.2.0 remain under the MIT licence.
- `NOTICE` credits the training data of the built-in model, RIFE (used as a teacher during training) and
  the Whisper models the extension can download.
- The privacy policy is rewritten, in English ([PRIVACY.md](PRIVACY.md)) and Spanish
  ([PRIVACY.es.md](PRIVACY.es.md)), and covers transcription on this computer and the smooth video.

### Fixed
- Chromium browsers: fullscreen while the subtitles were capturing the tab stayed inside the tab. Now the
  window goes fullscreen too, and it is restored afterwards.

### Security
- No new required permissions. Chromium browsers get one optional permission, to read all
  websites, only asked for when you tick the box that starts the smooth video automatically.
- No vulnerabilities fixed in this release.

## 2.2.0 — 2026-11-07

### Added
- **Check for updates**, at the bottom of the popup and in Settings → About. Only when you press it, the
  extension asks GitHub for the number of the latest release and says whether a newer one exists.
  **Update** then opens the page to get it: the add-on's page on Firefox Add-ons in Firefox (which also
  updates it by itself), or the release on GitHub in Chromium. The extension never downloads code or
  replaces itself, and nothing is checked in the background.
- In Settings → About, the same check says whether your Stream Transcription server is up to date, behind,
  or too old to report its version, and shows the commands to update it.
- The server reports its version with every answer to the extension.

### Changed
- The privacy policy and the README explain the request to GitHub.

### Security
- No vulnerabilities fixed in this release. No new permissions.

## 2.1.1 — 2026-11-02

### Fixed
- Extension: session ids no longer rely on `Math.random`.
- Server: errors no longer send exception text to clients; the details go to the server log.
- Server image: the NVIDIA wheels are pinned and declared in `NOTICE`.

### Added
- The Firefox Add-ons listing in 13 languages; a security policy, a contributing guide, tests in CI and
  CodeQL, with every GitHub Action pinned by commit.

### Security
- The three CodeQL alerts above (weak randomness for session ids, exception text sent to clients).

## 2.1.0 — 2026-10-31

### Added
- The interface in 13 more languages: Portuguese, French, German, Italian, Dutch, Polish, Russian,
  Ukrainian, Chinese, Japanese, Korean, Thai and Hindi, besides English and Spanish.

### Changed
- Firefox: minimum version 140 (Android 142).

## 2.0.0 — 2026-10-16

First release: live subtitles for any browser tab, transcribed and translated by your own WhisperLive
server, with model management from the extension, int8 precision, the translator on the CPU and clear
VRAM warnings.
