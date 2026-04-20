# Render Notes

Recommended command flow:

1. Render dialogue with Edge TTS.
2. Convert each line to mono WAV at a shared sample rate.
3. Generate ambience/cues synthetically when a sound library is unavailable.
4. Mix in Python or ffmpeg.
5. Export both WAV and MP3.

Suggested levels:
- dialogue peak target: -3 dBFS to -6 dBFS
- room ambience: -28 dBFS to -22 dBFS
- one-shot cues: -18 dBFS to -12 dBFS unless intentionally foregrounded

A clear mix beats a realistic mix.
