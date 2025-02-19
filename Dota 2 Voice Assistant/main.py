import time
import difflib
import json
from vosk import Model, KaldiRecognizer
import pyaudio
from pynput.keyboard import Controller
from pynput.mouse import Listener as MouseListener, Button

def get_cooldown_delay(level_token):
    """Return cooldown delay (in seconds) based on spoken level token."""
    mapping = {
        "1": 5,
        "one": 5,
        "2": 3,
        "two": 3,
        "3": 1,
        "three": 1
    }
    return mapping.get(level_token, None)

def wait_for_double_left_click():
    """Wait for two left mouse clicks to occur."""
    clicks = 0
    def on_click(x, y, button, pressed):
        nonlocal clicks
        if button == Button.left and pressed:
            clicks += 1
            print("Left click detected")
            if clicks >= 2:
                return False
    with MouseListener(on_click=on_click) as listener:
        listener.join()

def execute_spell(spell, keyboard, delay=0.005):
    """Execute a spell (list of keys) with a short delay between key presses."""
    for key in spell:
        print(f"Pressing: {key}")
        keyboard.press(key)
        keyboard.release(key)
        time.sleep(delay)

def listen_for_command(rec, stream, timeout=3):
    """Listen from the audio stream until a final result is available or timeout is reached."""
    start_time = time.time()
    while True:
        if time.time() - start_time > timeout:
            raise TimeoutError("Timeout waiting for command")
        data = stream.read(4096)
        if len(data) == 0:
            continue
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text = result.get("text", "").strip().lower()
            if text != "":
                return text

def get_and_execute_additional_commands(rec, stream, keyboard, word_to_key, cooldown_delay):
    """Listen for the next three commands and execute them if recognized."""
    print("Listening for additional commands (up to 3)...")
    for i in range(3):
        try:
            cmd = listen_for_command(rec, stream, timeout=2)
            print(f"Additional command {i+1} recognized: '{cmd}'")
            if cmd in word_to_key:
                command_matched = cmd
            else:
                matches = difflib.get_close_matches(cmd, word_to_key.keys(), n=1, cutoff=0.6)
                if matches:
                    command_matched = matches[0]
                    print(f"Fuzzy matched additional command '{cmd}' to '{command_matched}'")
                else:
                    print(f"Additional command '{cmd}' not recognized.")
                    continue

            keys = word_to_key[command_matched]
            if isinstance(keys, list) and keys and isinstance(keys[0], list):
                for spell in keys:
                    execute_spell(spell, keyboard)
                    time.sleep(cooldown_delay)
            elif isinstance(keys, list):
                execute_spell(keys, keyboard)
            else:
                print(f"Pressing: {keys}")
                keyboard.press(keys)
                keyboard.release(keys)
        except TimeoutError:
            print("Timeout while waiting for additional command.")
            continue

def main():
    # Initialize Vosk model and recognizer (update model path accordingly)
    model = Model(r"C:\Users\kayva\OneDrive\Desktop\vosk-model-small-en-us-0.15")
    rec = KaldiRecognizer(model, 16000)
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()

    keyboard = Controller()

    # Set default cooldown delay (default level is 1 -> 5 seconds)
    cooldown_delay = 5
    print(f"Default Invoker level set to 1, cooldown delay: {cooldown_delay} seconds.")

    # Define command mappings
    word_to_key = {
         # Mepo commands
        "one": ['1'],
        "two": ['2'],
        "three": ['3'],
        "four": ['4'],
        "five": ['5'],
        "six": ['6'],
        "all": ['6'],
         # Invoker commands
        "cold snap": ['q', 'q', 'q', 'r'],
        "ice wall": ['q', 'q', 'e', 'r'],
        "ghost walk": ['q', 'q', 'w', 'r'],
        "emp": ['w', 'w', 'w', 'r'],
        "tornado": ['w', 'w', 'q', 'r'],
        "alacrity": ['w', 'w', 'e', 'r'],
        "sun strike": ['e', 'e', 'e', 'r'],
        "forge spirit": ['e', 'e', 'q', 'r'],
        "chaos meteor": ['e', 'e', 'w', 'r'],
        "blast": ['q', 'w', 'e', 'r'],
        # Combo commands
        "combo one": [
            ['q', 'q', 'q', 'r'],  # Spell 1: cold snap
            ['w', 'w', 'q', 'r'],  # Spell 2: tornado
            ['e', 'e', 'w', 'r']   # Spell 3: chaos meteor (delayed by double left click)
        ],
        "combo two": [
            ['w', 'w', 'q', 'r'],  # Spell 1: tornado 
            ['w', 'w', 'w', 'r'],  # Spell 2: emp
            ['q', 'q', 'e', 'r'],  # Spell 3: example
            ['e', 'e', 'e', 'r']   # Spell 4: sun strike
        ],
        "combo three": [
            ['w', 'w', 'q', 'r'],  # Spell 1: tornado
            ['e', 'e', 'e', 'r'],  # Spell 2: sun strike
            ['e', 'e', 'w', 'r']   # Spell 3: chaos meteor
        ],
        "stop": "stop",
        "start": "start"
    }

    active = True

    while True:
        try:
            command = listen_for_command(rec, stream, timeout=3)
            print(f"Main command recognized: '{command}'")

            # Check for level setting command (e.g., "level one" or "level 1")
            if command.startswith("level "):
                parts = command.split()
                if len(parts) >= 2:
                    level_token = parts[1]
                    new_delay = get_cooldown_delay(level_token)
                    if new_delay is not None:
                        cooldown_delay = new_delay
                        print(f"Invoker level set to {level_token}, cooldown delay updated to {cooldown_delay} seconds.")
                    else:
                        print(f"Invalid level: {level_token}")
                continue

            if command in word_to_key:
                command_matched = command
            else:
                matches = difflib.get_close_matches(command, word_to_key.keys(), n=1, cutoff=0.6)
                if matches:
                    command_matched = matches[0]
                    print(f"Fuzzy matched main command '{command}' to '{command_matched}'")
                else:
                    print(f"Unrecognized main command: '{command}'")
                    continue

            # Handle stop/start commands
            if command_matched == "stop":
                active = False
                print("Commands suspended. Say 'start' to resume.")
                continue
            elif command_matched == "start":
                active = True
                print("Commands resumed.")
                continue

            if not active:
                continue

            keys = word_to_key[command_matched]
            if isinstance(keys, list) and keys and isinstance(keys[0], list):
                if command_matched == "combo one":
                    execute_spell(keys[0], keyboard)
                    time.sleep(cooldown_delay)
                    execute_spell(keys[1], keyboard)
                    time.sleep(cooldown_delay)
                    print("Waiting for two left mouse clicks to execute third spell...")
                    wait_for_double_left_click()
                    execute_spell(keys[2], keyboard)
                else:
                    for spell in keys:
                        execute_spell(spell, keyboard)
                        time.sleep(cooldown_delay)
            elif isinstance(keys, list):
                execute_spell(keys, keyboard)
            else:
                print(f"Pressing: {keys}")
                keyboard.press(keys)
                keyboard.release(keys)

            get_and_execute_additional_commands(rec, stream, keyboard, word_to_key, cooldown_delay)

        except TimeoutError:
            continue
        except KeyboardInterrupt:
            print("Exiting...")
            break

if __name__ == "__main__":
    main()
