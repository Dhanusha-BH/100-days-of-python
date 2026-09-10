#!/usr/bin/env python3
"""
Fuse — The Dangerous Writing App
==================================
Keep typing. If you stop for too long, everything you've written vanishes.
Inspired by "The Most Dangerous Writing App."

Run with: python fuse.py
Requires: Python 3 with tkinter (included in most standard installs)
"""

import json
import os
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

HIGH_SCORE_FILE = os.path.join(os.path.expanduser("~"), ".fuse_scores.json")
TIME_LIMITS = [5, 10, 15]  # seconds of allowed silence before the fuse burns out


def load_scores():
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_scores(scores):
    try:
        with open(HIGH_SCORE_FILE, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2)
    except OSError:
        pass


class FuseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fuse — The Dangerous Writing App")
        self.geometry("760x600")
        self.minsize(600, 480)
        self.configure(bg="#141414")

        self.scores = load_scores()

        self.time_limit = tk.IntVar(value=10)
        self.remaining_ticks = self.time_limit.get() * 10  # tenths of a second, for a smooth bar
        self.armed = False    # True once the fuse is actively counting down
        self.exploded = False
        self.tick_job = None
        self._fuse_color = None
        self._last_word_count = 0

        self._build_styles()
        self._build_layout()
        self._reset_session(full_reset=True)

    # ------------------------------------------------------------------
    # Styling
    # ------------------------------------------------------------------
    def _build_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background="#141414")
        style.configure("TLabel", background="#141414", foreground="#f2f2f2", font=("Segoe UI", 11))
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"), foreground="#e63946")
        style.configure("Stat.TLabel", font=("Segoe UI", 12, "bold"), foreground="#f2f2f2")
        style.configure("Msg.TLabel", font=("Segoe UI", 12), foreground="#f4a261")
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("TCombobox", padding=4)
        style.configure(
            "Fuse.Horizontal.TProgressbar",
            troughcolor="#2a2a2a", background="#2a9d8f",
            thickness=16, bordercolor="#141414",
            lightcolor="#2a9d8f", darkcolor="#2a9d8f",
        )

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _build_layout(self):
        outer = ttk.Frame(self, padding=20)
        outer.pack(fill="both", expand=True)

        # --- Header ---
        header = ttk.Frame(outer)
        header.pack(fill="x", pady=(0, 10))

        ttk.Label(header, text="🔥 Fuse", style="Title.TLabel").pack(side="left")

        controls = ttk.Frame(header)
        controls.pack(side="right")

        ttk.Label(controls, text="Fuse length:").pack(side="left", padx=(0, 6))
        limit_box = ttk.Combobox(
            controls, textvariable=self.time_limit, values=TIME_LIMITS,
            state="readonly", width=4
        )
        limit_box.pack(side="left", padx=(0, 10))
        limit_box.bind("<<ComboboxSelected>>", lambda e: self._reset_session(full_reset=True))

        ttk.Button(controls, text="Restart", command=lambda: self._reset_session(full_reset=True)).pack(side="left", padx=4)
        ttk.Button(controls, text="Finish & Save", command=self.finish_session).pack(side="left", padx=4)

        # --- Best score ---
        self.best_label = ttk.Label(outer, text="", style="Stat.TLabel")
        self.best_label.pack(anchor="w", pady=(0, 10))

        # --- Text widget ---
        self.text = tk.Text(
            outer, wrap="word", font=("Georgia", 14),
            bg="#1b1b1b", fg="#f2f2f2", insertbackground="#e63946",
            relief="flat", padx=16, pady=14, undo=False
        )
        self.text.pack(fill="both", expand=True, pady=(0, 12))
        self.text.bind("<KeyRelease>", self.on_key_release)

        # --- Fuse bar ---
        self.fuse_bar = ttk.Progressbar(
            outer, style="Fuse.Horizontal.TProgressbar", orient="horizontal",
            mode="determinate", maximum=self.time_limit.get() * 10
        )
        self.fuse_bar.pack(fill="x", pady=(0, 8))

        # --- Status row ---
        status = ttk.Frame(outer)
        status.pack(fill="x")

        self.word_label = ttk.Label(status, text="Words: 0", style="Stat.TLabel")
        self.word_label.pack(side="left")

        self.time_label = ttk.Label(status, text="", style="Stat.TLabel")
        self.time_label.pack(side="right")

        # --- Message ---
        self.message_label = ttk.Label(
            outer, text="", style="Msg.TLabel", wraplength=700
        )
        self.message_label.pack(anchor="w", pady=(10, 0))

        self._refresh_best_label()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _refresh_best_label(self):
        key = str(self.time_limit.get())
        best = self.scores.get(key, {}).get("words", 0)
        self.best_label.config(text=f"Best at a {self.time_limit.get()}s fuse: {best} words")

    def word_count(self):
        content = self.text.get("1.0", "end-1c").strip()
        return len(content.split()) if content else 0

    def _update_best_score(self, words):
        key = str(self.time_limit.get())
        current_best = self.scores.get(key, {}).get("words", 0)
        if words > current_best:
            self.scores[key] = {"words": words, "date": time.strftime("%Y-%m-%d %H:%M")}
            save_scores(self.scores)
        self._refresh_best_label()

    # ------------------------------------------------------------------
    # Typing / timer
    # ------------------------------------------------------------------
    def on_key_release(self, event):
        if self.exploded:
            return

        # Any keystroke re-lights the fuse to its full length.
        self.remaining_ticks = self.time_limit.get() * 10
        self.word_label.config(text=f"Words: {self.word_count()}")

        if not self.armed:
            self.armed = True
            self.message_label.config(text="Keep going. Stop for too long and it's gone.")
            self._tick()

    def _tick(self):
        if not self.armed or self.exploded:
            return

        self.fuse_bar["value"] = self.remaining_ticks
        seconds_left = self.remaining_ticks / 10
        self.time_label.config(text=f"Fuse: {seconds_left:.1f}s")

        pct = self.remaining_ticks / (self.time_limit.get() * 10)
        if pct > 0.5:
            color = "#2a9d8f"   # calm green
        elif pct > 0.2:
            color = "#f4a261"   # warning amber
        else:
            color = "#e63946"   # danger red

        if color != self._fuse_color:
            style = ttk.Style(self)
            style.configure("Fuse.Horizontal.TProgressbar", background=color, lightcolor=color, darkcolor=color)
            self._fuse_color = color

        if self.remaining_ticks <= 0:
            self._explode()
            return

        self.remaining_ticks -= 1
        self.tick_job = self.after(100, self._tick)

    # ------------------------------------------------------------------
    # Explosion
    # ------------------------------------------------------------------
    def _explode(self):
        self.exploded = True
        self._last_word_count = self.word_count()
        self._update_best_score(self._last_word_count)
        self._flash(count=5)

    def _flash(self, count):
        if count <= 0:
            self.text.configure(bg="#1b1b1b")
            self.text.delete("1.0", "end")
            self.message_label.config(
                text=f"💥 Gone. You made it to {self._last_word_count} words. Start typing to try again."
            )
            self.armed = False
            self.exploded = False
            self.remaining_ticks = self.time_limit.get() * 10
            self.fuse_bar["value"] = self.remaining_ticks
            self.word_label.config(text="Words: 0")
            self.time_label.config(text="")
            self._fuse_color = None
            return

        color = "#e63946" if count % 2 == 0 else "#1b1b1b"
        self.text.configure(bg=color)
        self.after(150, lambda: self._flash(count - 1))

    # ------------------------------------------------------------------
    # Finish & Save (a deliberate, non-punishing way to end a session)
    # ------------------------------------------------------------------
    def finish_session(self):
        if self.tick_job is not None:
            self.after_cancel(self.tick_job)
            self.tick_job = None

        content = self.text.get("1.0", "end-1c")
        words = self.word_count()

        if not content.strip():
            messagebox.showinfo("Nothing to save", "You haven't written anything yet.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile="fuse_session.txt",
            title="Save your writing",
        )

        if not file_path:
            # They backed out of saving — don't punish them for that.
            # Resume the fuse right where it left off instead of wiping anything.
            self.message_label.config(text="Save cancelled. Keep writing — the fuse is still lit.")
            self._tick()
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        except OSError as e:
            messagebox.showerror("Couldn't save", str(e))
            self.message_label.config(text="Couldn't save. Keep writing — the fuse is still lit.")
            self._tick()
            return

        self._update_best_score(words)
        self._reset_session(full_reset=True)
        self.message_label.config(text=f"Session ended at {words} words. Saved to {os.path.basename(file_path)}.")

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------
    def _reset_session(self, full_reset=False):
        if self.tick_job is not None:
            self.after_cancel(self.tick_job)
            self.tick_job = None

        self.armed = False
        self.exploded = False
        self.remaining_ticks = self.time_limit.get() * 10
        self._fuse_color = None

        if full_reset:
            self.text.delete("1.0", "end")

        self.text.configure(bg="#1b1b1b")
        self.fuse_bar.configure(maximum=self.time_limit.get() * 10)
        self.fuse_bar["value"] = self.remaining_ticks
        self.word_label.config(text="Words: 0")
        self.time_label.config(text="")
        self.message_label.config(text="Start typing. If you stop, it's gone.")
        self._refresh_best_label()
        self.text.focus_set()


if __name__ == "__main__":
    app = FuseApp()
    app.mainloop()