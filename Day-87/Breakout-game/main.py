import time
from turtle import Screen

from paddle import Paddle
from ball import Ball
from brick import Brick
from scoreboard import Scoreboard

# --- Screen setup ---
screen = Screen()
screen.setup(width=600, height=600)
screen.bgcolor("black")
screen.title("Breakout")
screen.tracer(0)  # turn off auto-refresh so we can control frame updates ourselves

paddle = Paddle()
ball = Ball()
scoreboard = Scoreboard()

# --- Build the wall of bricks ---
BRICK_COLORS = ["red", "orange", "yellow", "green", "cyan"]
ROWS = 5
COLS = 8
BRICK_WIDTH = 70   # horizontal spacing between brick centers
BRICK_HEIGHT = 30  # vertical spacing between brick rows
START_X = -(COLS - 1) * BRICK_WIDTH / 2
START_Y = 200

bricks = []
for row in range(ROWS):
    for col in range(COLS):
        x = START_X + col * BRICK_WIDTH
        y = START_Y - row * BRICK_HEIGHT
        brick = Brick(x, y, BRICK_COLORS[row % len(BRICK_COLORS)])
        bricks.append(brick)

# --- Keyboard controls ---
screen.listen()
screen.onkeypress(paddle.move_left, "Left")
screen.onkeypress(paddle.move_right, "Right")

# --- Main game loop ---
game_is_on = True
while game_is_on:
    screen.update()
    time.sleep(ball.move_speed)
    ball.move()

    # Bounce off left/right screen edges
    if ball.xcor() > 280 or ball.xcor() < -280:
        ball.bounce_x()

    # Bounce off the top of the screen
    if ball.ycor() > 280:
        ball.bounce_y()

    # Bounce off the paddle (only when moving downward, to avoid double-bounces)
    if (
        ball.y_move < 0
        and ball.ycor() < -260
        and ball.distance(paddle) < 60
        and abs(ball.xcor() - paddle.xcor()) < 55
    ):
        ball.bounce_y()

    # Ball fell past the paddle -> lose a life
    if ball.ycor() < -290:
        scoreboard.lose_life()
        if scoreboard.lives <= 0:
            game_is_on = False
            scoreboard.game_over()
        else:
            ball.reset_position()

    # Check collisions with bricks (only need to hit one per frame)
    for brick in bricks:
        if ball.distance(brick) < 35:
            ball.bounce_y()
            brick.hideturtle()
            bricks.remove(brick)
            scoreboard.increase_score()
            break

    # All bricks cleared -> player wins
    if len(bricks) == 0:
        game_is_on = False
        scoreboard.you_win()

screen.exitonclick()