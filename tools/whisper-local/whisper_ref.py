"""Reference Whisper in PyTorch, written from the model description, to check the WebGPU
engine (extension/shared/whisper-gpu.js and whisper-local.js) number by number.

It reads the Hugging Face safetensors file directly, builds the log-mel input the way
Whisper does (torch.stft, Slaney filters computed here), runs the encoder and a greedy
decode with a given prompt, and writes what it got to a .npz for check.ts to compare.

Usage: python whisper_ref.py <model dir> <audio.wav 16 kHz mono> <out.npz> [lang] [task]
"""
import json
import math
import struct
import sys
import wave

import numpy as np
import torch
import torch.nn.functional as F

model_dir, wav_path, out_path = sys.argv[1:4]
lang = sys.argv[4] if len(sys.argv) > 4 else "es"
task = sys.argv[5] if len(sys.argv) > 5 else "transcribe"
dev = "cuda" if torch.cuda.is_available() else "cpu"


def load_safetensors(path):
    with open(path, "rb") as fh:
        n = struct.unpack("<Q", fh.read(8))[0]
        header = json.loads(fh.read(n))
        data = fh.read()
    out = {}
    for name, t in header.items():
        if name == "__metadata__":
            continue
        a, b = t["data_offsets"]
        dtype = {"F32": np.float32, "F16": np.float16}[t["dtype"]]
        arr = np.frombuffer(data[a:b], dtype=dtype).reshape(t["shape"])
        if not name.startswith("model.") and name.split(".")[0] in ("encoder", "decoder"):
            name = "model." + name
        # same rounding as the engine: weights in half precision, sums in float32
        out[name] = torch.from_numpy(arr.astype(np.float16).astype(np.float32)).to(dev)
    return out


def hz_to_mel(f):
    fsp, min_log_hz = 200 / 3, 1000.0
    min_log_mel, step = min_log_hz / fsp, math.log(6.4) / 27
    return min_log_mel + math.log(f / min_log_hz) / step if f >= min_log_hz else f / fsp


def mel_to_hz(m):
    fsp, min_log_hz = 200 / 3, 1000.0
    min_log_mel, step = min_log_hz / fsp, math.log(6.4) / 27
    return min_log_hz * math.exp(step * (m - min_log_mel)) if m >= min_log_mel else fsp * m


def mel_filters(n_mels):
    fft = np.linspace(0, 8000, 201)
    pts = np.array([mel_to_hz(x) for x in np.linspace(hz_to_mel(0), hz_to_mel(8000), n_mels + 2)])
    w = np.zeros((n_mels, 201))
    for m in range(n_mels):
        lower = (fft - pts[m]) / (pts[m + 1] - pts[m])
        upper = (pts[m + 2] - fft) / (pts[m + 2] - pts[m + 1])
        w[m] = np.maximum(0, np.minimum(lower, upper)) * 2 / (pts[m + 2] - pts[m])
    return torch.tensor(w, dtype=torch.float32)


def log_mel(audio, n_mels):
    audio = F.pad(audio, (0, 480000 - audio.shape[0])) if audio.shape[0] < 480000 else audio[:480000]
    # zeros on the left like the engine's first window (Whisper itself reflects)
    padded = F.pad(audio, (200, 200))
    stft = torch.stft(padded, 400, 160, window=torch.hann_window(400), center=False, return_complex=True)
    power = stft.abs() ** 2
    mel = mel_filters(n_mels) @ power
    log = torch.clamp(mel, min=1e-10).log10()[:, :3000]
    log = torch.maximum(log, log.max() - 8.0)
    return (log + 4.0) / 4.0   # [n_mels, 3000]


def ln(x, w, p):
    return F.layer_norm(x, (x.shape[-1],), w[p + ".weight"], w[p + ".bias"], 1e-5)


def attn(x_q, x_kv, w, p, heads, mask=None):
    q = x_q @ w[p + ".q_proj.weight"].T + w[p + ".q_proj.bias"]
    k = x_kv @ w[p + ".k_proj.weight"].T
    v = x_kv @ w[p + ".v_proj.weight"].T + w[p + ".v_proj.bias"]
    def split(t):
        return t.view(t.shape[0], heads, 64).transpose(0, 1)
    s = (split(q) * 0.125) @ split(k).transpose(1, 2)
    if mask is not None:
        s = s + mask
    o = (s.softmax(-1) @ split(v)).transpose(0, 1).reshape(x_q.shape[0], -1)
    return o @ w[p + ".out_proj.weight"].T + w[p + ".out_proj.bias"]


def main():
    cfg = json.load(open(f"{model_dir}/config.json"))
    gen = json.load(open(f"{model_dir}/generation_config.json"))
    w = load_safetensors(f"{model_dir}/model.safetensors")
    with wave.open(wav_path) as wf:
        assert wf.getframerate() == 16000 and wf.getnchannels() == 1 and wf.getsampwidth() == 2
        audio = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768
    duration = len(audio) / 16000
    mel = log_mel(torch.from_numpy(audio), cfg["num_mel_bins"]).to(dev)
    heads = cfg["d_model"] // 64
    E, D = "model.encoder.", "model.decoder."
    with torch.no_grad():
        x = F.gelu(F.conv1d(mel[None], w[E + "conv1.weight"], w[E + "conv1.bias"], padding=1))
        x = F.gelu(F.conv1d(x, w[E + "conv2.weight"], w[E + "conv2.bias"], stride=2, padding=1))[0].T
        x = x + w[E + "embed_positions.weight"]
        for i in range(cfg["encoder_layers"]):
            p = f"{E}layers.{i}."
            x = x + attn(ln(x, w, p + "self_attn_layer_norm"), ln(x, w, p + "self_attn_layer_norm"), w, p + "self_attn", heads)
            h = ln(x, w, p + "final_layer_norm")
            x = x + F.gelu(h @ w[p + "fc1.weight"].T + w[p + "fc1.bias"]) @ w[p + "fc2.weight"].T + w[p + "fc2.bias"]
        enc = ln(x, w, E + "layer_norm")

        def decode(tokens):
            n = len(tokens)
            y = w[D + "embed_tokens.weight"][tokens] + w[D + "embed_positions.weight"][:n]
            mask = torch.full((n, n), float("-inf"), device=dev).triu(1)
            for i in range(cfg["decoder_layers"]):
                p = f"{D}layers.{i}."
                h = ln(y, w, p + "self_attn_layer_norm")
                y = y + attn(h, h, w, p + "self_attn", heads, mask)
                y = y + attn(ln(y, w, p + "encoder_attn_layer_norm"), enc, w, p + "encoder_attn", heads)
                h = ln(y, w, p + "final_layer_norm")
                y = y + F.gelu(h @ w[p + "fc1.weight"].T + w[p + "fc1.bias"]) @ w[p + "fc2.weight"].T + w[p + "fc2.bias"]
            y = ln(y, w, D + "layer_norm")
            return y @ w[D + "embed_tokens.weight"].T

        sot = cfg["decoder_start_token_id"]
        logits_sot = decode([sot])[-1]
        lang_id = gen["lang_to_id"][f"<|{lang}|>"]
        task_id = gen["task_to_id"][task]
        prompt = [sot, lang_id, task_id]
        logits_prompt = decode(prompt)[-1]
    import os
    os.makedirs(out_path, exist_ok=True)
    for name, t in (("mel", mel.T.contiguous()), ("enc", enc), ("logits_sot", logits_sot), ("logits_prompt", logits_prompt)):
        t.float().cpu().numpy().astype("<f4").tofile(f"{out_path}/{name}.f32")
    json.dump({"prompt": prompt, "duration": duration}, open(f"{out_path}/info.json", "w"))
    print("reference written", out_path, "audio", round(duration, 2), "s", "argmax after prompt", int(logits_prompt.argmax()))


main()
