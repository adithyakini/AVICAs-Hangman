# spelling_game_streamlit.py

import streamlit as st
import os
import random
import time
from gtts import gTTS
from io import BytesIO
from PIL import Image
import base64
from streamlit_autorefresh import st_autorefresh

# Setup folders
os.makedirs("images", exist_ok=True)  # For storing word images
os.makedirs("hangman_images", exist_ok=True)  # For hangman stage images (0.png to 7.png)
os.makedirs("sounds", exist_ok=True)  # For storing sound effects

# Word list
WORDS = ["apple", "banana", "grape", "family", "school", "pencil", "friend", "yellow"]

# Generate or retrieve audio for a word
def get_audio_bytes(word):
    tts = gTTS(text=word, lang='en')
    fp = BytesIO()
    tts.write_to_fp(fp)
    return fp.getvalue()

# Show hangman image based on number of wrong guesses
def show_hangman_image(stage):
    image_path = f"hangman_images/{stage}.png"
    if os.path.exists(image_path):
        st.image(image_path, width=300)
    else:
        st.text("[Missing hangman image]")

# Fun celebratory animation using GIF
def show_celebration():
    gif_path = "images/confetti.gif"
    if os.path.exists(gif_path):
        with open(gif_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
            <img src="data:image/gif;base64,{b64}" width="600">
            """
            st.markdown(md, unsafe_allow_html=True)

# Play sound effect (autoplay using HTML)
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

# Apply fun, colorful, kid-friendly styles
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

# Auto-refresh every second for countdown
st_autorefresh(interval=1000, limit=0, key="timer")

# Game logic with Streamlit
if 'word_index' not in st.session_state:
    st.session_state.word_index = 0
    st.session_state.correct_count = 0
    st.session_state.total_attempted = 0
    st.session_state.tries = 7
    st.session_state.guessed = []
    st.session_state.guessed_letters = []
    st.session_state.wrong_guesses = 0
    st.session_state.show_restart = False
    st.session_state.guess_submitted = False
    st.session_state.timer_start = time.time()
    random.shuffle(WORDS)
    st.session_state.word = WORDS[st.session_state.word_index].upper()
    st.session_state.guessed = ['_' for _ in st.session_state.word]

# Countdown timer (60 seconds)
elapsed = int(time.time() - st.session_state.timer_start)
remaining = max(0, 60 - elapsed)
st.markdown(f"### ⏱️ Time left: {remaining} seconds")
if remaining == 0 and '_' in st.session_state.guessed:
    st.warning("⏰ Time's up!")
    st.session_state.tries = 0
