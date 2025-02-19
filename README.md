# Voice-Controlled Invoker for Dota 2

This project is a Python-based tool that lets you control Invoker's spells in Dota 2 using your voice. It uses local speech recognition with Vosk, so everything runs offline for fast and reliable performance.

## Features

* **Local Offline Speech Recognition:** Uses Vosk for local speech recognition—no cloud services required.
* **Dynamic Cooldown Adjustment:** Adjusts the cooldown delay for Invoker's spells based on the spoken level:
   * "Level one" or "level 1" sets a 5-second delay.
   * "Level two" or "level 2" sets a 3-second delay.
   * "Level three" or "level 3" sets a 1-second delay.
* **Voice-Controlled Spell Casting:** Cast individual spells like "cold snap", "ice wall", "ghost walk", and more. Supports combo commands (e.g., "combo one") that execute a series of spells with appropriate delays. The tool also listens for up to three additional commands after a main command.
* **Console Output:** Recognized commands and results are printed to the console for easy debugging and monitoring.

## Requirements

* Python 3.x
* Vosk (`pip install vosk`)
* PyAudio (`pip install pyaudio`)
* pynput (`pip install pynput`)

**Note:** You'll need to download a Vosk model (for example, `vosk-model-small-en-us-0.15`) and update the model path in the code.

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/voice-to-keypress-invoker.git
cd voice-to-keypress-invoker
```

2. **Install dependencies:**
```bash
pip install vosk pyaudio pynput
```

3. **Download a Vosk Model:**
   * Visit Vosk Models and download an English model (e.g., `vosk-model-small-en-us-0.15`).
   * Extract the model to a folder on your computer.

4. **Update the Model Path:**
   Edit the `main.py` file and update the model path in the code:
   ```python
   model = Model(r"C:\Users\kayva\OneDrive\Desktop\vosk-model-small-en-us-0.15")
   ```
   (Use a raw string or double backslashes in your path.)

## Usage

Run the project with:
```bash
python main.py
```

### Voice Commands

* **Set Level:**
   * Say "level one" or "level 1" to set the cooldown delay to 5 seconds.
   * Say "level two" or "level 2" to set the cooldown delay to 3 seconds.
   * Say "level three" or "level 3" to set the cooldown delay to 1 second.
* **Spell Commands:** Use commands like "cold snap", "ice wall", "ghost walk", "emp", "tornado", etc.
* **Combo Commands:** For example, saying "combo one" will:
   * Cast the first spell.
   * Wait for the cooldown delay.
   * Cast the second spell.
   * Wait for the cooldown delay.
   * Then wait for two left mouse clicks to trigger the third spell.
* **Stop/Start:** Say "stop" to suspend command execution, and "start" to resume.

## How It Works

* **Local Recognition:** The tool uses Vosk to perform offline speech recognition, which minimizes latency and ensures the system works even without an internet connection.
* **Cooldown Delay Calculation:** The tool adjusts the delay between spell casts based on your spoken level command. This is essential for proper timing of Invoker's spells.
* **Command Execution:** Recognized commands are matched (using fuzzy matching for slight discrepancies) against a predefined dictionary, and the corresponding key presses are simulated using the `pynput` library.

## Contributing

Contributions, bug reports, and feature requests are welcome! Feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
