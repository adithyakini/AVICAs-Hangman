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
        st.text("[Missing Super Fartman image]")

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

# Define the flying image animation
def flying_super_fartman(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            st.markdown(
                f"""
                <div style="position: relative; height: 150px;">
                    <img src="data:image/png;base64,{b64}" 
                         style="position: absolute; animation: fly 5s linear infinite;">
                </div>
                <style>
                    @keyframes fly {{
                        0% {{ left: -150px; }}
                        100% {{ left: 100%; }}
                    }}
                    img {{ position: absolute; left: 0; top: 50px; height: 100px; }}
                </style>
                """,
                unsafe_allow_html=True,
            )

# Display the flying image animation
flying_super_fartman("path_to_your_uploaded_image.png")

# Initialize session state
if 'word_index' not in st.session_state:
    st.session_state.word_index = 0
    st.session_state.correct_count = 0
    st.session_state.total_attempted = 0
    st.session_state.tries = 7
    st.session_state.guessed_letters = []
    st.session_state.wrong_guesses = 0
    st.session_state.guess_input = ""
    random.shuffle(WORDS)
    st.session_state.word = WORDS[st.session_state.word_index].upper()
    st.session_state.guessed = ['_' for _ in st.session_state.word]

# Main game UI
st.title("🎉 SUPER FARTMAN Game! 🎉")
st.markdown(f"**Score**: {st.session_state.correct_count}/{st.session_state.total_attempted} | **Remaining Words**: {len(WORDS) - st.session_state.total_attempted}")

if st.button("🔊 Hear Word"):
    audio_bytes = get_audio_bytes(st.session_state.word)
    st.audio(audio_bytes, format='audio/mp3')

with st.form(key="letter_form"):
    guess = st.text_input("Type a letter:", max_chars=1, value=st.session_state.guess_input, key="guess_box")
    submit = st.form_submit_button("Submit")

if submit and guess and guess.isalpha():
    letter = guess.upper()
    st.session_state.guess_input = ""
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

st.header(' '.join(st.session_state.guessed))

if st.session_state.guessed_letters:
    st.markdown("**Wrong guesses**: " + ', '.join(st.session_state.guessed_letters))

img_path = f"images/{st.session_state.word.lower()}.png"
if os.path.exists(img_path):
    img = Image.open(img_path)
    st.image(img.resize((200, 200)))

show_hangman_image(st.session_state.wrong_guesses)

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
        st.session_state.guess_input = ""

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
        st.session_state.guess_input = ""
