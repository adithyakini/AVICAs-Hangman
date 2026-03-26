import streamlit as st
import os
import random
import base64
from io import BytesIO
from gtts import gTTS
from openai import OpenAI

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Fartman Spelling Game 💨", layout="centered")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------- DIRECTORIES ----------------
os.makedirs("fartman_images", exist_ok=True)
os.makedirs("sounds", exist_ok=True)

# ---------------- FALLBACK WORDS ----------------
FALLBACK_WORDS = {
    "Grade 1": ["cat", "dog", "sun", "hat", "pen", "cup"],
    "Grade 2": ["apple", "table", "chair", "green", "smile"],
    "Spell Bee": ["beautiful", "carefully", "machine", "tongue"]
}

LEVELS = {
    "Grade 1": "very simple words for kids age 5-6",
    "Grade 2": "slightly harder words for kids age 6-7",
    "Spell Bee": "challenging spelling bee level words"
}

# ---------------- SESSION INIT ----------------
def init_session():
    defaults = {
        "word": "",
        "guessed": [],
        "tries": 3,
        "score": 0,
        "used_words": [],
        "cache_words": {},
        "history": [],
        "game_over": False,
        "animation_played": False,
        "level": "Grade 1"
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ---------------- AUDIO ----------------
@st.cache_data
def get_audio_bytes(word):
    tts = gTTS(text=f"Spell the word: {word}", lang='en')
    fp = BytesIO()
    tts.write_to_fp(fp)
    return fp.getvalue()

# ---------------- IMAGE ----------------
def show_fartman_image(tries):
    images = {
        3: "fartman_images/fartman_full.png",
        2: "fartman_images/fartman_2.png",
        1: "fartman_images/fartman_1.png",
        0: "fartman_images/fartman_0.png"
    }
    path = images.get(tries)
    if path and os.path.exists(path):
        st.image(path, width=200)
    else:
        st.write("💨")

# ---------------- SOUND ----------------
def play_sound(file):
    path = f"sounds/{file}"
    if os.path.exists(path):
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            st.markdown(f"""
                <audio autoplay>
                <source src="data:audio/mp3;base64,{b64}">
                </audio>
            """, unsafe_allow_html=True)

# ---------------- FLYING ANIMATION ----------------
def flying_super_fartman():
    path = "fartman_images/fartman_full.png"
    if os.path.exists(path):
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()

        st.markdown(f"""
        <style>
        @keyframes fly {{
            0% {{ transform: translateX(100vw); }}
            100% {{ transform: translateX(-120vw); }}
        }}
        .fly {{
            position: fixed;
            top: 200px;
            z-index: 9999;
            animation: fly 3s linear;
        }}
        </style>
        <img src="data:image/png;base64,{b64}" class="fly">
        """, unsafe_allow_html=True)

# ---------------- AI WORD ----------------
def get_ai_word(level):
    # CACHE HIT
    if level in st.session_state.cache_words and st.session_state.cache_words[level]:
        return st.session_state.cache_words[level].pop()

    try:
        prompt = f"""
        Give ONE spelling word for {level}.
        Only return the word.
        Avoid: {st.session_state.used_words}
        """

        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        word = res.choices[0].message.content.strip().lower()

        # store extra words in cache (pre-fetch trick)
        st.session_state.cache_words.setdefault(level, []).append(word)

        return word

    except Exception:
        # FALLBACK
        return random.choice(FALLBACK_WORDS[level])

# ---------------- ADAPTIVE LEVEL ----------------
def adjust_level():
    score = st.session_state.score
    if score >= 5:
        return "Spell Bee"
    elif score >= 2:
        return "Grade 2"
    return "Grade 1"

# ---------------- NEW WORD ----------------
def new_word():
    st.session_state.word = get_ai_word(st.session_state.level)
    st.session_state.guessed = []
    st.session_state.tries = 3
    st.session_state.game_over = False
    st.session_state.animation_played = False
    st.session_state.used_words.append(st.session_state.word)

# ---------------- INIT FIRST WORD ----------------
if not st.session_state.word:
    new_word()

# ---------------- UI ----------------
st.title("💨 Fartman Spelling Game")

# Difficulty select
selected_level = st.selectbox("Choose Level 🎯", list(LEVELS.keys()))
st.session_state.level = selected_level

# Stats
st.metric("Score", st.session_state.score)
st.progress(min(max(st.session_state.score / 10, 0), 1))

# Show image
show_fartman_image(st.session_state.tries)

# Play audio
audio_bytes = get_audio_bytes(st.session_state.word)
st.audio(audio_bytes)

# Display blanks
display = " ".join([
    letter if letter in st.session_state.guessed else "_"
    for letter in st.session_state.word
])
st.subheader(display)

# Input
guess = st.text_input("Guess a letter", max_chars=1)

if guess:
    guess = guess.lower()

    if guess not in st.session_state.guessed:
        st.session_state.guessed.append(guess)

        if guess not in st.session_state.word:
            st.session_state.tries -= 1
            play_sound("fart.mp3")

# ---------------- GAME LOGIC ----------------
if "_" not in display:
    st.success("🎉 You Win!")
    st.session_state.score += 1
    st.session_state.game_over = True

    if not st.session_state.animation_played:
        flying_super_fartman()
        st.session_state.animation_played = True

elif st.session_state.tries <= 0:
    st.error(f"💀 You lost! Word was: {st.session_state.word}")
    st.session_state.score -= 1
    st.session_state.game_over = True

# ---------------- NEXT BUTTON ----------------
if st.session_state.game_over:
    if st.button("Next Word ➡️"):
        st.session_state.level = adjust_level()
        new_word()
        st.rerun()
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
