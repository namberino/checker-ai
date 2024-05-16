import pygame
from .constants import BLACK, ROWS, RED, SQUARE_SIZE, COLS, WHITE
from .piece import Piece
from copy import deepcopy

class Board:
    def __init__(self):
        self.board = [] # 2d array representing pieces on the board
        self.red_left = self.white_left = 12
        self.red_kings = self.white_kings = 0
        self.create_board()
    
    def draw_squares(self, win):
        win.fill(BLACK)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(win, RED, (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def get_all_pieces(self, color):
        pieces = []

        for row in self.board:
            for piece in row:
                if piece != 0 and piece.color == color:
                    pieces.append(piece)

        return pieces

    # evaluate current position
    def evaluate(self):
        # Constants for piece and king values
        piece_value = 1 # Importance of piece
        king_value = 3 # Importance of king
        
        evaluation = 0
        
        # Evaluate piece count
        evaluation += (self.white_left - self.red_left) * piece_value
        
        # Evaluate king count
        evaluation += (self.white_kings - self.red_kings) * king_value
        
        # Evaluate piece positioning
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0: # if there's a piece
                    if piece.color == WHITE:
                        evaluation += piece_value * (ROWS - row)  # reward advancement for white pieces
                    else:
                        evaluation -= piece_value * (ROWS - row)  # penalize for white pieces allowing red pieces to advance
        
        # Evaluate mobility (add sum of number of valid moves of all pieces)
        white_mobility = sum(len(self.get_valid_moves(piece)) for piece in self.get_all_pieces(WHITE))
        red_mobility = sum(len(self.get_valid_moves(piece)) for piece in self.get_all_pieces(RED))
        evaluation += (white_mobility - red_mobility) * 0.3 # 0.3 is the importance of mobility on evaluation
        
        # Evaluate king safety (kings positioned on the edges are safer)
        white_king_safety = sum(1 for piece in self.get_all_pieces(WHITE) if piece.king and (piece.row == 0 or piece.row == ROWS - 1 or piece.row == 1 or piece.row == ROWS - 2))
        red_king_safety = sum(1 for piece in self.get_all_pieces(RED) if piece.king and (piece.row == 0 or piece.row == ROWS - 1 or piece.row == 1 or piece.row == ROWS - 2))
        evaluation += (white_king_safety - red_king_safety) * 0.2
        
        # Evaluate control of the center
        center_control = 0
        for row in range(2, 6): # Central rows
            for col in range(2 if row % 2 == 0 else 1, COLS, 2): # Each columns based on whether current row is odd or not
                piece = self.board[row][col]
                if piece != 0:
                    if piece.color == WHITE:
                        center_control += piece_value
                    else:
                        center_control -= piece_value
        evaluation += center_control * 0.5
        
        return evaluation

    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)

        if row == ROWS - 1 or row == 0:
            piece.make_king()
            if piece.color == WHITE:
                self.white_kings += 1
            else:
                self.red_kings += 1 

    def get_piece(self, row, col):
        return self.board[row][col]

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if col % 2 == ((row +  1) % 2):
                    if row < 3:
                        self.board[row].append(Piece(row, col, WHITE))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, RED))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)
        
    def draw(self, win):
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)

    def remove(self, pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = 0
            if piece != 0:
                if piece.color == RED:
                    self.red_left -= 1
                else:
                    self.white_left -= 1
    
    def winner(self):
        if not self.player_has_valid_moves(RED):
            return WHITE
        elif not self.player_has_valid_moves(WHITE):
            return RED

        if self.red_left <= 0:
            return WHITE
        elif self.white_left <= 0:
            return RED
        
        return None 
    
    def get_valid_moves(self, piece):
        moves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row

        # max(row - 3, -1) and min(row + 3, ROWS) ensures the piece doesn't go off the board
        if piece.color == RED or piece.king:
            moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
            moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))
        if piece.color == WHITE or piece.king:
            moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))
    
        return moves
    
    def player_has_valid_moves(self, color):
        for row in self.board:
            for piece in row:
                if piece != 0 and piece.color == color:
                    if self.get_valid_moves(piece):
                        return True
                    
        return False

    '''
    start: starting row
    stop: 
    '''
    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break
            
            current = self.board[r][left]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last
                
                if last:
                    if step == -1:
                        row = max(r - 3, -1)
                    else:
                        row = min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, row, step, color, left - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, left + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            left -= 1
        
        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= COLS:
                break
            
            current = self.board[r][right]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r,right)] = last + skipped
                else:
                    moves[(r, right)] = last
                
                if last:
                    if step == -1:
                        row = max(r - 3, -1)
                    else:
                        row = min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, row, step, color, right - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, right + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            right += 1
        
        return moves
