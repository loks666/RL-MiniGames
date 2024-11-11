# Start your answer for this question by pasting your code from the auto-marked question above into here,
# and then extend it to add points 3 and 4 above.
from player import Bot
from game import State
import random
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 仅显示严重错误


class LoggerBot(Bot):
    def __init__(self, game, index, spy):
        super().__init__(game, index, spy)
        self.training_feature_vectors = {}
        self.num_missions_voted_up_with_total_suspect_count = {}
        self.num_missions_voted_down_with_total_suspect_count = {}
        self.missions_been_on = {}
        self.failed_missions_been_on = {}

    def select(self, players, count):
        return [self] + random.sample(self.others(), count - 1)

    def vote(self, team):
        return True

    def sabotage(self):
        return True

    def mission_total_suspect_count(self, team):
        total = 0
        for player in team:
            total += self.failed_missions_been_on[player]
        return total

    def onVoteComplete(self, votes):
        total_suspect_count = self.mission_total_suspect_count(self.game.team)
        if all(votes):  # If the mission is voted up
            index = min(total_suspect_count, 5)
            for player in self.game.players:
                self.num_missions_voted_up_with_total_suspect_count[player][index] += 1
        else:  # If the mission is voted down
            index = min(total_suspect_count, 5)
            for player in self.game.players:
                self.num_missions_voted_down_with_total_suspect_count[player][index] += 1
        for p in self.game.players:
            self.training_feature_vectors[p].append(
                [self.game.turn, self.game.tries, p.index, p.name, self.missions_been_on[p],
                 self.failed_missions_been_on[p]] + self.num_missions_voted_up_with_total_suspect_count[p] +
                self.num_missions_voted_down_with_total_suspect_count[p])

    def onGameRevealed(self, players, spies):
        """Initialize tracking dictionaries."""
        self.failed_missions_been_on = {}
        self.missions_been_on = {}
        self.num_missions_voted_up_with_total_suspect_count = {}
        self.num_missions_voted_down_with_total_suspect_count = {}

        for player in players:
            self.failed_missions_been_on[player] = 0
            self.missions_been_on[player] = 0
            self.num_missions_voted_up_with_total_suspect_count[player] = [0] * 6
            self.num_missions_voted_down_with_total_suspect_count[player] = [0] * 6
        self.training_feature_vectors = {}
        for p in players:
            self.training_feature_vectors[
                p] = []  # This is going to be a list of length-14 feature vectors for each player.

    def onMissionComplete(self, num_sabotages):
        for player in self.game.team:
            self.missions_been_on[player] += 1

        if num_sabotages > 0:
            for player in self.game.team:
                self.failed_missions_been_on[player] += 1

    def onGameComplete(self, win, spies):
        pass