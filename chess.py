# The aim of this project is to create a chess program using only turtle. Therefore, only turtle is imported here.
import turtle

# A function for common sizes that are needed for making the window and its elements resize well.
def sizes(get_cell_size: bool=False, get_square_size:bool=False, get_smallest:bool=False) -> float:
    smallest: float = min(window.window_width(), window.window_height())
    if get_smallest:
        return smallest
    elif get_square_size:
        return smallest * 0.9
    elif get_cell_size:
        return sizes(False, True) / 8

# Turn cells into the corresponding coordinates in the window
# These random fractions are from testing, so I have no idea why it works. It just does.
def cell_to_coord(row: int, col: int) -> tuple[float, float]:
    x: float = -sizes(False, True)/2 + col*sizes(True) + sizes(True)/8
    y: float = -sizes(False, True)/2 - sizes(False, False, True)/8 + (8-row)*sizes(True)
    return x, y

# Turn coordinates from event handler into the corresponding cells in the table
# These random fractions are from testing, so I have no idea why it works. It just does.
def coord_to_cell(x: float, y: float) -> tuple[int | None, int | None]:
    col: int = int((x + sizes(False, True) / 2) // sizes(True))
    row: int = int((y + sizes(False, True) / 2 - sizes(False, False, True)/10 + sizes(True)) // sizes(True))
    if 0 <= row and 0 <= col < 8:
        return row, col
    return None, None

# My version of the base 64 function which does not bother with padding. Created this to avoid using any extra modules.
def base64(data: str, encode: bool=True) -> str:
    alphabet: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    result: list[str | int] = []
    bytes_of_text: list[int] | str = ([ord(c) for c in data] if encode else data)
    for nibbling_bit in (range(0, len(bytes_of_text), 3) if encode else range(0, len(data), 4)):
        chunk = bytes_of_text[nibbling_bit:nibbling_bit+(3 if encode else 4)]
        chunk += ([0, 0, 0][:-len(chunk)] if encode else "")
        combined: int = ((chunk[0] << 16) | (chunk[1] << 8) | chunk[2]) if encode else sum(alphabet.index(character) << (6 * (3-index)) for index, character in enumerate(chunk))
        for shift in ((18, 12, 6, 0) if encode else (16, 8, 0)):
            result.append((alphabet[((combined >> shift) & 0b111111)]) if encode else ((combined >> shift) & 0b11111111))
    return "".join((b if encode else chr(b)) for b in result)

class GameState:
    # Initialise initial board and state
    def __init__(self) -> None:
        # To make identifying colour of piece later easier
        self.white_pieces: list[str] = ["♙", "♘", "♗", "♖", "♕", "♔"]
        self.black_pieces: list[str] = ["♟", "♞", "♝", "♜", "♛", "♚"]
        # For castling
        self.king_moved: list[bool] = [False, False]
        self.rook_moved: list[bool] = [False, False, False, False]
        # Chess board
        self.board: list[list[str]] = [
            ["♜","♞","♝","♛","♚","♝","♞","♜"],
            ["♟","♟","♟","♟","♟","♟","♟","♟"],
            ["","","","","","","",""],
            ["","","","","","","",""],
            ["","","","","","","",""],
            ["","","","","","","",""],
            ["♙","♙","♙","♙","♙","♙","♙","♙"],
            ["♖","♘","♗","♕","♔","♗","♘","♖"],
        ]
        # Mapping pieces to letters and vice versa - the unicode to utf-8 creates a code higher than 255, which my base 64 function
        # is unable to handle
        self.pieces_map: dict[str, str] = { "♙": "p", "♖": "r", "♘": "n", "♗": "b", "♕": "q", "♔": "k", "♟": "P", "♜": "R", "♞": "N", "♝": "B", "♛": "Q", "♚": "K" }
        self.letter_map: dict[str, str] = { letter: piece_name for piece_name, letter in self.pieces_map.items() }
        self.piece_type: dict[str, list[str, str]] = { "pawns": ["♙", "♟"], "rooks": ["♖", "♜"], "knights": ["♘", "♞"], "bishops": ["♗", "♝"], "queens": ["♕", "♛"], "kings": ["♔", "♚"] }
        # Selecting squares
        self.selected: list[tuple[int, int]] = []
        # Is it white's turn?
        self.white_turn: bool = True
        # Square a pawn can go on the next move for en passent
        self.en_passent_target: tuple[int, int] | None = None
        # Game over variable to stop the board from being changed afterwards (importing can bypass this. might want to improve it)
        self.game_over: bool = False
        # For 50 move rule
        self.halfmoves: int = 0
        # For 3-fold repetition
        self.history: dict[tuple, int] = {}
        # Tell program which square will be promoted.
        self.promotion_square: tuple[int, int] | None = None
        # The current message being displayed on the screen (so that draw_board won't overwrite it, or at least, it will redraw after overwriting. oh well.)
        self.message: tuple[str, int] | None = None

    # Convert row into a ripoff FEN notation and vice versa.
    def format_row(self, row: list[str], compress: bool=True) -> list[str] | str:
        result: list[str] | str = ("" if compress else [])
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
    
    # Exporting the board state.
    def export(self) -> str:
        return base64(("|".join(["/".join(self.format_row(row) for row in self.board), ("w" if self.white_turn else "b"), ("-" if self.en_passent_target is None else f"{self.en_passent_target[0]},{self.en_passent_target[1]}"), str(self.halfmoves), ("".join("1" if k else "0" for k in self.king_moved)), ("".join("1" if r else "0" for r in self.rook_moved))])))
    
    # Importing a game. Might need to add validation.
    def continue_game(self, data) -> None:
        data_sections = base64(data, False).split("|")
        self.board = [self.format_row(row, False) for row in data_sections[0].split("/")]
        self.white_turn = (data_sections[1] == "w")
        self.en_passent_target = None if data_sections[2] == "-" else tuple(map(int, data_sections[2].split(",")))
        self.halfmoves = int(data_sections[3])
        self.king_moved = [c == "1" for c in data_sections[4]]
        self.rook_moved = [c == "1" for c in data_sections[5]]
        self.game_over = False


class ChessGame:
    # Initialise the game and the turtles
    def __init__(self, window: turtle.Screen) -> None:
        self.window: turtle.Screen = window

        # t because I didn't have the foresight to see that I needed another 2 turtles for animation and messages
        t = self.t = turtle.Turtle()
        t.hideturtle()
        t.speed(0)

        # For piece animation
        animation = self.animation = turtle.Turtle()
        animation.hideturtle()
        animation.speed(0)

        # For displaying messages to the user.
        message = self.message = turtle.Turtle()
        message.hideturtle()
        message.speed(0)

        # Initialise game state
        self.state = GameState()
        self.piece_type = self.state.piece_type

        # Intialise vent listeners
        self.window.onclick(self.move_pieces)
        self.events()

        # Draw the board
        self.draw_board()
        # Tell the user the hotkeys to import and export the game.
        self.show_message("i - Import game.\ne - Export game")

    # Event listeners (not fully completed yet)
    def events(self) -> None:
        # Configure is getting the tkinter canvas in the background and redrawing the board every time it is resized
        self.window.getcanvas().bind("<Configure>", self.draw_board)
        # Exporting and importing game
        self.window.onkey(lambda: self.game_data(False), "i")
        self.window.onkey(lambda: self.game_data(), "e")
        self.window.listen()

    # Getting the position states for self.state.history
    def get_position_state(self) -> tuple[tuple[tuple[str] | bool] | bool]:
        state: GameState = self.state
        return (tuple(tuple(row) for row in state.board), state.white_turn, tuple(state.king_moved), tuple(state.rook_moved))

    # Importing and exporting games
    def game_data(self, export: bool=True) -> None:
        state: GameState = self.state
        if export:
            # Copying to clipboard immediately because turtle doesn't allow selecting text and I cannot use tkinter or anything else
            self.window._root.clipboard_clear()
            self.window._root.clipboard_append(state.export())
            self.show_message("Game code copied!")
        else:
            data: str = self.window.textinput("Import Game", "Enter your game code:")
            self.window.onkey(lambda: self.game_data(False), "i")
            self.window.onkey(lambda: self.game_data(), "e")
            self.window.listen()
            try:
                state.continue_game(data)
                self.draw_board()
                self.position_check()
            except:
                self.show_message("Invalid code")

    # Checking if the piece that is moved is valid for the current player, so black cannot play when it is white's turn
    def check_turn(self, row: int, col: int) -> bool:
        state: GameState = self.state
        if len(state.selected) == 0:
            check_turn: bool = ((state.board[row][col] in state.white_pieces) == state.white_turn)
        elif len(state.selected) == 1:
            check_turn: bool = ((state.board[row][col] in state.black_pieces) != state.white_turn) or state.board[row][col] == ""
        return check_turn

    # Make sure that the piece can't go through other pieces.
    def gonna_crash(self, row1: int, col1: int, row2: int, col2: int) -> bool:
        dy: int = (row2 - row1)
        dx: int = (col2 - col1)
        row_direction: int = (0 if dy == 0 else (-1 if dy < 0 else 1))
        col_direction: int = (0 if dx == 0 else (-1 if dx < 0 else 1))
        row: int = row1 + row_direction
        col: int = col1 + col_direction
        while (row, col) != (row2, col2):
            if self.state.board[row][col] != "":
                return False
            row += row_direction
            col += col_direction
        return True

    # The main validation logic for each chess piece
    def piece_move_valid(self, origin: tuple[int, int], target: tuple[int, int]) -> bool:
        state: GameState = self.state
        (row1, col1), (row2, col2) = origin, target
        dy: int = (row2 - row1)
        dx: int = (col2 - col1)
        piece_to_move: str = state.board[row1][col1]
        target_piece: str = state.board[row2][col2]
        
        # pawn logic
        if piece_to_move in state.piece_type["pawns"]:
            white_pawn: bool = (piece_to_move == "♙")
            if dx == 0 and target_piece == "":
                if (dy == -1 if white_pawn else dy == 1):
                    return True
                elif (row1 == 6 if white_pawn else row1 == 1) and (dy == -2 if white_pawn else dy == 2) and (state.board[row1-1][col1] == "" if white_pawn else state.board[row1+1][col1] == ""):
                    return True
            elif abs(dx) == 1 and (dy == -1 if white_pawn else dy == 1):
                if (target_piece in state.black_pieces if white_pawn else target_piece in state.white_pieces) or (state.en_passent_target == (row2, col2)):
                    return True
            return False

        # knight logic
        elif piece_to_move in state.piece_type["knights"]:
            return (abs(dy*dx) == 2)
        
        # king logic
        elif piece_to_move in state.piece_type["kings"]:
            if max(abs(dy), abs(dx)) == 1:
                return True
            elif dy == 0 and abs(dx) == 2:
                white_king: bool = (piece_to_move == "♔")
                if not state.king_moved[(0 if white_king else 1)]:
                    kingside: bool = (dx == 2)
                    if (state.rook_moved[((1 if kingside else 0) + (0 if white_king else 2))]) or (state.board[(7 if white_king else 0)][(7 if kingside else 0)] not in ["♖", "♜"]) or (state.board[row1][(5 if kingside else 1)] != "" or (state.board[row1][6] != "" if kingside else (state.board[row1][2] != "" or state.board[row1][3] != ""))):
                        return False
                    return True
            return False
        else:
            # bishops, rooks, and queen logic
            pieces: list[str] = (state.piece_type["bishops"] + state.piece_type["rooks"] + state.piece_type["queens"])
            valid_movements: list[bool] = [(a:=abs(dy)==abs(dx)), (b:=dy==0 or dx==0), (a or b)]

            if valid_movements[pieces.index(piece_to_move) // 2]:
                return self.gonna_crash(row1, col1, row2, col2)
            return False

    # Checking if the king is in check.
    def in_check(self, white: bool) -> bool:
        state: GameState = self.state
        king: tuple[int, int] | str = ("♔" if white else "♚")
        # Find the king
        for row in range(8):
            for col in range(8):
                if state.board[row][col] == king:
                    king = (row, col)
                    break
            if king not in state.piece_type["kings"]:
                break
        # Now do a very inefficient method of going through every square to see if king is attacked.
        for row in range(8):
            for col in range(8):
                piece_to_check: str = state.board[row][col]
                if piece_to_check == "":
                    continue
                elif white and piece_to_check in state.white_pieces:
                    continue
                elif not white and piece_to_check in state.black_pieces:
                    continue
                if self.piece_move_valid((row, col), king):
                    return True
        return False

    # The complete move validation for when a user does a move.
    # Note: The first section might become redundant, but not sure yet.
    def valid_move(self, origin: tuple[int, int], target: tuple[int, int]) -> bool:
        state: GameState = self.state
        (row1, col1), (row2, col2) = origin, target
        if state.board[row2][col2] != "":
            if (state.board[row1][col1] in state.white_pieces and state.board[row2][col2] in state.white_pieces) or (state.board[row1][col1] in state.black_pieces and state.board[row2][col2] in state.black_pieces):
                return False
        
        # Check piece is actually allowed to move there.
        if not self.piece_move_valid(origin, target):
            return False
        
        # Check that the piece is not moving into check. Check the king isn't moving through or into check when castling
        piece_to_move: str = state.board[row1][col1]
        target_piece: str = state.board[row2][col2]
        state.board[row2][col2], state.board[row1][col1] = state.board[row1][col1], ""
        if self.in_check((state.board[row2][col2] in state.white_pieces)):
            # Check if move will put king in check
            state.board[row1][col1], state.board[row2][col2] = piece_to_move, target_piece
            return False
        elif piece_to_move in state.piece_type["kings"] and abs(col2 - col1) == 2:
            # Check every square in between for castling
            state.board[row1][col1], state.board[row2][col2] = piece_to_move, target_piece
            white: bool = (piece_to_move == "♔")
            direction: int = (1 if col2 > col1 else -1)
            col: int = col1
            while col != col2:
                original_piece, state.board[row1][col1], state.board[row1][col] = state.board[row1][col], "", piece_to_move
                if self.in_check(white):
                    state.board[row1][col], state.board[row1][col1], state.board[row2][col2] = original_piece, piece_to_move, target_piece
                    return False
                state.board[row1][col], state.board[row1][col1] = original_piece, piece_to_move
                col += direction
        state.board[row1][col1], state.board[row2][col2] = piece_to_move, target_piece
        return True

    # Check if it is checkmate yet
    def checkmate_yet(self, white: bool) -> bool:
        state: GameState = self.state
        for row1 in range(8):
            for col1 in range(8):
                piece: str = state.board[row1][col1]
                if (piece == "") or (white and piece not in state.white_pieces) or (not white and piece not in state.black_pieces):
                    continue
                for row2 in range(8):
                    for col2 in range(8):
                        if self.valid_move((row1, col1), (row2, col2)):
                            return False
        return True

    # Check for special cases, ie, en passant, castling logic, promotion, 50 move rule
    def special_cases(self, current_player_piece: str, row1: int, col1: int, row2: int, col2: int) -> None:
        state: GameState = self.state
        # En passent
        if current_player_piece in state.piece_type["pawns"] and state.en_passent_target == (row2, col2):
            state.board[(row2-(-1 if current_player_piece == "♙" else 1))][col2] = ""
        if current_player_piece == "♙" and row1 == 6 and row2 == 4:
            state.en_passent_target = (5, col2)
        elif current_player_piece == "♟" and row1 == 1 and row2 == 3:
            state.en_passent_target = (2, col2)
        else:
            state.en_passent_target = None

        # 50 move rule
        if current_player_piece in state.piece_type["pawns"] or state.board[row2][col2] != "":
            state.halfmoves = 0
        else:
            state.halfmoves += 1

        # castling logic
        if current_player_piece in state.piece_type["kings"]:
            state.king_moved[(0 if current_player_piece == "♔" else 1)] = True
        elif current_player_piece in state.piece_type["rooks"] and ((row1 == 7 if current_player_piece == "♖" else row1 == 0) and (col1 == 0  or col1 == 7)):
            state.rook_moved[((0 if current_player_piece == "♖" else 2) + (0 if col1 == 0 else 1))] = True

        state.board[row2][col2] = current_player_piece
        
        # promotion
        if (current_player_piece == "♙" and row2 == 0) or (current_player_piece == "♟" and row2 == 7):
            state.promotion_square = (row2, col2)
            options: list[str] = (["♕", "♖", "♗", "♘"] if row2 == 0 else ["♛", "♜", "♝", "♞"])
            self.show_message("Promote to:\n1: Queen   2: Rook   3: Bishop   4: Knight\nEnter the number of your choice.", int(sizes(True)//6))
            self.window.onkey(lambda: self.promote(options[0]), "1")
            self.window.onkey(lambda: self.promote(options[1]), "2")
            self.window.onkey(lambda: self.promote(options[2]), "3")
            self.window.onkey(lambda: self.promote(options[3]), "4")
            self.window.update()
            self.window.listen()








    # Drawing the board.
    def draw_board(self, event=None) -> None:
        t, state = self.t, self.state
        self.window.tracer(0, 0)
        t.clear()
        x: float = -sizes(False, True) / 2
        y: float = -sizes(False, True) / 2 + sizes(False, False, True) * 0.1
        for i in range(8):
            for j in range(8):
                t.penup()
                t.goto(round(x + j*sizes(True)), round(y + i*sizes(True)))
                t.pendown()
                # Square colours (tested these hex colours, borrowed inverse colours idea from lichess and chess.com)
                if (i + j) % 2 == 0:
                    t.fillcolor("#E4C4B4")
                else:
                    t.fillcolor("#F5F5D5")
                t.begin_fill()
                # make the square
                for side in range(4):
                    t.forward(sizes(True))
                    t.right(90)
                t.end_fill()
                if (7-i, j) in state.selected:
                    t.penup()
                    t.goto(x + j*sizes(True), y + i*sizes(True))
                    t.pendown()
                    # selected square hex colours
                    t.fillcolor(("#D0FFD0" if state.white_turn else "#7F907F"))
                    t.begin_fill()
                    # redraw the square
                    for side in range(4):
                        t.forward(sizes(True))
                        t.right(90)
                    t.end_fill()
                piece: str = state.board[7-i][j]
                t.penup()
                # again, these magic numbers were from testing
                t.goto(x + j*sizes(True) + sizes(True)/8, y + i*sizes(True) - sizes(True))
                # write the piece
                t.write(piece, font=("Arial", int(sizes(True)*0.6)))
        if state.message != None:
            self.show_message(state.message[0], state.message[1])
        self.window.update()

    # Pawn Promotion
    def promote(self, piece: str) -> None:
        state: GameState = self.state
        row, col = state.promotion_square
        state.board[row][col] = piece
        # reset everything to before and continue
        state.promotion_square = None
        state.message = None
        self.message.clear()
        self.window.onkey(lambda: (), "1")
        self.window.onkey(lambda: (), "2")
        self.window.onkey(lambda: (), "3")
        self.window.onkey(lambda: (), "4")
        state.white_turn = not state.white_turn
        self.position_check()
        self.draw_board()
        self.window.update()

    # Animation of the piece movements.
    def animate(self, row1: int, col1: int, row2: int, col2: int) -> None:
        state: GameState = self.state
        animation: turtle.Turtle = self.animation
        current_player_piece: str = state.board[row1][col1]
        if current_player_piece in state.piece_type["kings"] and abs(col2 - col1) == 2:
            self.animate(row1, (7 if col1 < col2 else 0), row2, (col2 + (-1 if col1 < col2 else 1)))
        state.board[row1][col1], state.board[row2][col2], (x1, y1), (x2, y2) = "", "", cell_to_coord(row1, col1), cell_to_coord(row2, col2)
        dy: float = ((y2 - y1) / 75)
        dx: float = ((x2 - x1) / 75)
        self.draw_board()
        animation.clear()
        animation.penup()
        animation.goto(x1, y1)
        for frame in range(75):
            # iteration of nothing is for the pause (as this project will only use turtle module). it also blocks, so that the next part cannot run, which is good.
            for iteration_of_nothing in range(100000):
                pass
            animation.clear()
            animation.goto(x1 + dx*frame, y1 + dy*frame)
            animation.write(current_player_piece, font=("Arial", int(sizes(True)*0.6)))
            self.window.update()
        self.special_cases(current_player_piece, row1, col1, row2, col2)
        animation.clear()

    # Show messages to the user. Printing to console log creates a bad user experience.
    def show_message(self, msg: str, font_size: int | None=None) -> None:
        message: turtle.Turtle = self.message
        self.state.message = (msg, font_size)
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
        self.window.onclick(self.close_message)
        
    # Handler for closing message.
    def close_message(self, x: float, y: float) -> None:
        self.state.message = None
        self.message.clear()
        self.window.onclick(self.move_pieces)

    # Showing valid moves.
    def show_moves(self) -> None:
        t: turtle.Turtle = self.t
        row1, col1 = self.state.selected[0]
        for row in range(8):
            for col in range(8):
                if self.valid_move((row1, col1), (row, col)):
                    x, y = cell_to_coord(row, col)
                    t.goto(x + (2*sizes(True))/5, y + sizes(True)/2)
                    t.pendown()
                    t.dot(int(sizes(True) * 0.2), "green")
                    t.penup()

    # Checking if game is over yet or for check.
    def position_check(self) -> None:
        state: GameState = self.state
        show_message = self.show_message
        # Add current position for 3 fold repetition
        state.history[self.get_position_state()] = state.history.get(self.get_position_state(), 0) + 1
        if self.in_check(state.white_turn):
            if self.checkmate_yet(state.white_turn):
                show_message("Checkmate by " + ("Black" if state.white_turn else "White") + "!")
                state.game_over = True
            else:
                show_message("Check!")
        elif state.halfmoves > 99:
            show_message("Draw: 50-move rule")
            state.game_over = True
        elif state.history[self.get_position_state()] > 2:
            show_message("Draw: 3-fold repetition")
            state.game_over = True
        else:
            if self.checkmate_yet(state.white_turn):
                show_message("Stalemate!")
                state.game_over = True

    # The logic for the user clicking a piece and then moving it.
    def move_pieces(self, x: float, y: float) -> None:
        state: GameState = self.state
        if state.game_over:
            return
        row, col = coord_to_cell(x, y)
        if row == None:
            return
        if self.check_turn(7-row, col):
            state.selected.append((7-row, col))
        else:
            state.selected = []
        if len(state.selected) == 2:
            if self.valid_move(state.selected[0], state.selected[1]):
                row1, col1 = state.selected[0]
                row2, col2 = state.selected[1]
                self.animate(row1, col1, row2, col2)
                # check if promotion is currently in progress
                if state.promotion_square == None:
                    state.white_turn = not state.white_turn
                    self.position_check()
                state.selected = []
            else:
                state.selected = []
        self.draw_board()
        if len(state.selected) == 1:
            self.show_moves()


# Just saw this in many python projects, so I decided to copy it.
# I don't think there is a need here though, because I haven't split this into many files yet.
if __name__ == "__main__":
    # Create the screen
    window = turtle.Screen()
    window.title("Chess")
    # Do some random stuff and set the minimum size of window to be 500 by 500 to stop the user from shrinking the window too much,
    # as my resizing function does not work as well there for obvious reason.
    window.getcanvas().winfo_toplevel().minsize(500, 500)

    # Initialise the chess game.
    chess_game: ChessGame = ChessGame(window)

    # Make it wait for the turtle window to be closed.
    turtle.done()