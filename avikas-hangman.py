# spelling_game_streamlit.py

import streamlit as st
import os
import random
import time
from gtts import gTTS
from io import BytesIO
from PIL import Image
import base64

# Setup folders
os.makedirs("images", exist_ok=True)
os.makedirs("hangman_images", exist_ok=True)
os.makedirs("sounds", exist_ok=True)

WORDS = ["apple", "banana", "grape", "family", "school", "pencil", "friend", "yellow"]

def get_audio_bytes(word):
    tts = gTTS(text=word, lang='en')
    fp = BytesIO()
    tts.write_to_fp(fp)
    return fp.getvalue()

def show_hangman_image(stage):
    image_path = f"hangman_images/{stage}.png"
    if os.path.exists(image_path):
        st.image(image_path, width=300)
    else:
        st.text("[Missing hangman image]")

def show_celebration():
    gif_path = "images/confetti.gif"
    if os.path.exists(gif_path):
        with open(gif_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"<img src='data:image/gif;base64,{b64}' width='600'>"
            st.markdown(md, unsafe_allow_html=True)

def play_sound(file):
    sound_path = f"sounds/{file}"
    if os.path.exists(sound_path):
        with open(sound_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
            <audio autoplay>
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
            st.markdown(md, unsafe_allow_html=True)

st.markdown("""
    <style>
    html, body, .main {
        background-color: #FFF3E6;
        color: #000;
        font-family: 'Comic Sans MS', cursive, sans-serif;
    }
    h1, h2, h3, .stButton > button, .stTextInput > div > div > input {
        font-size: 32px !important;
    }
    .stButton > button {
        background-color: #FFB347 !important;
        color: white !important;
        font-size: 28px !important;
        border-radius: 15px !important;
        padding: 15px 30px !important;
        width: 100% !important;
        margin-top: 10px;
    }
    .stTextInput > div > div > input {
        font-size: 28px !important;
        height: 60px;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #ff5733;
    }
    </style>
""", unsafe_allow_html=True)

if 'word_index' not in st.session_state:
    st.session_state.word_index = 0
    st.session_state.correct_count = 0
    st.session_state.total_attempted = 0
    st.session_state.tries = 7
    st.session_state.guessed_letters = []
    st.session_state.wrong_guesses = 0
    random.shuffle(WORDS)
    st.session_state.word = WORDS[st.session_state.word_index].upper()
    st.session_state.guessed = ['_' for _ in st.session_state.word]

st.title("🎉 AVIKA's HANGMAN Game! 🎉")

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown(f"**Score**: {st.session_state.correct_count}/{st.session_state.total_attempted} | **Remaining**: {len(WORDS) - st.session_state.total_attempted}")
with col2:
    if st.button("🔊 Hear Word"):
        audio_bytes = get_audio_bytes(st.session_state.word)
        st.audio(audio_bytes, format='audio/mp3')

guess = st.text_input("Type a letter:", max_chars=1)
submit = st.button("Submit")

if submit and guess and guess.isalpha():
    letter = guess.upper()
    if letter in st.session_state.word:
        play_sound("correct.mp3")
        for i, l in enumerate(st.session_state.word):
            if l == letter:
                st.session_state.guessed[i] = letter
    else:
        if letter not in st.session_state.guessed_letters:
            play_sound("wrong.mp3")
            st.session_state.guessed_letters.append(letter)
            st.session_state.tries -= 1
            st.session_state.wrong_guesses += 1

show_hangman_image(st.session_state.wrong_guesses)

img_path = f"images/{st.session_state.word.lower()}.png"
if os.path.exists(img_path):
    img = Image.open(img_path)
    st.image(img.resize((200, 200)))

st.header(' '.join(st.session_state.guessed))

if st.session_state.guessed_letters:
    st.markdown("**Wrong guesses**: " + ', '.join(st.session_state.guessed_letters))

if '_' not in st.session_state.guessed:
    show_celebration()
    play_sound("win.mp3")
    st.success(f"🎉 Great job! You spelled '{st.session_state.word}' correctly!")
    st.session_state.correct_count += 1
    st.session_state.total_attempted += 1
    if st.button("Next Word"):
        st.session_state.word_index += 1
        st.session_state.word = WORDS[st.session_state.word_index % len(WORDS)].upper()
        st.session_state.guessed = ['_' for _ in st.session_state.word]
        st.session_state.guessed_letters = []
        st.session_state.tries = 7
        st.session_state.wrong_guesses = 0

elif st.session_state.tries == 0:
    play_sound("lose.mp3")
    st.error(f"Oops! The word was '{st.session_state.word}'")
    st.session_state.total_attempted += 1
    st.markdown(f"**Correct spelling:** {st.session_state.word}")
    if st.button("Try Next Word"):
        st.session_state.word_index += 1
        st.session_state.word = WORDS[st.session_state.word_index % len(WORDS)].upper()
        st.session_state.guessed = ['_' for _ in st.session_state.word]
        st.session_state.guessed_letters = []
        st.session_state.tries = 7
        st.session_state.wrong_guesses = 0
