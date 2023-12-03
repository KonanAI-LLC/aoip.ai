import wave
import torch
import numpy as np
from espnet2.bin.enh_inference_streaming import SeparateSpeechStreaming

# Initialize the speech separation model
separate_speech = SeparateSpeechStreaming.from_pretrained(
    "lichenda/wsj0_2mix_skim_small_causal",
    device='cpu',
    dtype='float32',
)

# get the frame size and hop size from the model (used for chunking the input)
frame_size = separate_speech.enh_model.encoder.kernel_size
hop_size = separate_speech.enh_model.encoder.stride

# Reset separator states
separate_speech.reset()

# Open the .wav file
input_wav_file = 'input.wav'
wave_file = wave.open(input_wav_file, 'rb')
sr = wave_file.getframerate()
assert wave_file.getnchannels() == 1, "Only mono files are supported."

# Prepare to write the separated audio to WAV files
output_wave_files = [wave.open(f'separated_channel_{i}.wav', 'wb') for i in range(separate_speech.num_spk)]
for output_wave_file in output_wave_files:
    output_wave_file.setnchannels(1)
    output_wave_file.setsampwidth(wave_file.getsampwidth())
    output_wave_file.setframerate(sr)

try:
    # Process the entire file in chunks matching the model's frame size
    while True:
        # Read a frame from the wav file
        frames = wave_file.readframes(frame_size)
        if len(frames) == 0:
            break  # We have reached the end of the file

        frames_array = np.frombuffer(frames, dtype=np.int16)

        # Ensure the last chunk is padded with zeros if it's shorter than the frame size
        if len(frames_array) < frame_size:
            frames_array = np.pad(frames_array, (0, frame_size - len(frames_array)), mode='constant')

        # Normalize and convert to tensor
        frames_tensor = torch.tensor(frames_array).unsqueeze(0).float() / 32768.0

        # Check if tensor needs to be reshaped
        if frames_tensor.ndim == 4:
            frames_tensor = frames_tensor.reshape(1, -1)

        # Pass the waveform through the separation model
        with torch.no_grad():
            separated_waveforms = separate_speech(frames_tensor)

        # Convert separated waveforms to bytes and write to output WAV files
        for i, waveform in enumerate(separated_waveforms):
            separated_data = (waveform.squeeze().numpy() * 32768.0).astype(np.int16).tobytes()
            output_wave_files[i].writeframes(separated_data)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the input wave file
    wave_file.close()

    # Close the output wave files
    for output_wave_file in output_wave_files:
        output_wave_file.close()

print("Processing complete.")
