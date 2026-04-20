# Hermes Audio Drama Implementation Plan

> **For Hermes:** Use the audio-drama-production skill to implement this plan task-by-task.

**Goal:** Build a reusable workflow and first English demo audio drama about Denis and his AI companion Aishka, with alternating voices and timed background sounds.

**Architecture:** Use a manifest-driven pipeline. Keep the story, voices, and sound cues in YAML/JSON files; render dialogue with Edge TTS; synthesize simple background ambiences and cues in Python/Numpy; mix and export the final audio with ffmpeg-compatible WAV/MP3 outputs.

**Tech Stack:** Python 3.11, Edge TTS, ffmpeg/ffprobe, numpy, YAML.

---

## Scope
- Create a reusable Hermes skill for audio-drama production.
- Create a project folder with screenplay, voice config, render script, and output artifacts.
- Translate the provided Russian story into concise English audio-drama scenes.
- Render an initial demo audio file.

## Non-goals
- Full cinematic SFX library.
- Human voice acting.
- Browser/UI video generation.

## Milestones
1. Define workflow and create Hermes skill.
2. Create screenplay and asset manifest.
3. Implement renderer for TTS + ambience + cue timing.
4. Render and verify demo audio.

## Expected Files
- `/root/projects/hermes-audio-drama/plan.md`
- `/root/projects/hermes-audio-drama/docs/concept.md`
- `/root/projects/hermes-audio-drama/assets/story.yaml`
- `/root/projects/hermes-audio-drama/assets/voices.yaml`
- `/root/projects/hermes-audio-drama/scripts/render_audio_drama.py`
- `/root/projects/hermes-audio-drama/build/...`
- Hermes skill: `~/.hermes/skills/creative/audio-drama-production/`

## Validation Strategy
- Confirm selected voices exist in edge-tts.
- Validate manifest parses correctly.
- Render all line audio files successfully.
- Produce final WAV and MP3.
- Verify output duration with ffprobe.

## Risks / Assumptions
- Synthetic ambience will be stylized rather than photorealistic.
- TTS timing varies slightly by line length, so cue alignment will be phrase-level rather than sample-perfect.
- English script should stay concise for a first demo.

## Definition of Done
- Skill exists and documents the workflow.
- English script exists with role switches and sound cues.
- Render script generates an audio drama with male Denis voice and female Aishka voice.
- Final MP3 is available for listening.