import keras

from player import Bot
from game import State
import random
import tensorflow as tf
# from tensorflow import keras  # commented out since 'keras' is imported directly
import numpy as np
import sys, os
from loggerbot import LoggerBot  # Assumes the LoggerBot class is in a file called loggerbot.py

# Model file path
model_filename = 'loggerbot_classifier.keras'
if os.path.exists("bots" + os.sep + model_filename):
    model_filename = "bots" + os.sep + model_filename  # Update the path if the model is located in the "bots" directory

# Load the pre-trained neural network model
model = keras.models.load_model(model_filename)

# Retrieve the model's trainable weights
trw = [w.numpy() for w in model.trainable_weights]


class NeuralBot(LoggerBot):
    def calc_player_probabilities_of_being_spy(self):
        """
        Calculate the probability of each player being a spy
        """
        probabilities = {}  # Dictionary to hold probabilities for each player
        vectors = []  # List to store the input vectors for all players

        # Loop through all players to construct input vectors
        for p in self.game.players:
            # Construct input vector in exactly the same way as during model training
            input_vector = [
                               self.game.turn,  # The current game turn
                               self.game.tries,  # The number of tries so far in the game
                               p.index,  # The player's index
                               p.name,  # The player's name
                               self.missions_been_on[p],  # Number of missions the player has been on
                               self.failed_missions_been_on[p]  # Number of missions the player failed
                           ] + self.num_missions_voted_up_with_total_suspect_count[p] + \
                           self.num_missions_voted_down_with_total_suspect_count[p]

            # Remove the first 4 non-essential fields from the input vector
            input_vector = input_vector[4:]

            # Append the constructed input vector to the list of vectors
            vectors.append(input_vector)

        # Convert the list of vectors into a numpy array
        vectors = np.stack(vectors, axis=0)

        # Use the neural network model to predict spy probabilities
        output_probabilities = model(vectors).numpy()

        # Map the output probabilities to their corresponding players
        for i in range(len(self.game.players)):
            probabilities[self.game.players[i]] = output_probabilities[i, 1]  # The second column is the probability of being a spy

        return probabilities  # Return a dictionary with players as keys and their spy probabilities as values

    def select(self, players, count):
        """
        Select players based on the spy probabilities calculated by the neural network
        """
        spy_probs = self.calc_player_probabilities_of_being_spy()  # Get the spy probabilities
        # Sort players based on their trustworthiness (low spy probability means more trustworthy)
        sorted_players_by_trustworthiness = [k for k, v in sorted(spy_probs.items(), key=lambda item: item[1])]

        # If the current player is in the top 'count' trustworthy players, select the first 'count' players
        if self in sorted_players_by_trustworthiness[:count]:
            result = sorted_players_by_trustworthiness[:count]
        else:
            # Otherwise, include the current player and select the remaining players
            result = [self] + sorted_players_by_trustworthiness[:count - 1]

        return result

    def vote(self, team):
        """
        Decide whether to vote for the team based on the spy probabilities from the neural network
        """
        spy_probs = self.calc_player_probabilities_of_being_spy()  # Get the spy probabilities
        sorted_players_by_trustworthiness = [k for k, v in sorted(spy_probs.items(), key=lambda item: item[1])]

        if not self.spy:
            # If the current player is not a spy, avoid selecting suspicious players for the team
            for x in team:
                if x in sorted_players_by_trustworthiness[-2:]:
                    return False  # Reject the team if it contains suspicious players
            return True  # Approve the team if no suspicious players are included
        else:
            # If the current player is a spy, always vote for the team
            return True

    def sabotage(self):
        """
        Decide whether to sabotage the mission (currently always returns True)
        """
        return True  # You can improve this logic based on the game scenario

    # The following three methods inherit from LoggerBot and keep the same functionality
    def onVoteComplete(self, votes):
        """
        Handle the actions after the voting is completed
        """
        total_suspect_count = self.mission_total_suspect_count(self.game.team)  # Get the total number of suspicious players in the team
        if all(votes):  # If the team is approved
            index = min(total_suspect_count, 5)  # Limit the index to 5 for stability
            for player in self.game.players:
                self.num_missions_voted_up_with_total_suspect_count[player][index] += 1  # Increment vote-up count for each player
        else:  # If the team is rejected
            index = min(total_suspect_count, 5)
            for player in self.game.players:
                self.num_missions_voted_down_with_total_suspect_count[player][index] += 1  # Increment vote-down count for each player

        # Append the updated feature vectors for all players
        for p in self.game.players:
            self.training_feature_vectors[p].append(
                [self.game.turn, self.game.tries, p.index, p.name, self.missions_been_on[p],
                 self.failed_missions_been_on[p]] + self.num_missions_voted_up_with_total_suspect_count[p] +
                self.num_missions_voted_down_with_total_suspect_count[p])

    def onGameRevealed(self, players, spies):
        """
        Initialize the game when it starts
        """
        self.failed_missions_been_on = {}  # Dictionary to track the number of failed missions for each player
        self.missions_been_on = {}  # Dictionary to track the number of missions each player has been on
        self.num_missions_voted_up_with_total_suspect_count = {}  # Dictionary to track the number of missions players voted 'up' on with suspect count
        self.num_missions_voted_down_with_total_suspect_count = {}  # Dictionary to track the number of missions players voted 'down' on with suspect count

        # Initialize all dictionaries for each player in the game
        for player in players:
            self.failed_missions_been_on[player] = 0
            self.missions_been_on[player] = 0
            self.num_missions_voted_up_with_total_suspect_count[player] = [0] * 6  # Initialize with 6 possible values
            self.num_missions_voted_down_with_total_suspect_count[player] = [0] * 6
        self.training_feature_vectors = {}  # Dictionary to store feature vectors for each player
        for p in players:
            self.training_feature_vectors[p] = []  # Initialize empty list for each player's feature vectors

    def onMissionComplete(self, num_sabotages):
        """
        Handle actions when a mission is completed
        """
        # Increment the number of missions each player has been on
        for player in self.game.team:
            self.missions_been_on[player] += 1

        if num_sabotages > 0:  # If there were sabotages, increment the number of failed missions for players on the team
            for player in self.game.team:
                self.failed_missions_been_on[player] += 1

    def onGameComplete(self, win, spies):
        """
        Handle actions when the game is completed
        """
        pass  # No need to output log data, so this method is left empty
