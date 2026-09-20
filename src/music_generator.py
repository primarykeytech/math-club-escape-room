"""
Synthesizer for retro 8-bit Game Boy menacing theme music.
Generates an authentic looping chiptune track in D minor.
"""
import os
import wave
import numpy as np

SAMPLE_RATE = 44100

def note_to_freq(note_name: str) -> float:
    """Convert note name like 'D4', 'C#3', 'Bb2' to Hz frequency."""
    pitch_map = {
        'C': 0, 'C#': 1, 'DB': 1, 'D': 2, 'D#': 3, 'EB': 3, 'E': 4,
        'F': 5, 'F#': 6, 'GB': 6, 'G': 7, 'G#': 8, 'AB': 8, 'A': 9,
        'A#': 10, 'BB': 10, 'B': 11
    }
    p = note_name[:-1].upper()
    octave = int(note_name[-1])
    semitone = pitch_map[p] + (octave - 4) * 12 - 9
    return 440.0 * (2.0 ** (semitone / 12.0))

def generate_pulse_wave(freq: float, duration: float, duty_cycle: float = 0.5, volume: float = 0.25) -> np.ndarray:
    """Generate pulse wave with specified duty cycle (e.g. 0.125, 0.25, 0.5 for Game Boy)."""
    n_samples = int(SAMPLE_RATE * duration)
    if n_samples <= 0:
        return np.array([])
    t = np.linspace(0, duration, n_samples, False)
    phase = (t * freq) % 1.0
    wave = np.where(phase < duty_cycle, 1.0, -1.0)

    # Apply 8-bit amplitude quantization (16 levels)
    wave = np.round(wave * 7.5) / 7.5

    # ADSR Envelope
    attack = min(int(SAMPLE_RATE * 0.01), n_samples // 4)
    release = min(int(SAMPLE_RATE * 0.04), n_samples // 4)
    env = np.ones(n_samples)
    if attack > 0:
        env[:attack] = np.linspace(0.1, 1.0, attack)
    if release > 0:
        env[-release:] = np.linspace(1.0, 0.0, release)

    return wave * env * volume

def generate_triangle_wave(freq: float, duration: float, volume: float = 0.35) -> np.ndarray:
    """Generate 4-bit stepped triangle wave characteristic of Game Boy wave channel."""
    n_samples = int(SAMPLE_RATE * duration)
    if n_samples <= 0:
        return np.array([])
    t = np.linspace(0, duration, n_samples, False)
    phase = (t * freq) % 1.0
    tri = 2.0 * np.abs(2.0 * phase - 1.0) - 1.0
    # 4-bit quantization (16 distinct volume steps)
    tri = np.round(tri * 7.5) / 7.5

    # Slight release to avoid pop
    release = min(int(SAMPLE_RATE * 0.015), n_samples // 4)
    env = np.ones(n_samples)
    if release > 0:
        env[-release:] = np.linspace(1.0, 0.0, release)

    return tri * env * volume

def generate_noise_hit(duration: float, volume: float = 0.12) -> np.ndarray:
    """Generate Game Boy LFSR-style periodic noise hit."""
    n_samples = int(SAMPLE_RATE * duration)
    if n_samples <= 0:
        return np.array([])
    # Pseudo-random noise with fast exponential decay
    raw = np.random.choice([-1.0, -0.5, 0.0, 0.5, 1.0], size=n_samples)
    t = np.linspace(0, duration, n_samples, False)
    env = np.exp(-t * 35.0)
    return raw * env * volume

def compose_menacing_theme() -> np.ndarray:
    """Compose and synthesize an authentic 8-bar looping menacing chiptune."""
    bpm = 108.0
    beat = 60.0 / bpm
    bar = beat * 4.0
    sixteenth = beat / 4.0
    total_duration = 8.0 * bar
    total_samples = int(SAMPLE_RATE * total_duration)

    mix = np.zeros(total_samples, dtype=np.float64)

    def add_sound(audio: np.ndarray, start_time: float):
        nonlocal mix
        idx = int(start_time * SAMPLE_RATE)
        end_idx = min(idx + len(audio), len(mix))
        length = end_idx - idx
        if length > 0:
            mix[idx:end_idx] += audio[:length]

    # --- 1. BASS CHANNEL (Driving, ominous, tritone tension) ---
    bass_pattern = [
        # Bar 1-2: D minor tension
        ('D2', beat * 0.75), ('D2', beat * 0.25), ('Eb2', beat * 0.5), ('D2', beat * 0.5),
        ('D2', beat * 0.5), ('Ab1', beat * 0.5), ('A1', beat * 1.0),
        ('D2', beat * 0.75), ('D2', beat * 0.25), ('F2', beat * 0.5), ('D2', beat * 0.5),
        ('C#2', beat * 1.0), ('A1', beat * 1.0),
        # Bar 3-4: Bb chromatic descent
        ('Bb1', beat * 0.75), ('Bb1', beat * 0.25), ('D2', beat * 0.5), ('Bb1', beat * 0.5),
        ('A1', beat * 1.0), ('G#1', beat * 1.0),
        ('G1', beat * 0.75), ('G1', beat * 0.25), ('Bb1', beat * 0.5), ('G1', beat * 0.5),
        ('A1', beat * 1.0), ('C#2', beat * 1.0),
        # Bar 5-6: Ascending diminished march
        ('D2', beat * 0.75), ('F2', beat * 0.25), ('Ab2', beat * 0.5), ('F2', beat * 0.5),
        ('A2', beat * 1.0), ('Ab2', beat * 1.0),
        ('F2', beat * 0.75), ('D2', beat * 0.25), ('Eb2', beat * 0.5), ('D2', beat * 0.5),
        ('C#2', beat * 1.0), ('Eb2', beat * 1.0),
        # Bar 7-8: Final cadence
        ('Bb1', beat * 1.0), ('A1', beat * 1.0),
        ('G#1', beat * 1.0), ('A1', beat * 1.0),
        ('Bb1', beat * 0.5), ('A1', beat * 0.5), ('G1', beat * 0.5), ('F1', beat * 0.5),
        ('E1', beat * 1.0), ('C#2', beat * 1.0),
    ]

    curr_time = 0.0
    for note, dur in bass_pattern:
        freq = note_to_freq(note)
        wave_data = generate_triangle_wave(freq, dur * 0.92, volume=0.32)
        add_sound(wave_data, curr_time)
        curr_time += dur

    # --- 2. LEAD MELODY CHANNEL (Nasal 25% pulse, haunting motif) ---
    lead_notes = [
        # Bar 1-2
        ('D4', beat * 1.5), ('F4', beat * 0.5), ('E4', beat * 1.0), ('C#4', beat * 1.0),
        ('D4', beat * 3.0), ('REST', beat * 1.0),
        # Bar 3-4
        ('F4', beat * 1.5), ('Ab4', beat * 0.5), ('G4', beat * 1.0), ('Eb4', beat * 1.0),
        ('E4', beat * 2.5), ('C#4', beat * 0.5), ('A3', beat * 1.0),
        # Bar 5-6
        ('A4', beat * 1.5), ('Bb4', beat * 0.5), ('A4', beat * 1.0), ('G#4', beat * 1.0),
        ('A4', beat * 2.0), ('F4', beat * 1.0), ('D4', beat * 1.0),
        # Bar 7-8
        ('Eb4', beat * 1.5), ('D4', beat * 0.5), ('C#4', beat * 1.0), ('E4', beat * 1.0),
        ('D4', beat * 3.0), ('REST', beat * 1.0),
    ]

    curr_time = 0.0
    for note, dur in lead_notes:
        if note != 'REST':
            freq = note_to_freq(note)
            wave_data = generate_pulse_wave(freq, dur * 0.90, duty_cycle=0.25, volume=0.22)
            add_sound(wave_data, curr_time)
        curr_time += dur

    # --- 3. RAPID ARPEGGIO CHANNEL (12.5% duty cycle, eerie polyphony) ---
    chords = [
        # Bar 1-2: D minor (D3, F3, A3, C#4)
        ['D3', 'F3', 'A3', 'C#4'],
        # Bar 3-4: Bb / G#dim (Bb2, D3, F3, G#3)
        ['BB2', 'D3', 'F3', 'G#3'],
        # Bar 5-6: Dmin / Adim (D3, F3, AB3, D4)
        ['D3', 'F3', 'AB3', 'D4'],
        # Bar 7-8: A7 / Dmin (A2, C#3, E3, G3)
        ['A2', 'C#3', 'E3', 'G3'],
    ]

    curr_time = 0.0
    for chord in chords:
        # Play for 2 bars = 32 sixteenths
        for step in range(32):
            note = chord[step % len(chord)]
            freq = note_to_freq(note)
            wave_data = generate_pulse_wave(freq, sixteenth * 0.75, duty_cycle=0.125, volume=0.09)
            add_sound(wave_data, curr_time)
            curr_time += sixteenth

    # --- 4. NOISE DRUM CHANNEL (Subtle slow march / ticking clock) ---
    curr_time = 0.0
    total_beats = 32
    for b in range(total_beats):
        if b % 2 == 1:
            # Snare/noise hit on beats 2 and 4
            noise = generate_noise_hit(0.08, volume=0.10)
            add_sound(noise, curr_time)
        else:
            # Soft hi-hat tick on beats 1 and 3
            tick = generate_noise_hit(0.02, volume=0.04)
            add_sound(tick, curr_time)
        curr_time += beat

    # Master volume normalization to prevent clipping
    max_amp = np.max(np.abs(mix))
    if max_amp > 0:
        mix = mix / max_amp * 0.85

    return mix

def build_menacing_theme_wav(dest_path: str = "assets/sounds/menacing_theme.wav") -> str:
    """Generate and save the menacing theme audio file."""
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    audio = compose_menacing_theme()
    audio_int16 = (audio * 32767).astype(np.int16)

    with wave.open(dest_path, "wb") as wf:
        wf.setnchannels(1)       # Mono
        wf.setsampwidth(2)      # 16-bit
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_int16.tobytes())

    return dest_path

if __name__ == "__main__":
    out = build_menacing_theme_wav()
    print(f"Menacing theme created at: {out}")
