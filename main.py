import os
import requests
import sounddevice as sd
import numpy as np
import tempfile
from scipy.io.wavfile import write
from dotenv import load_dotenv
from google import generativeai as genai
from modules.speak import speak
import pyttsx3

# -------------------------------------
# 1️⃣ Load environment variables
# -------------------------------------
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ Gemini API key missing in .env file!")
if not OPENWEATHER_API_KEY:
    print("⚠️ Weather API key not found — weather requests will be disabled.")

# -------------------------------------
# 2️⃣ Setup Gemini model
# -------------------------------------
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# -------------------------------------
# 3️⃣ Voice setup
# -------------------------------------
engine = pyttsx3.init()
engine.setProperty('rate', 175)
engine.setProperty('volume', 0.9)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)

def speak(text):
    print(f"🧠 Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

# -------------------------------------
# 4️⃣ Listen to user (speech to text)
# -------------------------------------
def listen():
    fs = 16000
    duration = 5
    speak("I'm listening...")
    print("🎧 Listening... Speak now.")

    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()

    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    write(temp_wav.name, fs, (audio * 32767).astype(np.int16))

    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.AudioFile(temp_wav.name) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data)
            print(f"🗣️ You said: {text}")
            return text.lower()
    except Exception as e:
        print("⚠️ Could not recognize speech:", e)
        return ""
    finally:
        os.unlink(temp_wav.name)

# -------------------------------------
# 5️⃣ Weather Function
# -------------------------------------
def get_weather(city):
    if not OPENWEATHER_API_KEY:
        return "Weather API key is missing."
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        data = requests.get(url).json()
        if data.get("cod") != 200:
            return f"Couldn't find weather data for {city}."
        desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        return f"The weather in {city} is {desc}. It's {temp}°C, feels like {feels_like}°C, with humidity at {humidity}%."
    except Exception as e:
        return f"Error fetching weather: {str(e)}"

# -------------------------------------
# 6️⃣ Handle all user queries (Gemini)
# -------------------------------------
def ask_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Gemini error: {str(e)}"

# -------------------------------------
# 7️⃣ Main loop
# -------------------------------------
def main():
    speak("Hello! I'm your AI Assistant powered by Gemini. How can I help you today?")
    while True:
        user_input = listen()
        if not user_input:
            speak("Sorry, I didn’t catch that. Can you repeat?")
            continue

        if any(word in user_input for word in ["exit", "stop", "quit", "goodbye"]):
            speak("Goodbye! Have a wonderful day.")
            break

        elif "weather" in user_input:
            speak("Sure! Please tell me the city name.")
            city = listen()
            if city:
                weather = get_weather(city)
                speak(weather)
            else:
                speak("I didn't hear a city name.")

        else:
            # Generic AI reasoning
            reply = ask_gemini(user_input)
            speak(reply)

# -------------------------------------
# 8️⃣ Run it
# -------------------------------------
if __name__ == "__main__":
    main()
