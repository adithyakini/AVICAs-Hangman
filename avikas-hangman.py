import streamlit as st
import os
import random
from gtts import gTTS
from io import BytesIO
from PIL import Image
import base64
import uuid

# Setup folders
os.makedirs("fartman_images", exist_ok=True)
os.makedirs("sounds", exist_ok=True)

WORDS = [
    "apple", "banana", "grape", "family", "school",
    "pencil", "friend", "yellow", "favourite", "spend"
]

def get_audio_bytes(word):
    tts = gTTS(text=word, lang='en')
    fp = BytesIO()
    tts.write_to_fp(fp)
    return fp.getvalue()

def show_fartman_image(tries, width=320):
    hangman_images = {
        3: "fartman_images/fartman_full.png",
        2: "fartman_images/fartman_2.png",
        1: "fartman_images/fartman_1.png",
        0: "fartman_images/fartman_0.png"
    }
    image_path = hangman_images.get(tries)
    abs_path = os.path.abspath(image_path) if image_path else None
    #st.write(f"DEBUG: Image path for tries={tries}: {image_path}")
    #st.write(f"DEBUG: Absolute path: {abs_path}")
    #st.write(f"DEBUG: os.path.exists: {os.path.exists(image_path)}")
    if image_path and os.path.exists(image_path):
        st.image(image_path, width=width, use_container_width=False)
    else:
        st.markdown(
            f"<div style='height:320px;border:2px dashed #aaa;display:flex;align-items:center;justify-content:center;font-size:1.4em;'>[fartman image missing]</div>", 
            unsafe_allow_html=True
        )
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

def flying_super_fartman(image_path):
    import base64
    import os
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            st.markdown(
                f"""
                <style>
                .flying-fartman-overlay {{
                    position: fixed;
                    top: 150px;
                    right: 0;
                    width: 1300px;
                    height: 340px;
                    pointer-events: none;
                    z-index: 9999;
                }}
                .flying-fartman-overlay img {{
                    position: absolute;
                    top: 0;
                    left: 100%;
                    height: 220px;
                    animation: fly-once 8s linear;
                }}
                @keyframes fly-once {{
                    0% {{ left: 100%; }}
                    100% {{ left: -300px; }}
                }}
                </style>
                <div class="flying-fartman-overlay">
                    <img src="data:image/png;base64,{b64}">
                </div>
                """,
                unsafe_allow_html=True,
            )

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

# Layout: two columns
col1, col2 = st.columns([2, 1], gap="large")

with col1:
    flying_super_fartman("super_fartman.png")
    st.markdown(
        "<h1 style='font-size: 30px; color: purple; text-align: left;'>Avika, Spell it right OR Fartman will get gassy! </h1>", 
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

    st.header(' '.join(st.session_state.guessed))

    if st.session_state.guessed_letters:
        st.markdown("**Wrong guesses**: " + ', '.join(st.session_state.guessed_letters))

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
            if st.session_state.word_index % len(WORDS) == 0:
                random.shuffle(WORDS)
            reset_word()

    progress = st.session_state.total_attempted / len(WORDS)
    st.progress(progress)

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

with col2:
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>Fartman Status</h2>", unsafe_allow_html=True)
    show_fartman_image(st.session_state.tries, width=820)
    # Show the word's image (if available)
    img_path = f"fartman_images/{st.session_state.word.lower()}.png"
    if os.path.exists(img_path):
        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
        img = Image.open(img_path)
        st.image(img.resize((600, 600)), caption=f"Hint for word", use_container_width=False)
    