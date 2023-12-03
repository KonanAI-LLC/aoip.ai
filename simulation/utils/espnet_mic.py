from espnet2.bin.enh_inference_streaming import SeparateSpeechStreaming
import torch

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

# Open the input stream
stream_in = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=frame_size, input_device_index=device_index)

# Prepare to write the separated audio to WAV files
output_wave_files = [wave.open(f'separated_2_channel_mic_{i}.wav', 'wb') for i in range(separate_speech.num_spk)]
for output_wave_file in output_wave_files:
    output_wave_file.setnchannels(1)
    output_wave_file.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    output_wave_file.setframerate(44100)

try:
    while True:
        # Read a frame from the microphone input stream
        frames = stream_in.read(frame_size)
        waveform_in = np.frombuffer(frames, dtype=np.int16)

        # Normalize and convert to tensor
        waveform_tensor = torch.tensor(waveform_in).unsqueeze(0).float() / 32768.0

        # Pass the waveform through the separation model
        with torch.no_grad():
            separated_waveforms = separate_speech(waveform_tensor)

        # Convert separated waveforms to bytes and write to output WAV files
        for i, waveform in enumerate(separated_waveforms):
            separated_data = (waveform.squeeze().numpy() * 32768.0).astype(np.int16).tobytes()
            output_wave_files[i].writeframes(separated_data)


except KeyboardInterrupt:
    print('Streaming stopped by user')

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the input stream
    stream_in.stop_stream()
    stream_in.close()

    # Close the output wave files
    for output_wave_file in output_wave_files:
        output_wave_file.close()

    # Terminate PyAudio
    p.terminate()

print("Processing complete.")