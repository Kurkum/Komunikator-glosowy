import sounddevice as sd
import numpy as np

duration = 10.5  # seconds
fs = 44100
myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
sd.wait()