from player import Bot
from game import State
import random


class LoggerBot(Bot):
    # Loggerbot makes very simple playing strategy.
    # We're not really trying to win here, but just to observe the other players
    # without disturbing them too much....
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
        """Callback once the whole team has voted.
        @param votes        Boolean votes for each player (ordered).
        """
        pass  # TODO complete this in Challenge 1b

    def onGameRevealed(self, players, spies):
        """This function will be called to list all the players, and if you're
        a spy, the spies too -- including others and yourself.
        @param players  List of all players in the game including you.
        @param spies    List of players that are spies, or an empty list.
        """
        self.failed_missions_been_on = {}
        self.missions_been_on = {}
        for player in players:
            self.failed_missions_been_on[player] = 0
            self.missions_been_on[player] = 0

    def onMissionComplete(self, num_sabotages):
        """Callback once the players have been chosen.
        @param num_sabotages    Integer how many times the mission was sabotaged.
        """
        for player in self.game.team:
            self.missions_been_on[player] += 1

        if num_sabotages > 0:
            for player in self.game.team:
                self.failed_missions_been_on[player] += 1

    def onGameComplete(self, win, spies):
        """Callback once the game is complete, and everything is revealed.
        @param win          Boolean true if the Resistance won.
        @param spies        List of only the spies in the game.
        """
        pass  # TODO complete this function in Challenge 2