# Author: A_lireza_ME
# How to run!
# 1. Install VAC from https://vac.muzychenko.net/en/download.htm
# 2. Install Visual C++ Redistributable (recommended: x64) from https://support.microsoft.com/en-us/help/2977003/the-latest-supported-visual-c-downloads
# 3. Open terminal and run `pip install -r requirements.txt` to install the dependencies.
# 4. For the PaddleOCR package, additional setup will occur during the first run.
# 5. Once setup is done, you can run the script.

import pyautogui
import pygame
import time
import os
import pandas as pd
import sys
import numpy as np
from paddleocr import PaddleOCR
from threading import Thread
from datetime import datetime
import pyaudio
import scipy.fftpack

# Function to save user click information to an Excel file
# Takes the phone number as input and appends a new entry with the current date and time.
def save_user_click_info(phone_number):
    file_name = 'user_click_info.xlsx'

    # Check if the file exists; if not, create a new DataFrame.
    if os.path.exists(file_name):
        df = pd.read_excel(file_name, engine='openpyxl')
    else:
        df = pd.DataFrame(columns=['PhoneNumber', 'Date'])

    # Add a new row with phone number and the current date and time.
    new_row = pd.DataFrame([{'PhoneNumber': phone_number, 'Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}])
    df = pd.concat([df, new_row], ignore_index=True)

    # Save the DataFrame back to the Excel file.
    df.to_excel(file_name, index=False, engine='openpyxl')

# Function to get the region of the screen for OCR
# Prompts the user to click on the top-left and bottom-right corners of the desired region.
def get_region():
    print("Please move to the top-left corner of the region you want to select and press Enter.")
    time.sleep(5)
    x1, y1 = pyautogui.position()
    print(f"Top-left coordinates: ({x1}, {y1})")

    print("Now move to the bottom-right corner of the region and press Enter.")
    time.sleep(5)
    x2, y2 = pyautogui.position()
    print(f"Bottom-right coordinates: ({x2}, {y2})")

    # Calculate the width and height of the region
    width = x2 - x1
    height = y2 - y1
    return (x1, y1, width, height)

# Function to get the position of the end call button
# Prompts the user to click on the end call button for automation purposes.
def get_end_call_button_position():
    print("Please move to the end call button and press Enter.")
    time.sleep(5)
    x, y = pyautogui.position()
    print(f"End call button coordinates: ({x}, {y})")
    return (x, y)

# Function to monitor the call status using OCR
# Captures screenshots of the defined region and uses OCR to detect call status (e.g., Idle or Connected).
def monitor_call(region):
    x1, y1, width, height = region
    ocr = PaddleOCR(use_angle_cls=True, lang='en')

    while True:
        try:
            # Take a screenshot of the defined region
            screenshot = pyautogui.screenshot(region=(x1, y1, width, height))
            image_np = np.array(screenshot)

            # Perform OCR to get the text
            result = ocr.ocr(image_np, cls=True)
            if result is None or len(result) == 0:
                print("OCR result is empty.")
                time.sleep(0.3)
                continue

            # Extract text from the OCR result
            text = ' '.join([line[1][0] for line in result[0]])

            print(text)

            # Detect if the call is idle or connected based on the OCR result
            if 'Idle' in text:
                print('Call has ended!')
                return False
            elif 'Connected' in text:
                print('Call accepted!')
                return True

        except Exception as e:
            print(f"Error in image processing or OCR: {e}")

        time.sleep(0.3)

# Function to play a sound during the call
# Plays an audio file located in the "voices" directory.
def play_sound():
    sound_file = 'voices/counsel-2.wav'
    pygame.mixer.init()

    # Check if the sound file exists and play it.
    if os.path.exists(sound_file):
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()

        # Wait until the sound finishes playing.
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    else:
        print(f"Sound file {sound_file} not found.")

# Function to read an Excel file and return its contents as a DataFrame
# Uses either openpyxl or xlrd to read the file, depending on the format.
def read_excel(file_path):
    if not os.path.isfile(file_path):
        print("File not found.")
        return None

    try:
        df = pd.read_excel(file_path, engine='openpyxl')
    except ValueError:
        try:
            df = pd.read_excel(file_path, engine='xlrd')
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            return None

    return df

# Function to process phone numbers from the Excel file
# Iterates through the list of numbers, automates dialing, and monitors the call.
def process_numbers(file_path):
    df = read_excel(file_path)
    if df is None:
        return

    phone_numbers = df.iloc[:, 0].dropna().tolist()
    num_numbers = len(phone_numbers)

    if num_numbers == 0:
        print("No phone numbers found for processing.")
        return

    region = get_region()  # Get the region for OCR
    end_call_button_position = get_end_call_button_position()  # Get the position of the end call button

    for phone_number in phone_numbers:
        time.sleep(1.5)

        if phone_number == 'PhoneNumber':
            print("All calls have ended.")
            sys.exit()

        print(f'Starting call with number: {phone_number}')
        pyautogui.typewrite(str(0) + str(phone_number))
        pyautogui.press('enter')

        # Monitor the call status using OCR
        call_established = monitor_call(region)

        if call_established:
            # Start playing the sound in a separate thread
            sound_thread = Thread(target=play_sound)
            sound_thread.start()

            # Wait for a specific time to ensure the sound is played fully
            time.sleep(2)  # Adjust based on sound length

            # Listen for keypresses or call status changes
            result = listen_for_keypresses(end_call_button_position, region, phone_number)

            # If the call ends, stop the sound and move to the next number
            if result == 'Idle':
                pygame.mixer.music.stop()
                sound_thread.join()
                print(f"Call with {phone_number} ended. Moving to the next number.")
                continue

        time.sleep(0.5)

# Bandpass filter helper functions
# These functions are used for filtering audio input to detect DTMF tones.
def butter_bandpass(lowcut, highcut, fs, order=5):
    from scipy.signal import butter
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, lowcut, highcut, fs, order=5):
    from scipy.signal import lfilter
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

# Function to listen for DTMF tones and handle call termination
# Detects DTMF tones using PyAudio and performs actions based on detected tones.
def listen_for_keypresses(end_call_button_position, region, phone_number):
    # Audio recording settings for PyAudio
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 2048

    # Open audio stream
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    # DTMF frequency table
    dtmf_frequencies = {
        '1': [697, 1209],
        '2': [697, 1336],
        '3': [697, 1477],
        'A': [697, 1633],
        '4': [770, 1209],
        '5': [770, 1336],
        '6': [770, 1477],
        'B': [770, 1633],
        '7': [852, 1209],
        '8': [852, 1336],
        '9': [852, 1477],
        'C': [852, 1633],
        '*': [941, 1209],
        '0': [941, 1336],
        '#': [941, 1477],
        'D': [941, 1633]
    }

    # Detect DTMF frequencies in the signal
    def detect_dtmf(signal, rate):
        fft = np.abs(scipy.fftpack.fft(signal))
        freqs = scipy.fftpack.fftfreq(len(signal), 1 / rate)
        fft = fft[:len(fft) // 2]
        freqs = freqs[:len(freqs) // 2]
        peak_indices = np.argsort(fft)[-2:]
        peak_freqs = [freqs[i] for i in peak_indices]
        return peak_freqs

    # Identify which DTMF key was pressed based on detected frequencies
    def identify_key(frequencies):
        for key, freqs in dtmf_frequencies.items():
            if all(any(np.isclose(f, freq, atol=10).any() for f in frequencies) for freq in freqs):
                return key
        return None

    print("Listening for DTMF tones...")

    ocr = PaddleOCR(use_angle_cls=True, lang='en')
    sleep_time = 0
    try:
        while True:
            # Read audio data and detect DTMF tones
            data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
            freqs = detect_dtmf(data, RATE)
            key = identify_key(freqs)

            if key:
                print(f"Detected DTMF key: {key}")
                if key == '1':  # Modify to match the key for ending the call
                    print("User clicked end call button!")
                    pyautogui.click(end_call_button_position[0], end_call_button_position[1])
                    save_user_click_info(phone_number)
                    return 'ended'

            # Continuously check call status using OCR
            screenshot = pyautogui.screenshot(region=region)
            image_np = np.array(screenshot)
            result = ocr.ocr(image_np, cls=True)

            if result is None or len(result) == 0:
                print("OCR result is empty.")
                continue

            text = ' '.join([line[1][0] for line in result[0]])

            if 'Idle' in text:
                print("Call ended!")
                return 'ended'

            # Timeout check (1 second)
            if sleep_time == 50:
                print("Call timed out!")
                sleep_time = 0
                return 'ended'
            else:
                sleep_time += 1
                time.sleep(0.1)

    except KeyboardInterrupt:
        print("Stopped listening for DTMF tones.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        return 'interrupted'

# Main script execution
if __name__ == "__main__":
    excel_file_path = 'phones.xlsx'
    process_numbers(excel_file_path)
