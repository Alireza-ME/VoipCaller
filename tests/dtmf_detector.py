import pyaudio
import numpy as np
import scipy.fftpack

# Audio stream configuration
FORMAT = pyaudio.paInt16  # Audio format: 16-bit signed integers
CHANNELS = 1  # Mono channel input (single microphone)
RATE = 44100  # Sample rate: 44100 samples per second (standard for audio)
CHUNK = 2048  # Number of frames per buffer (increasing this improves frequency resolution)

# Initialize PyAudio and open an audio input stream
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

# DTMF (Dual-Tone Multi-Frequency) frequency table
# Each key is associated with two distinct frequencies (one low frequency, one high frequency)
# These frequencies are used in telecommunication systems to represent digits
dtmf_frequencies = {
    '1': [697, 1209],  # Frequency pair for key '1'
    '2': [697, 1336],  # Frequency pair for key '2'
    '3': [697, 1477],  # Frequency pair for key '3'
    'A': [697, 1633],  # Frequency pair for key 'A'
    '4': [770, 1209],  # Frequency pair for key '4'
    '5': [770, 1336],  # Frequency pair for key '5'
    '6': [770, 1477],  # Frequency pair for key '6'
    'B': [770, 1633],  # Frequency pair for key 'B'
    '7': [852, 1209],  # Frequency pair for key '7'
    '8': [852, 1336],  # Frequency pair for key '8'
    '9': [852, 1477],  # Frequency pair for key '9'
    'C': [852, 1633],  # Frequency pair for key 'C'
    '*': [941, 1209],  # Frequency pair for key '*'
    '0': [941, 1336],  # Frequency pair for key '0'
    '#': [941, 1477],  # Frequency pair for key '#'
    'D': [941, 1633]   # Frequency pair for key 'D'
}

def detect_dtmf(signal, rate):
    """
    Detects the two dominant frequencies in the input audio signal using FFT.
    
    Args:
        signal (numpy array): The input audio signal in time-domain (1D array of int16 values).
        rate (int): The sample rate of the audio (e.g., 44100 Hz).

    Returns:
        list: A list containing the two highest frequency components found in the signal.
    """
    
    # Apply Fast Fourier Transform (FFT) to convert time-domain signal to frequency domain
    fft = np.abs(scipy.fftpack.fft(signal))
    
    # Generate the corresponding frequency values for the FFT results
    freqs = scipy.fftpack.fftfreq(len(signal), 1 / rate)

    # Take only the first half of the FFT result (positive frequencies)
    fft = fft[:len(fft) // 2]
    freqs = freqs[:len(freqs) // 2]

    # Find the indices of the two highest energy peaks in the FFT result
    peak_indices = np.argsort(fft)[-2:]  # Sort by amplitude and get indices of top 2
    peak_freqs = [freqs[i] for i in peak_indices]  # Convert indices to corresponding frequencies

    return peak_freqs  # Return the two dominant frequencies

def identify_key(frequencies):
    """
    Identifies the DTMF key based on the detected frequencies.

    Args:
        frequencies (list): A list of two detected frequencies.

    Returns:
        str: The corresponding DTMF key if found, otherwise None.
    """
    
    # Iterate over each DTMF key and its corresponding frequency pair
    for key, freqs in dtmf_frequencies.items():
        # Check if both the detected frequencies match the DTMF frequencies within a tolerance of 10 Hz
        # np.isclose ensures that the detected frequency is close enough to the target DTMF frequencies
        if all(any(np.isclose(f, freq, atol=10).any() for f in frequencies) for freq in freqs):
            return key  # Return the corresponding key if a match is found
    
    return None  # Return None if no match is found

try:
    print("Listening for DTMF tones...")
    
    # Continuous loop for real-time DTMF detection
    while True:
        # Read a chunk of audio data from the input stream and convert it to a numpy array of int16
        data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
        
        # Detect the two dominant frequencies in the captured audio signal
        freqs = detect_dtmf(data, RATE)
        
        # Identify the DTMF key that corresponds to the detected frequencies
        key = identify_key(freqs)
        
        # If a DTMF key is detected, print the key
        if key:
            print(f"Detected DTMF key: {key}")

except KeyboardInterrupt:
    # Gracefully handle the user interrupt (Ctrl+C)
    print("Recording stopped.")

finally:
    # Cleanup: Stop and close the audio stream, and terminate the PyAudio instance
    stream.stop_stream()
    stream.close()
    p.terminate()
