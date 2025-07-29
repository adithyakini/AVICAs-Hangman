import streamlit as st
import os
import random
from gtts import gTTS
from io import BytesIO
from PIL import Image
import base64

# Setup folders
os.makedirs("fartman_images", exist_ok=True)
os.makedirs("sounds", exist_ok=True)

WORDS = [
    "apple", "banana", "grape", "family", "school",
    "pencil", "friend", "yellow", "favourite", "spend"
]

# --- Audio Generator ---
def get_audio_bytes(word):
    tts = gTTS(text=word, lang='en')
    fp = BytesIO()
    tts.write_to_fp(fp)
    return fp.getvalue()

# --- Fartman Hangman Image ---
def show_fartman_image(tries):
    hangman_images = {
        3: "fartman_images/fartman_full.png",
        2: "fartman_images/fartman_2.png",
        1: "fartman_images/fartman_1.png",
        0: "fartman_images/fartman_0.png"
    }
    image_path = hangman_images.get(tries)
    if image_path and os.path.exists(image_path):
        st.image(image_path, use_container_width=True)
    else:
        st.text("[fartman image missing]")

# --- Play Sound ---
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

# --- Flying Fartman Animation ---
def flying_super_fartman(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            st.markdown(
                f"""
                <div style="position: relative; width: 100%; height: 300px; overflow: hidden;">
                    <img src="data:image/png;base64,{b64}" 
                         style="position: absolute; animation: fly-once 4s linear;">
                </div>
                <style>
                    @keyframes fly-once {{
                        0% {{ left: 100%; }}
                        100% {{ left: -300px; }}
                    }}
                    div > img {{
                        position: absolute; 
                        top: 50px; 
                        height: 200px;
                    }}
                </style>
                """,
                unsafe_allow_html=True,
            )

# Only show animation when a new game loads
flying_super_fartman("super_fartman.png")

# --- Session State Initialization ---
def reset_word():
    st.session_state.word = WORDS[st.session_state.word_index % len(WORDS)].upper()
    st.session_state.guessed = ['_' for _ in st.session_state.word]
    st.session_state.guessed_letters = []
    st.session_state.tries = 3
    st.session_state.wrong_guesses = 0
    st.session_state.guess_input = ""
    st.session_state.word_skipped = False
    st.session_state.word_guessed = False

if 'initialized' not in st.session_state:
    st.session_state.word_index = 0
    st.session_state.correct_count = 0
    st.session_state.total_attempted = 0
    random.shuffle(WORDS)
    reset_word()
    st.session_state.initialized = True

# --- Main UI ---
st.markdown(
    "<h1 style='font-size: 30px; color: purple; text-align: center;'>Avika, Spell it right OR Fartman will get gassy! </h1>", 
    unsafe_allow_html=True
)
st.markdown(f"**Score**: {st.session_state.correct_count}/{st.session_state.total_attempted} | **Remaining Words**: {len(WORDS) - st.session_state.total_attempted}")

if st.button("🔊 Hear Word"):
    audio_bytes = get_audio_bytes(st.session_state.word)
    st.audio(audio_bytes, format='audio/mp3')

with st.form(key="letter_form"):
    guess = st.text_input("Type a letter:", max_chars=1, value=st.session_state.guess_input, key="guess_box")
    submit = st.form_submit_button("Submit")

# --- Guess Logic ---
if submit and guess and guess.isalpha():
    letter = guess.upper()
    st.session_state.guess_input = ""
    if letter in st.session_state.guessed or letter in st.session_state.guessed_letters:
        st.warning("You already guessed that letter!")
    elif letter in st.session_state.word:
        play_sound("correct.mp3")
        for i, l in enumerate(st.session_state.word):
            if l == letter:
                st.session_state.guessed[i] = letter
    else:
        st.session_state.guessed_letters.append(letter)
        st.session_state.tries -= 1
        st.session_state.wrong_guesses += 1
        play_sound("wrongguess.mp3")

# --- Display Word State ---
st.header(' '.join(st.session_state.guessed))

if st.session_state.guessed_letters:
    st.markdown("**Wrong guesses**: " + ', '.join(st.session_state.guessed_letters))

img_path = f"fartman_images/{st.session_state.word.lower()}.png"
if os.path.exists(img_path):
    img = Image.open(img_path)
    st.image(img.resize((200, 200)))

show_fartman_image(st.session_state.tries)

# --- Win/Lose Logic ---
if '_' not in st.session_state.guessed:
    play_sound("win.mp3")
    st.success(f"🎉 YAY! You spelt '{st.session_state.word}' correctly!")
    if not st.session_state.word_guessed:
        st.session_state.correct_count += 1
        st.session_state.total_attempted += 1
        st.session_state.word_guessed = True

elif st.session_state.tries == 0:
    play_sound("lose.mp3")
    st.error(f"Oops! The word was '{st.session_state.word}'")
    if not st.session_state.word_skipped:
        st.session_state.total_attempted += 1
        st.session_state.word_skipped = True

# --- Next Word / Game Progression ---
if st.session_state.total_attempted >= len(WORDS):
    st.success("🎉 You've completed all words! Let's play again!")
    if st.button("Restart Game"):
        st.session_state.word_index = 0
        st.session_state.correct_count = 0
        st.session_state.total_attempted = 0
        random.shuffle(WORDS)
        reset_word()
else:
    if st.button("Next Word"):
        st.session_state.word_index += 1
        # Reshuffle after every full round
        if st.session_state.word_index % len(WORDS) == 0:
            random.shuffle(WORDS)
        reset_word()

progress = st.session_state.total_attempted / len(WORDS)
st.progress(progress)

# --- Optional Debug ---
if st.checkbox("Show debug info"):
    st.write({
        "word_index": st.session_state.word_index,
        "word": st.session_state.word,
        "correct_count": st.session_state.correct_count,
        "total_attempted": st.session_state.total_attempted,
        "tries": st.session_state.tries,
        "word_guessed": st.session_state.word_guessed,
        "word_skipped": st.session_state.word_skipped,
        "guessed": st.session_state.guessed,
        "guessed_letters": st.session_state.guessed_letters,
    })