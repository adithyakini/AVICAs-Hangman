# spelling_game_streamlit.py

import streamlit as st
import os
import random
from gtts import gTTS
from io import BytesIO
from PIL import Image
import streamlit.components.v1 as components

# Setup folders
os.makedirs("images", exist_ok=True)  # For storing word images
os.makedirs("hangman_images", exist_ok=True)  # For hangman stage images (0.png to 7.png)

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
        st.image(image_path, width=200)
    else:
        st.text("[Missing hangman image]")

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
    random.shuffle(WORDS)
    st.session_state.word = WORDS[st.session_state.word_index].upper()
    st.session_state.guessed = ['_' for _ in st.session_state.word]

st.title("🔤 Spelling Game for Kids")

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown(f"**Score**: {st.session_state.correct_count}/{st.session_state.total_attempted} | **Remaining**: {len(WORDS) - st.session_state.total_attempted}")
with col2:
    st.markdown("""
        <style>
        .big-button button {
            font-size: 24px !important;
            height: 60px !important;
            width: 100% !important;
        }
        </style>
        <div class='big-button'>
            <form action="/" method="post">
                <button name="play_audio" type="submit">🔊 Hear Word</button>
            </form>
        </div>
    """, unsafe_allow_html=True)
    if st.session_state.get("play_audio_clicked") or st.button(" ", key="hidden_audio_btn"):
        audio_bytes = get_audio_bytes(st.session_state.word)
        st.audio(audio_bytes, format='audio/mp3')

# Show hangman image
show_hangman_image(st.session_state.wrong_guesses)

# Show image if available
img_path = f"images/{st.session_state.word.lower()}.png"
if os.path.exists(img_path):
    img = Image.open(img_path)
    st.image(img.resize((150, 150)))

# Display word status
st.header(' '.join(st.session_state.guessed))

# Input box
if st.session_state.tries > 0 and '_' in st.session_state.guessed:
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
                st.session_state.wrong_guesses += 1

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
            st.session_state.wrong_guesses = 0
    else:
        st.info("🎉 You've completed all the words!")
        st.session_state.show_restart = True

# Word failed
elif st.session_state.tries == 0:
    st.error(f"Oops! The word was '{st.session_state.word}'")
    st.session_state.total_attempted += 1
    st.markdown(f"**Correct spelling:** {st.session_state.word}")
    if st.session_state.total_attempted < len(WORDS):
        if st.button("Try Next Word"):
            st.session_state.word_index += 1
            st.session_state.word = WORDS[st.session_state.word_index].upper()
            st.session_state.guessed = ['_' for _ in st.session_state.word]
            st.session_state.guessed_letters = []
            st.session_state.tries = 7
            st.session_state.wrong_guesses = 0
    else:
        st.info("🎉 You've completed all the words!")
        st.session_state.show_restart = True

# Restart game
if st.session_state.show_restart:
    if st.button("🔁 Restart Game"):
        st.session_state.word_index = 0
        st.session_state.correct_count = 0
        st.session_state.total_attempted = 0
        st.session_state.tries = 7
        st.session_state.guessed_letters = []
        st.session_state.wrong_guesses = 0
        st.session_state.show_restart = False
        random.shuffle(WORDS)
        st.session_state.word = WORDS[0].upper()
        st.session_state.guessed = ['_' for _ in st.session_state.word]
