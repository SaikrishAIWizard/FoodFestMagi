import streamlit as st

from interactive_quiz.quiz import InteractiveQuiz
from Guess_Number.guess_the_number import GuessTheNumber
from Memory_Matrix.memory_matrix import MemoryMatrix

# ===================== APP CONFIG =====================
st.set_page_config(
    page_title="🍔 Food Fest Games",
    page_icon="🎮",
    layout="centered"
)

# ===================== CONSTANTS =====================
PASSWORD = "fest2025"

# ===================== SESSION STATE INIT =====================
st.session_state.setdefault("authenticated", False)
st.session_state.setdefault("active_game", None)

# ===================== AUTHENTICATION =====================
if not st.session_state.authenticated:
    st.title("🔒 Food Fest Games")

    password = st.text_input("Enter Password", type="password")

    if st.button("Login"):
        if password == PASSWORD:
            st.session_state.authenticated = True
            st.success("Access granted!")
            st.rerun()
        else:
            st.error("Incorrect password")

    st.stop()

# ===================== SIDEBAR =====================
st.sidebar.title("🎮 Select a Game")

if st.sidebar.button("🧠 Interactive Quiz"):
    st.session_state.active_game = "quiz"
    st.session_state.pop("quiz", None)
    st.session_state.pop("number_game_instance", None)
    st.session_state.pop("matrix", None)

if st.sidebar.button("🔢 Guess the Hidden Number"):
    st.session_state.active_game = "number"
    st.session_state.pop("quiz", None)
    st.session_state.pop("matrix", None)

# (Optional – keep ready)
# if st.sidebar.button("🧩 Memory Matrix"):
#     st.session_state.active_game = "matrix"
#     st.session_state.pop("quiz", None)
#     st.session_state.pop("number_game_instance", None)

# ===================== MAIN UI =====================
st.title("🍔 Food Fest Games")

# ===================== QUIZ GAME =====================
if st.session_state.active_game == "quiz":
    st.header("🧠 Interactive Quiz")

    if "quiz" not in st.session_state:
        topic = st.text_input("Enter quiz topic")

        if st.button("Generate Quiz"):
            if not topic.strip():
                st.warning("Please enter a topic")
            else:
                with st.spinner("Generating quiz questions..."):
                    try:
                        questions = InteractiveQuiz.generate_questions(topic)

                        if questions:
                            st.session_state.quiz = InteractiveQuiz(questions)
                        else:
                            st.error("No questions generated. Try again.")

                    except Exception as e:
                        st.error("Error generating quiz")
                        st.code(str(e))

    if "quiz" in st.session_state:
        quiz = st.session_state.quiz
        quiz.display_score()
        quiz.display_feedback()
        quiz.display_question()

# ===================== NUMBER GAME =====================
elif st.session_state.active_game == "number":
    st.header("🔢 Guess the Hidden Number")

    if "number_game_instance" not in st.session_state:
        st.session_state.number_game_instance = GuessTheNumber(
            min_num=1,
            max_num=100,
            max_attempts=3
        )

    st.session_state.number_game_instance.play()

# ===================== DEFAULT =====================
else:
    st.info("👈 Please select a game from the sidebar")
