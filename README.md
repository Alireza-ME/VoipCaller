
# Automated Call Monitoring Script

- [نسخه فارسی داکیومنت نیز موجود است](README_FA.md)

This project is a Python script for monitoring phone calls and detecting user activities. It utilizes libraries such as `pyautogui`, `pygame`, `PaddleOCR`, and `pandas`. With this script, you can automatically make phone calls and log user click information.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Required Files](#required-files)
- [Key Functions](#key-functions)
- [Notes](#notes)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Prerequisites

Before running the script, please install the following:

1. **VAC**:
   - You can download VAC from [here](https://vac.muzychenko.net/en/download.htm).

2. **Visual C++ Redistributable**:
   - Download and install the x64 version from [here](https://support.microsoft.com/en-us/help/2977003/the-latest-supported-visual-c-downloads).

3. **Python Libraries**:
   - Run the following command in the terminal:
     ```bash
     pip install -r requirements.txt
     ```

## Installation

1. **Download the code**: Clone this project from GitHub:
   ```bash
   git clone https://github.com/Alireza-ME/VoipCaller.git
   cd your_repository
   ```

2. **Run**: Execute the script using Python:
   ```bash
   python main.py
   ```

## Usage

1. **Initial Setup**:
   - After running the script, you will be prompted to specify the area you want to monitor and the end call button.

2. **Script Functionality**:
   - The phone numbers listed in the `phones.xlsx` file are processed.
   - If a user click is detected, the call information and time are logged.
   - This script checks the status of calls using OCR and identifies user activities.
   - A specific sound is played after the call is established.

## Required Files

- **`phones.xlsx`**: A file that contains phone numbers.
- **`voices/counsel.wav`**: An audio file played during the call.

## Key Functions

- `save_user_click_info(phone_number)`: Saves user click information to an Excel file.
  
- `get_region()`: Identifies the area you want to monitor.
  
- `get_end_call_button_position()`: Identifies the coordinates of the end call button.
  
- `monitor_call(region)`: Monitors calls and detects their status.
  
- `play_sound()`: Plays a specific sound.
  
- `read_excel(file_path)`: Reads an Excel file and returns the existing information.
  
- `process_numbers(file_path)`: Processes phone numbers in the Excel file.
  
- `listen_for_keypresses(end_call_button_position, region, phone_number)`: Listens for sounds and responds to user activities.

## Notes

- I suggest using the MicroSip program because it supports DTMF.
- Make sure you have the necessary permissions to access sound and perform automated clicks.
- Using this script in commercial or public environments may conflict with local laws. Use it cautiously.
- Adjust the timings in the script (such as the wait time for sound playback) according to your needs.

## Contributing

If you would like to contribute to this project, feel free to Fork it and submit a Pull Request. You can also raise issues or suggestions in the Issues section.

## License

This project is licensed under the [MIT](LICENSE) license. For more details about your rights and responsibilities, please refer to the license file.

## Contact

If you have any questions or need further assistance, you can contact me:
- Email: alighafurgh82@gmail.com
- telegram: [A_Lireza_ME](https://t.me/A_Lireza_ME)
