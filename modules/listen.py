import sounddevice as sd
import numpy as np
import io
import wave
import speech_recognition as sr

def listen(duration=5, samplerate=16000):
    """
    Record user's voice using sounddevice (no PyAudio required),
    then recognize speech using Google Speech Recognition.
    """
    print("\n🎙️ Listening... Speak now!")

    try:
        # 🎧 Record from microphone
        audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
        sd.wait()

        # 🌀 Convert raw audio to WAV format in memory
        with io.BytesIO() as wav_buffer:
            with wave.open(wav_buffer, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(samplerate)
                wf.writeframes(audio_data.tobytes())
            wav_data = wav_buffer.getvalue()

        # 🎤 Recognize speech
        recognizer = sr.Recognizer()
        with sr.AudioFile(io.BytesIO(wav_data)) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio)
        print(f"🗣️ You said: {text}")
        return text.lower()

    except sr.UnknownValueError:
        print("❌ Sorry, I didn’t catch that.")
        return ""
    except sr.RequestError:
        print("⚠️ Could not connect to the recognition service.")
        return ""
    except Exception as e:
        print(f"⚠️ Microphone or audio error: {e}")
        return ""
