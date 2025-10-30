import os
from dotenv import load_dotenv
import google.generativeai as genai
import requests

# Load API keys from .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# 🔐 Configure Google Gemini
genai.configure(api_key=GEMINI_API_KEY)

# ✅ Choose a valid Gemini model
model_name = "models/gemini-2.5-pro"
model = genai.GenerativeModel(model_name)

# 🧠 Test Gemini
prompt = "Write a short poem about AI and creativity."
response = model.generate_content(prompt)
print("\n🤖 Gemini generated text:")
print(response.text)

# 🌦️ Test OpenWeather
city = "Kolkata"
url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"

weather_data = requests.get(url).json()
if "main" in weather_data:
    temp = weather_data["main"]["temp"]
    desc = weather_data["weather"][0]["description"]
    print(f"\n🌤️ Current weather in {city}: {temp}°C, {desc}")
else:
    print("⚠️ Failed to fetch weather data.")
