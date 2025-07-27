# spelling_game_streamlit.py

import streamlit as st
import os
import random
from gtts import gTTS
from io import BytesIO
import base64
from PIL import Image

# Setup folders
os.makedirs("images", exist_ok=True)  # For storing word images

# Word list
WORDS = ["apple", "banana", "grape", "family", "school", "pencil", "friend", "yellow"]

# Generate or retrieve audio for a word
def get_audio_bytes(word):
    tts = gTTS(text=word, lang='en')
    fp = BytesIO()
    tts.write_to_fp(fp)
    return fp.getvalue()

# Hangman visual (using emojis or text)
def get_hangman_art(tries_left):
    stages = [
        """
           _______
          |/      |
          |      (_)
          |      \|/
          |       |
          |      / \\
          |
        __|___
        """,
        """
           _______
          |/      |
          |      (_)
          |      \|/
          |       |
          |      /
          |
        __|___
        """,
        """
           _______
          |/      |
          |      (_)
          |      \|/
          |       |
          |
          |
        __|___
        """,
        """
           _______
          |/      |
          |      (_)
          |      \|
          |       |
          |
          |
        __|___
        """,
        """
           _______
          |/      |
          |      (_)
          |       |
          |       |
          |
          |
        __|___
        """,
        """
           _______
          |/      |
          |      (_)
          |
          |
          |
          |
        __|___
        """,
        """
           _______
          |/      |
          |
          |
          |
          |
          |
        __|___
        """,
        """







"""
    ]
    return stages[7 - tries_left]

# Game logic with Streamlit
if 'word_index' not in st.session_state:
    st.session_state.word_index = 0
    st.session_state.correct_count = 0
    st.session_state.total_attempted = 0
    st.session_state.tries = 7
    st.session_state.guessed = []
    st.session_state.guessed_letters = []
    random.shuffle(WORDS)
    st.session_state.word = WORDS[st.session_state.word_index].upper()
    st.session_state.guessed = ['_' for _ in st.session_state.word]

st.title("🔤 Spelling Game for Kids")

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown(f"**Score**: {st.session_state.correct_count}/{st.session_state.total_attempted} | **Remaining**: {len(WORDS) - st.session_state.total_attempted}")
with col2:
    if st.button("🔊 Hear Word"):
        audio_bytes = get_audio_bytes(st.session_state.word)
        st.audio(audio_bytes, format='audio/mp3')

# Show image if available
img_path = f"images/{st.session_state.word.lower()}.png"
if os.path.exists(img_path):
    img = Image.open(img_path)
    st.image(img.resize((150, 150)))

# Hangman drawing
st.text(get_hangman_art(st.session_state.tries))

# Display word status
st.header(' '.join(st.session_state.guessed))

# Input box
guess = st.text_input("Type a letter:", max_chars=1)
submit = st.button("Submit")

if submit and guess and guess.isalpha():
    letter = guess.upper()
    if letter in st.session_state.word:
        for i, l in enumerate(st.session_state.word):
            if l == letter:
                st.session_state.guessed[i] = letter
    else:
        if letter not in st.session_state.guessed_letters:
            st.session_state.guessed_letters.append(letter)
            st.session_state.tries -= 1

# Show guessed letters
if st.session_state.guessed_letters:
    st.markdown("**Wrong guesses**: " + ', '.join(st.session_state.guessed_letters))

# Word completed
if '_' not in st.session_state.guessed:
    st.success(f"Great job! You spelled '{st.session_state.word}' correctly!")
    st.session_state.correct_count += 1
    st.session_state.total_attempted += 1
    if st.session_state.total_attempted < len(WORDS):
        if st.button("Next Word"):
            st.session_state.word_index += 1
            st.session_state.word = WORDS[st.session_state.word_index].upper()
            st.session_state.guessed = ['_' for _ in st.session_state.word]
            st.session_state.guessed_letters = []
            st.session_state.tries = 7
    else:
        st.info("🎉 You've completed all the words!")

# Word failed
elif st.session_state.tries == 0:
    st.error(f"Oops! The word was '{st.session_state.word}'")
    st.session_state.total_attempted += 1
    if st.session_state.total_attempted < len(WORDS):
        if st.button("Try Next Word"):
            st.session_state.word_index += 1
            st.session_state.word = WORDS[st.session_state.word_index].upper()
            st.session_state.guessed = ['_' for _ in st.session_state.word]
            st.session_state.guessed_letters = []
            st.session_state.tries = 7
    else:
        st.info("🎉 You've completed all the words!")
