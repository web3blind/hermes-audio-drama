#!/usr/bin/env python3
import json
import math
import random
import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np
import yaml

ROOT = Path('/root/projects/hermes-audio-drama')
ASSETS = ROOT / 'assets'
BUILD = ROOT / 'build'
LINES_DIR = BUILD / 'lines'
SCENES_DIR = BUILD / 'scenes'
TMP_DIR = BUILD / 'tmp'


def run(cmd):
    subprocess.run(cmd, check=True)


def db_to_amp(db: float) -> float:
    return float(10 ** (db / 20.0))


def ms_to_samples(ms: int, sr: int) -> int:
    return int(sr * (ms / 1000.0))


def pad_to(arr: np.ndarray, length: int) -> np.ndarray:
    if len(arr) >= length:
        return arr
    out = np.zeros(length, dtype=np.float32)
    out[: len(arr)] = arr
    return out


def overlay(base: np.ndarray, clip: np.ndarray, start: int) -> np.ndarray:
    end = start + len(clip)
    if end > len(base):
        base = pad_to(base, end)
    base[start:end] += clip
    return base


def normalize(arr: np.ndarray, peak: float = 0.92) -> np.ndarray:
    current = np.max(np.abs(arr)) if len(arr) else 0.0
    if current <= 1e-6:
        return arr
    if current <= peak:
        return arr
    return arr * (peak / current)


def fade(arr: np.ndarray, sr: int, fade_in_ms: int = 20, fade_out_ms: int = 40) -> np.ndarray:
    arr = arr.copy()
    fi = min(len(arr), ms_to_samples(fade_in_ms, sr))
    fo = min(len(arr), ms_to_samples(fade_out_ms, sr))
    if fi > 1:
        arr[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)
    if fo > 1:
        arr[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)
    return arr


def write_wav(path: Path, arr: np.ndarray, sr: int):
    path.parent.mkdir(parents=True, exist_ok=True)
    clipped = np.clip(arr, -1.0, 1.0)
    pcm = (clipped * 32767.0).astype(np.int16)
    with wave.open(str(path), 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())


def read_wav(path: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(path), 'rb') as wf:
        sr = wf.getframerate()
        data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
        if wf.getnchannels() != 1:
            raise ValueError(f'{path} is not mono')
        return data, sr


def sine(freq: float, duration_s: float, sr: int, amp: float = 0.2, phase: float = 0.0) -> np.ndarray:
    t = np.arange(int(duration_s * sr), dtype=np.float32) / sr
    return amp * np.sin(2 * np.pi * freq * t + phase)


def chirp(freq_a: float, freq_b: float, duration_s: float, sr: int, amp: float = 0.2) -> np.ndarray:
    t = np.arange(int(duration_s * sr), dtype=np.float32) / sr
    k = (freq_b - freq_a) / max(duration_s, 1e-6)
    phase = 2 * np.pi * (freq_a * t + 0.5 * k * t * t)
    return amp * np.sin(phase)


def white_noise(duration_s: float, sr: int, amp: float = 0.1, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.normal(0.0, amp, int(duration_s * sr)).astype(np.float32)


def smooth(arr: np.ndarray, window: int) -> np.ndarray:
    if window <= 1:
        return arr
    kernel = np.ones(window, dtype=np.float32) / window
    return np.convolve(arr, kernel, mode='same')


def bandish_noise(duration_s: float, sr: int, amp: float = 0.06, seed: int = 0, smooth_window: int = 80) -> np.ndarray:
    return smooth(white_noise(duration_s, sr, amp, seed), smooth_window)


def short_click(sr: int, amp: float = 0.4) -> np.ndarray:
    dur = 0.035
    n = int(sr * dur)
    burst = white_noise(dur, sr, amp=amp, seed=random.randint(0, 10_000))
    env = np.exp(-np.linspace(0.0, 8.0, n)).astype(np.float32)
    return burst[:n] * env


def thump(sr: int, amp: float = 0.35, dur: float = 0.14) -> np.ndarray:
    n = int(sr * dur)
    t = np.arange(n, dtype=np.float32) / sr
    tone = np.sin(2 * np.pi * 90 * t) * np.exp(-np.linspace(0.0, 6.0, n)).astype(np.float32)
    return tone * amp


def notification(sr: int, dur_s: float = 0.7, amp: float = 0.24) -> np.ndarray:
    a = chirp(880, 1320, dur_s * 0.55, sr, amp=amp)
    b = sine(1320, dur_s * 0.45, sr, amp=amp * 0.7)
    out = np.concatenate([a, b]).astype(np.float32)
    return fade(out, sr, 10, 90)


def success_glow(sr: int, dur_s: float = 1.2, amp: float = 0.22) -> np.ndarray:
    n = int(dur_s * sr)
    t = np.arange(n, dtype=np.float32) / sr
    chord = (
        0.55 * np.sin(2 * np.pi * 523.25 * t)
        + 0.35 * np.sin(2 * np.pi * 659.25 * t)
        + 0.25 * np.sin(2 * np.pi * 783.99 * t)
    )
    env = np.exp(-np.linspace(0.0, 3.4, n)).astype(np.float32)
    return (chord * env * amp).astype(np.float32)


def thinking_ai(sr: int, dur_s: float = 2.0, amp: float = 0.1) -> np.ndarray:
    total = np.zeros(int(sr * dur_s), dtype=np.float32)
    pulse = fade(sine(640, 0.12, sr, amp=amp), sr, 8, 80)
    gap = int(sr * 0.28)
    pos = 0
    while pos < len(total):
        total = overlay(total, pulse, pos)
        pos += gap
    return total


def typing(sr: int, dur_s: float = 2.0, amp: float = 0.14) -> np.ndarray:
    total = np.zeros(int(sr * dur_s), dtype=np.float32)
    rng = random.Random(42 + int(dur_s * 100))
    pos = 0
    while pos < len(total):
        click = short_click(sr, amp=amp * rng.uniform(0.8, 1.2))
        total = overlay(total, click, pos)
        pos += int(sr * rng.uniform(0.055, 0.16))
    return total


def room_night(sr: int, dur_s: float) -> np.ndarray:
    hum = sine(72, dur_s, sr, amp=0.018) + sine(144, dur_s, sr, amp=0.008)
    air = bandish_noise(dur_s, sr, amp=0.02, seed=101, smooth_window=180)
    return fade(hum + air, sr, 100, 200)


def room_evening(sr: int, dur_s: float) -> np.ndarray:
    hum = sine(85, dur_s, sr, amp=0.016) + sine(170, dur_s, sr, amp=0.007)
    air = bandish_noise(dur_s, sr, amp=0.018, seed=202, smooth_window=160)
    return fade(hum + air, sr, 100, 200)


def room_morning(sr: int, dur_s: float) -> np.ndarray:
    base = room_evening(sr, dur_s) * 0.8
    out = base.copy()
    for start in [0.7, 2.4, 4.2, 6.0, 7.4]:
        if start >= dur_s:
            break
        cue = chirp(1200, 1800, 0.18, sr, amp=0.028) * np.exp(-np.linspace(0.0, 2.0, int(sr * 0.18))).astype(np.float32)
        out = overlay(out, cue.astype(np.float32), int(start * sr))
    return fade(out, sr, 100, 220)


def walk_outside(sr: int, dur_s: float) -> np.ndarray:
    wind = bandish_noise(dur_s, sr, amp=0.03, seed=303, smooth_window=50)
    city = sine(180, dur_s, sr, amp=0.01) + sine(240, dur_s, sr, amp=0.006)
    out = fade(wind + city, sr, 80, 120)
    step_gap = 0.52
    t = 0.35
    while t < dur_s:
        out = overlay(out, thump(sr, amp=0.06), int(t * sr))
        t += step_gap
    return out


def ad_research(sr: int, dur_s: float) -> np.ndarray:
    out = room_evening(sr, dur_s) * 0.6
    pulse = fade(sine(420, 0.08, sr, amp=0.08), sr, 5, 70)
    click = short_click(sr, amp=0.10)
    t = 0.25
    while t < dur_s:
        out = overlay(out, pulse, int(t * sr))
        t += 0.42
    t = 0.4
    while t < dur_s:
        out = overlay(out, click * 0.5, int(t * sr))
        t += 0.27
    return out


def footstep_focus(sr: int, dur_s: float) -> np.ndarray:
    out = np.zeros(int(dur_s * sr), dtype=np.float32)
    t = 0.0
    while t < dur_s:
        out = overlay(out, thump(sr, amp=0.12), int(t * sr))
        t += 0.56
    return out


def phone_memo(sr: int, dur_s: float) -> np.ndarray:
    tone = chirp(620, 930, min(dur_s, 0.35), sr, amp=0.12)
    total = np.zeros(int(sr * dur_s), dtype=np.float32)
    total = overlay(total, fade(tone, sr, 8, 90), 0)
    return total


AMBIENCE = {
    'room_night': room_night,
    'room_evening': room_evening,
    'room_morning': room_morning,
    'walk_outside': walk_outside,
}

CUES = {
    'typing': lambda sr, dur: typing(sr, dur, amp=0.12),
    'notification': lambda sr, dur: notification(sr, dur, amp=0.24),
    'thinking_ai': lambda sr, dur: thinking_ai(sr, dur, amp=0.08),
    'success_glow': lambda sr, dur: success_glow(sr, dur, amp=0.2),
    'ad_research': lambda sr, dur: ad_research(sr, dur),
    'footstep_focus': lambda sr, dur: footstep_focus(sr, dur),
    'phone_memo': lambda sr, dur: phone_memo(sr, dur),
}


def render_tts_line(text_path: Path, mp3_path: Path, wav_path: Path, voice: str, rate: str, pitch: str, sr: int):
    run([
        shutil.which('edge-tts') or 'edge-tts',
        '--voice', voice,
        '--file', str(text_path),
        '--write-media', str(mp3_path),
        '--rate', rate,
        '--pitch', pitch,
    ])
    run([
        shutil.which('ffmpeg') or 'ffmpeg', '-y', '-loglevel', 'error',
        '-i', str(mp3_path),
        '-ac', '1', '-ar', str(sr), '-c:a', 'pcm_s16le',
        str(wav_path),
    ])


def main():
    BUILD.mkdir(parents=True, exist_ok=True)
    LINES_DIR.mkdir(parents=True, exist_ok=True)
    SCENES_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    story = yaml.safe_load((ASSETS / 'story.yaml').read_text())
    voices = yaml.safe_load((ASSETS / 'voices.yaml').read_text())
    sr = int(story.get('sample_rate') or voices.get('sample_rate') or 24000)
    scene_gap_ms = int(story.get('scene_gap_ms', voices.get('scene_gap_ms', 700)))
    roles = voices['roles']

    final = np.zeros(0, dtype=np.float32)
    manifest = {
        'title': story.get('title', 'Untitled'),
        'sample_rate': sr,
        'scenes': [],
    }

    for scene_idx, scene in enumerate(story['scenes']):
        line_segments = []
        timings = []
        cursor = ms_to_samples(int(scene.get('intro_pause_ms', 0)), sr)

        for line_idx, line in enumerate(scene['lines']):
            speaker = line['speaker']
            cfg = roles[speaker]
            text = line['text'].strip()
            base_name = f"scene{scene_idx+1:02d}_line{line_idx+1:02d}_{speaker}"
            text_path = TMP_DIR / f'{base_name}.txt'
            mp3_path = LINES_DIR / f'{base_name}.mp3'
            wav_path = LINES_DIR / f'{base_name}.wav'
            text_path.write_text(text)
            render_tts_line(
                text_path,
                mp3_path,
                wav_path,
                cfg['voice'],
                line.get('rate', cfg.get('rate', '+0%')),
                line.get('pitch', cfg.get('pitch', '+0Hz')),
                sr,
            )
            arr, arr_sr = read_wav(wav_path)
            if arr_sr != sr:
                raise ValueError(f'Unexpected sample rate {arr_sr} for {wav_path}')
            arr = arr * db_to_amp(float(cfg.get('gain_db', 0.0) + line.get('volume_db', 0.0)))
            arr = normalize(arr, peak=0.86)
            line_segments.append((cursor, arr, speaker, text, wav_path))
            start_ms = round(cursor * 1000 / sr)
            end_ms = round((cursor + len(arr)) * 1000 / sr)
            timings.append({
                'speaker': speaker,
                'text': text,
                'start_ms': start_ms,
                'end_ms': end_ms,
                'file': str(wav_path),
            })
            cursor += len(arr)
            cursor += ms_to_samples(int(line.get('pause_after_ms', 350)), sr)

        total_len = max(cursor, 1)
        ambience_name = scene.get('ambience')
        if ambience_name:
            base = AMBIENCE[ambience_name](sr, total_len / sr).astype(np.float32)
        else:
            base = np.zeros(total_len, dtype=np.float32)

        for cue in scene.get('cues', []):
            cue_type = cue['type']
            cue_level = float(cue.get('level', 1.0))
            cue_dur = float(cue.get('duration_ms', 500)) / 1000.0
            cue_audio = CUES[cue_type](sr, cue_dur).astype(np.float32) * cue_level
            start = ms_to_samples(int(cue.get('start_ms', 0)), sr)
            base = overlay(base, cue_audio, start)

        for start, arr, speaker, text, wav_path in line_segments:
            base = overlay(base, arr, start)

        scene_audio = normalize(base, peak=0.9)
        scene_audio = fade(scene_audio, sr, 30, 80)
        scene_path = SCENES_DIR / f"{scene_idx+1:02d}_{scene['id']}.wav"
        write_wav(scene_path, scene_audio, sr)

        manifest['scenes'].append({
            'id': scene['id'],
            'ambience': ambience_name,
            'duration_ms': round(len(scene_audio) * 1000 / sr),
            'scene_wav': str(scene_path),
            'lines': timings,
            'cues': scene.get('cues', []),
        })

        if len(final) > 0:
            final = np.concatenate([final, np.zeros(ms_to_samples(scene_gap_ms, sr), dtype=np.float32)])
        final = np.concatenate([final, scene_audio])

    final = final * db_to_amp(float(story.get('master_gain_db', 0.0)))
    final = normalize(final, peak=0.92)
    wav_out = BUILD / 'final_mix.wav'
    mp3_out = BUILD / 'final_mix.mp3'
    write_wav(wav_out, final, sr)

    run([
        shutil.which('ffmpeg') or 'ffmpeg', '-y', '-loglevel', 'error',
        '-i', str(wav_out), '-codec:a', 'libmp3lame', '-q:a', '2', str(mp3_out),
    ])

    duration = subprocess.check_output([
        shutil.which('ffprobe') or 'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', str(mp3_out)
    ], text=True).strip()

    manifest['final_wav'] = str(wav_out)
    manifest['final_mp3'] = str(mp3_out)
    manifest['duration_seconds'] = float(duration)
    (BUILD / 'render_manifest.json').write_text(json.dumps(manifest, indent=2))
    print(json.dumps({'final_mp3': str(mp3_out), 'duration_seconds': float(duration)}, indent=2))


if __name__ == '__main__':
    main()
