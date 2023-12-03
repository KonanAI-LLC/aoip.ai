import pyaudio
import numpy as np
import wave

def gain_normalize(waveform):
    amplitude = np.iinfo(np.int16).max
    waveform  = np.int16(0.8 * amplitude * waveform / np.max(np.abs(waveform)))
    return waveform

# Initialize PyAudio
p = pyaudio.PyAudio()

# Find the device index of the virtual microphone
device_index = None
for i in range(p.get_device_count()):
    device_info = p.get_device_info_by_index(i)
    if device_info['name'] == 'pulse':
        device_index = i
        break

if device_index is None:
    print('Could not find virtual microphone')
    exit(1)

# Open the input and output streams
stream_in = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024, input_device_index=device_index)

# Open a .wav file for writing
wav_file = wave.open('gain.wav', 'wb')
wav_file.setnchannels(1)
wav_file.setsampwidth(p.get_sample_size(pyaudio.paInt16))
wav_file.setframerate(44100)

while True:
    # Read from the input stream
    data_in = stream_in.read(1024)
    # Convert the data to a NumPy array
    waveform_in = np.frombuffer(data_in, dtype=np.int16)
    # Perform gain normalization
    waveform_out = gain_normalize(waveform_in)
    # Convert the NumPy array back to bytes
    data_out = waveform_out.tobytes()
    # Write to the .wav file
    wav_file.writeframes(data_out)

# Close the streams
stream_in.stop_stream()
stream_in.close()

# Close the .wav file
wav_file.close()

# Terminate PyAudio
p.terminate()