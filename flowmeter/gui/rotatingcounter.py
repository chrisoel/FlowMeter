import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import tkinter as tk

class RotatingCounter:
    def __init__(self, root, x, y, initial_value=0, highlight=False):
        self.canvas = tk.Canvas(root, width=50, height=150, bg="black", highlightthickness=2)
        self.canvas.place(x=x, y=y)
        self.canvas.config(highlightbackground="red" if highlight else "black")
        self.current_value = initial_value
        self.render_counter()
        self.canvas.bind("<Button-1>", self.scroll_up)
        self.canvas.bind("<Button-3>", self.scroll_down)

    def render_counter(self):
        self.canvas.delete("all")
        self.canvas.create_text(25, 25, text=(self.current_value - 1) % 10, fill="gray", font=("Arial", 24))
        self.canvas.create_text(25, 75, text=self.current_value, fill="white", font=("Arial", 32))
        self.canvas.create_text(25, 125, text=(self.current_value + 1) % 10, fill="gray", font=("Arial", 24))

    def scroll_up(self, event=None):
        self.current_value = (self.current_value + 1) % 10
        self.render_counter()

    def scroll_down(self, event=None):
        self.current_value = (self.current_value - 1) % 10
        self.render_counter()

    def set_value(self, value):
        self.current_value = value
        self.render_counter()

    def get_value(self):
        return self.current_value