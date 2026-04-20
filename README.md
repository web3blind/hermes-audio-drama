# Hermes Audio Drama

Blind-first creative tooling for audio storytelling with Hermes Agent.

This repository contains:
- a reusable Hermes skill for multi-voice audio drama production,
- a manifest-driven renderer based on Edge TTS + synthetic ambience,
- a finished English demo audio drama: "Aishka and the Blog".

## What it does

The workflow turns a story brief into a short audio drama with:
- multiple TTS voices,
- explicit speaker switching,
- timed background sound cues,
- final WAV/MP3 export,
- a render manifest with scene and line timings.

The first included demo is based on Denis building his blog together with Aishka, his AI companion.

## Included demo

- Final audio: `build/final_mix.mp3`
- Render metadata: `build/render_manifest.json`
- Story manifest: `assets/story.yaml`
- Voice mapping: `assets/voices.yaml`

## Repository structure

```text
assets/
  story.yaml
  voices.yaml
build/
  final_mix.mp3
  render_manifest.json
docs/
  concept.md
scripts/
  render_audio_drama.py
skill/
  audio-drama-production/
    SKILL.md
    templates/
    references/
plan.md
README.md
```

## Requirements

Python packages:
- `numpy`
- `PyYAML`
- `edge-tts`

System tools:
- `ffmpeg`
- `ffprobe`

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Make sure `ffmpeg` and `ffprobe` are available in `PATH`.

## Render the demo

```bash
python3 scripts/render_audio_drama.py
```

Expected output:
- `build/final_mix.wav`
- `build/final_mix.mp3`
- `build/render_manifest.json`

## How the pipeline works

1. Read `assets/story.yaml` and `assets/voices.yaml`
2. Render each spoken line with Edge TTS
3. Convert lines to a common mono WAV format
4. Synthesize stylized ambience and one-shot cues in Python
5. Mix scene-by-scene on a shared timeline
6. Export WAV + MP3 and save timing metadata

## Voice casting in the demo

- Denis: `en-US-AndrewNeural`
- Aishka: `en-US-AvaNeural`

Aishka is intentionally voiced as female.

## Why this matters

Most creative-agent demos are visual-first. This project explores an alternative:

text-driven, audio-first, accessible creative tooling.

That makes it a fit for:
- audio storytelling,
- creative agent workflows,
- accessibility-focused creative software,
- hackathon demos where the tool is part of the creative output.

## Hermes skill

The reusable Hermes skill lives in:

- `skill/audio-drama-production/SKILL.md`

It includes templates and notes for creating new short audio dramas with the same workflow.

## Notes

- Background sounds are synthetic and stylized by design.
- The goal is readability and atmosphere, not full cinematic realism.
- The first demo is intentionally short and hackathon-friendly.

## License

MIT
