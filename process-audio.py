import numpy as np
from scipy.fft import fft
import wave
import json
import sys
import os
import subprocess

def convert_to_wav(input_file):
    """Convert audio file to WAV format using ffmpeg."""
    output_file = input_file + '.wav'
    subprocess.run([
        'ffmpeg', '-i', input_file,
        '-acodec', 'pcm_s16le',  # 16-bit PCM
        '-ar', '44100',          # 44.1kHz sample rate
        '-ac', '1',              # mono
        '-y',                    # overwrite output file
        output_file
    ], check=True, capture_output=True)
    return output_file

def process_chunk(chunk, chunk_size):
    """Process a chunk of audio data using FFT."""
    # Apply Hanning window to reduce spectral leakage
    window = np.hanning(len(chunk))
    chunk = chunk * window
    
    # Compute FFT
    fft_data = fft(chunk)
    # Get magnitude of first half (second half is redundant for real signals)
    fft_data = np.abs(fft_data[:len(fft_data)//2])
    
    # Use a modified logarithmic scale that starts higher to reduce bass dominance
    # Create a more balanced distribution with slight right shift
    freq_range = np.concatenate([
        np.linspace(50, 200, 10),     # Bass region
        np.linspace(200, 500, 15),    # Low-mids
        np.linspace(500, 1000, 15),   # Mid frequencies
        np.linspace(1000, 2000, 15),  # Upper mids
        np.logspace(np.log10(2000), np.log10(20000), 15)  # High frequencies
    ])
    
    bands = []
    for i in range(len(freq_range) - 1):
        # Convert frequencies to FFT indices
        start_idx = int((freq_range[i] * len(fft_data)) / (44100/2))
        end_idx = int((freq_range[i+1] * len(fft_data)) / (44100/2))
        # Ensure we have at least one sample per band
        end_idx = max(start_idx + 1, end_idx)
        # Get the mean amplitude for this frequency range
        band = np.mean(fft_data[start_idx:end_idx])
        bands.append(band)
    
    # Normalize and apply some smoothing
    bands = np.array(bands)
    if bands.max() > 0:
        bands = bands / bands.max()
        # Scale down more to prevent overflow
        bands = bands * 0.7  # Increased from 0.6 to 0.7 for more presence
        
    # Apply a gentle boost to mid and upper frequencies
    boost = np.linspace(1.0, 1.2, len(bands))  # Progressive boost from left to right
    bands *= boost
    
    return bands.tolist()

def process_audio_file(audio_path):
    """Process an audio file and return frequency band data over time."""
    # If not a WAV file, convert it first
    temp_wav = None
    if not audio_path.lower().endswith('.wav'):
        try:
            temp_wav = convert_to_wav(audio_path)
            audio_path = temp_wav
        except Exception as e:
            print(f"Error converting audio file: {e}")
            sys.exit(1)

    try:
        # Open the WAV file
        with wave.open(audio_path, 'rb') as wav_file:
            # Get audio properties
            n_channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            framerate = wav_file.getframerate()
            n_frames = wav_file.getnframes()
            
            # Read raw audio data
            raw_data = wav_file.readframes(n_frames)
            
            # Convert to numpy array
            data = np.frombuffer(raw_data, dtype=np.int16)
            
            # If stereo, convert to mono by averaging channels
            if n_channels == 2:
                data = data.reshape(-1, 2).mean(axis=1)
            
            # Convert to float and normalize
            data = data.astype(float)
            if data.max() != 0:
                data = data / np.max(np.abs(data))
            
            # Process audio in chunks
            chunk_size = framerate // 30  # 30 fps -> chunk size for ~1 frame
            n_chunks = len(data) // chunk_size
            
            # Store frequency data for each chunk
            frequency_data = []
            for i in range(n_chunks):
                start = i * chunk_size
                end = start + chunk_size
                chunk = data[start:end]
                if len(chunk) == chunk_size:  # Only process full chunks
                    bands = process_chunk(chunk, chunk_size)
                    # Normalize bands for visualization
                    if max(bands) > 0:
                        bands = np.array(bands) / max(bands)
                    bands = (bands * 15).tolist()  # Scale to roughly half display height
                    frequency_data.append(bands)
            
            # Clean up temporary file if we created one
            if temp_wav:
                os.remove(temp_wav)
            
            return frequency_data
            
    except Exception as e:
        print(f"Error processing audio file: {e}")
        if temp_wav and os.path.exists(temp_wav):
            os.remove(temp_wav)
        sys.exit(1)

def save_waveform(frequency_data, output_path):
    """Save the frequency data to a JSON file."""
    with open(output_path, 'w') as f:
        json.dump(frequency_data, f)

def main():
    # Fixed paths
    audio_path = "sample/audio.mp3"
    output_path = "sample/waveform.json"
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--simulator-only":
        print("Starting simulator...")
        subprocess.run(['python', 'simulator.py', output_path])
        return
    
    run_simulator = len(sys.argv) > 1 and sys.argv[1] == "--simulator"
    
    if not os.path.exists(audio_path):
        print(f"Error: Audio file '{audio_path}' not found")
        sys.exit(1)
    
    print(f"Processing audio file: {audio_path}")
    frequency_data = process_audio_file(audio_path)
    save_waveform(frequency_data, output_path)
    print(f"Frequency data saved to: {output_path}")
    
    # Run the simulator if requested
    if run_simulator:
        print("Starting simulator...")
        subprocess.run(['python', 'simulator.py', output_path])
    else:
        print("To run the simulator, use: python process_audio.py --simulator")
        print("To run only the simulator, use: python process_audio.py --simulator-only")

if __name__ == "__main__":
    main() 