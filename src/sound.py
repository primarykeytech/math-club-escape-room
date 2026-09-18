"""
Procedural 8-bit audio synthesizer for retro Game Boy style sound effects.
Does not require external audio files.
"""
import numpy as np
import pygame

class RetroSoundFX:
    def __init__(self):
        self.enabled = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            self.sample_rate = 44100
            self.enabled = True
        except Exception:
            self.enabled = False

    def _generate_tone(self, freq: float, duration: float, wave_type: str = "square", volume: float = 0.3) -> pygame.mixer.Sound:
        if not self.enabled:
            return None
        n_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, n_samples, False)

        if wave_type == "square":
            wave = np.sign(np.sin(2 * np.pi * freq * t))
        elif wave_type == "triangle":
            wave = 2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1
        elif wave_type == "noise":
            wave = np.random.uniform(-1, 1, n_samples)
        else:
            wave = np.sin(2 * np.pi * freq * t)

        # Apply simple envelope to prevent clicking
        attack = int(self.sample_rate * 0.005)
        decay = int(self.sample_rate * 0.015)
        envelope = np.ones(n_samples)
        if attack > 0 and len(envelope) > attack:
            envelope[:attack] = np.linspace(0, 1, attack)
        if decay > 0 and len(envelope) > decay:
            envelope[-decay:] = np.linspace(1, 0, decay)

        sound_array = (wave * envelope * volume * 32767).astype(np.int16)
        # Check active mixer channels and adjust dimensions
        init_info = pygame.mixer.get_init()
        if init_info:
            _, _, channels = init_info
            if channels == 2:
                sound_array = np.column_stack((sound_array, sound_array))
        return pygame.sndarray.make_sound(sound_array)

    def play_key_click(self):
        if not self.enabled:
            return
        snd = self._generate_tone(880, 0.02, wave_type="square", volume=0.15)
        if snd:
            snd.play()

    def play_enter_click(self):
        if not self.enabled:
            return
        snd = self._generate_tone(1174, 0.06, wave_type="square", volume=0.2)
        if snd:
            snd.play()

    def play_error_buzz(self):
        if not self.enabled:
            return
        # Low buzz tone
        snd = self._generate_tone(140, 0.25, wave_type="square", volume=0.35)
        if snd:
            snd.play()

    def play_success_jingle(self):
        if not self.enabled:
            return
        # Quick 3-note arpeggio: C5 -> E5 -> G5
        notes = [523.25, 659.25, 783.99]
        total_samples = []
        for f in notes:
            n_samples = int(self.sample_rate * 0.08)
            t = np.linspace(0, 0.08, n_samples, False)
            wave = np.sign(np.sin(2 * np.pi * f * t)) * 0.25
            total_samples.extend(wave)
        sound_array = (np.array(total_samples) * 32767).astype(np.int16)
        init_info = pygame.mixer.get_init()
        if init_info:
            _, _, channels = init_info
            if channels == 2:
                sound_array = np.column_stack((sound_array, sound_array))
        snd = pygame.sndarray.make_sound(sound_array)
        snd.play()
