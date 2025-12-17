import os
import streamlit as st

# ===================== IMPORTANT =====================
# Disable CrewAI telemetry globally (prevents SIGTERM error)
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"

from interactive_quiz.quiz import InteractiveQuiz
from Guess_Number.guess_the_number import GuessTheNumber
# from Memory_Matrix.memory_matrix import MemoryMatrix  # optional

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
st.session_state.setdefault("quiz", None)
st.session_state.setdefault("number_game_instance", None)

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
    st.session_state.quiz = None
    st.session_state.number_game_instance = None

if st.sidebar.button("🔢 Guess the Hidden Number"):
    st.session_state.active_game = "number"
    st.session_state.quiz = None
    st.session_state.number_game_instance = None

# ===================== MAIN UI =====================
st.title("🍔 Food Fest Games")

# ====================================================
# ===================== QUIZ GAME =====================
# ====================================================
if st.session_state.active_game == "quiz":
    st.header("🧠 Interactive Quiz")

    # Quiz not generated yet
    if st.session_state.quiz is None:
        topic = st.text_input(
            "Enter quiz topic",
            placeholder="e.g., Python, SQL, AI, Food Safety"
        )

        if st.button("🚀 Generate Quiz"):
            if not topic.strip():
                st.warning("Please enter a topic")
            else:
                with st.spinner("Generating quiz questions..."):
                    try:
                        questions = InteractiveQuiz.generate_questions(topic)

                        if questions:
                            st.session_state.quiz = InteractiveQuiz(questions)
                            st.success("Quiz ready!")
                            st.rerun()
                        else:
                            st.error("Failed to generate quiz. Try again.")

                    except Exception as e:
                        st.error("Error generating quiz")
                        st.code(str(e))

    # Quiz running / results view
    if st.session_state.quiz:
        quiz = st.session_state.quiz
        quiz.display_score()
        quiz.display_feedback()
        quiz.display_question()

# ====================================================
# ===================== NUMBER GAME ===================
# ====================================================
elif st.session_state.active_game == "number":
    st.header("🔢 Guess the Hidden Number")

    if st.session_state.number_game_instance is None:
        st.session_state.number_game_instance = GuessTheNumber(
            min_num=1,
            max_num=100,
            max_attempts=3
        )

    st.session_state.number_game_instance.play()

# ====================================================
# ===================== DEFAULT =======================
# ====================================================
else:
    st.info("👈 Please select a game from the sidebar")
