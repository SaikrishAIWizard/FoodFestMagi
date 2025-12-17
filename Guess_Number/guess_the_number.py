import streamlit as st
import random
import time
import os 
from collections import deque # Using deque for efficient append/pop (if max history is set)

# --- LOCAL SOUND FILE PATHS ---
# Ensure these files exist in a directory named 'sounds' relative to your main app file.
SOUNDS = {
    "win": "sounds/win.mp3",
    "fire": "sounds/fire.mp3",
    "warm": "sounds/warm.mp3",
    "lukewarm": "sounds/lukewarm.mp3",
    "cold": "sounds/cold.mp3",
    "lose": "sounds/lose.mp3",
}

# --- HISTORY CONSTANT ---
# Define how many past guesses to display (optional, but good practice)
MAX_HISTORY_DISPLAY = 10 


class GuessTheNumber:
    def __init__(self, min_num=1, max_num=100, max_attempts=5):
        """Initializes the game parameters and sets up session state."""
        self.min_num = min_num
        self.max_num = max_num
        self.max_attempts = max_attempts

        # --- INITIALIZE ALL SESSION STATE KEYS ---
        if "gn_number" not in st.session_state:
            self.reset_game()
        
        if "gn_attempts" not in st.session_state:
            st.session_state.gn_attempts = 0
        if "gn_won" not in st.session_state:
            st.session_state.gn_won = False
        if "gn_feedback" not in st.session_state:
            st.session_state.gn_feedback = ""
        
        if "gn_input_value" not in st.session_state:
            st.session_state.gn_input_value = self.min_num
        if "gn_last_guess" not in st.session_state:
            st.session_state.gn_last_guess = None
            
        # 1. New History Key
        if "gn_history" not in st.session_state:
            st.session_state.gn_history = [] 
            
        # Sound control key (stores the local path)
        if "gn_sound_path" not in st.session_state:
            st.session_state.gn_sound_path = None 
        
        # Audio Path Cleanup (from prior versions)
        if "gn_sound_url" in st.session_state:
             st.session_state.gn_sound_path = st.session_state.gn_sound_url
             del st.session_state.gn_sound_url 

    def reset_game(self):
        """Resets all game state variables for a new round."""
        st.session_state.gn_number = random.randint(self.min_num, self.max_num)
        st.session_state.gn_attempts = 0
        st.session_state.gn_won = False
        st.session_state.gn_feedback = ""
        st.session_state.gn_input_value = self.min_num
        st.session_state.gn_last_guess = None
        st.session_state.gn_sound_path = None 
        # 3. Clear History
        st.session_state.gn_history = []

    def play(self):
        """Renders the Streamlit UI for the game, including guess processing logic."""
        
        # --- INNER FUNCTION TO PROCESS GUESS ---
        def _process_guess():
            """Handles the game logic when the submit button is clicked."""
            
            guess = st.session_state["gn_input_value"] 
            
            st.session_state.gn_attempts += 1
            current_attempt = st.session_state.gn_attempts
            st.session_state.gn_feedback = ""
            st.session_state.gn_last_guess = guess
            st.session_state.gn_sound_path = None 

            st.session_state.gn_input_value = self.min_num 

            with st.status(f"🔍 Checking guess: {guess}...", expanded=False):
                time.sleep(1.2)

            # 4. Check for Win
            if guess == st.session_state.gn_number:
                feedback = (
                    f"🎉 **Perfect!** You nailed the number **{st.session_state.gn_number}** "
                    f"in just **{current_attempt}** tries!"
                )
                st.session_state.gn_feedback = feedback
                st.session_state.gn_won = True
                st.session_state.gn_sound_path = SOUNDS["win"] 
                
                # 2. Append Win to History
                st.session_state.gn_history.append({
                    "Attempt": current_attempt,
                    "Guess": guess,
                    "Result": "🎉 **WIN**",
                    "Closeness": "Exact Match!"
                })
                return

            # 5. Provide Hints
            diff = abs(guess - st.session_state.gn_number)

            print("Guess number is :",guess)
            print("Secret number is :", st.session_state.gn_number)

            direction = "📉 **Too low**" if guess < st.session_state.gn_number else "📈 **Too high**"

            # Closeness logic: More interactive and emotional language
            if diff <= 5: 
                closeness_text = ":green[🔥🔥 On Fire!]"
                closeness_detail = "Extremely close! Diff between guess and secret number is 5 digits"
                st.session_state.gn_sound_path = SOUNDS["fire"]
            elif diff <= 10:
                closeness_text = ":green[✅ Getting HOT!]"
                closeness_detail = "Very close! Diff between guess and secret number is 10 digits"
                st.session_state.gn_sound_path = SOUNDS["warm"]
            elif diff <= 20:
                closeness_text = "orange[🟡 Lukewarm.]"
                closeness_detail = "Getting closer. Diff between guess and secret number is 20 digits"
                st.session_state.gn_sound_path = SOUNDS["lukewarm"]
            else:
                closeness_text = ":red[🥶 BRRR! It's FREEZING!]"
                closeness_detail = "Far away. Try a big change."
                st.session_state.gn_sound_path = SOUNDS["cold"]
                
            feedback = f"Your last guess ({guess}): {direction}. {closeness_text} → {closeness_detail.replace('$', '')}"
            st.session_state.gn_feedback = feedback
            
            # 2. Append Guess to History
            st.session_state.gn_history.append({
                "Attempt": current_attempt,
                "Guess": guess,
                "Result": direction.replace('**', ''),
                "Closeness": closeness_text.replace(':', '').replace('[', '').replace(']', '')
            })

            # 6. Loss condition
            if current_attempt >= self.max_attempts:
                st.session_state.gn_feedback = (
                    f"😭 **Tough Luck!** You ran out of attempts.\n\n"
                    f"The secret number was **{st.session_state.gn_number}**."
                )
                st.session_state.gn_sound_path = SOUNDS["lose"]
                # Final loss entry in history
                st.session_state.gn_history[-1]['Result'] = f"❌ **LOSE** (Actual: {st.session_state.gn_number})"
                
        # --- END OF INNER FUNCTION ---

        attempts_left = max(0, self.max_attempts - st.session_state.gn_attempts)
        last_guess_display = st.session_state.gn_last_guess if st.session_state.gn_last_guess is not None else 'N/A'

        # ===== AUDIO PLAYER (LOCAL FILE HANDLER FIX) =====
        if st.session_state.gn_sound_path and os.path.exists(st.session_state.gn_sound_path):
            try:
                with open(st.session_state.gn_sound_path, "rb") as audio_file:
                    audio_bytes = audio_file.read()
                
                st.audio(audio_bytes, format="audio/mp3", start_time=0)
                
            except Exception:
                pass
            
            st.session_state.gn_sound_path = None


        # ===== UI RENDERING START =====
        
        # ===== ATTEMPTS + PROGRESS =====
        st.markdown(
            f"""
            🧠 **Attempts Left:** `{attempts_left}` / `{self.max_attempts}`  
            📏 *Range:* `{self.min_num}` → `{self.max_num}`
            """
        )
        
        st.markdown(f"👉 **Your Last Guess Was:** `{last_guess_display}`")

        progress = min(st.session_state.gn_attempts / self.max_attempts, 1.0)
        st.progress(progress)

        # 4. Display History of Guesses
        if st.session_state.gn_history:
            st.subheader("📜 Guess History")
            
            # Show the last few entries
            display_history = st.session_state.gn_history[-MAX_HISTORY_DISPLAY:] 
            
            st.dataframe(
                display_history,
                column_config={
                    "Attempt": st.column_config.NumberColumn("Attempt #", help="The count of the guess."),
                    "Guess": st.column_config.NumberColumn("Your Guess", help="The number you guessed."),
                    "Result": st.column_config.TextColumn("Direction", help="Too High or Too Low."),
                    "Closeness": st.column_config.TextColumn("Temperature", help="How close you were.")
                },
                hide_index=True,
            )

        st.divider()

        # ===== HINT RULES (USER VISIBLE) - Simplified =====
        st.markdown("ℹ️ **Closeness Meter Rules**")
        st.markdown(
                """
                *Use the direction arrows and the color of the hint to guide your next guess!*
                
                **Direction**
                - 📉 **Too low** (Guess is smaller)
                - 📈 **Too high** (Guess is larger)
                
                **Temperature (How Close You Are - based on $ |Guess - Actual| $ )**
                - :green[🔥🔥 On Fire!] → Extremely close! Difference between guess and secret number is 5 digits 
                - :green[✅ Getting HOT!] → Very close! Difference between guess and secret number is 10 digits 
                - :orange[🟡 Lukewarm.] → Getting closer, Difference between guess and secret number is 20 digits 
                - :red[🥶 BRRR! It's FREEZING!] → Far away, try a big change.
                """
            )

        st.divider()

        # ===== GAME STATES =====

        if st.session_state.gn_won:
            st.balloons()
            st.success(st.session_state.gn_feedback)
            if st.button("🔄 Play Again", key="gn_win_reset"):
                self.reset_game()

        elif st.session_state.gn_attempts >= self.max_attempts:
            st.error(st.session_state.gn_feedback)
            if st.button("🔄 Try Again", key="gn_lose_reset"):
                self.reset_game()

        else:
            # Active game
            if st.session_state.gn_feedback:
                # Highlight current feedback for the current attempt
                st.markdown(f"<div style='background-color:#EBF8FF; padding: 10px; border-radius: 5px; border-left: 5px solid #007BFF;'>**Attempt {st.session_state.gn_attempts}:** {st.session_state.gn_feedback}</div>", unsafe_allow_html=True)
            elif st.session_state.gn_last_guess is None:
                st.info("Start the game by entering your first guess!")

            with st.form("gn_guess_form"):
                
                st.number_input(
                    "Enter your guess:",
                    min_value=self.min_num,
                    max_value=self.max_num,
                    step=1,
                    value=st.session_state.gn_input_value,
                    key="gn_input_value" 
                )

                st.form_submit_button(
                    "🔍 Check Guess",
                    on_click=_process_guess, 
                )