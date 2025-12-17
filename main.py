import streamlit as st
from interactive_quiz.quiz import InteractiveQuiz
from Memory_Matrix.memory_matrix import MemoryMatrix
from Guess_Number.guess_the_number import GuessTheNumber

# import sys
# if sys.platform == "win32":
#     import signal
#     signal.signal = lambda x, y: None  # Skip signal registration on Windows

# Now import your other modules
import streamlit as st
from crewai import Agent, Task, Crew

# Set password (change this to your desired password)
PASSWORD = "fest2025"

st.set_page_config(page_title="Food Fest Games", layout="centered")

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "active_game" not in st.session_state:
    st.session_state.active_game = None

# Authentication page
if not st.session_state.authenticated:
    st.title("🔒 Food Fest Games - Password Protected")
    password = st.text_input("Enter Password:", type="password")
    if st.button("Submit"):
        if password == PASSWORD:
            st.session_state.authenticated = True
            st.success("Access granted!")
            st.rerun()
        else:
            st.error("Incorrect password. Try again.")
else:
    # Game selection and main logic
    st.sidebar.title("🎮 Select a Game")

    if st.sidebar.button("🧠 Interactive Quiz"):
        st.session_state.active_game = "quiz"
        if "number_game" in st.session_state: del st.session_state.number_game
        if "matrix" in st.session_state: del st.session_state.matrix

    if st.sidebar.button("🧩 Memory Matrix"):
        st.session_state.active_game = "matrix"
        if "number_game" in st.session_state: del st.session_state.number_game
        if "quiz" in st.session_state: del st.session_state.quiz

    if st.sidebar.button("🔢 Guess the Hidden Number"):
        st.session_state.active_game = "number_game"
        if "matrix" in st.session_state: del st.session_state.matrix
        if "quiz" in st.session_state: del st.session_state.quiz

    st.title("🍔 Food Fest Games")

    if st.session_state.active_game == "quiz":
        st.header("🧠 Interactive Quiz")
        
        if "quiz" not in st.session_state:
            topic = st.text_input("Enter the quiz topic:")
            if st.button("Generate Quiz"):
                with st.spinner("Generating questions..."):
                    try:
                        questions = InteractiveQuiz.generate_questions(topic)
                        if questions:
                            st.session_state.quiz = InteractiveQuiz(questions)
                        else:
                            st.error("Failed to generate questions. Please try again.")
                    except Exception as e:
                        st.error(f"Error generating questions: {e}")
        
        if "quiz" in st.session_state:
            st.session_state.quiz.display_question()
            st.session_state.quiz.display_feedback()
            st.session_state.quiz.display_score()

    elif st.session_state.active_game == "number_game":
        st.header("🔢 Guess the Hidden Number")
        if "number_game_instance" not in st.session_state:
            st.session_state.number_game_instance = GuessTheNumber(min_num=1, max_num=100, max_attempts=3)
        st.session_state.number_game_instance.play()

    else:
        st.info("👈 Please select a game from the sidebar.")
