import itertools
import math
import os
import random

import keras
import numpy as np

from loggerbot import LoggerBot

model_filename = 'loggerbot_classifier.keras'
model = keras.models.load_model(model_filename)
if os.path.exists("bots" + os.sep + model_filename):
    model_filename = "bots" + os.sep + model_filename
model = keras.models.load_model(model_filename)
trw = [w.numpy() for w in model.trainable_weights]


class NeuralBot(LoggerBot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.spies = getattr(self.game, 'spies', [])

    def calc_player_probabilities_of_being_spy(self):
        probabilities = {}
        vectors = []
        for p in self.game.players:
            input_vector = [self.game.turn, self.game.tries, p.index, p.name, self.missions_been_on[p],
                            self.failed_missions_been_on[p]] + self.num_missions_voted_up_with_total_suspect_count[p] + \
                           self.num_missions_voted_down_with_total_suspect_count[p]
            input_vector = input_vector[4:]
            vectors.append(input_vector)
        vectors = np.stack(vectors, axis=0)
        output_probabilities = model(vectors).numpy()
        for i in range(len(self.game.players)):
            probabilities[self.game.players[i]] = output_probabilities[i, 1]
        return probabilities

    @staticmethod
    def evaluate_state(state, is_spy):
        if state.wins >= 3:
            return 1 if not is_spy else -1
        elif state.losses >= 3:
            return -1 if not is_spy else 1
        score = 0
        for player in state.players:
            score += player.spy_probability if is_spy else -player.spy_probability
        return score

    def minimax(self, state, depth, maximizing_player, is_spy):
        if depth == 0 or state:
            return self.evaluate_state(state, is_spy)

        if maximizing_player:
            max_eval = float('-inf')
            for child_state in self.get_possible_states(state):
                eval = self.minimax(child_state, depth - 1, False, is_spy)
                max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = float('inf')
            for child_state in self.get_possible_states(state):
                eval = self.minimax(child_state, depth - 1, True, is_spy)
                min_eval = min(min_eval, eval)
            return min_eval

    def mcts(self, root, iterations=100):
        for _ in range(iterations):
            node = root
            while node.children:
                node = node.select()
            if not node.state:
                node = node.expand()
            result = node.simulate()
            node.backpropagate(result)
        return max(root.children, key=lambda child: child.visits)

    def select(self, players, count):
        spy_probs = self.calc_player_probabilities_of_being_spy()
        sorted_players_by_trustworthiness = [k for k, v in sorted(spy_probs.items(), key=lambda item: item[1])]

        root = MCTSNode(self.game, bot=self)
        best_node = self.mcts(root, iterations=100)

        if self in sorted_players_by_trustworthiness[:count]:
            result = sorted_players_by_trustworthiness[:count]
        else:
            result = [self] + sorted_players_by_trustworthiness[:count - 1]

        self.log.info(f"Selecting team: {result}, Spy probabilities: {spy_probs}")
        return result

    def vote(self, team):
        spy_probs = self.calc_player_probabilities_of_being_spy()
        sorted_players_by_trustworthiness = [k for k, v in sorted(spy_probs.items(), key=lambda item: item[1])]

        if not self.spy:
            if self.game.turn >= 4 or self.game.tries == 5:
                for x in team:
                    if x in sorted_players_by_trustworthiness[-2:]:
                        return False
            return True
        else:
            return True

    def sabotage(self):
        if self.game.turn >= 4 and self.game.losses == 2:
            return True
        if len([p for p in self.game.team if p in self.spies]) == 1:
            return False
        return True

    def onGameComplete(self, win, spies):
        pass

    def get_possible_states(self, state):
        possible_states = []
        # 使用传入的 state 对象，而不是 self.game
        for team in itertools.combinations(state.players, state.participants[state.turn - 1]):
            new_state = state.clone()
            new_state.team = set(team)
            possible_states.append(new_state)
        return possible_states


class MCTSNode:
    def __init__(self, state, parent=None, bot=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.wins = 0
        self.bot = bot  # 引入 bot 对象以便访问 get_possible_states

    def get_possible_states(self, state):
        return self.bot.get_possible_states(state)  # 使用 bot 的 get_possible_states 方法

    def ucb1(self):
        if self.visits == 0:
            return float('inf')
        return self.wins / self.visits + math.sqrt(2 * math.log(self.parent.visits) / self.visits)

    def select(self):
        return max(self.children, key=lambda child: child.ucb1())

    def expand(self):
        new_state = self.state.clone()
        new_child = MCTSNode(new_state, parent=self, bot=self.bot)
        self.children.append(new_child)
        return new_child

    def simulate(self):
        simulated_state = self.state.clone()
        while not simulated_state:
            possible_states = self.get_possible_states(simulated_state)
            simulated_state = random.choice(possible_states)
        return 1 if simulated_state else 0

    def backpropagate(self, result):
        self.visits += 1
        self.wins += result
        if self.parent:
            self.parent.backpropagate(result)
