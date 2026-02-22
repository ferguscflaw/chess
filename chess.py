# The aim of this project is to create a chess program using only turtle. Therefore, only turtle is imported here.
import turtle

# My version of the base 64 function which does not bother with padding.
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
    def __init__(self) -> None:
        self.king_moved: list[bool] = [False, False]
        self.rook_moved: list[bool] = [False, False, False, False]
        self.king_castled: list[bool, str] = [False, False]
        self.king_coords: list[tuple[int, int]] = [(7, 4), (0, 4)]
        self.board: list[list[str]] = [
            ["R","N","B","Q", "K","B","N","R"],
            ["P","P","P","P","P","P","P","P"],
            ["","","","","","","",""],
            ["","","","","","","",""],
            ["","","","","","","",""],
            ["","","","","","","",""],
            ["p","p","p","p","p","p","p","p"],
            ["r","n","b","q","k","b", "n","r"],
        ]
        self.letter_map: dict[str, str] = { "p": "♙", "r": "♖", "n": "♘", "b": "♗", "q": "♕", "k": "♔", "P": "♟", "R": "♜", "N": "♞", "B": "♝", "Q": "♛", "K": "♚", "": "" }
        self.selected: list[tuple[int, int]] = []
        self.white_turn: bool = True
        self.en_passent_target: tuple[int, int] | None = None
        self.game_over: bool = False
        self.halfmoves: int = 0
        self.history: dict[tuple, int] = {}
        self.promotion_square: tuple[int, int] | None = None
        self.message: tuple[str, int] | None = None
        self.transposition_table: dict[tuple[list[list[str]] | int | bool]] = {}
        self.material_scores: dict[str, int] = { "p": 100, "P": -100, "n": 320, "N": -320, "b": 330, "B": -330, "r": 500, "R": -500, "q": 900, "Q": -900, "k": 999999, "K": -999999 }
        pawn_ps_table: list[list[int]] = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [5, 5, 10, 25, 25, 10, 5, 5],
            [0, 0, 0, 20, 20, 0, 0, 0],
            [5, -5, -10, 0, 0, -10, -5, 5],
            [5, 10, 10, -20, -20, 10, 10, 5],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        knight_ps_table: list[list[int]] = [
            [-50, -40, -30, -30, -30, -30, -40, -50],
            [-40, -20, 0, 0, 0, 0, -20, -40],
            [-30, 0, 10, 15, 15, 10, 0, -30],
            [-30, 5, 15, 20, 20, 15, 5, -30],
            [-30, 0, 15, 20, 20, 15, 0, -30],
            [-30, 5, 10, 15, 15, 10, 5, -30],
            [-40, -20, 0, 5, 5, 0, -20, -40],
            [-50, -40, -30, -30, -30, -30, -40, -50]
        ]
        bishop_ps_table: list[list[int]] = [
            [-20, -10, -10, -10, -10, -10, -10, -20],
            [-10, 0, 0, 0, 0, 0, 0, -10],
            [-10, 0, 5, 10, 10, 5, 0, -10],
            [-10, 5, 5, 10, 10, 5, 5, -10],
            [-10, 0, 10, 10, 10, 10, 0, -10],
            [-10, 10, 10, 10, 10, 10, 10, -10],
            [-10, 5, 0, 0, 0, 0, 5, -10],
            [-20, -10, -10, -10, -10, -10, -10, -20]
        ]
        rook_ps_table: list[list[int]] = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [5, 10, 10, 10, 10, 10, 10, 5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [0, 0, 0, 5, 5, 0, 0, 0]
        ]
        queen_ps_table: list[list[int]] = [
            [-20, -10, -10, -5, -5, -10, -10, -20],
            [-10, 0, 0, 0, 0, 0, 0, -10],
            [-10, 0, 5, 5, 5, 5, 0, -10],
            [-5, 0, 5, 5, 5, 5, 0, -5],
            [0, 0, 5, 5, 5, 5, 0, -5],
            [-10, 5, 5, 5, 5, 5, 0, -10],
            [-10, 0, 5, 0, 0, 0, 0, -10],
            [-20, -10, -10, -5, -5, -10, -10, -20]
        ]
        king_ps_table: list[list[int]] = [
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-20, -30, -30, -40, -40, -30, -30, -20],
            [-10, -20, -20, -20, -20, -20, -20, -10],
            [20, 20, 0, 0, 0, 0, 20, 20],
            [20, 30, 10, 0, 0, 10, 30, 20]
        ]
        self.piece_tables: dict[str, list[list[int]]] = {
            "p": pawn_ps_table,
            "n": knight_ps_table,
            "b": bishop_ps_table,
            "r": rook_ps_table,
            "q": queen_ps_table,
            "k": king_ps_table,
            "P": [[-score for score in row] for row in pawn_ps_table[::-1]],
            "N": [[-score for score in row] for row in knight_ps_table[::-1]],
            "B": [[-score for score in row] for row in bishop_ps_table[::-1]],
            "R": [[-score for score in row] for row in rook_ps_table[::-1]],
            "Q": [[-score for score in row] for row in queen_ps_table[::-1]],
            "K": [[-score for score in row] for row in king_ps_table[::-1]],
        }
        self.knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        self.enumerated_brq_moves = list(enumerate([(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]))
        self.current_score = 0

    # Convert row into a ripoff FEN notation and vice versa.
    def format_row(self, row: list[str], compress: bool=True) -> list[str] | str:
        result: list[str] | str = ("" if compress else [])
        if compress:
            for piece in row:
                result = (result+piece if piece != "" else (result+"1" if (len(result) == 0 or result[-1] in "prnbqkPRNBQK") else result[:-1]+str(int(result[-1])+1)))
        else:
            for letter in row:
                if letter in "prnbqkPRNBQK":
                    result.append(letter)
                else:
                    result.extend(([""]*(int(letter))))
        return result
    
    def export(self) -> str:
        return base64(("|".join(["/".join(self.format_row(row) for row in self.board), ("w" if self.white_turn else "b"), ("-" if self.en_passent_target is None else f"{self.en_passent_target[0]},{self.en_passent_target[1]}"), str(self.halfmoves), ("".join("1" if k else "0" for k in self.king_moved)), ("".join("1" if r else "0" for r in self.rook_moved)), ("/".join(self.king_castled))])))
    
    def continue_game(self, data) -> None:
        data_sections = base64(data, False).split("|")
        self.board = [self.format_row(row, False) for row in data_sections[0].split("/")]
        self.white_turn = (data_sections[1] == "w")
        self.en_passent_target = None if data_sections[2] == "-" else tuple(map(int, data_sections[2].split(",")))
        self.halfmoves = int(data_sections[3])
        self.king_moved = [bit == "1" for bit in data_sections[4]]
        self.rook_moved = [bit == "1" for bit in data_sections[5]]
        self.king_castled = [(False if string == "False" else string) for string in data_sections[6].split("/")]
        self.game_over = False


class ChessGame:
    def __init__(self, window: turtle.Screen, ai_active: str) -> None:
        self.window: turtle.Screen = window
        self.ai_active: bool = (True if ai_active == "y" else False)
        self.ai_black: bool | None = None
        if self.ai_active:
            self.ai_black = (False if window.textinput("Chess AI", "What colour would you like to play as? (w/b)") == "b" else True)
        # t because I didn't have the foresight to see that I needed another 2 turtles for animation and messages and I can't be bothered to change it now
        t = self.t = turtle.Turtle()
        t.hideturtle()
        t.speed(0)

        animation = self.animation = turtle.Turtle()
        animation.hideturtle()
        animation.speed(0)

        message = self.message = turtle.Turtle()
        message.hideturtle()
        message.speed(0)

        self.state = GameState()
        self.window.onclick(self.move_pieces)
        self.window.getcanvas().bind("<Configure>", self.draw_board)
        self.window.onkey(lambda: self.game_data(False), "i")
        self.window.onkey(lambda: self.game_data(), "e")
        self.window.listen()

        self.draw_board()
        self.show_message("i - Import game.\ne - Export game")

        if self.ai_active and not self.ai_black:
            self.ai()

    def flip_board(self):
        return ((True if self.ai_black else False) if self.ai_active else self.state.white_turn)

    def sizes(self, get_cell_size: bool=False, get_square_size:bool=False, get_smallest:bool=False) -> float:
        if get_smallest:
            return min(window.window_width(), window.window_height())
        elif get_square_size:
            return min(window.window_width(), window.window_height()) * 0.9
        elif get_cell_size:
            return self.sizes(False, True) / 8

    # These random fractions are from testing, so I have no idea why it works. It just does.
    def cell_to_coord(self, row: int, col: int) -> tuple[float, float]:
        sizes = self.sizes
        row, col = (row if self.flip_board() else 7-row), (col if self.flip_board() else 7-col)
        x: float = -sizes(False, True)/2 + col*sizes(True) + sizes(True)/8
        y: float = -sizes(False, True)/2 - sizes(False, False, True)/8 + (8-row)*sizes(True)
        return x, y

    def coord_to_cell(self, x: float, y: float) -> tuple[int | None, int | None]:
        sizes = self.sizes
        col: int = int((x + sizes(False, True) / 2) // sizes(True))
        row: int = int((y + sizes(False, True) / 2 - sizes(False, False, True)/10 + sizes(True)) // sizes(True))
        if 0 <= row < 8 and 0 <= col < 8:
            return (row if self.flip_board() else 7-row), (col if self.flip_board() else 7-col)
        return None, None

    def game_data(self, export: bool=True) -> None:
        state: GameState = self.state
        if export:
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
                if self.ai_active:
                    if not state.white_turn and self.ai_black:
                        self.ai()
                    if state.white_turn and not self.ai_black:
                        self.ai()
            except:
                self.show_message("Invalid code")

    def check_turn(self, row: int, col: int) -> bool:
        state: GameState = self.state
        if len(state.selected) == 0:
            check_turn: bool = (state.board[row][col].islower() == state.white_turn)
        elif len(state.selected) == 1:
            check_turn: bool = (state.board[row][col].islower() != state.white_turn) or state.board[row][col] == ""
        return check_turn

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

    def piece_move_valid(self, origin: tuple[int, int], target: tuple[int, int]) -> bool:
        state: GameState = self.state
        (row1, col1), (row2, col2) = origin, target
        dy: int = (row2 - row1)
        dx: int = (col2 - col1)
        board = state.board
        piece_to_move: str = board[row1][col1]
        target_piece: str = board[row2][col2]

        if piece_to_move.lower() == "p":
            direction_y = (-1 if piece_to_move == "p" else 1)
            if dx == 0 and target_piece == "" and (dy == direction_y or (dy == direction_y*2 and board[row1+direction_y][col1] == "" and row1 << 1 == 7-5*direction_y)):
                return True
            elif abs(dx) == 1 and dy == direction_y and (target_piece != "" or state.en_passent_target == (row2, col2)):
                return True
            return False

        elif piece_to_move.lower() == "n":
            return (abs(dy*dx) == 2)
        
        elif piece_to_move.lower() == "k":
            if max(abs(dy), abs(dx)) == 1:
                return True
            elif dy == 0 and abs(dx) == 2:
                white_king: bool = (piece_to_move == "k")
                king_index = (0 if white_king else 1)
                if not state.king_moved[king_index]:
                    kingside: bool = (dx == 2)
                    if (state.rook_moved[(kingside + king_index*2)]) or (board[white_king*7][kingside*7].lower() != "r") or (board[row1][4*kingside+1] != "" or (board[row1][6] != "" if kingside else (board[row1][2] + board[row1][3] != ""))):
                        return False
                    return True
            return False
        else:
            pieces: list[str] = ["b", "r", "q"]
            valid_movements: list[bool] = [(a:=abs(dy)==abs(dx)), (b:=dy==0 or dx==0), (a or b)]

            if valid_movements[pieces.index(piece_to_move.lower())]:
                return self.gonna_crash(row1, col1, row2, col2)
            return False

    def in_check(self, white: bool) -> bool:
        state: GameState = self.state
        k_row, k_col = state.king_coords[1-white]
        board = state.board

        pawn = ("P" if white else "p")
        for dx in (-1, 1):
            if 0 <= (row:=k_row+(1-(white*2))) < 8 and 0 <= (col:=k_col+dx) < 8 and board[row][col] == pawn:
                return True
            
        knight = ("N" if white else "n")
        for dx, dy in state.knight_moves:
            if 0 <= (row:=k_row+dy) < 8 and 0 <= (col:=k_col+dx) < 8 and board[row][col] == knight:
                return True
            
        king = ("K" if white else "k")
        for index, (dx, dy) in state.enumerated_brq_moves:
            if 0 <= (row:=k_row+dy) < 8 and 0 <= (col:=k_col+dx) < 8 and board[row][col] == king:
                return True

        bishop, rook, queen = ("B" if white else "b"), ("R" if white else "r"), ("Q" if white else "q")
        for index, (dx, dy) in state.enumerated_brq_moves:
            row, col = k_row+dy, k_col+dx
            while 0 <= row < 8 and 0 <= col < 8:
                piece = board[row][col]
                if piece != "":
                    if piece == queen or (piece == bishop and index < 4) or (piece == rook and index > 3):
                        return True
                    break
                row += dy
                col += dx
        
        return False

    def valid_move(self, origin: tuple[int, int], target: tuple[int, int]) -> bool:
        state: GameState = self.state
        (row1, col1), (row2, col2) = origin, target
        if state.board[row1][col1].islower() == state.board[row2][col2].islower() and state.board[row2][col2] != "":
            return False
        
        if not self.piece_move_valid(origin, target):
            return False
        
        piece_to_move: str = state.board[row1][col1]
        target_piece: str = state.board[row2][col2]
        state.board[row2][col2], state.board[row1][col1] = state.board[row1][col1], ""
        if piece_to_move.lower() == "k":
            state.king_coords[piece_to_move.isupper()] = (row2, col2)
        if self.in_check(state.board[row2][col2].islower()):
            state.board[row1][col1], state.board[row2][col2] = piece_to_move, target_piece
            if piece_to_move.lower() == "k":
                state.king_coords[piece_to_move.isupper()] = (row1, col1)
            return False
        elif piece_to_move.lower() == "k" and abs(col2 - col1) == 2:
            state.board[row1][col1], state.board[row2][col2] = piece_to_move, target_piece
            state.king_coords[piece_to_move.isupper()] = (row1, col1)
            white: bool = (piece_to_move == "k")
            col: int = col1
            while col != col2:
                original_piece, state.board[row1][col1], state.board[row1][col] = state.board[row1][col], "", piece_to_move
                state.king_coords[piece_to_move.isupper()] = (row2, col)
                if self.in_check(white):
                    state.board[row1][col], state.board[row1][col1], state.board[row2][col2] = original_piece, piece_to_move, target_piece
                    state.king_coords[piece_to_move.isupper()] = (row1, col1)
                    return False
                state.board[row1][col], state.board[row1][col1] = original_piece, piece_to_move
                col += (1 if col2 > col1 else -1)
        state.board[row1][col1], state.board[row2][col2] = piece_to_move, target_piece
        if piece_to_move.lower() == "k":
            state.king_coords[piece_to_move.isupper()] = (row1, col1)
        return True

    def checkmate_yet(self, white: bool) -> bool:
        state: GameState = self.state
        for row1 in range(8):
            for col1 in range(8):
                piece: str = state.board[row1][col1]
                if piece == "" or white != piece.islower():
                    continue
                for row2 in range(8):
                    for col2 in range(8):
                        if self.valid_move((row1, col1), (row2, col2)):
                            return False
        return True

    def special_cases(self, current_player_piece: str, row1: int, col1: int, row2: int, col2: int) -> None:
        state: GameState = self.state
        if current_player_piece.lower() == "p" and state.en_passent_target == (row2, col2):
            state.board[(row2+(1 if current_player_piece == "p" else -1))][col2] = ""
        if current_player_piece == "p" and row1 == 6 and row2 == 4:
            state.en_passent_target = (5, col2)
        elif current_player_piece == "P" and row1 == 1 and row2 == 3:
            state.en_passent_target = (2, col2)
        else:
            state.en_passent_target = None

        if current_player_piece.lower() == "p" or state.board[row2][col2] != "":
            state.halfmoves = 0
        else:
            state.halfmoves += 1

        if current_player_piece.lower() == "k":
            state.king_moved[current_player_piece.isupper()] = True
            state.king_coords[current_player_piece.isupper()] = (row2, col2)
        elif current_player_piece.lower() == "r" and ((row1 == 7 if current_player_piece == "r" else row1 == 0) and (col1 == 0  or col1 == 7)):
            state.rook_moved[((0 if current_player_piece == "r" else 2) + (col1 != 0))] = True

        state.board[row2][col2] = current_player_piece
        
        if (current_player_piece == "p" and row2 == 0) or (current_player_piece == "P" and row2 == 7):
            state.promotion_square = (row2, col2)
            options: list[str] = (["q", "r", "b", "n"] if row2 == 0 else ["Q", "R", "B", "N"])
            self.show_message("Promote to:\n1: Queen   2: Rook   3: Bishop   4: Knight\nType the number of your choice.", int(self.sizes(True)//6), False)
            self.window.onkey(lambda: self.promote(options[0]), "1")
            self.window.onkey(lambda: self.promote(options[1]), "2")
            self.window.onkey(lambda: self.promote(options[2]), "3")
            self.window.onkey(lambda: self.promote(options[3]), "4")
            self.window.update()
            self.window.listen()





    def score_board(self) -> int:
        #Most of the features came from here: https://www.chessprogramming.org/Evaluation#Basic_Evaluation_Features
        state = self.state
        piece_score: int = 0
        pstables_score: int = 0
        castling_score: int = 0
        for row_i, row in enumerate(state.board):
            for col_i, piece in enumerate(row):
                if piece == "":
                    continue
                piece_score += state.material_scores[piece]
                pstables_score += state.piece_tables[piece][row_i][col_i]

        castling_score += sum(((20 if rook // 2 == 0 else -20) if moved_yet else 0) for rook, moved_yet in enumerate(state.rook_moved))
        castling_score += sum(((35 if king == 0 else -35) if moved_yet else 0) for king, moved_yet in enumerate(state.king_moved))
        castling_score += sum(0 if castled == False else ((100 if castled == "k" else 75) if king == 0 else (-100 if castled == "k" else -75)) for king, castled in enumerate(state.king_castled))
        return piece_score + pstables_score + castling_score
    

    def possible_moves(self, white: bool) -> list[tuple[tuple[int]]]:
        state = self.state
        key = "".join(piece or "." for row in state.board for piece in row) + ("w" if state.white_turn else "b") + "".join(str(int(boolean)) for boolean in state.king_moved) + "".join(str(int(boolean)) for boolean in state.rook_moved) + (str(state.en_passent_target) if state.en_passent_target != None else "") + "-possible_moves"
        if key in state.transposition_table:
            return state.transposition_table[key]
        moves: list[tuple[tuple[int]]] = []
        board = state.board
        for row1 in range(8):
            for col1 in range(8):
                piece: str = board[row1][col1]
                if piece == "" or white != piece.islower():
                    continue
                
                elif piece.lower() == "p":
                    direction: int =  (-1 if piece == "p" else 1)
                    for jump in (1, 2):
                        row2: int = row1 + jump * direction
                        if 0 <= row2 < 8 and ((jump == 1 and board[row2][col1] == "") or (jump == 2 and row1 in [6, 1] and board[row2][col1] == "" and board[row1 + direction][col1] == "")) and self.piece_move_valid((row1, col1), (row2, col1)):
                            for promotion_piece in (["q", "r", "b", "n"] if (piece == "p" and row2 == 0) else (["Q", "R", "B", "N"] if (piece == "P" and row2 == 7) else [None])):
                                moves.append(((row1, col1), (row2, col1), promotion_piece))
                    for side in (-1, 1):
                        row2, col2 = row1 + direction, col1 + side
                        if 0 <= row2 < 8 and 0 <= col2 < 8 and self.piece_move_valid((row1, col1), (row2, col2)):
                            for promotion_piece in (["q", "r", "b", "n"] if (piece == "p" and row2 == 0) else (["Q", "R", "B", "N"] if (piece == "P" and row2 == 7) else [None])):
                                moves.append(((row1, col1), (row2, col2), promotion_piece))
                        if (row2, col2) == state.en_passent_target:
                            moves.append(((row1, col1), (row2, col2), None))

                elif piece.lower() == "n":
                    for dy, dx in state.knight_moves:
                        row2, col2 = row1 + dy, col1 + dx
                        if 0 <= row2 < 8 and 0 <= col2 < 8 and self.piece_move_valid((row1, col1), (row2, col2)):
                            moves.append(((row1, col1), (row2, col2), None))

                elif piece.lower() == "k":
                    for dy in range(-1, 2):
                        for dx in range(-1, 2):
                            if dy == 0 and dx == 0:
                                continue
                            row2, col2 = row1 + dy, col1 + dx
                            if 0 <= row2 < 8 and 0 <= col2 < 8 and self.piece_move_valid((row1, col1), (row2, col2)):
                                moves.append(((row1, col1), (row2, col2), None))
                    for dx in (-2, 2):
                        col2 = col1 + dx
                        if 0 <= col2 < 8 and self.piece_move_valid((row1, col1), (row1, col2)):
                            moves.append(((row1, col1), (row1, col2), "castling"))

                else:
                    pieces: list[str] = ["b", "B", "r", "R", "q", "Q"]
                    valid_movements: list[list[tuple[int]]] = [(a:=[(-1,-1), (-1,1), (1,1), (1,-1)]), (b:=[(-1, 0), (0, 1), (0, -1), (1, 0)]), (a+b)]
                    for dy, dx in valid_movements[pieces.index(piece) // 2]:
                        row2, col2 = row1 + dy, col1 + dx
                        while 0 <= row2 < 8 and 0 <= col2 < 8:
                            if self.piece_move_valid((row1, col1), (row2, col2)):
                                moves.append(((row1, col1), (row2, col2), None))
                            if board[row2][col2] != "":
                                break
                            row2 += dy
                            col2 += dx

        state.transposition_table[key] = moves
        return moves


    def negamax(self, depth: int, alpha: float=float("-inf"), beta: float=float("inf")) -> tuple[tuple[tuple[int, int]] | None, int]:
        state: GameState = self.state
        king_coords = state.king_coords
        alpha_original = alpha
        if depth == 0:
            return (None, state.current_score if state.white_turn else -state.current_score)
        key = "".join(piece or "." for row in state.board for piece in row) + ("w" if state.white_turn else "b") + "".join(str(int(boolean)) for boolean in state.king_moved) + "".join(str(int(boolean)) for boolean in state.rook_moved) + (str(state.en_passent_target) if state.en_passent_target != None else "") + "-negamax"
        if key in state.transposition_table:
            previous_search = state.transposition_table[key]
            if previous_search[0] >= depth:
                if previous_search[3] == "EXACT":
                    return (previous_search[1], previous_search[2])
                elif previous_search[3] == "LOWERBOUND":
                    alpha = max(alpha, previous_search[2])
                elif previous_search[3] == "UPPERBOUND":
                    beta = min(beta, previous_search[2])
                if alpha >= beta:
                    return (previous_search[1], previous_search[2])
        probably_possible_moves: list[tuple[tuple[int]]] = self.possible_moves(state.white_turn)
        moves = []
        for move in probably_possible_moves:
            (row1, col1), (row2, col2), promotion_piece = move
            piece_to_move, target_piece = state.board[row1][col1], state.board[row2][col2]
            if piece_to_move.islower() == target_piece.islower() and target_piece != "":
                continue
            if promotion_piece == "castling":
                col: int = col1
                illegal_move = False
                while col != col2+(1 if col2 > col1 else -1):
                    state.board[row1][col1], state.board[row1][col] = "", piece_to_move
                    state.king_coords[piece_to_move.isupper()] = (row2, col)
                    if self.in_check(state.white_turn):
                        illegal_move = True
                        state.board[row1][col], state.board[row1][col1] = "", piece_to_move
                        king_coords[piece_to_move.isupper()] = (row1, col1)
                        break
                    state.board[row1][col], state.board[row1][col1] = "", piece_to_move
                    king_coords[piece_to_move.isupper()] = (row1, col1)
                    col += (1 if col2 > col1 else -1)
                if not illegal_move:
                    moves.append(((row1, col1), (row2, col2), None))
            else:
                state.board[row2][col2], state.board[row1][col1] = state.board[row1][col1], ""
                if piece_to_move.lower() == "k":
                    king_coords[piece_to_move.isupper()] = (row2, col2)
                if not self.in_check(state.white_turn):
                    moves.append(move)
                state.board[row1][col1], state.board[row2][col2] = piece_to_move, target_piece
                if piece_to_move.lower() == "k":
                    king_coords[piece_to_move.isupper()] = (row1, col1)
        if len(moves) == 0:
            if self.in_check(state.white_turn):
                return (None, -4453421-depth)
            return (None, 0)
        moves.sort(key=lambda move:(1000 * (state.board[move[1][0]][move[1][1]] != "") + (state.material_scores[state.board[move[1][0]][move[1][1]]] if state.board[move[1][0]][move[1][1]] != "" else 0) - (state.material_scores[state.board[move[0][0]][move[0][1]]]) + (0 if move[2] == None else 900)), reverse=True)
        best_score: int | float = float("-inf")
        best_move: tuple[tuple[int]] | None = None
        for move in moves:
            (row1, col1), (row2, col2), promotion_piece = move
            piece_to_move, target_piece = state.board[row1][col1], state.board[row2][col2]
            state.board[row1][col1], state.board[row2][col2] = "", (promotion_piece if promotion_piece else piece_to_move)
            previous_score = state.current_score
            state.current_score -= state.piece_tables[piece_to_move][row1][col1]
            if target_piece != "":
                state.current_score -= state.material_scores[target_piece] + state.piece_tables[target_piece][row2][col2]
            state.current_score += state.piece_tables[(piece_to_move if promotion_piece == None else promotion_piece)][row2][col2]
            if abs(col2-col1) == 2:
                state.king_castled[piece_to_move.isupper()] = ("k" if col2-col1 == 2 else "q")
            state.current_score += ((100 if col2-col1 == 2 else (75 if col2-col1 == -2 else 0)) if piece_to_move == "k" else ((-100 if col2-col1 == 2 else (-75 if col2-col1 == -2 else 0)) if piece_to_move.lower() == "k" else 0))
            for rook, moved_yet in enumerate(state.rook_moved):
                state.current_score += ((20 if rook // 2 == 0 else -20) if moved_yet else 0)
            for king, moved_yet in enumerate(state.king_moved):
                state.current_score += ((35 if king == 0 else -35) if moved_yet else 0)

            if piece_to_move.lower() == "k":
                king_coords[piece_to_move.isupper()] = (row2, col2)
            state.white_turn = not state.white_turn
            position_key = "".join(piece or "." for row in state.board for piece in row) + ("w" if state.white_turn else "b")
            state.history[position_key] = state.history.get(position_key, 0) + 1
            if target_piece.lower() == "k":
                score: int = -842938
            elif state.history[position_key] == 3:
                score: int = 0
            else:
                score: int = -(self.negamax(depth-1, -beta, -alpha)[1])

            state.history[position_key] -= 1
            if state.history[position_key] == 0:
                del state.history[position_key]
            state.board[row1][col1], state.board[row2][col2] = piece_to_move, target_piece
            state.current_score = previous_score

            if piece_to_move.lower() == "k":
                king_coords[piece_to_move.isupper()] = (row1, col1)
            state.white_turn = not state.white_turn
            if score > best_score:
                best_move, best_score = move, score
            alpha = max(alpha, score)  
            if alpha >= beta:
                break
        state.transposition_table[key] = (depth, best_move, best_score, ("UPPERBOUND" if best_score <= alpha_original else ("LOWERBOUND" if best_score >= beta else "EXACT")))
        return (best_move, best_score)
        
    def ai(self) -> None:
        state: GameState = self.state
        if state.game_over:
            return
        state.current_score = self.score_board()
        #(row1, col1), (row2, col2), promotion_piece = self.negamax((4 if state.white_turn else 4))[0]
        (row1, col1), (row2, col2), promotion_piece = self.negamax((min(5, 4 + (8000 - sum(abs(state.material_scores[piece]) for row in state.board for piece in row if piece.lower() != "k" and piece != "")) // 5000)))[0]
        if promotion_piece != None:
            self.state.board[row1][col1] = promotion_piece
        if state.board[row1][col1].lower() == "k":
            state.king_coords[state.board[row1][col1].isupper()] = (row2, col2)
        self.animate(row1, col1, row2, col2)
        state.white_turn = not state.white_turn
        self.position_check()
        self.draw_board()






    def draw_board(self, event=None) -> None:
        t, state, sizes = self.t, self.state, self.sizes
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
                for side in range(4):
                    t.forward(sizes(True))
                    t.right(90)
                t.end_fill()
                piece_coords = (7-i if self.flip_board() else i), (j if self.flip_board() else 7-j)
                if piece_coords in state.selected:
                    t.penup()
                    t.goto(x + j*sizes(True), y + i*sizes(True))
                    t.pendown()
                    t.fillcolor(("#D0FFD0" if state.white_turn else "#7F907F"))
                    t.begin_fill()
                    for side in range(4):
                        t.forward(sizes(True))
                        t.right(90)
                    t.end_fill()
                piece: str = state.letter_map[state.board[piece_coords[0]][piece_coords[1]]]
                t.penup()
                # again, these magic numbers were from testing
                t.goto(x + j*sizes(True) + sizes(True)/8, y + i*sizes(True) - sizes(True))
                t.write(piece, font=("Arial", int(sizes(True)*0.6)))
        if state.message != None:
            self.show_message(state.message[0], state.message[1], state.message[2])
        self.window.update()

    def promote(self, piece: str) -> None:
        state: GameState = self.state
        row, col = state.promotion_square
        state.board[row][col] = piece
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
        if self.ai_active:
            self.ai()

    def animate(self, row1: int, col1: int, row2: int, col2: int) -> None:
        state: GameState = self.state
        animation: turtle.Turtle = self.animation
        current_player_piece: str = state.board[row1][col1]
        if current_player_piece.lower() == "k" and abs(col2 - col1) == 2:
            state.king_castled[int(not state.white_turn)] = ("k" if col2 - col1 == 2 else "q")
            self.animate(row1, (7 if col1 < col2 else 0), row2, (col2 + (-1 if col1 < col2 else 1)))
        state.board[row1][col1], state.board[row2][col2], (x1, y1), (x2, y2) = "", "", self.cell_to_coord(row1, col1), self.cell_to_coord(row2, col2)
        dy: float = ((y2 - y1) / 75)
        dx: float = ((x2 - x1) / 75)
        self.draw_board()
        animation.clear()
        animation.penup()
        animation.goto(x1, y1)
        for frame in range(75):
            animation.clear()
            animation.goto(x1 + dx*frame, y1 + dy*frame)
            animation.write(state.letter_map[current_player_piece], font=("Arial", int(self.sizes(True)*0.6)))
            self.window.update()
            # iteration of nothing is for the pause (as this project will only use turtle module). it also blocks, so that the next part cannot run, which is good.
            for iteration_of_nothing in range(100000):
                pass
        self.special_cases(current_player_piece, row1, col1, row2, col2)
        animation.clear()

    def show_message(self, msg: str, font_size: int | None=None, auto_close: bool=True) -> None:
        sizes = self.sizes
        message: turtle.Turtle = self.message
        self.state.message = (msg, font_size, auto_close)
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
        if auto_close:
            self.window.ontimer(lambda: self.close_message(0, 0), 2000)
        
    def close_message(self, x: float, y: float) -> None:
        self.state.message = None
        self.message.clear()
        self.window.onclick(self.move_pieces)

    def show_moves(self) -> None:
        t, sizes = self.t, self.sizes
        row1, col1 = self.state.selected[0]
        for row in range(8):
            for col in range(8):
                if self.valid_move((row1, col1), (row, col)):
                    x, y = self.cell_to_coord(row, col)
                    t.goto(x + (2*sizes(True))/5, y + sizes(True)/2)
                    t.pendown()
                    t.dot(int(sizes(True) * 0.2), "green")
                    t.penup()

    def position_check(self) -> None:
        state: GameState = self.state
        show_message = self.show_message
        position_state = "".join(piece or "." for row in state.board for piece in row) + ("w" if state.white_turn else "b")
        state.history[position_state] = state.history.get(position_state, 0) + 1
        if self.in_check(state.white_turn):
            if self.checkmate_yet(state.white_turn):
                state.game_over = True
                show_message("Checkmate by " + ("Black" if state.white_turn else "White") + "!")
            else:
                show_message("Check!")
        elif state.halfmoves > 99:
            state.game_over = True
            show_message("Draw: 50-move rule")
        elif state.history[position_state] > 2:
            state.game_over = True
            show_message("Draw: 3-fold repetition")
        else:
            if self.checkmate_yet(state.white_turn):
                state.game_over = True
                show_message("Stalemate!")
                

    def move_pieces(self, x: float, y: float) -> None:
        state: GameState = self.state
        run_ai: bool = False
        if state.game_over:
            return
        """
        # AI against AI - can config which side has better depth analysis on line 591.
        # This will not slow the speed down, but the messages may not display, or may display and instantly disappear
        while not state.game_over:
            self.ai()
        return
        #"""

        """
        # To show the messages properly, the speed is slowed down.
        def ai_vs_ai(self):
            if self.state.game_over:
                return
            self.ai()
            self.window.ontimer(lambda: ai_vs_ai(self), 1000)

        if self.ai_active:
            self.window.ontimer(lambda: ai_vs_ai(self), 1000)
        return
        #"""
        row, col = self.coord_to_cell(x, y)
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
                    if self.ai_active:
                        run_ai = True
                state.selected = []
            else:
                state.selected = []
        self.draw_board()
        if run_ai and not state.game_over:
            self.ai()
            state.selected = []
        if len(state.selected) == 1:
            self.show_moves()


# Just saw this in many python projects, so I decided to copy it.
# I don't think there is a need here though, because I haven't split this into many files yet.
if __name__ == "__main__":
    window = turtle.Screen()
    window.title("Chess")
    window.getcanvas().winfo_toplevel().minsize(500, 500)

    chess_game: ChessGame = ChessGame(window, window.textinput("Chess AI", "Would you like to play against an AI? (y/n)"))

    turtle.done()