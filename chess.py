from turtle import *
import time

window = Screen()
window.title("Chess")
window.getcanvas().winfo_toplevel().minsize(500, 500)

t = Turtle()
t.hideturtle()
t.speed(0)
t.setheading(0)
t.pensize(1)

animation = Turtle()
animation.hideturtle()
animation.speed(0)

white_pieces = ["♙", "♘", "♗", "♖", "♕", "♔"]
black_pieces = ["♟", "♞", "♝", "♜", "♛", "♚"]

board = [
    ["♜","♞","♝","♛","♚","♝","♞","♜"],
    ["♟","♟","♟","♟","♟","♟","♟","♟"],
    ["","","","","","","",""],
    ["","","","","","","",""],
    ["","","","","","","",""],
    ["","","","","","","",""],
    ["♙","♙","♙","♙","♙","♙","♙","♙"],
    ["♖","♘","♗","♕","♔","♗","♘","♖"],
]

selected = []
white_turn = True

def cell_to_coord(row, col):
    x = -sizes(False, True)/2 + col*sizes(True) + sizes(True)/8
    y = -sizes(False, True)/2 - sizes(False, False, True)*0.125 + (8-row)*sizes(True)
    return x, y

def coord_to_cell(x, y):
    col = int((x + sizes(False, True) / 2) // sizes(True))
    row = int((y + sizes(False, True) / 2 - sizes(False, False, True) * 0.1 + sizes(True)) // sizes(True))
    if 0 <= row and 0 <= col < 8:
        return row, col
    else:
        return None, None
    
def sizes(get_cell_size=False, get_square_size=False, get_smallest=False):
    smallest = min(window.window_width(), window.window_height())
    if get_smallest:
        return smallest
    elif get_square_size:
        return smallest * 0.9
    elif get_cell_size:
        return sizes(False, True) / 8

def check_turn(row, col):
    global white_turn
    if len(selected) == 0:
        if white_turn:
            check_turn = board[row][col] in white_pieces
        else:
            check_turn = board[row][col] in black_pieces
    elif len(selected) == 1:
        if white_turn:
            check_turn = board[row][col] in black_pieces or board[row][col] == ""
        else:
            check_turn = board[row][col] in white_pieces or board[row][col] == ""
    return check_turn

def draw_board(event=None):
    window.tracer(0, 0)
    t.clear()
    x = -sizes(False, True) / 2
    y = -sizes(False, True) / 2 + sizes(False, False, True) * 0.1
    for i in range(8):
        for j in range(8):
            t.penup()
            t.goto(round(x + j*sizes(True)), round(y + i*sizes(True)))
            t.pendown()
            for side in range(4):
                t.forward(sizes(True))
                t.right(90)
            if (7-i, j) in selected:
                t.penup()
                t.goto(x + j*sizes(True), y + i*sizes(True))
                t.pendown()
                t.pensize(3)
                for _ in range(4):
                    t.forward(sizes(True))
                    t.right(90)
                t.pensize(1)
            piece = board[7-i][j]
            t.penup()
            t.goto(x + j*sizes(True) + sizes(True)/8, y + i*sizes(True) - sizes(True))
            t.write(piece, font=("Arial", int(sizes(True)*0.6)))
    window.update()

def animate(row1, col1, row2, col2):
    current_player_piece = board[row1][col1]
    board[row1][col1], board[row2][col2], (x1, y1), (x2, y2) = "", "", cell_to_coord(row1, col1), cell_to_coord(row2, col2)
    dy, dx = ((y2 - y1) / 75), ((x2 - x1) / 75)
    draw_board()
    animation.clear()
    animation.penup()
    animation.goto(x1, y1)
    for frame in range(75):
        time.sleep(0.001)
        animation.clear()
        animation.goto(x1 + dx*frame, y1 + dy*frame)
        animation.write(current_player_piece, font=("Arial", int(sizes(True)*0.6)))
        window.update()
    board[row2][col2] = current_player_piece
    animation.clear()

def move_pieces(x, y):
    global selected, white_turn
    row, col = coord_to_cell(x, y)
    if row == None:
        return
    if check_turn(7-row, col):
        selected.append((7-row, col))
    else:
        selected = []
    if len(selected) == 2:
        row1, col1 = selected[0]
        row2, col2 = selected[1]
        animate(row1, col1, row2, col2)
        white_turn = not white_turn
        selected = []
    draw_board()

window.getcanvas().bind("<Configure>", draw_board)
window.onclick(move_pieces)

draw_board()

done()