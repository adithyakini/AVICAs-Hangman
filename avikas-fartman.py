import streamlit as st
import os
import random
from gtts import gTTS
from io import BytesIO
from PIL import Image
import base64

# ---------------- SETUP ----------------
os.makedirs("fartman_images", exist_ok=True)
os.makedirs("sounds", exist_ok=True)

WORDS = [
    "beautiful", "carefully", "everywhere", "soup", "friend",
    "garden", "tongue", "terrace", "machine", "ground"
]

# ---------------- AUDIO ----------------
@st.cache_data
def get_audio_bytes(word):
    tts = gTTS(text=word, lang='en')
    fp = BytesIO()
    tts.write_to_fp(fp)
    return fp.getvalue()

# ---------------- IMAGE ----------------
def show_fartman_image(tries, width=200):
    images = {
        3: "fartman_images/fartman_full.png",
        2: "fartman_images/fartman_2.png",
        1: "fartman_images/fartman_1.png",
        0: "fartman_images/fartman_0.png"
    }
    path = images.get(tries)

    if path and os.path.exists(path):
        st.image(path, width=width)
    else:
        st.markdown(
            "<div style='height:200px;border:2px dashed #aaa;display:flex;align-items:center;justify-content:center;'>[image missing]</div>",
            unsafe_allow_html=True
        )

# ---------------- SOUND ----------------
def play_sound(file):
    path = f"sounds/{file}"
    if os.path.exists(path):
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            st.markdown(f"""
                <audio autoplay>
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
            """, unsafe_allow_html=True)

# ---------------- ANIMATION ----------------
def flying_super_fartman(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            st.markdown(f"""
                <style>
                .flying-fartman-overlay {{
                    position: fixed;
                    top: 150px;
                    right: 0;
                    width: 1500px;
                    height: 840px;
                    pointer-events: none;
                    z-index: 9999;
                }}
                .flying-fartman-overlay img {{
                    position: absolute;
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
            """, unsafe_allow_html=True)

# ---------------- RESET ----------------
def reset_word():
    st.session_state.word = WORDS[st.session_state.word_index % len(WORDS)].upper()
    st.session_state.guessed = ['_' for _ in st.session_state.word]
    st.session_state.guessed_letters = []
    st.session_state.tries = 3
    st.session_state.wrong_guesses = 0
    st.session_state.word_guessed = False
    st.session_state.word_skipped = False

# ---------------- INIT ----------------
if "initialized" not in st.session_state:
    st.session_state.word_index = 0
    st.session_state.correct_count = 0
    st.session_state.total_attempted = 0
    random.shuffle(WORDS)
    reset_word()
    st.session_state.initialized = True

# ---------------- LAYOUT ----------------
col1, col2 = st.columns([1.5, 1.5])

with col1:
    flying_super_fartman("super_fartman.png")

    st.markdown(
        "<h1 style='color: purple;'>AVIKA's \"Fartman\" Spelling Game!</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"**Score**: {st.session_state.correct_count}/{st.session_state.total_attempted}"
    )

    # 🔊 AUDIO
    if st.button("🔊 Hear Word"):
        st.audio(get_audio_bytes(st.session_state.word), format="audio/mp3")

    # ---------------- INPUT ----------------
    with st.form("letter_form", clear_on_submit=True):
        guess = st.text_input(
            "Type letters (e.g. abc):",
            key="guess_box",
            placeholder="Enter letters"
        )
        submit = st.form_submit_button("Submit")

    # ---------------- GUESS LOGIC ----------------
    if submit and guess:
        letters = [l.upper() for l in guess if l.isalpha()]

        for letter in letters:
            if letter in st.session_state.guessed_letters or letter in st.session_state.guessed:
                continue

            if letter in st.session_state.word:
                play_sound("correct.mp3")
                for i, l in enumerate(st.session_state.word):
                    if l == letter:
                        st.session_state.guessed[i] = letter
            else:
                st.session_state.guessed_letters.append(letter)
                st.session_state.tries -= 1
                st.session_state.wrong_guesses += 1
                play_sound("wrongguess.mp3")

    # ---------------- DISPLAY ----------------
    st.header(' '.join(st.session_state.guessed))

    if st.session_state.guessed_letters:
        st.markdown("**Wrong guesses**: " + ', '.join(st.session_state.guessed_letters))

    word_finished = ('_' not in st.session_state.guessed) or (st.session_state.tries == 0)

    # ---------------- WIN ----------------
    if '_' not in st.session_state.guessed and not st.session_state.word_guessed:
        play_sound("win.mp3")
        st.success(f"🎉 Correct! The word is '{st.session_state.word}'")
        st.session_state.correct_count += 1
        st.session_state.total_attempted += 1
        st.session_state.word_guessed = True

    # ---------------- LOSE ----------------
    elif st.session_state.tries == 0 and not st.session_state.word_skipped:
        play_sound("lose.mp3")
        st.error(f"Oops! The word was '{st.session_state.word}'")
        st.session_state.total_attempted += 1
        st.session_state.word_skipped = True

    # ---------------- NEXT WORD ----------------
    if st.session_state.total_attempted >= len(WORDS):
        st.success("🎉 Game complete!")
        if st.button("Restart Game"):
            st.session_state.word_index = 0
            st.session_state.correct_count = 0
            st.session_state.total_attempted = 0
            random.shuffle(WORDS)
            reset_word()
            st.rerun()
    else:
        if word_finished:
            if st.button("Next Word"):
                st.session_state.word_index += 1
                reset_word()
                st.rerun()   # ✅ CRITICAL FIX

    st.progress(st.session_state.total_attempted / len(WORDS))

    # ---------------- AUTO FOCUS ----------------
    st.markdown("""
    <script>
    const input = window.parent.document.querySelector('input[data-testid="stTextInput"]');
    if (input) { input.focus(); }
    </script>
    """, unsafe_allow_html=True)

# ---------------- RIGHT PANEL ----------------
with col2:
    show_fartman_image(st.session_state.tries)

    img_path = f"fartman_images/{st.session_state.word.lower()}.png"
    if os.path.exists(img_path):
        img = Image.open(img_path)
        st.image(img, caption="Hint", use_container_width=True)
