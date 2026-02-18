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
        self.white_pieces: list[str] = ["♙", "♘", "♗", "♖", "♕", "♔"]
        self.black_pieces: list[str] = ["♟", "♞", "♝", "♜", "♛", "♚"]
        self.king_moved: list[bool] = [False, False]
        self.rook_moved: list[bool] = [False, False, False, False]
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
        self.pieces_map: dict[str, str] = { "♙": "p", "♖": "r", "♘": "n", "♗": "b", "♕": "q", "♔": "k", "♟": "P", "♜": "R", "♞": "N", "♝": "B", "♛": "Q", "♚": "K" }
        self.letter_map: dict[str, str] = { letter: piece for piece, letter in self.pieces_map.items() }
        self.piece_type: dict[str, list[str, str]] = { "pawns": ["♙", "♟"], "rooks": ["♖", "♜"], "knights": ["♘", "♞"], "bishops": ["♗", "♝"], "queens": ["♕", "♛"], "kings": ["♔", "♚"] }
        self.selected: list[tuple[int, int]] = []
        self.white_turn: bool = True
        self.en_passent_target: tuple[int, int] | None = None
        self.game_over: bool = False
        self.halfmoves: int = 0
        self.history: dict[tuple, int] = {}
        self.promotion_square: tuple[int, int] | None = None
        self.message: tuple[str, int] | None = None
        self.transposition_table: dict[tuple[list[list[str]] | int | bool]] = {}
        self.material_scores: dict[str, int] = { "♙": 100, "♟": -100, "♘": 320, "♞": -320, "♗": 330, "♝": -330, "♖": 500, "♜": -500, "♕": 900, "♛": -900, "♔": 999999, "♚": -999999 }
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
            "♙": pawn_ps_table,
            "♘": knight_ps_table,
            "♗": bishop_ps_table,
            "♖": rook_ps_table,
            "♕": queen_ps_table,
            "♔": king_ps_table,
            "♟": [[-score for score in row] for row in pawn_ps_table[::-1]],
            "♞": [[-score for score in row] for row in knight_ps_table[::-1]],
            "♝": [[-score for score in row] for row in bishop_ps_table[::-1]],
            "♜": [[-score for score in row] for row in rook_ps_table[::-1]],
            "♛": [[-score for score in row] for row in queen_ps_table[::-1]],
            "♚": [[-score for score in row] for row in king_ps_table[::-1]],
        }

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
    
    def export(self) -> str:
        return base64(("|".join(["/".join(self.format_row(row) for row in self.board), ("w" if self.white_turn else "b"), ("-" if self.en_passent_target is None else f"{self.en_passent_target[0]},{self.en_passent_target[1]}"), str(self.halfmoves), ("".join("1" if k else "0" for k in self.king_moved)), ("".join("1" if r else "0" for r in self.rook_moved))])))
    
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
        if 0 <= row and 0 <= col < 8:
            return (row if self.flip_board() else 7-row), (col if self.flip_board() else 7-col)
        return None, None


    def get_position_state(self) -> tuple[tuple[tuple[str] | bool] | bool]:
        state: GameState = self.state
        return (tuple(tuple(row) for row in state.board), state.white_turn)

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
            except:
                self.show_message("Invalid code")

    def check_turn(self, row: int, col: int) -> bool:
        state: GameState = self.state
        if len(state.selected) == 0:
            check_turn: bool = ((state.board[row][col] in state.white_pieces) == state.white_turn)
        elif len(state.selected) == 1:
            check_turn: bool = ((state.board[row][col] in state.white_pieces) != state.white_turn) or state.board[row][col] == ""
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
        piece_to_move: str = state.board[row1][col1]
        target_piece: str = state.board[row2][col2]
        
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

        elif piece_to_move in state.piece_type["knights"]:
            return (abs(dy*dx) == 2)
        
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
            pieces: list[str] = (state.piece_type["bishops"] + state.piece_type["rooks"] + state.piece_type["queens"])
            valid_movements: list[bool] = [(a:=abs(dy)==abs(dx)), (b:=dy==0 or dx==0), (a or b)]

            if valid_movements[pieces.index(piece_to_move) // 2]:
                return self.gonna_crash(row1, col1, row2, col2)
            return False

    # TODO: Store king location instead of finding it.
    def in_check(self, white: bool) -> bool:
        state: GameState = self.state
        king: tuple[int, int] | str = ("♔" if white else "♚")
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

    def valid_move(self, origin: tuple[int, int], target: tuple[int, int]) -> bool:
        state: GameState = self.state
        (row1, col1), (row2, col2) = origin, target
        if (state.board[row1][col1] in state.white_pieces and state.board[row2][col2] in state.white_pieces) or (state.board[row1][col1] in state.black_pieces and state.board[row2][col2] in state.black_pieces):
                return False
        
        if not self.piece_move_valid(origin, target):
            return False
        
        piece_to_move: str = state.board[row1][col1]
        target_piece: str = state.board[row2][col2]
        state.board[row2][col2], state.board[row1][col1] = state.board[row1][col1], ""
        if self.in_check((state.board[row2][col2] in state.white_pieces)):
            state.board[row1][col1], state.board[row2][col2] = piece_to_move, target_piece
            return False
        elif piece_to_move in state.piece_type["kings"] and abs(col2 - col1) == 2:
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

    def special_cases(self, current_player_piece: str, row1: int, col1: int, row2: int, col2: int) -> None:
        state: GameState = self.state
        if current_player_piece in state.piece_type["pawns"] and state.en_passent_target == (row2, col2):
            state.board[(row2-(-1 if current_player_piece == "♙" else 1))][col2] = ""
        if current_player_piece == "♙" and row1 == 6 and row2 == 4:
            state.en_passent_target = (5, col2)
        elif current_player_piece == "♟" and row1 == 1 and row2 == 3:
            state.en_passent_target = (2, col2)
        else:
            state.en_passent_target = None

        if current_player_piece in state.piece_type["pawns"] or state.board[row2][col2] != "":
            state.halfmoves = 0
        else:
            state.halfmoves += 1

        if current_player_piece in state.piece_type["kings"]:
            state.king_moved[(0 if current_player_piece == "♔" else 1)] = True
        elif current_player_piece in state.piece_type["rooks"] and ((row1 == 7 if current_player_piece == "♖" else row1 == 0) and (col1 == 0  or col1 == 7)):
            state.rook_moved[((0 if current_player_piece == "♖" else 2) + (0 if col1 == 0 else 1))] = True

        state.board[row2][col2] = current_player_piece
        
        if (current_player_piece == "♙" and row2 == 0) or (current_player_piece == "♟" and row2 == 7):
            state.promotion_square = (row2, col2)
            options: list[str] = (["♕", "♖", "♗", "♘"] if row2 == 0 else ["♛", "♜", "♝", "♞"])
            self.show_message("Promote to:\n1: Queen   2: Rook   3: Bishop   4: Knight\nEnter the number of your choice.", int(self.sizes(True)//6), False)
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
        for rook, moved_yet in enumerate(state.rook_moved):
            if moved_yet:
                castling_score += (50 if rook // 2 == 0 else -50)
        for king, moved_yet in enumerate(state.king_moved):
            if moved_yet:
                castling_score += (100 if king == 0 else -100)
        return piece_score + pstables_score
    

    def possible_moves(self, white: bool) -> list[tuple[tuple[int]]]:
        state = self.state
        moves: list[tuple[tuple[int]]] = []
        board = state.board
        for row1 in range(8):
            for col1 in range(8):
                piece: str = board[row1][col1]
                if (piece == "") or (white and piece not in state.white_pieces) or (not white and piece not in state.black_pieces):
                    continue
                
                elif piece in state.piece_type["pawns"]:
                    direction: int =  (-1 if piece == "♙" else 1)
                    for jump in (1, 2):
                        row2: int = row1 + jump * direction
                        if 0 <= row2 < 8 and ((jump == 1 and board[row2][col1] == "") or (jump == 2 and row1 in [6, 1] and board[row2][col1] == "" and board[row1 + direction][col1] == "")) and self.valid_move((row1, col1), (row2, col1)):
                            for promotion_piece in (["♕", "♖", "♗", "♘"] if (piece == "♙" and row2 == 0) else (["♛", "♜", "♝", "♞"] if (piece == "♟" and row2 == 7) else [None])):
                                moves.append(((row1, col1), (row2, col1), promotion_piece))
                    for side in (-1, 1):
                        row2, col2 = row1 + direction, col1 + side
                        if 0 <= row2 < 8 and 0 <= col2 < 8 and self.valid_move((row1, col1), (row2, col2)):
                            for promotion_piece in (["♕", "♖", "♗", "♘"] if (piece == "♙" and row2 == 0) else (["♛", "♜", "♝", "♞"] if (piece == "♟" and row2 == 7) else [None])):
                                moves.append(((row1, col1), (row2, col2), promotion_piece))
                        if (row2, col2) == state.en_passent_target:
                            moves.append(((row1, col1), (row2, col2), None))

                elif piece in state.piece_type["knights"]:
                    for dy, dx in [(-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2)]:
                        row2, col2 = row1 + dy, col1 + dx
                        if 0 <= row2 < 8 and 0 <= col2 < 8 and self.valid_move((row1, col1), (row2, col2)):
                            moves.append(((row1, col1), (row2, col2), None))

                elif piece in state.piece_type["kings"]:
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            if dy == 0 and dx == 0:
                                continue
                            row2, col2 = row1 + dy, col1 + dx
                            if 0 <= row2 < 8 and 0 <= col2 < 8 and self.valid_move((row1, col1), (row2, col2)):
                                moves.append(((row1, col1), (row2, col2), None))
                    for dx in (-2, 2):
                        col2 = col1 + dx
                        if 0 <= col2 < 8 and self.valid_move((row1, col1), (row1, col2)):
                            moves.append(((row1, col1), (row1, col2), None))

                else:
                    pieces: list[str] = (state.piece_type["bishops"] + state.piece_type["rooks"] + state.piece_type["queens"])
                    valid_movements: list[list[tuple[int]]] = [(a:=[(-1,-1), (-1,1), (1,1), (1,-1)]), (b:=[(-1, 0), (0, 1), (0, -1), (1, 0)]), (a+b)]
                    for dy, dx in valid_movements[pieces.index(piece) // 2]:
                        row2, col2 = row1 + dy, col1 + dx
                        while 0 <= row2 < 8 and 0 <= col2 < 8:
                            if self.valid_move((row1, col1), (row2, col2)):
                                moves.append(((row1, col1), (row2, col2), None))
                            if board[row2][col2] != "":
                                break
                            row2 += dy
                            col2 += dx
        return moves


    def negamax(self, depth: int, alpha: float=float("-inf"), beta: float=float("inf")) -> int:
        state: GameState = self.state
        if depth == 0:
            return (None, (self.score_board() if state.white_turn else -self.score_board()))
        key = (tuple(tuple(row) for row in state.board), state.white_turn, tuple(state.king_moved), tuple(state.rook_moved), state.en_passent_target)
        if key in state.transposition_table:
            if state.transposition_table[key][0] >= depth:
                return (state.transposition_table[key][1], state.transposition_table[key][2])
        moves: list[tuple[tuple[int]]] = self.possible_moves(state.white_turn)
        if len(moves) == 0:
            if self.in_check(state.white_turn):
                return (None, -453421-depth)
            return (None, 0)
        moves.sort(key=lambda move: (0 if state.board[move[1][0]][move[1][1]] == "" else abs(state.material_scores[state.board[move[0][0]][move[0][1]]]) - abs(state.material_scores[state.board[move[1][0]][move[1][1]]])))
        best_score: int | float = float("-inf")
        best_move: tuple[tuple[int]] | None = None
        for move in moves:
            (row1, col1), (row2, col2), promotion_piece = move
            piece_to_move, target_piece = state.board[row1][col1], state.board[row2][col2]
            if target_piece in state.piece_type["kings"]:
                return (move, -452154)
            state.board[row1][col1], state.board[row2][col2] = "", (promotion_piece if promotion_piece else piece_to_move)
            state.white_turn = not state.white_turn
            position_key = self.get_position_state()
            state.history[position_key] = state.history.get(position_key, 0) + 1
            if state.history[position_key] == 3:
                score: int = 0
            else:
                score: int = -(self.negamax(depth-1, -beta, -alpha)[1])
            state.history[position_key] -= 1
            if state.history[position_key] == 0:
                del state.history[position_key]
            state.board[row1][col1], state.board[row2][col2] = piece_to_move, target_piece
            state.white_turn = not state.white_turn
            if score > best_score:
                best_move, best_score = move, score
            alpha, best_score = max(alpha, score), max(best_score, score)    
            if alpha >= beta:
                break
        state.transposition_table[key] = (depth, best_move, best_score)
        return (best_move, best_score)
        
    def ai(self) -> None:
        state: GameState = self.state
        if state.game_over:
            return
        #(row1, col1), (row2, col2), promotion_piece = self.negamax((4 if state.white_turn else 4))[0]
        (row1, col1), (row2, col2), promotion_piece = self.negamax((min(6, 3 + (8000 - sum(abs(state.material_scores[piece]) for row in state.board for piece in row if piece not in "♔♚")) // 2000)))[0]
        if promotion_piece != None:
            self.state.board[row1][col1] = promotion_piece
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
                piece: str = state.board[piece_coords[0]][piece_coords[1]]
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
        if current_player_piece in state.piece_type["kings"] and abs(col2 - col1) == 2:
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
            animation.write(current_player_piece, font=("Arial", int(self.sizes(True)*0.6)))
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
        state.history[self.get_position_state()] = state.history.get(self.get_position_state(), 0) + 1
        if self.in_check(state.white_turn):
            if self.checkmate_yet(state.white_turn):
                state.game_over = True
                show_message("Checkmate by " + ("Black" if state.white_turn else "White") + "!")
            else:
                show_message("Check!")
        elif state.halfmoves > 99:
            state.game_over = True
            show_message("Draw: 50-move rule")
        elif state.history[self.get_position_state()] > 2:
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
        # AI against AI - can config which side has better depth analysis on line 520.
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