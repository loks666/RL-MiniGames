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
import pygame
import sys
import math
from connect4Board import Board
from minimax import minimax, static_evaluator
from enum import Enum
from mcts import expand_mcts_tree_once, expand_mcts_tree_repeatedly, build_initial_blank_mcts_tree


BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)

class Agents(Enum):
    USER = 1
    MCTS = 2
    MINIMAX = 3    
    RANDOM = 4
    STATIC_EVALUATOR = 5

#uncomment one of the following lines to choose your AI vs human/AI opponent...
#controllers=[Agents.USER,Agents.USER]
controllers=[Agents.STATIC_EVALUATOR,Agents.USER]
#controllers=[Agents.MINIMAX,Agents.USER]
#controllers=[Agents.USER,Agents.MINIMAX]
#controllers=[Agents.MINIMAX,Agents.USER]
#controllers=[Agents.MCTS,Agents.MINIMAX]
#controllers=[Agents.USER,Agents.MINIMAX]
#controllers=[Agents.MINIMAX,Agents.USER]
#controllers=[Agents.MINIMAX,Agents.MCTS]
#controllers=[Agents.MINIMAX, Agents.STATIC_EVALUATOR]


def create_empty_board():
    return Board()

def draw_board(board):
    board=np.flip(board.grid, 0)
    for c in range(Board.COLUMN_COUNT):
        for r in range(Board.ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
    
    for c in range(Board.COLUMN_COUNT):
        for r in range(Board.ROW_COUNT):        
            if board[r][c] == Board.PLAYER1:
                pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
            elif board[r][c] == Board.PLAYER2: 
                pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
    pygame.display.update()
    
    
board = create_empty_board()
print(board.grid)

game_over = False

pygame.init()

SQUARESIZE = 100
RADIUS = int(SQUARESIZE/2 - 5)

width = Board.COLUMN_COUNT * SQUARESIZE
height = (Board.ROW_COUNT+1) * SQUARESIZE

size = (width, height)


screen = pygame.display.set_mode(size)
pygame.display.set_caption("Connect 4: Player1="+str(controllers[0])[7:]+" Player2="+str(controllers[1])[7:])
pygame.display.update()
myfont = pygame.font.SysFont("monospace", 75)
draw_board(board)

if Agents.MCTS in controllers:
    mcts_tree = build_initial_blank_mcts_tree()
else:
    mcts_tree = None
start_time = pygame.time.get_ticks()-500
while not game_over:
    turn=board.get_player_turn() # This will be 1 or 2, for player 1 or player 2, respectievly.
    current_agent=controllers[turn-1]
    move_choice=None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
            posx = event.pos[0]
            if current_agent == Agents.USER:
                pygame.draw.circle(screen, RED if turn==1 else YELLOW, (posx, int(SQUARESIZE/2)), RADIUS)

        pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
            # Ask for User Input
            if current_agent == Agents.USER:
                posx = event.pos[0]
                col = int(math.floor(posx/SQUARESIZE))
                if board.can_play(col):
                    move_choice=col

    # Make decision for AI players (if it's their turn...)
    if current_agent != Agents.USER and not game_over:                
        if current_agent == Agents.MINIMAX:
            move_choice, minimax_score = minimax(board, current_depth=0, max_depth=3, player=turn) # increase the max_depth to make a stronger player
        elif current_agent == Agents.RANDOM:
            move_choice = random.choice(board.valid_moves())
        elif current_agent == Agents.STATIC_EVALUATOR:
            valid_moves = board.valid_moves()
            move_scores = np.array([static_evaluator(board.play(move),turn) for move in valid_moves]) # This is the one-step look ahead
            best_score = move_scores.max()
            best_score_indices = np.where(move_scores == best_score)[0]
            print("move_scores",move_scores,best_score_indices)
            move_choice = valid_moves[random.choice(best_score_indices)]
        elif current_agent == Agents.MCTS:
            assert mcts_tree.board==board
            expand_mcts_tree_repeatedly(mcts_tree, tree_expansion_time_ms=600)# increase the expansion time to make a stronger player
            mcts_tree, move_choice = mcts_tree.select_best_move()
        else:
            raise Exception("Unknown agent "+str(current_agent))
        assert move_choice!=None
        assert board.can_play(move_choice)
        time_elapsed = pygame.time.get_ticks()-start_time
        if time_elapsed<1000:
            # make any AI player wait at least a second before responding, otherwise it gets confusing to user
            pygame.time.wait((int)(1000-time_elapsed))
        
    if move_choice!=None:
        assert board.can_play(move_choice)
        board=board.play(move_choice)
        if board.is_game_over():
            label = myfont.render("Player "+str(turn)+" wins!!", 1, YELLOW if turn==2 else RED)
            screen.blit(label, (40,10))
            game_over = True

        print(board.grid)
        draw_board(board)
        start_time = pygame.time.get_ticks()
        if mcts_tree!=None and current_agent!=Agents.MCTS:
            # update the MCTS tree to say it has a new root node.
            expand_mcts_tree_once(mcts_tree)
            mcts_tree=mcts_tree.get_child_with_move(move_choice)
            assert mcts_tree.board==board

        move_choice=None 

    if game_over:
        pygame.time.wait(3000)
