from copy import deepcopy
import pygame

RED = (255,0,0)
WHITE = (255, 255, 255)

def minimax(position, depth, max_player, alpha, beta, game):
    best_position = None

    if depth == 0 or position.winner() != None:
        return position.evaluate(), position
    
    if max_player:
        max_eval = float('-inf')

        for move in get_all_moves(position, WHITE):
            child_eval = minimax(move, depth - 1, False, alpha, beta, game)[0]
            
            if child_eval > max_eval:
                max_eval = child_eval
                best_position = move

            alpha = max(alpha, max_eval)
            if beta <= alpha:
                break
 
            # if max_eval == child_eval:
            #     best_position = move

        return max_eval, best_position
    
    else:
        min_eval = float('inf')

        for move in get_all_moves(position, RED):
            child_eval = minimax(move, depth - 1, True, alpha, beta, game)[0]
            
            if child_eval < min_eval:
                min_eval = child_eval
                best_position = move

            beta = min(beta, min_eval)
            if beta <= alpha:
                break

            # if min_eval == child_eval:
            #     best_position = move

        return min_eval, best_position


def get_all_moves(board, color):
    moves = []

    for piece in board.get_all_pieces(color):
        valid_moves = board.get_valid_moves(piece)

        for move, skip in valid_moves.items():
            #draw_moves(game, board, piece)
            
            tmp_board = deepcopy(board)
            tmp_piece = tmp_board.get_piece(piece.row, piece.col)
            new_board = simulate_move(tmp_board, tmp_piece, move, skip)

            moves.append(new_board)
    
    return moves


def draw_moves(game, board, piece):
    valid_moves = board.get_valid_moves(piece)

    board.draw(game.win)
    pygame.draw.circle(game.win, (0, 255, 0), (piece.x, piece.y), 50, 5)

    game.draw_valid_moves(valid_moves.keys())
    pygame.display.update()

    #pygame.time.delay(100)


def simulate_move(board, piece, move, skip):
    board.move(piece, move[0], move[1])

    if skip:
        board.remove(skip)

    return board
