from player import Bot 
from game import State
import random
import tensorflow as tf
from tensorflow import keras
import numpy as np
import sys,os
from loggerbot import LoggerBot # this assumes our loggerbot was in a file called loggerbot.py

model_filename='loggerbot_classifier.keras'
if os.path.exists("bots"+os.sep+model_filename):
    model_filename="bots"+os.sep+model_filename
model = keras.models.load_model(model_filename)
trw=[w.numpy() for w in model.trainable_weights] # capture all of the weights and biases in the saved model.

class NeuralBot(LoggerBot):
    def calc_player_probabilities_of_being_spy(self):
        probabilities = {}
        vectors = []
        for p in self.game.players:
            # This list comprising the input vector must build in **exactly** the same way as
            # we built data to train our neural network - otherwise the neural network
            # is not bieng used to approximate the same function it's been trained to model.
            # That's why this class inherits from the class LoggerBot- so we can ensure that logic is replicated exactly.
            input_vector = [self.game.turn, self.game.tries, p.index, p.name, self.missions_been_on[p],
                            self.failed_missions_been_on[p]] + self.num_missions_voted_up_with_total_suspect_count[p] + \
                           self.num_missions_voted_down_with_total_suspect_count[p]
            input_vector = input_vector[
                           4:]  # remove the first 4 cosmetic details, as we did when training the neural network
            vectors.append(input_vector)
        vectors = np.stack(vectors, axis=0)
        output_probabilities = model(vectors).numpy()  # run the neural network.  Its output layer was using softmax (and it was trained with cross-entropy 
        # If you are interested, then the following 3 lines of the code currently would work much faster than the above line!  Starting up a tensorflow model is slower than numpy, it seems.
        #x=np.tanh(np.matmul(vectors,trw[0])+trw[1]) # This executes the first layer of the network, but with numpy operations
        #x=np.tanh(np.matmul(x,trw[2])+trw[3]) # This executes the second layer of the network, but with numpy operations
        #output_probabilities=np.matmul(x,trw[4])+trw[5] # This executes the final layer of the network, but with numpy operations
        for i in range(len(self.game.players)):
            probabilities[self.game.players[i]] = output_probabilities[i, 1]  # this [i,1] pulls off the row for player i, and the second column (which corresponds to probability of being a spy; the first column is the probability of being not-spy)
        return probabilities  # This returns a dictionary of {player: spyProbability}
        
    def select(self, players, count):
        # here I'm replicating logic we used in the CountingBot exercise of lab1-challenge3.
        # But instead of using the count as an estimation of how spy-like a player is, instead
        # we'll use the neural network's estimation of the probability.
        spy_probs=self.calc_player_probabilities_of_being_spy()
        sorted_players_by_trustworthiness=[k for k, v in sorted(spy_probs.items(), key=lambda item: item[1])]
        if self in sorted_players_by_trustworthiness[:count]:
            result= sorted_players_by_trustworthiness[:count]
        else:
            result= [self] + sorted_players_by_trustworthiness[:count-1]
        return result

    def vote(self, team): 
        spy_probs=self.calc_player_probabilities_of_being_spy()
        sorted_players_by_trustworthiness=[k for k, v in sorted(spy_probs.items(), key=lambda item: item[1])]
        if not self.spy:
            for x in team:
                if x in sorted_players_by_trustworthiness[-2:]:
                    return False
            return True
        else:
            return True

    def sabotage(self):
        # the logic here is a bit boring and maybe could be improved.
        return True 

    ''' The 3 methods onVoteComplete, onGameRevealed, onMissionComplete
    will inherit their functionality from ancestor.  We want them to do exactly 
    the same as they did when we captured the training data, so that the variables 
    for input to the NN are set correctly.  Hence we don't override these methods
    '''
    
    # This function used to output log data to the log file. 
    # We don't need to log any data any more so let's override that function
    # and make it do nothing...
    def onGameComplete(self, win, spies):
        pass


