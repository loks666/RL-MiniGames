# Connect 4 implementation for MCTS and Minimax.
# University of Essex.
# M. Fairbank November 2021 for course CE811 Game Artificial Intelligence
#
# Acknowedgements:
# All of the graphics and some other code for the main game loop and minimax came from https://github.com/KeithGalli/Connect4-Python
# Some of the connect4Board logic and MCTS algorithm came from https://github.com/floriangardin/connect4-mcts
# Other designs are implemented from the Millington and Funge Game AI textbook chapter on Minimax.
import numpy as np
import random

from connect4Board import Board


class MCTS_Node:

    def __init__(self, board, move, parent):
        self.board = board  # The Board object that this node represents
        self.parent = parent  # Parent Node
        self.move = move  # This is the move used to get to this Node from the parent node (an int from 0 to 6)
        self.games = 0  # How many times this node has had rollout games played through it
        self.wins_for_player_just_moved = 0  # How many rollout games through this node have won (for the player who has just played)
        self.children = None  # A list of child Nodes

    def set_children(self, children):
        self.children = children

    def get_ucb1_score(self):
        if self.games == 0:
            return None
        return (self.wins_for_player_just_moved / self.games) + np.sqrt(2 * np.log(self.parent.games) / self.games)

    def select_best_move(self):
        """
        Select best move and advance
        :return:
        """
        if self.children is None:
            return None, None

        winners = [child for child in self.children if
                   (child.is_terminal_node() and child.board.get_victorious_player() != 0)]
        if len(winners) > 0:
            return winners[0], winners[0].move

        child_win_rates = [child.wins_for_player_just_moved / child.games if child.games > 0 else 0 for child in
                           self.children]
        best_child = self.children[np.argmax(child_win_rates)]
        return best_child, best_child.move

    def is_terminal_node(self):
        return self.board.is_game_over()

    def get_child_with_move(self, move):
        if self.children is None:
            raise Exception('No existing child')
        for child in self.children:
            if child.move == move:
                return child
        raise Exception('No existing child')


def random_play(board):
    # Play a random game starting at board state. Return winner (1 or 2 (or 0 if draw))
    while True:
        if board.is_game_over():
            return board.get_victorious_player()
        moves = board.valid_moves()
        assert len(moves) > 0
        selected_move = random.choice(moves)
        board = board.play(selected_move)


def expand_mcts_tree_repeatedly(mcts_tree, tree_expansion_time_ms):
    import time
    start_time = int(round(time.time() * 1000))
    current_time = start_time
    while (current_time - start_time) < tree_expansion_time_ms:
        expand_mcts_tree_once(mcts_tree)
        current_time = int(round(time.time() * 1000))


def build_initial_blank_mcts_tree():
    # we've not started building our game tree at all yet.  Make a top-level node for it.
    mcts_tree = MCTS_Node(Board(), move=None, parent=None)
    expand_mcts_tree_once(mcts_tree)
    return mcts_tree


def expand_mcts_tree_once(mcts_node):
    # this is the main MCTS algorithm.  On entry, mcts_node should be the top-level node of the tree
    # This function modifies the mcts tree, expanding it by adding new children as appropriate, and
    # updating the win/loss statistics of all nodes along the path chosen.

    # 1. Selection
    # TODO

    # 2. Expansion
    # TODO

    # 3. Playout (also called "Simulation" or "Random Rollout")
    # TODO

    # 4. Backpropagation
    # TODO
    return
