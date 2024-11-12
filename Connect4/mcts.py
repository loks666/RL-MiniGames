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
    # 1. Selection
    # Traverse down the tree to select a node to expand. We keep moving down the tree
    # by selecting children nodes with the highest UCB1 score until we reach a node without children.
    while mcts_node.children is not None:
        assert (not mcts_node.is_terminal_node())  # Ensure that we are not at a terminal node
        terminal_state_children = [child for child in mcts_node.children if child.is_terminal_node()]

        # If there are terminal children nodes (end states), select one of them.
        if terminal_state_children:
            mcts_node = terminal_state_children[0]
        else:
            # Calculate UCB1 scores for all children nodes to decide the next node to explore
            ucts = [child.get_ucb1_score() for child in mcts_node.children]  # Select the highest UCB1 score
            if None in ucts:
                # If there are unvisited nodes (UCB1 score is None), randomly select one to expand
                unvisited_children = [mcts_node.children[i] for i, x in enumerate(ucts) if x is None]
                mcts_node = random.choice(unvisited_children)
            else:
                # If all nodes have been visited, select the child with the highest UCB1 score
                mcts_node = mcts_node.children[np.argmax(ucts)]

    # 2. Expansion
    # If the selected node is not a terminal node, expand it by adding all possible moves as children nodes.
    if not mcts_node.is_terminal_node():
        moves = mcts_node.board.valid_moves()  # Get all valid moves for the current board state
        assert len(moves) > 0  # Ensure there are valid moves
        assert mcts_node.children is None  # Ensure this node has no children yet

        # Generate successor states (child nodes) for each valid move
        successor_states = [(mcts_node.board.play(move), move) for move in moves]
        # Create new MCTS_Node instances for each successor state, with the current node as their parent
        new_children = [MCTS_Node(board, move=move, parent=mcts_node) for (board, move) in successor_states]
        mcts_node.set_children(new_children)  # Set the newly created nodes as children of the current node

    # 3. Playout
    # Perform a playout (simulation) from the current node to determine a winner
    if mcts_node.is_terminal_node():
        # If the current node is terminal, get the victorious player
        victorious_player = mcts_node.board.get_victorious_player()
        assert mcts_node.board.get_victorious_player() in [mcts_node.board.get_player_who_just_moved(), 0]
    else:
        # If it's not a terminal node, choose a random child node and perform a playout from there
        mcts_node = random.choice(mcts_node.children)
        if mcts_node.is_terminal_node():
            # If the chosen child is a terminal node, get the victorious player
            victorious_player = mcts_node.board.get_victorious_player()
            assert mcts_node.board.get_victorious_player() in [mcts_node.board.get_player_who_just_moved(), 0]
        else:
            # If the chosen child is not a terminal node, perform a random playout until the game ends
            victorious_player = random_play(mcts_node.board)

    # 4. Backpropagation
    # Backpropagate the results of the playout up the tree, updating visit counts and win counts.
    while mcts_node is not None:
        mcts_node.games += 1  # Increment the visit count for the node
        # If the victorious player is the player who just moved, update the win count for that player
        if victorious_player != 0 and mcts_node.board.get_player_who_just_moved() == victorious_player:
            mcts_node.wins_for_player_just_moved += 1
        mcts_node = mcts_node.parent  # Move up to the parent node and continue backpropagation


