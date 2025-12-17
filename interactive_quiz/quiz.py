import streamlit as st
from crewai import Agent, Task, Crew
from dotenv import load_dotenv
import os
load_dotenv()

from crewai import Agent, Task, Crew
from crewai.llm import LLM
import os

import json

class InteractiveQuiz:
    def __init__(self, questions):
        self.questions = questions
        self.current_question = 0
        self.score = 0
        self.feedback = None

    def display_question(self):
        if self.current_question < len(self.questions):
            question_data = self.questions[self.current_question]
            st.subheader(f"Question {self.current_question + 1}/{len(self.questions)}")
            st.write(question_data['question'])
            selected_option = st.radio('Choose an answer:', question_data['options'], key=f"quiz_radio_{self.current_question}")
            if st.button('Submit', key=f"quiz_submit_{self.current_question}"):
                if selected_option == question_data['answer']:
                    self.feedback = ('success', 'Correct! 🎉')
                    self.score += 1
                else:
                    self.feedback = ('error', f"Wrong! The correct answer was: {question_data['answer']}")
                self.current_question += 1
                st.rerun()
        else:
            st.subheader('Quiz Finished! 🎉')
            st.write(f"Your final score is {self.score}/{len(self.questions)}.")

    def display_feedback(self):
        if self.feedback:
            msg_type, msg_content = self.feedback
            if msg_type == "success":
                st.success(msg_content)
            elif msg_type == "error":
                st.error(msg_content)
            self.feedback = None

    def display_score(self):
        st.metric('Current Score', self.score)

    def restart(self):
        self.current_question = 0
        self.score = 0
        self.feedback = None

    @staticmethod
    def generate_questions(topic):
        # Set up the LLM
        #llm = OpenAI(temperature=0.7, model_name="gpt-3.5-turbo")

        llm = LLM(
                model="openai/openai/gpt-oss-120b",
                api_key=os.getenv("Custom_OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_COMPATIBLE_ENDPOINT")
            )
        
        # Define agent and task for generating questions
        question_agent = Agent(
            role="Quiz Master",
            goal="Generate 5 multiple-choice questions on a given topic",
            backstory="You are an expert in creating engaging quiz questions.",
            llm=llm
        )
        
        task = Task(
            description=f"Generate 5 multiple-choice questions on the topic: {topic}. Each question should have 3 options and indicate the correct answer.",
            agent=question_agent,
            expected_output="A list of 5 dictionaries, each containing 'question', 'options', and 'answer'."
        )
        
        crew = Crew(agents=[question_agent], tasks=[task])
        result = crew.kickoff()
        
        # Parse result and return questions list
        try:
            questions = json.loads(result)
        except json.JSONDecodeError:
            # Handle case where result is not valid JSON
            questions = []
        return questions
