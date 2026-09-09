from turtle import Turtle

SCREEN_WIDTH = 600
MOVE_DISTANCE = 25
PADDLE_START_X = 0
PADDLE_START_Y = -280


class Paddle(Turtle):
    """The player-controlled paddle at the bottom of the screen."""

    def __init__(self):
        super().__init__()
        self.shape("square")
        self.color("white")
        self.shapesize(stretch_wid=1, stretch_len=5)  # 20x20 -> 100x20
        self.penup()
        self.goto(PADDLE_START_X, PADDLE_START_Y)

    def move_left(self):
        new_x = self.xcor() - MOVE_DISTANCE
        left_bound = -SCREEN_WIDTH / 2 + 50  # +50 = half the paddle's width
        if new_x > left_bound:
            self.goto(new_x, self.ycor())

    def move_right(self):
        new_x = self.xcor() + MOVE_DISTANCE
        right_bound = SCREEN_WIDTH / 2 - 50
        if new_x < right_bound:
            self.goto(new_x, self.ycor())