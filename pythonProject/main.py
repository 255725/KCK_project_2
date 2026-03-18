import pyttsx3
import speech_recognition as sr
from deep_translator import GoogleTranslator

def speak(text):
    print(text)
    engine = pyttsx3.init()
    engine.setProperty('rate', 180)
    engine.say(text)
    engine.runAndWait()
    engine.stop()

def recognise(lang_code):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            audio = r.listen(source)
            return r.recognize_google(audio, language=lang_code).lower()
        except:
            return ""

src, dest, listen = "pl", "en", "pl-PL"
speak("Wybierz język: polski lub angielski")

check = 1
while True:
    phrase = recognise(listen)

    if not phrase:
        speak("Nie rozumiem")
        continue

    if check:
        if "polski" not in phrase and "angielski" not in phrase:
            speak("Nie podałeś poprawnego języka")
            continue
        check = 0

    if "bywaj" in phrase or "goodbye" in phrase:
        speak("Do widzenia")
        break

    if "polski" in phrase:
        src, dest, listen = "pl", "en", "pl-PL"
        speak("Wybrano polski. Powiedz coś (jeśli chcesz zakończyć program - powiedz bywaj)")
        continue
    elif "angielski" in phrase:
        src, dest, listen = "en", "pl", "en-US"
        speak("English selected. Say something. (If u want to stop the program, say Goodbye)")
        continue

    translated = GoogleTranslator(source=src, target=dest).translate(phrase)
    speak(translated)