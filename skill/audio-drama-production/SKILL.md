---
name: audio-drama-production
description: Create short audio dramas from a story brief using multiple TTS voices, timed ambience, and a manifest-driven render pipeline.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  author: web3blind
  hermes:
    tags: [audio, tts, sound-design, storytelling, edge-tts, ffmpeg]
    category: creative
    related_skills: [article-to-tts-audio, songwriting-and-ai-music]
    requires_toolsets: [terminal, file, skill_manage]
---

# Audio Drama Production

Use when the user wants to turn a written story, scene outline, or concept into a short audio drama with:
- multiple voices,
- explicit speaker switching,
- timed background sounds,
- a final renderable audio file.

This skill is optimized for Hermes-first workflows where the goal is a polished demo fast, not a full DAW production.

## Core Deliverables

Create these artifacts:
1. `plan.md` — brief implementation plan.
2. `docs/concept.md` — one-page concept, format, tone, target duration.
3. `assets/story.yaml` — canonical screenplay/manifest.
4. `assets/voices.yaml` — role → voice mapping.
5. `scripts/render_audio_drama.py` — render pipeline.
6. `build/final_mix.wav` and `build/final_mix.mp3`.
7. `build/render_manifest.json` — durations and generated files.

## Recommended Format

Keep the first demo short:
- 3 to 5 minutes total
- 6 to 10 scenes
- 2 or 3 speaking roles max
- 4 to 7 ambience types reused across scenes

A short, coherent piece beats a long rough piece.

## Voice Casting Rules

Pick voices that contrast clearly.

Recommended default pair for English:
- human male protagonist: `en-US-AndrewNeural`
- female AI companion: `en-US-AvaNeural`

Alternatives:
- protagonist: `en-US-BrianNeural`, `en-GB-RyanNeural`
- AI companion: `en-US-AriaNeural`, `en-US-EmmaNeural`, `en-US-JennyNeural`

Guidelines:
- protagonist should sound grounded and conversational
- AI companion should sound clear, warm, and slightly more precise
- avoid two voices with nearly identical timbre

## Story Adaptation Rules

Translate/adapt the story for oral performance, not literal reading.

### Keep
- the emotional arc
- the turning points
- the repeated ritual / nightly posting loop
- the final message of persistence and community

### Compress
- repetitive UI descriptions
- purely visual details that do not help in audio
- long explanations that can become one line plus a sound cue

### Replace visual-only moments with audio signals
- screen updates → AI voice status messages / notification chimes
- time shifts → clock chime, ambience changes, narration cue
- browsing / multitasking → tabs clicks, keyboard, soft interface beeps
- walks outside → footsteps, city/park ambience, phone memo cue

## Manifest Structure

Store the screenplay in `assets/story.yaml`.

Recommended scene schema:

```yaml
title: Aishka and the Blog
sample_rate: 24000
scenes:
  - id: intro-night
    ambience: room_night
    intro_pause_ms: 600
    lines:
      - speaker: narrator
        text: "April seventeenth, twenty twenty-six. Denis sits at his computer."
      - speaker: denis
        text: "Aishka, help me shape tonight's blog post."
      - speaker: aishka
        text: "Searching for information."
    cues:
      - type: typing
        start_ms: 1200
        duration_ms: 2600
        level: 0.18
      - type: notification
        start_ms: 6800
        duration_ms: 700
        level: 0.35
```
```

Minimal fields per line:
- `speaker`
- `text`

Useful optional per-line fields:
- `pause_after_ms`
- `rate`
- `pitch`
- `volume_db`

## Ambience Palette

For a fast first demo, synthesize stylized ambience instead of hunting for sound libraries.

Recommended reusable palette:
- `room_night` — low HVAC hum + very soft room noise
- `room_morning` — lighter hum + subtle bird-like tones
- `typing` — click bursts
- `notification` — short soft digital chime
- `walk_outside` — filtered noise + footstep thumps
- `thinking_ai` — gentle digital pulses
- `success_glow` — warm confirm chime
- `ad_research` — light UI beeps + scrolling pulse texture

These cues do not need realism; they need readability.

## Rendering Workflow

1. Validate voice names with `edge-tts --list-voices`.
2. Save story and voice manifests.
3. Render each dialogue line to MP3/WAV.
4. Normalize all spoken lines to one sample rate.
5. Generate ambience beds and one-shot cues.
6. Mix scene by scene on a shared timeline.
7. Export WAV master.
8. Encode MP3 deliverable.
9. Verify durations with `ffprobe`.
10. Save a JSON manifest with scene and line timings.

## Mixing Rules

- speech must always dominate ambience
- ambience is support, not the main event
- use short pauses between lines so the scene can breathe
- switch voices only at line boundaries
- when an AI status sequence appears, keep ambience low and let the AI rhythm lead
- for emotional scenes, reduce cue density instead of adding more sounds

## Verification Checklist

Before delivery, confirm:
- all scenes rendered
- no missing voice files
- final MP3 exists
- final audio duration is plausible for the script length
- female AI voice is used consistently for the AI character
- background sounds appear in the intended moments

## Pitfalls

- Literal translation often sounds stiff. Rewrite for speech.
- Too many cues makes the piece feel noisy.
- Long scenes without pauses flatten the drama.
- Two similar TTS voices make character switches hard to follow.
- Background sounds must be timed intentionally; random ambience everywhere weakens the piece.

## Fast Default for This User's Story

If the story is about Denis and his AI companion building a blog:
- role names: `denis`, `aishka`
- tone: reflective, resilient, warm
- duration target: ~4 minutes
- structure: struggle → iteration → improvement → community → payoff
- tagline: `A blind-first audio drama about building with an AI companion.`
