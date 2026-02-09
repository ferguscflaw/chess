from turtle import *

def sizes(get_cell_size=False, get_square_size=False, get_smallest=False):
    smallest = min(window.window_width(), window.window_height())
    if get_smallest:
        return smallest
    elif get_square_size:
        return smallest * 0.9
    elif get_cell_size:
        return sizes(False, True) / 8

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

def base64(data, encode=True):
    # I specially created this to work for only my program (definitely not because I couldn't care less about padding), so it will decrypt incorrectly if you try it with programs other people made.
    # Unless you turn all = into A, where it will work. This base 64 code is copyright. Unless you ask to use it and I give permission.
    # The changing of for loop to enumerating was Google AI's idea, so that section, sum(alphabet.index(character) << (6 * (3-index)) for index, character in enumerate(chunk)), is not copyright. Nothing more.
    # I have changed this into oneline as much as I can (but I am pretty sure it can still be shortened further), but if you want the original base 64 code I made, feel free to ask.
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    result = []
    bytes_of_text = ([ord(c) for c in data] if encode else data)
    for nibbling_bit in (range(0, len(bytes_of_text), 3) if encode else range(0, len(data), 4)):
        chunk = bytes_of_text[nibbling_bit:nibbling_bit+(3 if encode else 4)]
        chunk += ([0, 0, 0][:-len(chunk)] if encode else "")
        combined = ((chunk[0] << 16) | (chunk[1] << 8) | chunk[2]) if encode else sum(alphabet.index(character) << (6 * (3-index)) for index, character in enumerate(chunk))
        for shift in ((18, 12, 6, 0) if encode else (16, 8, 0)):
            result.append((alphabet[((combined >> shift) & 0b111111)]) if encode else ((combined >> shift) & 0b11111111))
    return "".join((b if encode else chr(b)) for b in result)

class GameState:
    def __init__(self):
        self.setup_start_position()
        
    def setup_start_position(self):
        self.white_pieces = ["♙", "♘", "♗", "♖", "♕", "♔"]
        self.black_pieces = ["♟", "♞", "♝", "♜", "♛", "♚"]
        self.king_moved = [False, False]
        self.rook_moved = [False, False, False, False]
        self.board = [
            ["♜","♞","♝","♛","♚","♝","♞","♜"],
            ["♟","♟","♟","♟","♟","♟","♟","♟"],
            ["","","","","","","",""],
            ["","","","","","","",""],
            ["","","","","","","",""],
            ["","","","","","","",""],
            ["♙","♙","♙","♙","♙","♙","♙","♙"],
            ["♖","♘","♗","♕","♔","♗","♘","♖"],
        ]
        self.pieces_map = { "♙": "p", "♖": "r", "♘": "n", "♗": "b", "♕": "q", "♔": "k", "♟": "P", "♜": "R", "♞": "N", "♝": "B", "♛": "Q", "♚": "K" }
        self.letter_map = { letter: piece_name for piece_name, letter in self.pieces_map.items() }
        self.selected = []
        self.white_turn = True
        self.en_passent_target = None
        self.game_over = False
        self.halfmoves = 0
        self.history = {}
        self.promotion_square = None
        self.message = ""

    def format_row(self, row, compress=True):
        result = ("" if compress else [])
        if compress:
            for piece in row:
                result = (result+self.pieces_map[piece] if piece != "" else (result+"1" if (len(result) == 0 or result[-1] in "prnbqkPRNBQK") else result[:-1]+str(int(result[-1])+1)))
        else:
            for letter in row:
                if letter in "prnbqkPRNBQK":
                    result.append((self.letter_map[letter]))
                else:
                    result.extend(([""]*(int(letter))))
        return result
    
    def export(self):
        return base64(("|".join(["/".join(self.format_row(row) for row in self.board), ("w" if self.white_turn else "b"), ("-" if self.en_passent_target is None else f"{self.en_passent_target[0]},{self.en_passent_target[1]}"), str(self.halfmoves), ("".join("1" if k else "0" for k in self.king_moved)), ("".join("1" if r else "0" for r in self.rook_moved))])))
    
    def continue_game(self, data):
        data_sections = base64(data, False).split("|")
        self.board = [self.format_row(row, False) for row in data_sections[0].split("/")]
        self.white_turn = (data_sections[1] == "w")
        self.en_passent_target = None if data_sections[2] == "-" else tuple(map(int, data_sections[2].split(",")))
        self.halfmoves = int(data_sections[3])
        self.king_moved = [c == "1" for c in data_sections[4]]
        self.rook_moved = [c == "1" for c in data_sections[5]]
        self.game_over = False


class ChessGame:
    def __init__(self):
        t = self.t = Turtle()
        t.hideturtle()
        t.speed(0)

        animation = self.animation = Turtle()
        animation.hideturtle()
        animation.speed(0)

        message = self.message = Turtle()
        message.hideturtle()
        message.speed(0)

        self.game_state = GameState()
    
        window.getcanvas().bind("<Configure>", self.draw_board)
        window.onclick(self.move_pieces)
        window.onkey(lambda: self.game_data(False), "i")
        window.onkey(lambda: self.game_data(), "e")
        window.listen()

        self.draw_board()
        self.show_message("i - import game.\ne - export game")

    def get_position_state(self):
        game = self.game_state
        return (tuple(tuple(row) for row in game.board), game.white_turn, tuple(game.king_moved), tuple(game.rook_moved))

    def game_data(self, export=True):
        game_state = self.game_state
        if export:
            window._root.clipboard_clear()
            window._root.clipboard_append(game_state.export())
            self.show_message("Game code copied!")
        else:
            data = window.textinput("Import Game", "Enter your game code:")
            window.onkey(lambda: self.game_data(False), "i")
            window.onkey(lambda: self.game_data(), "e")
            window.listen()
            try:
                game_state.continue_game(data)
                self.draw_board()
                self.position_check()
            except:
                self.show_message("Invalid code")

    def check_turn(self, row, col):
        game_state = self.game_state
        if len(game_state.selected) == 0:
            if game_state.white_turn:
                check_turn = game_state.board[row][col] in game_state.white_pieces
            else:
                check_turn = game_state.board[row][col] in game_state.black_pieces
        elif len(game_state.selected) == 1:
            if game_state.white_turn:
                check_turn = game_state.board[row][col] in game_state.black_pieces or game_state.board[row][col] == ""
            else:
                check_turn = game_state.board[row][col] in game_state.white_pieces or game_state.board[row][col] == ""
        return check_turn

    def gonna_crash(self, row1, col1, row2, col2):
        dy, dx = (row2 - row1), (col2 - col1)
        row_direction, col_direction = (0 if dy == 0 else (-1 if dy < 0 else 1)), (0 if dx == 0 else (-1 if dx < 0 else 1))
        row, col = row1 + row_direction, col1 + col_direction
        while (row, col) != (row2, col2):
            if self.game_state.board[row][col] != "":
                return False
            row += row_direction
            col += col_direction
        return True

    def piece_move_valid(self, origin, target):
        game_state = self.game_state
        (row1, col1), (row2, col2) = origin, target
        dy, dx = (row2 - row1), (col2 - col1)
        piece_to_move, target_piece = game_state.board[row1][col1], game_state.board[row2][col2]
        
        if piece_to_move in ["♙", "♟"]:
            white_pawn = (piece_to_move == "♙")
            if dx == 0 and target_piece == "":
                if (dy == -1 if white_pawn else dy == 1):
                    return True
                elif (row1 == 6 if white_pawn else row1 == 1) and (dy == -2 if white_pawn else dy == 2) and (game_state.board[row1-1][col1] == "" if white_pawn else game_state.board[row1+1][col1] == ""):
                    return True
            elif abs(dx) == 1 and (dy == -1 if white_pawn else dy == 1):
                if (target_piece in game_state.black_pieces if white_pawn else target_piece in game_state.white_pieces):
                    return True
                elif game_state.en_passent_target == (row2, col2):
                    return True
            return False

        elif piece_to_move in ["♘", "♞"]:
            return (abs(dy), abs(dx)) in [(1, 2), (2, 1)]
        
        elif piece_to_move in ["♔", "♚"]:
            if max(abs(dy), abs(dx)) == 1:
                return True
            elif dy == 0 and abs(dx) == 2:
                white_king = (piece_to_move == "♔")
                if not game_state.king_moved[(0 if white_king else 1)]:
                    kingside = (dx == 2)
                    if (game_state.rook_moved[((1 if kingside else 0) + (0 if white_king else 2))]) or (game_state.board[(7 if white_king else 0)][(7 if kingside else 0)] not in ["♖", "♜"]) or (game_state.board[row1][(5 if kingside else 1)] != "" or (game_state.board[row1][6] != "" if kingside else (game_state.board[row1][2] != "" or game_state.board[row1][3] != ""))):
                        return False
                    return True
            return False
        else:
            pieces = ["♗", "♝", "♖", "♜", "♕", "♛"]
            valid_movements = [(a:=abs(dy)==abs(dx)), (b:=dy==0 or dx==0), (a or b)]

            if valid_movements[pieces.index(piece_to_move) // 2]:
                return self.gonna_crash(row1, col1, row2, col2)
            return False

    def in_check(self, white):
        game_state = self.game_state
        king = "♔" if white else "♚"
        for row in range(8):
            for col in range(8):
                if game_state.board[row][col] == king:
                    king = (row, col)
                    break
            if king not in ["♔", "♚"]:
                break
        for row in range(8):
            for col in range(8):
                piece_to_check = game_state.board[row][col]
                if piece_to_check == "":
                    continue
                elif white and piece_to_check in game_state.white_pieces:
                    continue
                elif not white and piece_to_check in game_state.black_pieces:
                    continue
                if self.piece_move_valid((row, col), king):
                    return True
        return False

    def valid_move(self, origin, target):
        game_state = self.game_state
        (row1, col1), (row2, col2) = origin, target
        if game_state.board[row2][col2] != "":
            if (game_state.board[row1][col1] in game_state.white_pieces and game_state.board[row2][col2] in game_state.white_pieces) or (game_state.board[row1][col1] in game_state.black_pieces and game_state.board[row2][col2] in game_state.black_pieces):
                return False
            
        if not self.piece_move_valid(origin, target):
            return False
        
        piece_to_move, target_piece, game_state.board[row2][col2], game_state.board[row1][col1] = game_state.board[row1][col1], game_state.board[row2][col2], game_state.board[row1][col1], ""
        if self.in_check((game_state.board[row2][col2] in game_state.white_pieces)):
            game_state.board[row1][col1], game_state.board[row2][col2] = piece_to_move, target_piece
            return False
        elif piece_to_move in ["♔", "♚"] and abs(col2 - col1) == 2:
            game_state.board[row1][col1], game_state.board[row2][col2] = piece_to_move, target_piece
            white, direction, col = (piece_to_move == "♔"), (1 if col2 > col1 else -1), col1
            while col != col2:
                original_piece, game_state.board[row1][col1], game_state.board[row1][col] = game_state.board[row1][col], "", piece_to_move
                if self.in_check(white):
                    game_state.board[row1][col], game_state.board[row1][col1], game_state.board[row2][col2] = original_piece, piece_to_move, target_piece
                    return False
                game_state.board[row1][col], game_state.board[row1][col1] = original_piece, piece_to_move
                col += direction
        game_state.board[row1][col1], game_state.board[row2][col2] = piece_to_move, target_piece
        return True

    def checkmate_yet(self, white):
        game_state = self.game_state
        for row1 in range(8):
            for col1 in range(8):
                piece = game_state.board[row1][col1]
                if (piece == "") or (white and piece not in game_state.white_pieces) or (not white and piece not in game_state.black_pieces):
                    continue
                for row2 in range(8):
                    for col2 in range(8):
                        if self.valid_move((row1, col1), (row2, col2)):
                            return False
        return True

    def special_cases(self, current_player_piece, row1, col1, row2, col2):
        game_state = self.game_state
        if current_player_piece in ["♙", "♟"] and game_state.en_passent_target == (row2, col2):
            game_state.board[(row2-(-1 if current_player_piece == "♙" else 1))][col2] = ""
        if current_player_piece == "♙" and row1 == 6 and row2 == 4:
            game_state.en_passent_target = (5, col2)
        elif current_player_piece == "♟" and row1 == 1 and row2 == 3:
            game_state.en_passent_target = (2, col2)
        else:
            game_state.en_passent_target = None


        if current_player_piece in ["♙", "♟"] or game_state.board[row2][col2] != "":
            game_state.halfmoves = 0
        else:
            game_state.halfmoves += 1

        if current_player_piece in ["♔", "♚"]:
            game_state.king_moved[(0 if current_player_piece == "♔" else 1)] = True
        elif current_player_piece in ["♖", "♜"] and ((row1 == 7 if current_player_piece == "♖" else row1 == 0) and (col1 == 0  or col1 == 7)):
            game_state.rook_moved[((0 if current_player_piece == "♖" else 2) + (0 if col1 == 0 else 1))] = True

        game_state.board[row2][col2] = current_player_piece
        
        if (current_player_piece == "♙" and row2 == 0) or (current_player_piece == "♟" and row2 == 7):
            game_state.promotion_square = (row2, col2)
            options = (["♕", "♖", "♗", "♘"] if row2 == 0 else ["♛", "♜", "♝", "♞"])
            self.show_message("Promote to:\n1: Queen   2: Rook   3: Bishop   4: Knight\nEnter the number of your choice.", int(sizes(True)//6))
            window.onkey(lambda: self.promote(options[0]), "1")
            window.onkey(lambda: self.promote(options[1]), "2")
            window.onkey(lambda: self.promote(options[2]), "3")
            window.onkey(lambda: self.promote(options[3]), "4")
            window.update()
            window.listen()









    def draw_board(self, event=None):
        t, game_state = self.t, self.game_state
        window.tracer(0, 0)
        t.clear()
        x = -sizes(False, True) / 2
        y = -sizes(False, True) / 2 + sizes(False, False, True) * 0.1
        for i in range(8):
            for j in range(8):
                t.penup()
                t.goto(round(x + j*sizes(True)), round(y + i*sizes(True)))
                t.pendown()
                if (i + j) % 2 == 0:
                    t.fillcolor("#E4C4B4")
                else:
                    t.fillcolor("#F5F5D5")
                t.begin_fill()
                for side in range(4):
                    t.forward(sizes(True))
                    t.right(90)
                t.end_fill()
                if (7-i, j) in game_state.selected:
                    t.penup()
                    t.goto(x + j*sizes(True), y + i*sizes(True))
                    t.pendown()
                    t.fillcolor(("#D0FFD0" if game_state.white_turn else "#7F907F"))
                    t.begin_fill()
                    for side in range(4):
                        t.forward(sizes(True))
                        t.right(90)
                    t.end_fill()
                piece = game_state.board[7-i][j]
                t.penup()
                t.goto(x + j*sizes(True) + sizes(True)/8, y + i*sizes(True) - sizes(True))
                t.write(piece, font=("Arial", int(sizes(True)*0.6)))
        if game_state.message != "":
            self.show_message(game_state.message[0], game_state.message[1])
        window.update()

    def promote(self, piece):
        game_state = self.game_state
        row, col = game_state.promotion_square
        game_state.board[row][col] = piece
        game_state.promotion_square = None
        game_state.message = ""
        self.message.clear()
        window.onkey(lambda: (), "1")
        window.onkey(lambda: (), "2")
        window.onkey(lambda: (), "3")
        window.onkey(lambda: (), "4")
        game_state.white_turn = not game_state.white_turn
        self.position_check()
        self.draw_board()
        window.update()

    def animate(self, row1, col1, row2, col2):
        game_state, animation = self.game_state, self.animation
        current_player_piece = game_state.board[row1][col1]
        if current_player_piece in ["♔", "♚"] and abs(col2 - col1) == 2:
            self.animate(row1, (7 if col1 < col2 else 0), row2, (col2 + (-1 if col1 < col2 else 1)))
        game_state.board[row1][col1], game_state.board[row2][col2], (x1, y1), (x2, y2) = "", "", cell_to_coord(row1, col1), cell_to_coord(row2, col2)
        dy, dx = ((y2 - y1) / 75), ((x2 - x1) / 75)
        self.draw_board()
        animation.clear()
        animation.penup()
        animation.goto(x1, y1)
        for frame in range(75):
            for iteration_of_nothing in range(100000):
                pass
            animation.clear()
            animation.goto(x1 + dx*frame, y1 + dy*frame)
            animation.write(current_player_piece, font=("Arial", int(sizes(True)*0.6)))
            window.update()
        self.special_cases(current_player_piece, row1, col1, row2, col2)
        animation.clear()


    def show_message(self, msg, font_size=None):
        message = self.message
        self.game_state.message = (msg, font_size)
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
        message.write(msg, align="center", font=("Arial", (font_size if font_size != None else int(sizes(True) * 0.35)), "bold"))
        window.onclick(self.close_message)
        
    def close_message(self, x, y):
        self.game_state.message = ""
        self.message.clear()
        window.onclick(self.move_pieces)

    def show_moves(self):
        t = self.t
        row1, col1 = self.game_state.selected[0]
        for row in range(8):
            for col in range(8):
                if self.valid_move((row1, col1), (row, col)):
                    x, y = cell_to_coord(row, col)
                    t.goto(x + (2*sizes(True))/5, y + sizes(True)/2)
                    t.pendown()
                    t.dot(int(sizes(True) * 0.2), "green")
                    t.penup()

    def position_check(self):
        game_state = self.game_state
        show_message = self.show_message
        game_state.history[self.get_position_state()] = game_state.history.get(self.get_position_state(), 0) + 1
        if self.in_check(game_state.white_turn):
            if self.checkmate_yet(game_state.white_turn):
                show_message("Checkmate by " + ("Black" if game_state.white_turn else "White") + "!")
                game_state.game_over = True
            else:
                show_message("Check!")
        elif game_state.halfmoves > 99:
            show_message("Draw: 50-move rule")
            game_state.game_over = True
        elif game_state.history[self.get_position_state()] > 2:
            show_message("Draw: 3-fold repetition")
            game_state.game_over = True
        else:
            if self.checkmate_yet(game_state.white_turn):
                show_message("Stalemate!")
                game_state.game_over = True

    def move_pieces(self, x, y):
        game_state = self.game_state
        if game_state.game_over:
            return
        row, col = coord_to_cell(x, y)
        if row == None:
            return
        if self.check_turn(7-row, col):
            game_state.selected.append((7-row, col))
        else:
            game_state.selected = []
        if len(game_state.selected) == 2:
            if self.valid_move(game_state.selected[0], game_state.selected[1]):
                row1, col1 = game_state.selected[0]
                row2, col2 = game_state.selected[1]
                self.animate(row1, col1, row2, col2)
                if game_state.promotion_square == None:
                    game_state.white_turn = not game_state.white_turn
                    self.position_check()
                game_state.selected = []
            else:
                game_state.selected = []
        self.draw_board()
        if len(game_state.selected) == 1:
            self.show_moves()


if __name__ == "__main__":
    window = Screen()
    window.title("Chess")
    window.getcanvas().winfo_toplevel().minsize(500, 500)

    chess_game = ChessGame()

    done()