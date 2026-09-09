from turtle import Turtle

BALL_START_X = 0
BALL_START_Y = -200
STARTING_MOVE = 4


class Ball(Turtle):
    """The ball that bounces around the screen."""

    def __init__(self):
        super().__init__()
        self.shape("circle")
        self.color("white")
        self.penup()
        self.goto(BALL_START_X, BALL_START_Y)
        self.x_move = STARTING_MOVE
        self.y_move = STARTING_MOVE
        self.move_speed = 0.01

    def move(self):
        new_x = self.xcor() + self.x_move
        new_y = self.ycor() + self.y_move
        self.goto(new_x, new_y)

    def bounce_x(self):
        self.x_move *= -1

    def bounce_y(self):
        self.y_move *= -1

    def reset_position(self):
        self.goto(BALL_START_X, BALL_START_Y)
        self.x_move = STARTING_MOVE
        self.y_move = STARTING_MOVE
        # Slightly speed the ball up isn't required, but you could
        # increase self.move_speed here over time for extra challenge.