from player import Bot
from game import State
import random


class LoggerBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vote_record = {}  # 记录每个玩家投反对票的次数
        self.missions_been_on = {}  # 记录每个玩家参与的任务次数
        self.failed_missions_been_on = {}  # 记录每个玩家参与且任务失败的次数

    def select(self, players, count):
        return [self] + random.sample(self.others(), count - 1)

    def vote(self, team):
        return True

    def sabotage(self):
        return True

    def mission_total_suspect_count(self, team):
        suspect_count = 0
        for player in team:
            if self.vote_record.get(player, 0) > 3:
                suspect_count += 1
        return suspect_count

    def onVoteComplete(self, votes):
        for player, vote in zip(self.game.players, votes):
            if player not in self.vote_record:
                self.vote_record[player] = 0
            if not vote:
                self.vote_record[player] += 1

    def onGameRevealed(self, players, spies):
        self.players = players
        self.spies = spies
        self.vote_record = {player: 0 for player in players}
        self.missions_been_on = {player: 0 for player in players}
        self.failed_missions_been_on = {player: 0 for player in players}

    def onMissionComplete(self, num_sabotages):
        if num_sabotages > 0:
            for player in self.game.team:
                self.failed_missions_been_on[player] += 1
        for player in self.game.team:
            self.missions_been_on[player] += 1

    def onGameComplete(self, win, spies):
        self.log.info(f"Game completed. Resistance {'won' if win else 'lost'}.")
        self.log.info(f"Spies were: {', '.join([str(spy) for spy in spies])}")
        for player in self.players:
            self.log.info(f"Player {player}:")
            self.log.info(f"  Voted down count: {self.vote_record[player]}")
            self.log.info(f"  Missions participated: {self.missions_been_on[player]}")
            self.log.info(f"  Failed missions participated: {self.failed_missions_been_on[player]}")
