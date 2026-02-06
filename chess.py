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

message = Turtle()
message.hideturtle()
message.speed(0)

white_pieces = ["♙", "♘", "♗", "♖", "♕", "♔"]
black_pieces = ["♟", "♞", "♝", "♜", "♛", "♚"]
king_moved = [False, False]
rook_moved = [False, False, False, False]
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
en_passent_target = None
game_over = False
halfmoves = 0
history = {}
promotion_square = None

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

def get_position_state():
    return (tuple(tuple(row) for row in board), white_turn, tuple(king_moved), tuple(rook_moved))
    





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

def gonna_crash(row1, col1, row2, col2):
    dy, dx = (row2 - row1), (col2 - col1)
    row_direction, col_direction = (0 if dy == 0 else (-1 if dy < 0 else 1)), (0 if dx == 0 else (-1 if dx < 0 else 1))
    row, col = row1 + row_direction, col1 + col_direction
    while (row, col) != (row2, col2):
        if board[row][col] != "":
            return False
        row += row_direction
        col += col_direction
    return True

def piece_move_valid(origin, target):
    global en_passent_target
    (row1, col1), (row2, col2) = origin, target
    dy, dx = (row2 - row1), (col2 - col1)
    piece_to_move, target_piece = board[row1][col1], board[row2][col2]
    if piece_to_move in ["♙", "♟"]:
        white_pawn = (piece_to_move == "♙")
        if dx == 0 and target_piece == "":
            if (dy == -1 if white_pawn else dy == 1):
                return True
            elif (row1 == 6 if white_pawn else row1 == 1) and (dy == -2 if white_pawn else dy == 2) and (board[row1-1][col1] == "" if white_pawn else board[row1+1][col1] == ""):
                return True
        elif abs(dx) == 1 and (dy == -1 if white_pawn else dy == 1):
            if (target_piece in black_pieces if white_pawn else target_piece in white_pieces):
                return True
            elif en_passent_target == (row2, col2):
                return True
        return False

    elif piece_to_move in ["♘", "♞"]:
        return (abs(dy), abs(dx)) in [(1, 2), (2, 1)]
    
    elif piece_to_move in ["♔", "♚"]:
        if max(abs(dy), abs(dx)) == 1:
            return True
        elif dy == 0 and abs(dx) == 2:
            white_king = (piece_to_move == "♔")
            if not king_moved[(0 if white_king else 1)]:
                kingside = (dx == 2)
                if (dx == 2 if kingside else dx == -2):
                    if rook_moved[((0 if kingside else 1) + (0 if white_king else 2))]:
                        return False
                    elif board[(7 if white_king else 0)][(7 if kingside else 0)] not in ["♖", "♜"]:
                        return False
                    elif board[row1][(5 if kingside else 1)] != "" or (board[row1][6] != "" if kingside else (board[row1][2] != "" or board[row1][3] != "")):
                        return False
                    else:
                        return True
                else:
                    return False
            else:
                return False
        else:
            return False
    else:
        pieces = ["♗", "♝", "♖", "♜", "♕", "♛"]
        valid_movements = [(abs(dy) == abs(dx)), (dy == 0 or dx == 0)]
        valid_movements.append((valid_movements[0] or valid_movements[1]))

        if valid_movements[pieces.index(piece_to_move) // 2]:
            return gonna_crash(row1, col1, row2, col2)
        else:
            return False

def in_check(white):
    king = "♔" if white else "♚"
    for row in range(8):
        for col in range(8):
            if board[row][col] == king:
                king = (row, col)
                break
        if king not in ["♔", "♚"]:
            break
    for row in range(8):
        for col in range(8):
            piece_to_check = board[row][col]
            if piece_to_check == "":
                continue
            elif white and piece_to_check in white_pieces:
                continue
            elif not white and piece_to_check in black_pieces:
                continue
            if piece_move_valid((row, col), king):
                return True
    return False

def valid_move(origin, target):
    global white_turn
    (row1, col1), (row2, col2) = origin, target
    if board[row2][col2] != "":
        if board[row1][col1] in white_pieces and board[row2][col2] in white_pieces:
            return False
        if board[row1][col1] in black_pieces and board[row2][col2] in black_pieces:
            return False
        
    if not piece_move_valid(origin, target):
        return False
    
    piece_to_move, target_piece = board[row1][col1], board[row2][col2]
    board[row1][col1], board[row2][col2] = "", board[row1][col1]
    if in_check((board[row2][col2] in white_pieces)):
        board[row1][col1], board[row2][col2] = piece_to_move, target_piece
        return False
    elif piece_to_move in ["♔", "♚"] and abs(col2 - col1) == 2:
        white = (piece_to_move == "♔")
        if in_check(white):
            board[row1][col1], board[row2][col2] = piece_to_move, target_piece
            return False
        direction = 1 if col2 > col1 else -1
        col = col1 + direction
        while col != col2:
            original_piece = board[row1][col]
            board[row1][col1], board[row1][col] = "", piece_to_move
            if in_check(white):
                board[row1][col], board[row1][col1], board[row2][col2] = original_piece, piece_to_move, target_piece
                return False
            board[row1][col] = original_piece
            board[row1][col1] = piece_to_move
            col += direction
    
    board[row1][col1], board[row2][col2] = piece_to_move, target_piece

    return True

def checkmate_yet(white):
    for row1 in range(8):
        for col1 in range(8):
            piece = board[row1][col1]
            if piece == "":
                continue
            elif white and piece not in white_pieces:
                continue
            elif not white and piece not in black_pieces:
                continue

            for row2 in range(8):
                for col2 in range(8):
                    if valid_move((row1, col1), (row2, col2)):
                        return False
    return True







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
    if len(selected) == 1:
        show_moves()
    window.update()

def promote(piece):
    global promotion_square, white_turn
    row, col = promotion_square
    board[row][col] = piece
    promotion_square = None
    message.clear()
    window.onclick(move_pieces)
    white_turn = not white_turn
    position_check()
    draw_board()

def animate(row1, col1, row2, col2):
    global en_passent_target, king_moved, rook_moved, halfmoves, promotion_square
    current_player_piece = board[row1][col1]
    if current_player_piece in ["♔", "♚"] and abs(col2 - col1) == 2:
        animate(row1, (7 if col1 < col2 else 0), row2, (col2 + (-1 if col1 < col2 else 1)))
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
    if current_player_piece in ["♙", "♟"] and en_passent_target == (row2, col2):
        board[(row2-(-1 if current_player_piece == "♙" else 1))][col2] = ""
    if current_player_piece == "♙" and row1 == 6 and row2 == 4:
        en_passent_target = (5, col2)
    elif current_player_piece == "♟" and row1 == 1 and row2 == 3:
        en_passent_target = (2, col2)
    else:
        en_passent_target = None
    if current_player_piece in ["♙", "♟"] or board[row2][col2] != "":
        halfmoves = 0
    else:
        halfmoves += 1
    if current_player_piece in ["♔", "♚"]:
        king_moved[(0 if current_player_piece == "♔" else 1)] = True
    elif current_player_piece in ["♖", "♜"]:
        if (row1 == 7 if current_player_piece == "♖" else row1 == 0) and (col1 == 0  or col1 == 7):
            rook_moved[((0 if current_player_piece == "♖" else 2) + (0 if col1 == 0 else 1))] = True
    board[row2][col2] = current_player_piece
    if current_player_piece in ["♙", "♟"] and (row2 == 0 or row2 == 7):
        promotion_square = (row2, col2)
        message.clear()
        message.penup()
        message.goto(0, 0)
        options = (["♕", "♖", "♗", "♘"] if row2 == 0 else ["♛", "♜", "♝", "♞"])
        message.write("Promote to:\n1: Queen   2: Rook   3: Bishop   4: Knight\nType the number of your choice.", align="center", font=("Arial", 16, "bold"))
        window.onkey(lambda: promote(options[0]), "1")
        window.onkey(lambda: promote(options[1]), "2")
        window.onkey(lambda: promote(options[2]), "3")
        window.onkey(lambda: promote(options[3]), "4")
        window.listen()
    animation.clear()

def show_message(msg):
    message.color("red", "lightblue")
    message.goto(-sizes(False, True) * 0.3, -sizes(False, True) * 0.075)
    message.pendown()
    message.begin_fill()
    for two_sides in range(2):
        message.forward(sizes(False, True) * 0.6)
        message.left(90)
        message.forward(sizes(False, True) * 0.24)
        message.left(90)
    message.end_fill()
    message.penup()
    message.goto(0, 0)
    message.write(msg, align="center", font=("Arial", int(sizes(True) * 0.3), "bold"))
    window.onclick(close_message)
    
def close_message(x, y):
    message.clear()
    window.onclick(move_pieces)

def show_moves():
    row1, col1 = selected[0]
    for row in range(8):
        for col in range(8):
            if valid_move((row1, col1), (row, col)):
                x, y = cell_to_coord(row, col)
                t.goto(x + (2*sizes(True))/5, y + sizes(True)/2)
                t.pendown()
                t.dot(int(sizes(True) * 0.2), "green")
                t.penup()







def position_check():
    global history, game_over
    history[get_position_state()] = history.get(get_position_state(), 0) + 1
    if in_check(white_turn):
        if checkmate_yet(white_turn):
            show_message("Checkmate by " + ("Black" if white_turn else "White") + "!")
            game_over = True
        else:
            show_message("Check!")
    elif halfmoves > 99:
        show_message("Draw by 50-move rule")
        game_over = True
    elif history[get_position_state()] > 2:
        show_message("Draw by threefold repetition")
        game_over = True
    else:
        if checkmate_yet(white_turn):
            show_message("Stalemate!")
            game_over = True

def move_pieces(x, y):
    global selected, white_turn, game_over
    if game_over:
        return
    row, col = coord_to_cell(x, y)
    if row == None:
        return
    if check_turn(7-row, col):
        selected.append((7-row, col))
    else:
        selected = []
    if len(selected) == 2:
        if valid_move(selected[0], selected[1]):
            row1, col1 = selected[0]
            row2, col2 = selected[1]
            animate(row1, col1, row2, col2)
            if promotion_square is None:
                white_turn = not white_turn
                position_check()
            selected = []
        else:
            selected = []
    draw_board()

window.getcanvas().bind("<Configure>", draw_board)
window.onclick(move_pieces)

draw_board()

done()