from turtle import Turtle

BRICK_STRETCH_LEN = 3   # 20 * 3 = 60px wide
BRICK_STRETCH_WID = 1   # 20 * 1 = 20px tall


class Brick(Turtle):
    """A single brick in the wall. One instance per block."""

    def __init__(self, x, y, color):
        super().__init__()
        self.shape("square")
        self.color(color)
        self.shapesize(stretch_wid=BRICK_STRETCH_WID, stretch_len=BRICK_STRETCH_LEN)
        self.penup()
        self.goto(x, y)