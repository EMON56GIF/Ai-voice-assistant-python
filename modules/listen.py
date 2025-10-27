import tempfile
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import os
import time
import speech_recognition as sr

def listen():
    fs = 16000
    duration = 5
    speak("I'm listening...")
    print("🎧 Listening... Speak now.")

    # Record from microphone
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()

    # Save audio to a normal file (not locked)
    temp_filename = os.path.join(tempfile.gettempdir(), "assistant_record.wav")
    write(temp_filename, fs, (audio * 32767).astype(np.int16))

    recognizer = sr.Recognizer()
    text = ""

    try:
        with sr.AudioFile(temp_filename) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            print(f"🗣️ You said: {text}")
            return text.lower()
    except sr.UnknownValueError:
        print("⚠️ Could not understand your voice.")
        return ""
    except Exception as e:
        print(f"⚠️ Could not recognize speech: {e}")
        return ""
    finally:
        # Small delay ensures Windows releases the file
        time.sleep(1)
        try:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
        except Exception as e:
            print(f"⚠️ Could not delete temp file: {e}")
