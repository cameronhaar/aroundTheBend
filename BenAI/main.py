from game import AroundTheBendGame
from collections import deque
import random
import numpy as np
import torch as torch
from helper import plot
from model import Linear_QNet, QTrainer

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001
# Press the green button in the gutter to run the script.
class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0  # randomness
        self.gamma = 0.9  # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)  # popleft()
        self.model = Linear_QNet(11, 256, 9)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game):

        state = [
            # current die sumsin roll
            (np.array(game.currentRoll) == 1).sum() >= 1,
            (np.array(game.currentRoll) == 5).sum() >= 1,
            (np.array(game.currentRoll) == 2).sum() >= 3,
            (np.array(game.currentRoll) == 3).sum() >= 3,
            (np.array(game.currentRoll) == 4).sum() >= 3,
            (np.array(game.currentRoll) == 5).sum() >= 3,
            (np.array(game.currentRoll) == 6).sum() >= 3,
            # num dice left
            len(game.currentRoll),
            # current points
            game.tempScore,
            int(game.diTaken),
            game.turns
        ]
        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))  # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)  # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.n_games
        final_move = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0,8)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        return final_move


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = AroundTheBendGame()
    while True:
        # get old state
        state_old = agent.get_state(game)

        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, done, score = game.play_step(final_move)
        print(str(reward) )
        state_new = agent.get_state(game)

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # train long memory, plot result
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

# used to play the game yourself
def IWannaPlay():
    game = AroundTheBendGame()
    while True:
        myInput = input("Your current dice are: " + str(game.currentRoll) + " What move would you like to make? (Enter number between 0 and 8, type HELP for move explanations)")
        if not myInput.isnumeric() or (int(myInput) > 8 or int(myInput) < 0):
            continue
        finalMove = [0,0,0,0,0,0,0,0,0]
        if myInput == "0":
            finalMove[0] = 1
        elif myInput == "1":
            finalMove[1] = 1
        elif myInput == "2":
            finalMove[2] = 1
        elif myInput == "3":
            finalMove[3] = 1
        elif myInput == "4":
            finalMove[4] = 1
        elif myInput == "5":
            finalMove[5] = 1
        elif myInput == "6":
            finalMove[6] = 1
        elif myInput == "7":
            finalMove[7] = 1
        elif myInput == "8":
            finalMove[8] = 1
        elif myInput == "HELP":
            print("Moves: \n"
                  "'0' = Take a 1 from set of die for 100pts\n"
                  "'1' = Take a 5 from set of die for 50pts\n"
                  "'2' = Take three 2s from set of die for 200pts\n"
                  "'3' = Take three 3s from set of die for 300pts\n"
                  "'4' = Take three 4s from set of die for 400pts\n"
                  "'5' = Take three 5s from set of die for 500pts\n"
                  "'6' = Take three 6s from set of die for 600pts\n"
                  "'7' = If you have already taken at least 1 die from your current roll, you may reroll the "
                  "remaining dice for a chance at more points\n"
                  "'8' = Keep your current hand of points and end your turn\n")
            continue
        reward, gameState, score = game.play_step(finalMove)
        print("Reward: " + str(reward) + " This turn score: " + str(game.tempScore) + " Game Score: " + str(game.score) + " Turns: " + str(100 - game.turns))


if __name__ == '__main__':
    # train()
    IWannaPlay()

