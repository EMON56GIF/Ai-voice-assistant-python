import os
import io
import wave
import numpy as np
import requests
import sounddevice as sd
import speech_recognition as sr
import pyttsx3
from dotenv import load_dotenv
import google.generativeai as genai


# -------------------------------
# 1️⃣ Load Environment Variables
# -------------------------------
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Choose Gemini model
model = genai.GenerativeModel("models/gemini-2.5-flash")

# -------------------------------
# 2️⃣ Initialize Text-to-Speech
# -------------------------------
engine = pyttsx3.init('sapi5')
engine.setProperty('rate', 170)
engine.setProperty('volume', 1.0)
voices = engine.getProperty('voices')
if len(voices) > 0:
    engine.setProperty('voice', voices[0].id)  # male or female depending on voice[1]

# -------------------------------
# 3️⃣ Listen Function
# -------------------------------
def listen_alt(duration=5, samplerate=16000):
    print("\n🎙️ Listening... Speak now!")

    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()

    with io.BytesIO() as wav_buffer:
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(samplerate)
            wf.writeframes(audio_data.tobytes())
        wav_data = wav_buffer.getvalue()

    recognizer = sr.Recognizer()
    with sr.AudioFile(io.BytesIO(wav_data)) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio)
        print(f"🗣️ You said: {text}")
        return text
    except sr.UnknownValueError:
        print("❌ Sorry, I didn't catch that.")
        return ""
    except sr.RequestError:
        print("⚠️ Could not connect to the recognition service.")
        return ""

# -------------------------------
# 4️⃣ Gemini Response Function
# -------------------------------
def get_gemini_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"❌ Error generating response: {e}")
        return "Sorry, something went wrong."

# -------------------------------
# 5️⃣ Speak Function
# -------------------------------
def speak(text):
    print(f"\n🤖 Assistant: {text}\n")
    try:
        print("🔊 Speaking...")
        engine.say(text)
        engine.runAndWait()
        print("✅ Speech complete")
    except Exception as e:
        print(f"❌ Speech error: {e}")

# -------------------------------
# 6️⃣ Main Assistant Loop
# -------------------------------
def main():
    print("\n" + "="*50)
    print("🤖 AI Voice Assistant Started")
    print("="*50 + "\n")
    
    speak("Hello! I'm your AI assistant. How can I help you today?")
    
    exit_words = ["exit", "quit", "stop", "bye", "goodbye"]
    
    while True:
        user_input = listen_alt()

        if user_input == "":
            continue

        if any(word in user_input.lower() for word in exit_words):
            speak("Goodbye! Have a great day!")
            break

        ai_reply = get_gemini_response(user_input)
        speak(ai_reply)

# -------------------------------
# 7️⃣ Run Program
# -------------------------------
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Program stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
    finally:
        print("\n✅ Goodbye!\n")
