from turtle import Turtle

STARTING_LIVES = 3
FONT = ("Courier", 18, "normal")
BIG_FONT = ("Courier", 26, "bold")


class Scoreboard(Turtle):
    """Displays and tracks the player's score and remaining lives."""

    def __init__(self):
        super().__init__()
        self.score = 0
        self.lives = STARTING_LIVES
        self.color("white")
        self.penup()
        self.hideturtle()
        self.goto(0, 260)
        self.update_display()

    def update_display(self):
        self.clear()
        self.write(
            f"Score: {self.score}    Lives: {self.lives}",
            align="center",
            font=FONT,
        )

    def increase_score(self, points=10):
        self.score += points
        self.update_display()

    def lose_life(self):
        self.lives -= 1
        self.update_display()

    def game_over(self):
        self.goto(0, 0)
        self.write("GAME OVER", align="center", font=BIG_FONT)

    def you_win(self):
        self.goto(0, 0)
        self.write("YOU WIN!", align="center", font=BIG_FONT)