import random
import numpy as np
from connect4Board import Board
import math

def static_evaluator(board, piece):
    grid = board.grid
    score = 0

    # 中心列加分
    center_array = [int(i) for i in list(grid[:, Board.COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    def score_position(window, piece):
        score = 0
        opponent_piece = 1 if piece == 2 else 2
        if window.count(piece) == 4:
            score += 10000
        elif window.count(piece) == 3 and window.count(0) == 1:
            score += 100
        elif window.count(piece) == 2 and window.count(0) == 2:
            score += 10
        if window.count(opponent_piece) == 3 and window.count(0) == 1:
            score -= 80
        return score

    # 水平打分
    for r in range(Board.ROW_COUNT):
        row_array = [int(i) for i in list(grid[r, :])]
        for c in range(Board.COLUMN_COUNT - 3):
            window = row_array[c:c + 4]
            score += score_position(window, piece)

    # 垂直打分
    for c in range(Board.COLUMN_COUNT):
        col_array = [int(i) for i in list(grid[:, c])]
        for r in range(Board.ROW_COUNT - 3):
            window = col_array[r:r + 4]
            score += score_position(window, piece)

    # 正对角线打分
    for r in range(Board.ROW_COUNT - 3):
        for c in range(Board.COLUMN_COUNT - 3):
            window = [grid[r + i][c + i] for i in range(4)]
            score += score_position(window, piece)

    # 反对角线打分
    for r in range(Board.ROW_COUNT - 3):
        for c in range(Board.COLUMN_COUNT - 3):
            window = [grid[r + 3 - i][c + i] for i in range(4)]
            score += score_position(window, piece)

    return score

def minimax(board, current_depth, max_depth, player, alpha, beta):
    if board.is_game_over() or current_depth == max_depth:
        return (None, static_evaluator(board, player))

    valid_moves = board.valid_moves()
    if player == board.get_player_turn():
        value = -math.inf
        best_move = random.choice(valid_moves)
        for move in valid_moves:
            new_board = board.play(move)
            _, new_score = minimax(new_board, current_depth + 1, max_depth, 3 - player, alpha, beta)
            if new_score > value:
                value = new_score
                best_move = move
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_move, value
    else:
        value = math.inf
        best_move = random.choice(valid_moves)
        for move in valid_moves:
            new_board = board.play(move)
            _, new_score = minimax(new_board, current_depth + 1, max_depth, 3 - player, alpha, beta)
            if new_score < value:
                value = new_score
                best_move = move
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_move, value
