import pyttsx3
import speech_recognition as sr
from deep_translator import GoogleTranslator
import sys

def speak(text):
    print(f"Mówię: {text}")

    engine = pyttsx3.init()
    engine.setProperty('rate', 180)
    engine.say(text)
    engine.runAndWait()

def recognise(lang_code):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print(f"[{lang_code}] Nasłuchuję...")
        try:
            audio = r.listen(source)
            return r.recognize_google(audio, language=lang_code).lower()
        except Exception:
            return ""

src, dest, listen = "pl", "en", "pl-PL"

speak("Wybierz język początkowy: polski lub angielski")
phrase_start = recognise(listen)

if "polski" not in phrase_start and "angielski" not in phrase_start:
    speak("Nie podałeś poprawnego języka. Zamykam program.")
    sys.exit()

if "polski" in phrase_start:
    src, dest, listen = "pl", "en", "pl-PL"
    speak("Wybrano polski. Powiedz coś (jeśli chcesz zakończyć program - powiedz: bywaj)")
elif "angielski" in phrase_start:
    src, dest, listen = "en", "pl", "en-US"
    speak("English selected. Say something. (If you want to stop the program, say: goodbye)")

while True:
    phrase = recognise(listen)

    if not phrase:
        if src == "pl":
            speak("Nie rozumiem")
        else:
            speak("I don't understand")
        continue

    if "bywaj" in phrase or "goodbye" in phrase:
        if src == "pl":
            speak("Do widzenia")
        else:
            speak("Goodbye")
        break

    if "zmień na angielski" in phrase or "switch to english" in phrase:
        src, dest, listen = "en", "pl", "en-US"
        speak("You switched to English. (If you want to stop the program, say goodbye)")
        continue

    if "zmień na polski" in phrase or "switch to polish" in phrase:
        src, dest, listen = "pl", "en", "pl-PL"
        speak("Język został zmieniony na polski. (jeśli chcesz zakończyć program - powiedz bywaj)")
        continue

    translated = GoogleTranslator(source=src, target=dest).translate(phrase)
    speak(translated)