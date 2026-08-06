import turtle as t
import random

tim=t.Turtle()
t.colormode(255)
tim.speed("fastest")

def random_color():
    r = random.randint(0,255)
    g = random.randint(0,255)
    b = random.randint(0,255)
    color = (r,g,b)
    return color

def draw_spirograph(size_of_gap):
    for i in range(int(360/size_of_gap)):
        tim.color(random_color())
        tim.circle(100)
        tim.setheading(tim.heading()+size_of_gap)

draw_spirograph(5)

screen=t.Screen()
screen.exitonclick()


#directions = [0,90,180,270]
#tim.pensize(13)
#tim.speed("fastest")

#def draw_shape(num_sides):
#   for _ in range(num_sides):
#        angle = 360/num_sides
#        tim.forward(100)
#        tim.right(angle)

#for shape_side_n in range(3,11):
#    tim.color(random.choice(colours))
#    draw_shape(shape_side_n)

#for _ in range(200):
#    tim.color(random_color())
#    tim.forward(30)
#    tim.setheading(random.choice(directions))











