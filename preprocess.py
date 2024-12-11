import librosa
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sounddevice as sd
import json

def preprocess(filePath):
    print("Preprocess\n\n")
    vibrators_map = {
    "low": {"min": 20, "max": 200},         
    "mid": {"min": 200, "max": 2000},      
    "high": {"min": 2000, "max": 8000},     
    }
    y, sr = librosa.load(filePath, sr=None)

    hop_length = 2048
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop_length)
    beat_times = librosa.frames_to_time(beats, sr=sr, hop_length=hop_length)

    D = librosa.stft(y, hop_length=hop_length)
    frequencies = librosa.fft_frequencies(sr=sr)
    magnitude, _ = librosa.magphase(D)
    result = {}
    result['y'] = y.tolist()
    result["sr"] = sr
    result["beats"] = beats.tolist()
    for key in vibrators_map:
        min_freq = vibrators_map[key]['min']
        max_freq = vibrators_map[key]['max']
        current_mask = np.where((frequencies >= min_freq) & (frequencies < max_freq))[0]
        current_vibrator_energy = np.mean(magnitude[current_mask, :], axis=0)
        result[key] = current_vibrator_energy.tolist()
        if "stft_times" not in result:
            stft_times = librosa.frames_to_time(np.arange(current_vibrator_energy.shape[0]), sr=sr, hop_length=hop_length)
            result["stft_times"] = stft_times.tolist()
    with open(r'data/processed/vibration_pattern.json', 'w') as fp:
        json.dump(result, fp)

'''if __name__ == "__main__":
    
    #Trocar para qualqer arquivo .mp3
    filePath = librosa.example('nutcracker')
    vibrators_map = {
    "low": {"min": 20, "max": 200},         
    "mid": {"min": 200, "max": 2000},      
    "high": {"min": 2000, "max": 8000},     
}
    result = preprocess(filePath, vibrators_map)
    with open(r'data/processed/nutcracker_vibration_pattern.json', 'w') as fp:
        json.dump(result, fp)'''