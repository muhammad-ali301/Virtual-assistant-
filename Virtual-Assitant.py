import speech_recognition as sr
import webbrowser
import requests
from gtts import gTTS
import pygame
import os
import wikipedia
import pywhatkit
import pyautogui
import time
import pyjokes  
from dotenv import load_dotenv
load_dotenv()

# ================== SPEAK FUNCTION ==================
def speak(text, lang="en", accent="co.uk", slow=False):
    print("Jarvis:", text)
    tts = gTTS(text=text, lang=lang, slow=slow, tld=accent)
    tts.save("voice.mp3")

    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load("voice.mp3")
    pygame.mixer.music.play(0)

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.unload()
    os.remove("voice.mp3")

# ================== CONTACTS LIST ==================
contacts = {
    "khan": "+923021510390",
    "ali": "+923455657301",
    "dildar": "+923409292276"
}

# ================== WEATHER FUNCTION ==================
def get_weather(city):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    complete_url = f"{base_url}?q={city}&appid={api_key}&units=metric"

    response = requests.get(complete_url)
    data = response.json()

    if response.status_code == 200:
        main = data["main"]
        weather = data["weather"][0]

        report = (f"Weather in {city}. "
                  f"Temperature {main['temp']} degree centigrade. "
                  f"Feels like {main['feels_like']} degree centigrade. "
                  f"Humidity {main['humidity']} percent. "
                  f"Condition {weather['description']}.")
        
        print(report)
        speak(report)
    else:
        speak("Sorry, I could not fetch the weather.")

# ================== SEND WHATSAPP MESSAGE FUNCTION ==================
def send_whatsapp_message(command):
    words = command.lower().split()
    name = None
    message = None

    # Find contact name inside command
    for contact in contacts:
        if contact in words:
            name = contact
            idx = words.index(contact)
            message = " ".join(words[idx+1:])
            break

    if not name:
        speak("Sorry, I could not find a contact in your command.")
        return
    if not message:
        speak("What message do you want to send?")
        return

    phone = contacts[name]

    try:
        speak(f"Sending your message to {name}")
        pywhatkit.sendwhatmsg_instantly(phone, message, wait_time=10, tab_close=True)

        time.sleep(12)
        pyautogui.press("enter")

        speak(f"Message sent to {name}")
        print(f"Message sent to {name} ({phone}): {message}")
    except Exception as e:
        speak("Sorry, I could not send the message")
        print(f"Error: {e}")

# ================== PROCESS COMMAND ==================
def processcommand(c):
    print(f"Jarvis heard: {c}")

    if "open google" in c:
        webbrowser.open("https://google.com")
        speak("Opening Google")

    elif "open facebook" in c:
        webbrowser.open("https://facebook.com")
        speak("Opening Facebook")

    elif "open youtube" in c:
        webbrowser.open("https://youtube.com")
        speak("Opening YouTube")

    elif "open linked in" in c:
        webbrowser.open("https://linkedin.com/")
        speak("Opening LinkedIn")

    elif "weather in" in c:
        city = c.lower().split("weather in")[-1].strip()
        if city:
            get_weather(city)
        else:
            speak("Please tell me the city name.")

    # ---- Wikipedia (Who / What) ----
    elif "who is" in c or "what is" in c:
        try:
            if "who is" in c:
                query = c.replace("who is", "").strip()
            else:
                query = c.replace("what is", "").strip()

            info = wikipedia.summary(query, sentences=2)
            speak(info)
        except:
            speak("Sorry, I could not find information on that.")

    elif "youtube" in c and "search" in c:
        query = c.replace("youtube", "").replace("search", "").strip()
        speak(f"Searching {query} on YouTube")
        pywhatkit.playonyt(query)

    elif "google" in c and "search" in c:
        query = c.replace("google", "").replace("search", "").strip()
        speak(f"Searching {query} on Google")
        pywhatkit.search(query)

    elif "chatgpt" in c and "search" in c:
        query = c.replace("chatgpt", "").replace("search", "").strip()
        speak(f"Opening ChatGPT with query {query}")
        webbrowser.open(f"https://chat.openai.com/?q={query}")

    elif "play" in c:
        song = c.replace("play", "").strip()
        speak(f"Playing {song} on YouTube")
        pywhatkit.playonyt(song)

    elif "joke" in c:   # jokes wala feature
        joke = pyjokes.get_joke()
        speak(joke)

    elif "message" in c and any(contact in c for contact in contacts):
        send_whatsapp_message(c)

    else:
        speak("Sorry, I don't understand that command.")

# ================== MAIN LOOP ==================
recognizer = sr.Recognizer()
speak("Initializing ...")

while True:
    try:
        with sr.Microphone() as source:
            print("Say Jarvis to activate...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)

        word = recognizer.recognize_google(audio).lower()

        if "jarvis" in word:   
            speak("Yaa, ...")

            with sr.Microphone() as source:
                print("Jarvis active, listening for command...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)
                command = recognizer.recognize_google(audio).lower()
                processcommand(command)

    except Exception as e:
        print(f"Error: {e}")

