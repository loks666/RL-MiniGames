import random
from connect4Board import Board
import math


def static_evaluator(board, piece):
    # The static evaluator function estimates the board score for a given player.
    # The score is calculated based on center control, horizontal, vertical, and diagonal connections.

    grid = board.grid
    score = 0

    # Center column score - prioritize control of the center column
    center_array = [int(i) for i in list(grid[:, Board.COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3  # Each piece in the center column contributes extra score

    def score_position(window, piece):
        # Helper function to score a "window" of four cells
        score = 0
        opponent_piece = 1 if piece == 2 else 2

        # High score for winning positions (4 in a row)
        if window.count(piece) == 4:
            score += 10000
        # Moderate score for almost winning positions (3 in a row with an empty space)
        elif window.count(piece) == 3 and window.count(0) == 1:
            score += 100
        # Lower score for 2 in a row with two empty spaces
        elif window.count(piece) == 2 and window.count(0) == 2:
            score += 10
        # Negative score for opponent's almost winning positions (3 in a row with an empty space)
        if window.count(opponent_piece) == 3 and window.count(0) == 1:
            score -= 80

        return score

    # Horizontal scoring
    for r in range(Board.ROW_COUNT):
        row_array = [int(i) for i in list(grid[r, :])]
        for c in range(Board.COLUMN_COUNT - 3):
            # Evaluate every possible horizontal "window" of four cells in each row
            window = row_array[c:c + 4]
            score += score_position(window, piece)

    # Vertical scoring
    for c in range(Board.COLUMN_COUNT):
        col_array = [int(i) for i in list(grid[:, c])]
        for r in range(Board.ROW_COUNT - 3):
            # Evaluate every possible vertical "window" of four cells in each column
            window = col_array[r:r + 4]
            score += score_position(window, piece)

    # Positive diagonal scoring (bottom-left to top-right)
    for r in range(Board.ROW_COUNT - 3):
        for c in range(Board.COLUMN_COUNT - 3):
            # Evaluate every possible diagonal "window" of four cells in the positive slope direction
            window = [grid[r + i][c + i] for i in range(4)]
            score += score_position(window, piece)

    # Negative diagonal scoring (top-left to bottom-right)
    for r in range(Board.ROW_COUNT - 3):
        for c in range(Board.COLUMN_COUNT - 3):
            # Evaluate every possible diagonal "window" of four cells in the negative slope direction
            window = [grid[r + 3 - i][c + i] for i in range(4)]
            score += score_position(window, piece)

    return score  # Return the final score for the board position


def minimax(board, current_depth, max_depth, player, alpha, beta):
    # The minimax function with alpha-beta pruning finds the best move for the current player.
    # It uses recursion to explore possible moves up to max_depth, then evaluates with static_evaluator.

    # Base case: check if game is over or max search depth is reached
    if board.is_game_over() or current_depth == max_depth:
        return (None, static_evaluator(board, player))  # Return the board evaluation if terminal state or depth limit

    valid_moves = board.valid_moves()  # Get all valid moves for the current board state
    if player == board.get_player_turn():
        # Maximizing player logic
        value = -math.inf
        best_move = random.choice(valid_moves)  # Initialize with a random valid move
        for move in valid_moves:
            # Recursively call minimax on the new board state after playing the move
            new_board = board.play(move)
            _, new_score = minimax(new_board, current_depth + 1, max_depth, 3 - player, alpha, beta)
            # Update the best move if we find a higher score
            if new_score > value:
                value = new_score
                best_move = move
            # Update alpha and check for alpha-beta pruning
            alpha = max(alpha, value)
            if alpha >= beta:
                break  # Prune the branch if alpha is greater than or equal to beta
        return best_move, value

    else:
        # Minimizing player logic
        value = math.inf
        best_move = random.choice(valid_moves)  # Initialize with a random valid move
        for move in valid_moves:
            # Recursively call minimax on the new board state after playing the move
            new_board = board.play(move)
            _, new_score = minimax(new_board, current_depth + 1, max_depth, 3 - player, alpha, beta)
            # Update the best move if we find a lower score
            if new_score < value:
                value = new_score
                best_move = move
            # Update beta and check for alpha-beta pruning
            beta = min(beta, value)
            if alpha >= beta:
                break  # Prune the branch if alpha is greater than or equal to beta
        return best_move, value
