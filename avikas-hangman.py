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

WORDS = ["apple", "banana", "grape", "family", "school", "pencil", "friend", "yellow", "favourite", "spend"]

def get_audio_bytes(word):
    tts = gTTS(text=word, lang='en')
    fp = BytesIO()
    tts.write_to_fp(fp)
    return fp.getvalue()

def show_hangman_image(stage):
    image_path = f"hangman_images/{stage}.png"
    if os.path.exists(image_path):
        st.image(image_path, use_container_width=True)
    else:
        st.text("[Missing hangman image]")

def show_celebration():
    gif_path = "images/confetti.gif"
    if os.path.exists(gif_path):
        with open(gif_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"<img src='data:image/gif;base64,{b64}' style='width: 100%;'>"
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
        background-color: #000000;
        color: #FFF;
        font-family: 'Comic Sans MS', cursive, sans-serif;
        margin: 0;
        padding: 0;
        overflow-x: hidden;
    }
    h1, h2, h3, .stTextInput > div > div > input {
        font-size: 5vw !important;
    }
    .stButton > button {
        background-color: #FFB347 !important;
        color: white !important;
        font-size: 5vw !important;
        border-radius: 15px !important;
        padding: 10px 20px !important;
        width: 100% !important;
        margin-top: 10px;
        transition: all 0.3s ease-in-out;
    }
    .stButton > button:hover {
        transform: scale(1.05);
    }
    .stButton > button:has(span:contains("🔊 Hear Word")) {
        background-color: purple !important;
        font-size: 6vw !important;
        border: 3px solid #ffffff;
        animation: pulse 1s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(128, 0, 128, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(128, 0, 128, 0); }
        100% { box-shadow: 0 0 0 0 rgba(128, 0, 128, 0); }
    }
    .stTextInput > div > div > input {
        font-size: 6vw !important;
        height: 60px;
        color: #000 !important;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #ff5733;
    }
    @media (min-width: 768px) {
        h1, h2, h3, .stTextInput > div > div > input {
            font-size: 32px !important;
        }
        .stButton > button {
            font-size: 28px !important;
        }
        .stButton > button:has(span:contains("🔊 Hear Word")) {
            font-size: 36px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# (rest of the code remains unchanged)
