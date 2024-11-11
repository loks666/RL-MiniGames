import random

from Connect4.connect4Board import Board
from Connect4.mcts import expand_mcts_tree_once, MCTSNode


# 假设您的 MCTS 类和其他代码已经在同一个文件中定义
# 或者您可以将它们导入此文件中

class TestAgents:
    RANDOM = 'RANDOM'
    MCTS = 'MCTS'


def play_game(mcts_budget, expand_mcts_tree_once):
    # 创建一个新的游戏板
    board = Board()

    # 初始化 MCTS 根节点
    mcts_tree = MCTSNode(board, move=None, parent=None)

    # 模拟交替走棋，直到游戏结束
    while not board.is_game_over():
        if board.get_player_turn() == 1:
            # 随机玩家的走法
            move = random.choice(board.valid_moves())
            board = board.play(move)
        else:
            # MCTS 玩家使用 expand_mcts_tree_once 并选择最佳移动
            for _ in range(mcts_budget):
                expand_mcts_tree_once(mcts_tree)
            mcts_tree, move = mcts_tree.select_best_move()
            board = board.play(move)

            # 更新 MCTS 树，根节点转到新的游戏状态
            mcts_tree = mcts_tree.get_child_with_move(move) if mcts_tree is not None else MCTSNode(board, move=None,
                                                                                                    parent=None)

    # 返回获胜的玩家
    return board.get_victorious_player()


def test_mcts_vs_random(mcts_budget=40, num_games=10):
    mcts_wins = 0
    random_wins = 0
    draws = 0

    for i in range(num_games):
        result = play_game(mcts_budget, expand_mcts_tree_once)
        if result == 1:
            random_wins += 1
        elif result == 2:
            mcts_wins += 1
        else:
            draws += 1
        print(f"Game {i + 1}: Winner - {'MCTS' if result == 2 else 'Random' if result == 1 else 'Draw'}")

    print("\nFinal Results:")
    print(f"Wins for MCTS agent: {mcts_wins}")
    print(f"Wins for random agent: {random_wins}")
    print(f"Draws: {draws}")
    print(f"Success Rate for MCTS agent: {(mcts_wins / num_games) * 100:.2f}%")

    if mcts_wins >= (0.9 * num_games):
        print("Success!")
    else:
        print("Failure. Consider increasing mcts_budget or improving the MCTS strategy.")


# 测试代码
test_mcts_vs_random(mcts_budget=40, num_games=10)
