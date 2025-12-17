import os
import json
import streamlit as st
from dotenv import load_dotenv

# ================== IMPORTANT ==================
# Disable CrewAI telemetry (fixes SIGTERM issue)
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"

from crewai import Agent, Task, Crew
from crewai.llm import LLM

# ================== LOAD ENV ==================
load_dotenv()

# ===================== QUIZ CLASS =====================
class InteractiveQuiz:
    def __init__(self, questions):
        self.questions = questions
        self.current_question = 0
        self.score = 0
        self.feedback = None
        self.user_answers = []

    def display_question(self):
        if self.current_question < len(self.questions):
            q = self.questions[self.current_question]

            st.subheader(
                f"Question {self.current_question + 1}/{len(self.questions)}"
            )
            st.write(q["question"])

            selected_option = st.radio(
                "Choose an answer:",
                q["options"],
                key=f"radio_{self.current_question}"
            )

            if st.button("Submit", key=f"submit_{self.current_question}"):

                # Store user answer
                self.user_answers.append(selected_option)

                if selected_option == q["answer"]:
                    self.feedback = ("success", "Correct! 🎉")
                    self.score += 1
                else:
                    self.feedback = (
                        "error",
                        f"Wrong! Correct answer: {q['answer']}"
                    )

                self.current_question += 1
                st.rerun()

        else:
            self.display_results()

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

    # ===================== FINAL RESULTS =====================
    def display_results(self):
        st.subheader("🎉 Quiz Completed")
        st.write(
            f"### Final Score: **{self.score}/{len(self.questions)}**"
        )

        st.divider()
        st.subheader("📋 Answer Review")

        for idx, q in enumerate(self.questions):
            user_ans = self.user_answers[idx]
            correct = q["answer"]

            st.markdown(f"**Q{idx+1}. {q['question']}**")

            if user_ans == correct:
                st.success(f"Your Answer: {user_ans} ✅")
            else:
                st.error(f"Your Answer: {user_ans} ❌")
                st.info(f"Correct Answer: {correct}")

        st.divider()

        if st.button("🔄 Restart Quiz"):
            self.restart()
            st.rerun()

    def restart(self):
        self.current_question = 0
        self.score = 0
        self.feedback = None
        self.user_answers = []

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
            goal="Generate high-quality multiple-choice questions in strict JSON",
            backstory=(
                "You are an expert educator who creates precise, factual, "
                "and unambiguous quiz questions."
            ),
            llm=llm
        )

        task = Task(
            description=(
                f"You are an expert educator.\n\n"
                f"Generate EXACTLY 5 multiple-choice questions "
                f"on the topic: '{topic}'.\n\n"
                "STRICT RULES:\n"
                "- Questions must be factual and unambiguous\n"
                "- Only ONE option must be correct\n"
                "- Avoid subjective or opinion-based questions\n"
                "- Difficulty: intermediate to advanced\n"
                "- Each option must be concise and distinct\n\n"
                "OUTPUT FORMAT (JSON ONLY — NO EXTRA TEXT):\n"
                "[\n"
                "  {\n"
                "    \"question\": \"Clear question text\",\n"
                "    \"options\": [\"Option A\", \"Option B\", \"Option C\"],\n"
                "    \"answer\": \"Option A\"\n"
                "  }\n"
                "]"
            ),
            agent=agent,
            expected_output="A valid JSON array strictly matching the schema"
        )

        crew = Crew(
            agents=[agent],
            tasks=[task]
        )

        result = crew.kickoff()

        # Extract raw LLM text
        output_text = result.raw

        try:
            parsed = json.loads(output_text)

            # Basic validation
            assert isinstance(parsed, list)
            for q in parsed:
                assert "question" in q
                assert "options" in q
                assert "answer" in q
                assert q["answer"] in q["options"]

            return parsed

        except Exception:
            st.error("❌ Failed to parse valid quiz data")
            st.code(output_text)
            return []


