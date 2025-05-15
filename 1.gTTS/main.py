from gtts import gTTS
import os

text = "Привіт! Класна погода. Потрібно іти гуляти. Сало - це сила"

tts = gTTS(text=text, lang='uk')
tts.save("voice.mp3")

os.system("start voice.mp3")  # Для Windows
