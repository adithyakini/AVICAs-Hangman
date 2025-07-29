import streamlit as st
import os
import random
import time
from gtts import gTTS
from io import BytesIO
from PIL import Image
import base64

# Setup folders
os.makedirs("fartman_images", exist_ok=True)
os.makedirs("sounds", exist_ok=True)

WORDS = ["apple", "banana", "grape", "family", "school", "pencil", "friend", "yellow", "favourite", "spend"]

def get_audio_bytes(word):
    tts = gTTS(text=word, lang='en')
    fp = BytesIO()
    tts.write_to_fp(fp)
    return fp.getvalue()

def show_hangman_image(tries):
    # Map tries to corresponding hangman stage images
    hangman_images = {
        3: "fartman_images/fartman_full.png",  # Full health
        2: "fartman_images/fartman_2.png",    # 2 tries left
        1: "fartman_images/fartman_1.png",    # 1 try left
        0: "fartman_images/fartman_lost.png"  # Game over
    }
    image_path = hangman_images.get(tries)
    if image_path and os.path.exists(image_path):
        st.image(image_path, use_container_width=True)
    else:
        st.text("[Hangman image missing]")
        
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

# Define the flying image animation (scrolls right to left, only once, and larger)
def flying_super_fartman(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            st.markdown(
                f"""
                <div style="position: relative; width: 100%; height: 300px; overflow: hidden;">
                    <img src="data:image/png;base64,{b64}" 
                         style="position: absolute; animation: fly-once 5s linear;">
                </div>
                <style>
                    @keyframes fly-once {{
                        0% {{ right: -300px; }}
                        100% {{ right: 100%; }}
                    }}
                    img {{
                        position: absolute; 
                        top: 50px; 
                        height: 200px; /* Adjust height for a larger image */
                    }}
                </style>
                """,
                unsafe_allow_html=True,
            )

# Call the function to display the flying image
flying_super_fartman("super_fartman.png")

# Initialize session state
if 'word_index' not in st.session_state:
    st.session_state.word_index = 0
    st.session_state.correct_count = 0
    st.session_state.total_attempted = 0
    st.session_state.tries = 3
    st.session_state.guessed_letters = []
    st.session_state.wrong_guesses = 0
    st.session_state.guess_input = ""
    random.shuffle(WORDS)
    st.session_state.word = WORDS[st.session_state.word_index].upper()
    st.session_state.guessed = ['_' for _ in st.session_state.word]

# Main game UI
st.title("🎉 Avika's SUPER FARTMAN spelling Game!")
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
            play_sound("wrongguess.mp3")
            st.session_state.guessed_letters.append(letter)
            st.session_state.tries -= 1
            st.session_state.wrong_guesses += 1

st.header(' '.join(st.session_state.guessed))

if st.session_state.guessed_letters:
    st.markdown("**Wrong guesses**: " + ', '.join(st.session_state.guessed_letters))

img_path = f"fartman_images/{st.session_state.word.lower()}.png"
if os.path.exists(img_path):
    img = Image.open(img_path)
    st.image(img.resize((200, 200)))

show_hangman_image(st.session_state.tries)

if '_' not in st.session_state.guessed:
    play_sound("win.mp3")
    st.success(f"🎉 YAY! You spelt '{st.session_state.word}' correctly!")
    st.session_state.correct_count += 1
    st.session_state.total_attempted += 1
    if st.button("Next Word"):
        st.session_state.word_index += 1
        st.session_state.word = WORDS[st.session_state.word_index % len(WORDS)].upper()
        st.session_state.guessed = ['_' for _ in st.session_state.word]
        st.session_state.guessed_letters = []
        st.session_state.tries = 3
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
        st.session_state.tries = 3
        st.session_state.wrong_guesses = 0
        st.session_state.guess_input = ""
#DEBUG
st.write("Available images:", os.listdir("fartman_images"))
