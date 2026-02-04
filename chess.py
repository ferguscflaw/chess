from turtle import *

window = Screen()
window.title("Chess")
window.getcanvas().winfo_toplevel().minsize(500, 500)

t = Turtle()
t.hideturtle()
t.speed(0)
t.setheading(0)
t.pensize(1)

def draw_board(event):
    window.tracer(0, 0)
    t.clear()
    smallest = min(window.window_width(), window.window_height())
    square_size = smallest * 0.9
    cell_size = square_size / 8
    x = -square_size / 2
    y = -square_size / 2 + smallest * 0.1
    for i in range(8):
        for j in range(8):
            t.penup()
            t.goto(round(x + j*cell_size), round(y + i*cell_size))
            t.pendown()
            for side in range(4):
                t.forward(cell_size)
                t.right(90)
    window.update()

window.getcanvas().bind("<Configure>", draw_board)

draw_board(None)

done()