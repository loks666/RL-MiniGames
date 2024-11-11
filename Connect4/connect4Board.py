# Connect 4 implementation for MCTS and Minimax.
# University of Essex.
# M. Fairbank November 2021 for course CE811 Game Artificial Intelligence
# 
# Acknowedgements: 
# All of the graphics and some other code for the main game loop and minimax came from https://raw.githubusercontent.com/KeithGalli/Connect4-Python
# Some of the connect4Board logic and MCTS algorithm came from https://github.com/floriangardin/connect4-mcts 
# Other designs are implemented from the Millington and Funge Game AI textbook chapter on Minimax.
import numpy as np

class Board:
    PLAYER1=1
    PLAYER2=2
    EMPTY=0
    ROW_COUNT = 6
    COLUMN_COUNT = 7
    def __init__(self, grid=np.zeros((ROW_COUNT, COLUMN_COUNT), dtype=int), game_over=False, victorious_player=None, player_to_play=None): 
        self.grid=grid# A numpy array of the board.  It will be filled with 0s or 1s or 2s indicating the cell contents (Empty / Player1 / Player2)
        self._game_over=game_over 
        self._victorious_player=victorious_player if game_over else None
        if player_to_play==None:
            player_to_play=self._calculate_player_to_play()
        self._player_to_play=player_to_play
        
    def valid_moves(self):
        # returns a list of integers, representing the valid moves (columns) that can be played from this grid.
        return [i for i in range(self.grid.shape[1]) if self.can_play(i)]

    def is_game_over(self):
        # returns True if this board state is game over (either a win or a draw)
        return self._game_over
        
    def get_player_turn(self):
        # returns the player number of whose turn it is next
        return self._player_to_play

    def get_player_who_just_moved(self):
        # returns the player number of who has just taken their turn.
        return 3-self._player_to_play        
        
    def get_victorious_player(self):
        # returns who won the game (1=PLAYER1, 2=PLAYER2 or 0=DRAW)
        assert self.is_game_over()
        return self._victorious_player
        
    def can_play(self, column):
        #Check if the given column is free
        assert column>=0 and column<Board.COLUMN_COUNT
        return self._get_column_height(column) < Board.ROW_COUNT
        
    def _get_column_height(self, column):
        return (self.grid[:, column]!=Board.EMPTY).astype(int).sum()

    def _calculate_player_to_play(self):
        #    Works out whose turn it is, for this board
        # Returns Board.PLAYER1 or Board.PLAYER2 depending on which player
        num_player_1_turns = (self.grid==Board.PLAYER1).astype(int).sum()
        num_player_2_turns = (self.grid==Board.PLAYER2).astype(int).sum()
        if num_player_1_turns > num_player_2_turns:
            return Board.PLAYER2
        else:
            return Board.PLAYER1
            
    def __eq__(self, obj):
        return isinstance(obj, Board) and np.all(obj.grid==self.grid)
            
    def play(self, column):
        """  Play at given column (for whichever player's turn it is to move next).
        Returns new Board state, which itself contains details of who has won (if anyone)
        (Note this function does not modify the current Board state, it returns a new copy 
        of the new modified board state.  Board class should be treated as immutable.)
        """
        grid = self.grid.copy()
        player = self.get_player_turn()

        if self.can_play(column):
            row = Board.ROW_COUNT - 1 - self._get_column_height(column)# calculates how high this column is
            grid[row, column] = player
        else:
            raise Exception("Invalid move attempt")
        winning_move=Board._has_won(grid, player, row, column)
        game_over=winning_move or Board._game_board_full(grid)
        return Board(grid, game_over, player if winning_move else 0, 3-player)

    @staticmethod
    def _game_board_full(grid):
        """
        Check if grid is full of pieces - no more spaces to go in.
        """
        return (grid==Board.EMPTY).astype(int).sum()==0

    @staticmethod
    def _has_won(grid, player, row, column):
        # Check if player has just won with its new piece.  
        # Returns True if player has just won by moving at (row, col); otherwise returns False.
        # For efficiency, we only need to check the row/cols/diagnols through the most recent move (at (row, column))
        row_str = ''.join(grid[row, :].astype(str).tolist())
        col_str = ''.join(grid[:, column].astype(str).tolist())
        up_diag_str = ''.join(np.diagonal(grid, offset=(column - row)).astype(str).tolist())
        down_diag_str = ''.join(np.diagonal(np.rot90(grid), offset=-grid.shape[1] + (column + row) + 1).astype(str).tolist())
        victory_pattern = str(player)*4
        if victory_pattern in row_str:
            return True
        if victory_pattern in col_str:
            return True
        if victory_pattern in up_diag_str:
            return True
        if victory_pattern in down_diag_str:
            return True
        return False
