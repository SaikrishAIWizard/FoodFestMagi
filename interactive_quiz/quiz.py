import os
import json
import streamlit as st
from dotenv import load_dotenv

# ------------------ IMPORTANT: Disable CrewAI Telemetry ------------------
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"

from crewai import Agent, Task, Crew
from crewai.llm import LLM

# ------------------ Load Environment Variables ------------------
load_dotenv()


# ===================== QUIZ CLASS =====================
class InteractiveQuiz:
    def __init__(self, questions):
        self.questions = questions
        self.current_question = 0
        self.score = 0
        self.feedback = None

    def display_question(self):
        if self.current_question < len(self.questions):
            q = self.questions[self.current_question]

            st.subheader(f"Question {self.current_question + 1}/{len(self.questions)}")
            st.write(q["question"])

            selected_option = st.radio(
                "Choose an answer:",
                q["options"],
                key=f"radio_{self.current_question}"
            )

            if st.button("Submit", key=f"submit_{self.current_question}"):
                if selected_option == q["answer"]:
                    self.feedback = ("success", "Correct! 🎉")
                    self.score += 1
                else:
                    self.feedback = ("error", f"Wrong! Correct answer: {q['answer']}")

                self.current_question += 1
                st.rerun()
        else:
            st.subheader("Quiz Finished 🎉")
            st.write(f"Final Score: **{self.score}/{len(self.questions)}**")

            if st.button("Restart Quiz"):
                self.restart()
                st.rerun()

    def display_feedback(self):
        if self.feedback:
            msg_type, msg = self.feedback
            if msg_type == "success":
                st.success(msg)
            else:
                st.error(msg)
            self.feedback = None

    def display_score(self):
        st.metric("Score", self.score)

    def restart(self):
        self.current_question = 0
        self.score = 0
        self.feedback = None

    # ===================== QUESTION GENERATION =====================
    @staticmethod
    def generate_questions(topic):
        llm = LLM(
            model="openai/openai/gpt-oss-120b",
            api_key=os.getenv("Custom_OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_COMPATIBLE_ENDPOINT"),
        )

        agent = Agent(
            role="Quiz Master",
            goal="Generate quiz questions in strict JSON format",
            backstory="You create clean multiple-choice quizzes for students.",
            llm=llm
        )

        task = Task(
            description=(
                f"Generate EXACTLY 5 multiple-choice questions on '{topic}'.\n"
                "Rules:\n"
                "- Return ONLY valid JSON\n"
                "- No explanations, no markdown\n"
                "- Each question must have exactly 3 options\n\n"
                "JSON format:\n"
                "[\n"
                "  {\n"
                "    \"question\": \"...\",\n"
                "    \"options\": [\"A\", \"B\", \"C\"],\n"
                "    \"answer\": \"A\"\n"
                "  }\n"
                "]"
            ),
            agent=agent,
            expected_output="Valid JSON array only"
        )

        crew = Crew(agents=[agent], tasks=[task])

        result = crew.kickoff()

        # ✅ FIX: Extract raw text from CrewOutput
        output_text = result.raw

        try:
            return json.loads(output_text)
        except json.JSONDecodeError:
            st.error("❌ Failed to parse JSON from LLM")
            st.code(output_text)
            return []


# ===================== STREAMLIT APP =====================
st.set_page_config(page_title="AI Quiz App", page_icon="🧠")

st.title("🧠 AI-Powered Quiz Generator")

