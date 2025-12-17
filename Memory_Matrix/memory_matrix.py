import streamlit as st
import random

class MemoryMatrix:
    def __init__(self, size=3):
        self.matrix = [[random.randint(1, 9) for _ in range(size)] for _ in range(size)]
        self.attempts = 0
        self.revealed = False
        self.guess = None

    def display_matrix(self):
        st.write("Memorize the numbers below for 5 seconds:")
        for row in self.matrix:
            st.write(row)
        if st.button('Reveal', key="matrix_reveal"):
            self.revealed = True
            st.rerun()

    def get_guess(self):
        if self.revealed:
            st.write("Now guess a number from the matrix:")
            self.guess = st.number_input("Enter a number:", min_value=1, max_value=9, key="matrix_guess")
            if st.button('Submit', key="matrix_submit"):
                if self.guess in [num for row in self.matrix for num in row]:
                    st.success("Correct! 🎉")
                else:
                    st.error("Wrong! Try again.")
                self.attempts += 1
                if self.attempts >= 3:
                    st.write("You lose! The matrix was:")
                    for row in self.matrix:
                        st.write(row)
                st.rerun()
