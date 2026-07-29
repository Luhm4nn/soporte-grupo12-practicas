import os
import threading
import time
import traceback
import queue

from gtts import gTTS
import pygame
from pynput import keyboard

MORSE_CODE_DICT = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
    '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
    '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
    '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
    '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
    '--..': 'Z',
    '-----': '0', '.----': '1', '..---': '2', '...--': '3', '....-': '4',
    '.....': '5', '-....': '6', '--...': '7', '---..': '8', '----.': '9',
    '.-.-.-': '.', '--..--': ',', '..--..': '?', '.----.': "'",
    '-.-.--': '!', '-..-.': '/', '-.--.': '(', '-.--.-': ')',
    '.-...': '&', '---...': ':', '-.-.-.': ';', '-...-': '=',
    '.-.-.': '+', '-....-': '-', '..--.-': '_', '.-..-.': '"',
    '...-..-': '$', '.--.-.': '@',
}

DOT_THRESHOLD = 0.3
LETTER_GAP = 0.5
WORD_GAP = 1.5
PHRASE_GAP = 3.0

state_lock = threading.Lock()
gui_queue = queue.Queue()

current_morse = ''
current_letter = ''
current_text = ''
press_start = None
last_release = None

pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)

AUDIO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'morse_word.mp3')
audio_lock = threading.Lock()


def play_audio(text):
    try:
        with audio_lock:
            tts = gTTS(text=text, lang='es')
            tts.save(AUDIO_FILE)
            sound = pygame.mixer.Sound(AUDIO_FILE)
        channel = sound.play()
        while channel is not None and channel.get_busy():
            time.sleep(0.1)
    except:
        traceback.print_exc()


def on_press(key):
    global press_start

    if key == keyboard.Key.space and press_start is None:
        press_start = time.time()
        gui_queue.put(('status', 'Presionando ESPACIO...'))


def on_release(key):
    global current_morse, current_letter, current_text, press_start, last_release

    if key == keyboard.Key.space and press_start is not None:
        duration = time.time() - press_start
        press_start = None

        if duration < DOT_THRESHOLD:
            current_morse += '.'
            gui_queue.put(('morse_add', '.'))
        else:
            current_morse += '-'
            gui_queue.put(('morse_add', '-'))

        last_release = time.time()
        gui_queue.put(('press_end', duration))

    elif key == keyboard.KeyCode.from_char('q'):
        frase = (current_text + current_letter).strip()
        gui_queue.put(('final', frase))
        if frase:
            threading.Thread(target=play_audio, args=(frase,), daemon=True).start()
        gui_queue.put(('quit',))
        return False


def check_gaps():
    global current_morse, current_letter, current_text, last_release

    while True:
        time.sleep(0.05)

        if last_release is None or press_start is not None:
            gui_queue.put(('gap', 0.0))
            continue

        gap = time.time() - last_release
        gui_queue.put(('gap', min(gap, PHRASE_GAP + 0.5)))

        if gap > PHRASE_GAP:
            if current_letter:
                current_text += current_letter + ' '
                current_letter = ''
                current_morse = ''
            frase = current_text.strip()
            if frase:
                gui_queue.put(('phrase', frase))
                threading.Thread(target=play_audio, args=(frase,), daemon=True).start()
                current_text = ''
            last_release = None
            gui_queue.put(('reset_all',))

        elif gap > WORD_GAP and current_letter:
            current_text += current_letter + ' '
            gui_queue.put(('word', current_letter))
            current_letter = ''
            current_morse = ''
            last_release = time.time()
            gui_queue.put(('reset_morse',))

        elif gap > LETTER_GAP and current_morse:
            char = MORSE_CODE_DICT.get(current_morse, '?')
            current_letter += char
            gui_queue.put(('char', char))
            current_morse = ''
            last_release = time.time()
            gui_queue.put(('reset_morse',))
