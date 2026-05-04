import math
import struct
import wave
from pathlib import Path


SAMPLE_RATE = 44_100
DURATION = 24.0
BPM = 124
BEAT = 60.0 / BPM
OUT = Path("assets/polimiru-original-tech-beat.wav")


def midi_to_hz(note):
    return 440.0 * (2 ** ((note - 69) / 12))


def env(t, start, length, attack=0.01, release=0.08):
    local = t - start
    if local < 0 or local >= length:
        return 0.0
    if local < attack:
        return local / attack
    if local > length - release:
        return max(0.0, (length - local) / release)
    return 1.0


def soft_saw(phase):
    return 0.5 * math.sin(phase) + 0.18 * math.sin(2 * phase) + 0.07 * math.sin(3 * phase)


def pluck(t, start, note, length=0.24, gain=0.13):
    e = env(t, start, length, attack=0.006, release=0.18)
    if e == 0:
        return 0.0
    local = t - start
    hz = midi_to_hz(note)
    body = 0.7 * math.sin(2 * math.pi * hz * local)
    shimmer = 0.55 * math.sin(2 * math.pi * hz * 2.01 * local)
    return gain * e * (body + shimmer)


def pad(t, start, notes, length, gain=0.035):
    e = env(t, start, length, attack=0.22, release=0.42)
    if e == 0:
        return 0.0
    local = t - start
    wobble = 1.0 + 0.035 * math.sin(2 * math.pi * 0.42 * local)
    total = 0.0
    for note in notes:
        hz = midi_to_hz(note)
        total += 0.7 * math.sin(2 * math.pi * hz * wobble * local)
        total += 0.25 * math.sin(2 * math.pi * (hz * 2.0) * local)
    return gain * e * total / max(1, len(notes))


def kick(t, start):
    local = t - start
    if local < 0 or local > 0.22:
        return 0.0
    e = math.exp(-local * 18)
    hz = 78 - 28 * min(1, local / 0.12)
    click = math.exp(-local * 95) * math.sin(2 * math.pi * 880 * local)
    return 0.34 * e * math.sin(2 * math.pi * hz * local) + 0.05 * click


def snare(t, start):
    local = t - start
    if local < 0 or local > 0.18:
        return 0.0
    noise = math.sin(2 * math.pi * 1731 * local) * math.sin(2 * math.pi * 977 * local)
    tone = math.sin(2 * math.pi * 190 * local)
    e = math.exp(-local * 22)
    return 0.13 * e * noise + 0.05 * e * tone


def hat(t, start, gain=0.052):
    local = t - start
    if local < 0 or local > 0.055:
        return 0.0
    noise = math.sin(2 * math.pi * 7013 * local) * math.sin(2 * math.pi * 3229 * local)
    return gain * math.exp(-local * 72) * noise


def riser(t):
    if t < 18.8 or t > 21.2:
        return 0.0
    x = (t - 18.8) / 2.4
    hz = 520 + 980 * x * x
    return 0.045 * x * math.sin(2 * math.pi * hz * (t - 18.8))


chords = [
    [62, 66, 69, 74],  # D add9
    [57, 61, 64, 69],  # A add9
    [59, 62, 66, 71],  # Bm7, softened by bright top line
    [55, 59, 62, 67],  # G add9
]
arp = [74, 78, 81, 86, 81, 78, 76, 74]


def bell(t, start, note, gain=0.07):
    e = env(t, start, 0.42, attack=0.004, release=0.34)
    if e == 0:
        return 0.0
    local = t - start
    hz = midi_to_hz(note)
    return gain * e * (
        math.sin(2 * math.pi * hz * local)
        + 0.48 * math.sin(2 * math.pi * hz * 2.01 * local)
        + 0.18 * math.sin(2 * math.pi * hz * 3.02 * local)
    )


def sample_at(t):
    value = 0.0
    chord_len = BEAT * 4

    for i in range(int(DURATION / chord_len) + 2):
        start = i * chord_len
        value += pad(t, start, chords[i % len(chords)], chord_len + 0.15)

    step = BEAT / 2
    for i in range(int(DURATION / step) + 1):
        start = i * step
        note = arp[i % len(arp)]
        value += pluck(t, start, note)

    hook_step = BEAT
    hook = [86, 85, 81, 78, 81, 83, 86, 90]
    for i in range(int(DURATION / hook_step) + 1):
        if i % 8 in (0, 2, 4, 6):
            value += bell(t, i * hook_step + BEAT * 0.08, hook[i % len(hook)])

    for i in range(int(DURATION / BEAT) + 2):
        b = i * BEAT
        if i % 4 in (0, 2):
            value += kick(t, b)
        if i % 4 == 1:
            value += kick(t, b + BEAT * 0.5) * 0.55
        if i % 4 in (1, 3):
            value += snare(t, b)
        value += hat(t, b, 0.045)
        value += hat(t, b + BEAT * 0.5, 0.03)

    value += riser(t)

    if t < 0.35:
        value *= t / 0.35
    if t > DURATION - 1.4:
        value *= max(0.0, (DURATION - t) / 1.4)

    return max(-0.96, min(0.96, value * 0.62))


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    total = int(SAMPLE_RATE * DURATION)
    with wave.open(str(OUT), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        for n in range(total):
            t = n / SAMPLE_RATE
            left = sample_at(t)
            right = sample_at(t + 0.006) * 0.96
            wav.writeframes(struct.pack("<hh", int(left * 32767), int(right * 32767)))
    print(OUT)


if __name__ == "__main__":
    main()
