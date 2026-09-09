
"""
Typing Speed Trainer
=====================
A Tkinter desktop app that measures typing speed (WPM) and accuracy.

Features
--------
- Multiple sample texts across three difficulty levels
- Live highlighting of correct/incorrect characters as you type
- Timer starts automatically on your first keystroke
- Live WPM & accuracy readout while you type
- Final results screen with Net WPM, Gross WPM, and Accuracy
- Persistent high-score leaderboard (saved to your home directory)
- "New Text" and "Restart" controls to keep practicing

Run with:  python typing_speed_trainer.py
Requires: Python 3 with tkinter (included in most standard installs)
"""

import json
import os
import random
import time
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

# --------------------------------------------------------------------------
# Sample texts, grouped by difficulty
# --------------------------------------------------------------------------
SAMPLE_TEXTS = {
    "Easy": [
        "The quick brown fox jumps over the lazy dog near the old barn.",
        "She sells seashells by the seashore every single summer morning.",
        "A gentle breeze moved through the trees as the sun began to rise.",
        "Cats and dogs often become the best of friends if given enough time.",
    ],
    "Medium": [
        "Learning to type quickly and accurately takes regular practice over "
        "time. The more you type, the more your fingers remember where each "
        "key is located, and soon you will not even need to look at the keyboard.",
        "Python is a popular programming language known for its readability "
        "and simplicity. It is widely used for web development, data science, "
        "automation, and building desktop applications like this one.",
        "Good posture and finger placement can make a huge difference in your "
        "typing speed. Keep your wrists straight, your fingers curved, and "
        "rest them lightly on the home row keys between each keystroke.",
    ],
    "Hard": [
        "Artificial intelligence, machine learning, and natural language "
        "processing have transformed the way software understands human "
        "communication; however, mastering the fundamentals of programming "
        "still requires patience, curiosity, and countless hours of practice.",
        "The history of the printing press demonstrates how a single "
        "invention can reshape civilization: Gutenberg's movable-type system, "
        "developed in the fifteenth century, dramatically increased the "
        "availability of books and accelerated the spread of literacy across Europe.",
        "Quantum computing exploits phenomena such as superposition and "
        "entanglement to perform certain calculations exponentially faster "
        "than classical computers, though building stable, error-corrected "
        "qubits remains one of the greatest engineering challenges of our time.",
    ],
}

HIGH_SCORE_FILE = os.path.join(os.path.expanduser("~"), ".typing_speed_scores.json")
MAX_HIGH_SCORES = 10


# --------------------------------------------------------------------------
# High score persistence
# --------------------------------------------------------------------------
def load_high_scores():
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []
    return []


def save_high_scores(scores):
    try:
        with open(HIGH_SCORE_FILE, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2)
    except OSError:
        pass


def qualifies_for_leaderboard(scores, wpm):
    if len(scores) < MAX_HIGH_SCORES:
        return True
    return wpm > min(s["wpm"] for s in scores)


# --------------------------------------------------------------------------
# Main Application
# --------------------------------------------------------------------------
class TypingSpeedApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Typing Speed Trainer")
        self.geometry("780x600")
        self.minsize(650, 520)
        self.configure(bg="#1e1f26")

        self.high_scores = load_high_scores()

        self.current_text = ""
        self.start_time = None
        self.finished = False
        self.timer_job = None

        self._build_styles()
        self._build_layout()
        self.new_text()

    # ---------------------------------------------------------------
    # Styling
    # ---------------------------------------------------------------
    def _build_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        bg = "#1e1f26"
        fg = "#f2f2f2"
        accent = "#6ee7b7"

        style.configure("TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=fg, font=("Segoe UI", 11))
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"), foreground=accent)
        style.configure("Stat.TLabel", font=("Segoe UI", 13, "bold"), foreground=accent)
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("TCombobox", padding=4)

    # ---------------------------------------------------------------
    # Layout
    # ---------------------------------------------------------------
    def _build_layout(self):
        outer = ttk.Frame(self, padding=20)
        outer.pack(fill="both", expand=True)

        # --- Header ---
        header = ttk.Frame(outer)
        header.pack(fill="x", pady=(0, 12))

        ttk.Label(header, text="⌨  Typing Speed Trainer", style="Title.TLabel").pack(side="left")

        controls = ttk.Frame(header)
        controls.pack(side="right")

        ttk.Label(controls, text="Difficulty:").pack(side="left", padx=(0, 6))
        self.difficulty_var = tk.StringVar(value="Medium")
        difficulty_box = ttk.Combobox(
            controls, textvariable=self.difficulty_var,
            values=list(SAMPLE_TEXTS.keys()), state="readonly", width=10
        )
        difficulty_box.pack(side="left", padx=(0, 10))
        difficulty_box.bind("<<ComboboxSelected>>", lambda e: self.new_text())

        ttk.Button(controls, text="New Text", command=self.new_text).pack(side="left", padx=4)
        ttk.Button(controls, text="Restart", command=self.restart).pack(side="left", padx=4)
        ttk.Button(controls, text="High Scores", command=self.show_high_scores).pack(side="left", padx=4)

        # --- Sample text display ---
        ttk.Label(outer, text="Type the text below:").pack(anchor="w")
        self.sample_display = tk.Text(
            outer, height=6, wrap="word", font=("Consolas", 14),
            bg="#2a2b36", fg="#cfcfcf", insertbackground="#cfcfcf",
            relief="flat", padx=12, pady=10, state="disabled", cursor="arrow"
        )
        self.sample_display.pack(fill="x", pady=(4, 14))
        self.sample_display.tag_configure("correct", foreground="#6ee7b7")
        self.sample_display.tag_configure("incorrect", foreground="#f87171", underline=True)
        self.sample_display.tag_configure("current", background="#3a3b4a")

        # --- Input box ---
        ttk.Label(outer, text="Your input:").pack(anchor="w")
        self.input_box = tk.Text(
            outer, height=6, wrap="word", font=("Consolas", 14),
            bg="#2a2b36", fg="#f2f2f2", insertbackground="#f2f2f2",
            relief="flat", padx=12, pady=10
        )
        self.input_box.pack(fill="x", pady=(4, 14))
        self.input_box.bind("<KeyRelease>", self.on_key_release)
        self.input_box.bind("<Return>", lambda e: "break")  # no newlines allowed

        # --- Stats bar ---
        stats = ttk.Frame(outer)
        stats.pack(fill="x", pady=(0, 10))

        self.time_label = ttk.Label(stats, text="Time: 0.0s", style="Stat.TLabel")
        self.time_label.pack(side="left", padx=(0, 25))

        self.wpm_label = ttk.Label(stats, text="WPM: 0", style="Stat.TLabel")
        self.wpm_label.pack(side="left", padx=(0, 25))

        self.acc_label = ttk.Label(stats, text="Accuracy: 100%", style="Stat.TLabel")
        self.acc_label.pack(side="left")

        # --- Progress bar ---
        self.progress = ttk.Progressbar(outer, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", pady=(0, 10))

        # --- Status / result message ---
        self.status_label = ttk.Label(outer, text="Start typing to begin the timer.", wraplength=700)
        self.status_label.pack(anchor="w")

    # ---------------------------------------------------------------
    # Test lifecycle
    # ---------------------------------------------------------------
    def new_text(self):
        difficulty = self.difficulty_var.get()
        self.current_text = random.choice(SAMPLE_TEXTS[difficulty])
        self._reset(clear_sample=True)

    def restart(self):
        self._reset(clear_sample=True)

    def _reset(self, clear_sample=False):
        if self.timer_job is not None:
            self.after_cancel(self.timer_job)
            self.timer_job = None

        self.start_time = None
        self.finished = False

        self.input_box.configure(state="normal")
        self.input_box.delete("1.0", "end")

        self.sample_display.configure(state="normal")
        if clear_sample:
            self.sample_display.delete("1.0", "end")
            self.sample_display.insert("1.0", self.current_text)
        self.sample_display.tag_remove("correct", "1.0", "end")
        self.sample_display.tag_remove("incorrect", "1.0", "end")
        self.sample_display.tag_remove("current", "1.0", "end")
        self.sample_display.configure(state="disabled")

        self.time_label.config(text="Time: 0.0s")
        self.wpm_label.config(text="WPM: 0")
        self.acc_label.config(text="Accuracy: 100%")
        self.progress["value"] = 0
        self.status_label.config(text="Start typing to begin the timer.")

        self.input_box.focus_set()

    def on_key_release(self, event):
        if self.finished:
            return

        typed = self.input_box.get("1.0", "end-1c")

        # Start the timer on the very first character typed.
        if self.start_time is None and len(typed) > 0:
            self.start_time = time.time()
            self._tick()

        self._update_highlighting(typed)
        self._update_live_stats(typed)

        if len(typed) >= len(self.current_text):
            self.finish_test(typed)

    def _update_highlighting(self, typed):
        self.sample_display.configure(state="normal")
        self.sample_display.tag_remove("correct", "1.0", "end")
        self.sample_display.tag_remove("incorrect", "1.0", "end")
        self.sample_display.tag_remove("current", "1.0", "end")

        sample = self.current_text
        limit = min(len(typed), len(sample))

        for i in range(limit):
            start = f"1.0+{i}c"
            end = f"1.0+{i+1}c"
            tag = "correct" if typed[i] == sample[i] else "incorrect"
            self.sample_display.tag_add(tag, start, end)

        if limit < len(sample):
            cur_start = f"1.0+{limit}c"
            cur_end = f"1.0+{limit+1}c"
            self.sample_display.tag_add("current", cur_start, cur_end)

        self.sample_display.configure(state="disabled")

        self.progress["value"] = (limit / len(sample)) * 100 if sample else 0

    def _update_live_stats(self, typed):
        if self.start_time is None:
            return
        elapsed = max(time.time() - self.start_time, 0.001)
        wpm, accuracy = self._compute_stats(typed, elapsed)
        self.time_label.config(text=f"Time: {elapsed:.1f}s")
        self.wpm_label.config(text=f"WPM: {wpm}")
        self.acc_label.config(text=f"Accuracy: {accuracy}%")

    def _tick(self):
        if self.finished or self.start_time is None:
            return
        elapsed = time.time() - self.start_time
        self.time_label.config(text=f"Time: {elapsed:.1f}s")
        self.timer_job = self.after(100, self._tick)

    def _compute_stats(self, typed, elapsed_seconds):
        """Standard typing metric: 1 'word' = 5 characters. Returns (net_wpm, accuracy)."""
        sample = self.current_text
        limit = min(len(typed), len(sample))
        correct_chars = sum(1 for i in range(limit) if typed[i] == sample[i])
        total_typed = len(typed)

        minutes = elapsed_seconds / 60.0
        net_wpm = round((correct_chars / 5) / minutes) if minutes > 0 else 0
        accuracy = round((correct_chars / total_typed) * 100) if total_typed > 0 else 100

        return net_wpm, accuracy

    def finish_test(self, typed):
        self.finished = True
        if self.timer_job is not None:
            self.after_cancel(self.timer_job)
            self.timer_job = None

        elapsed = max(time.time() - self.start_time, 0.001)
        minutes = elapsed / 60.0
        sample = self.current_text
        limit = min(len(typed), len(sample))
        correct_chars = sum(1 for i in range(limit) if typed[i] == sample[i])
        total_typed = len(typed)

        net_wpm = round((correct_chars / 5) / minutes)
        gross_wpm = round((total_typed / 5) / minutes)
        accuracy = round((correct_chars / total_typed) * 100) if total_typed > 0 else 100

        self.input_box.configure(state="disabled")
        self.time_label.config(text=f"Time: {elapsed:.1f}s")
        self.wpm_label.config(text=f"WPM: {net_wpm}")
        self.acc_label.config(text=f"Accuracy: {accuracy}%")
        self.progress["value"] = 100

        avg_note = "above" if net_wpm > 40 else "around" if net_wpm > 30 else "below"
        self.status_label.config(
            text=(
                f"Done! Net WPM: {net_wpm}  |  Gross WPM: {gross_wpm}  |  Accuracy: {accuracy}%\n"
                f"That's {avg_note} the average typing speed of 40 WPM. "
                f"Click 'Restart' to try the same text again, or 'New Text' for a fresh one."
            )
        )

        if qualifies_for_leaderboard(self.high_scores, net_wpm):
            self._prompt_for_high_score(net_wpm, accuracy)

    def _prompt_for_high_score(self, wpm, accuracy):
        name = simpledialog.askstring(
            "New High Score!",
            f"You scored {wpm} WPM at {accuracy}% accuracy — that makes the leaderboard!\n"
            "Enter your name:",
            parent=self,
        )
        if not name:
            name = "Anonymous"

        entry = {
            "name": name.strip()[:20],
            "wpm": wpm,
            "accuracy": accuracy,
            "difficulty": self.difficulty_var.get(),
            "date": time.strftime("%Y-%m-%d %H:%M"),
        }
        self.high_scores.append(entry)
        self.high_scores.sort(key=lambda s: s["wpm"], reverse=True)
        self.high_scores = self.high_scores[:MAX_HIGH_SCORES]
        save_high_scores(self.high_scores)

    def show_high_scores(self):
        win = tk.Toplevel(self)
        win.title("High Scores")
        win.geometry("420x400")
        win.configure(bg="#1e1f26")

        ttk.Label(win, text="🏆 Leaderboard", style="Title.TLabel").pack(pady=(15, 10))

        if not self.high_scores:
            ttk.Label(win, text="No scores yet. Go take a test!").pack(pady=20)
            return

        columns = ("rank", "name", "wpm", "acc", "difficulty", "date")
        tree = ttk.Treeview(win, columns=columns, show="headings", height=10)
        headings = {
            "rank": "#", "name": "Name", "wpm": "WPM",
            "acc": "Acc%", "difficulty": "Level", "date": "Date",
        }
        widths = {"rank": 30, "name": 100, "wpm": 50, "acc": 50, "difficulty": 70, "date": 110}
        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=widths[col], anchor="center")
        tree.pack(fill="both", expand=True, padx=15, pady=10)

        for i, s in enumerate(self.high_scores, start=1):
            tree.insert("", "end", values=(i, s["name"], s["wpm"], s["accuracy"], s["difficulty"], s["date"]))

        ttk.Button(win, text="Close", command=win.destroy).pack(pady=(0, 15))


if __name__ == "__main__":
    app = TypingSpeedApp()
    app.mainloop()