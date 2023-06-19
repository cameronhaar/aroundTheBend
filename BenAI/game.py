import random
import numpy as np
import pygame


pygame.init()


class AroundTheBendGame:

    def __init__(self):
        self.score = 0
        self.aroundTheBendPoints = 0
        self.tempScore = 0
        self.turns = 100
        self.currentRoll = self.getRoll(6)
        self.diTaken = False
        self.needReroll = False
        self.lastAction = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.reset()

    def reset(self):
        self.score = 0
        self.aroundTheBendPoints = 0
        self.tempScore = 0
        self.turns = 100
        self.currentRoll = self.getRoll(6)
        self.lastAction = [0,0,0,0,0,0,0,0,0]
        self.diTaken = False
        self.needReroll = False


    # returns a roll of the specified number of dice
    def getRoll(self, numDice):
        if numDice > 6 or 1 > numDice:
            print("number of dice rolled is out of range")
            return
        roll = []
        for x in range(numDice):
            roll.append(random.randint(1, 6))
        return roll

    # check if there are any possible moves
    def checkForPossibleMoves(self):
        if 1 in self.currentRoll:
            return True
        elif 5 in self.currentRoll:
            return True
        elif (np.array(self.currentRoll) == 2).sum() >= 3:
            return True
        elif (np.array(self.currentRoll) == 3).sum() >= 3:
            return True
        elif (np.array(self.currentRoll) == 4).sum() >= 3:
            return True
        elif (np.array(self.currentRoll) == 6).sum() >= 3:
            return True
        else:
            return False

    # check for high value moves
    def checkForHighValueMoves(self):
        if (np.array(self.currentRoll) == 5).sum() >= 3:
            return True
        elif (np.array(self.currentRoll) == 3).sum() >= 3:
            return True
        elif (np.array(self.currentRoll) == 4).sum() >= 3:
            return True
        elif (np.array(self.currentRoll) == 6).sum() >= 3:
            return True
        else:
            return False

    def checkForAroundTheBend(self):
        sum = (np.array(self.currentRoll) == 1).sum()
        sum = sum + (np.array(self.currentRoll) == 5).sum()
        if (np.array(self.currentRoll) == 2).sum() >= 3:
            sum = sum+3
        elif (np.array(self.currentRoll) == 3).sum() >= 3:
            sum = sum+3
        elif (np.array(self.currentRoll) == 4).sum() >= 3:
            sum = sum+3
        elif (np.array(self.currentRoll) == 6).sum() >= 3:
            sum = sum+3
        if(sum == len(self.currentRoll)):
            return True
        return False


    def printCurrentStateAndMove(self, action):
        move = ""
        if action[0]:
            move = "1"
        elif action[1]:
            move = "5"
        elif action[2]:
            move = "222"
        elif action[3]:
            move = "333"
        elif action[4]:
            move = "444"
        elif action[5]:
            move = "555"
        elif action[6]:
            move = "666"
        elif action[7]:
            move = "RR"
        elif action[8]:
            move = "Keep"
        print("Your dice were: " + str(self.currentRoll) + " and your game state was: DiTaken: " + str(self.diTaken) + " Temp pts: " + str(
            self.tempScore) + " totalScore: " + str(self.score) + " the action made was: " + move)

    def moveReroll(self):
        reward = 0
        if not self.diTaken:
            reward = reward - 10
        else:
            if self.checkForHighValueMoves() or self.checkForAroundTheBend():
                reward = reward - 10
            # else:
            #     reward = reward + 2
            self.currentRoll = self.getRoll(len(self.currentRoll))
            self.diTaken = False
        return reward

    def moveKeepScore(self):
        reward = 0
        if not self.diTaken:
            reward = reward - 15
        else:
            # attempt to reward more points for keeping hire scores
            if self.tempScore <= 150:
                reward = reward - 30
            elif self.tempScore > 500:
                reward = reward + 20
            else:
                reward = reward + 5
            if self.checkForPossibleMoves():
                reward = reward - 30
            else:
                reward = reward + 10
            # setup Next turn and end this one
            self.score = self.score + self.aroundTheBendPoints + self.tempScore
            self.aroundTheBendPoints = 0
            self.tempScore = 0
            self.currentRoll = self.getRoll(6)
            self.diTaken = False
            self.needReroll = False
            self.turns = self.turns - 1
        return reward

    def takeDi(self, action):
        reward = 0
        newRoll = self.currentRoll.copy()
        # check if the right number of di are in the roll and remove them
        numberOfDice = self.getNumberOfDice(action)
        di = self.getDi(action)
        for x in range(numberOfDice):
            if di in newRoll:
                newRoll.remove(di)
            else:
                # print("there is/are not " + str(numberOfDice) + " " + str(di) + " in your roll: " + str(self.currentRoll))
                reward = -20
                print("insufficient di")
                return reward

        # score based on the given di taken
        OneTimescore = -1
        if di == 1:
            OneTimescore = numberOfDice * 100
            reward = reward + 1000
        elif di == 5:
            if numberOfDice == 3:
                OneTimescore = di * 100
                reward = reward + 20
            else:
                OneTimescore = numberOfDice * 50
                reward = reward + 5
        else:
            if numberOfDice == 3:
                OneTimescore = di * 100
                reward = reward + 20
            else:
                # print("Invalid Move")
                reward = reward - 10
                return reward
        self.tempScore = self.tempScore + OneTimescore
        self.diTaken = True
        if len(newRoll) == 0:
            self.aroundTheBendPoints = self.tempScore
            self.tempScore = 0
            reward = reward + 30
            self.needReroll = True
        self.currentRoll = newRoll.copy()
        return reward

    def play_step(self, action):

        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        reward = 0
        # 2. check if game over
        game_over = False
        if self.score >= 5000 :
            game_over = True
            reward = 25 - (100 - self.turns)
            return reward, game_over, self.turns

        # Check if reset is needed, this could either be inital roll is needed or no moves are possible and turn is over
        if self.needReroll:
            self.currentRoll = self.getRoll(6)
            self.diTaken = False
            self.needReroll = False

        if not self.checkForPossibleMoves() and not self.diTaken:
            self.needReroll = True
            self.turns = self.turns - 1
            self.score = self.score + self.aroundTheBendPoints
            self.tempScore = 0
            self.aroundTheBendPoints = 0
            self.diTaken = False
            return reward, game_over, self.turns

        # 3. check if they want to REROLL
        if action[7] == 1:
            reward = reward + self.moveReroll()

        # 4. check if they want to KEEP SCORE
        elif action[8] == 1:
            reward = reward + self.moveKeepScore()


        # 5. They must be taking di
        else:
            reward =  reward + self.takeDi(action)
        return reward, game_over, self.turns

    def getNumberOfDice(self, action):
        if action[0] == 1:
            return 1
        elif action[1] == 1:
            return 1
        elif action[2] == 1:
            return 3
        elif action[3] == 1:
            return 3
        elif action[4] == 1:
            return 3
        elif action[5] == 1:
            return 3
        elif action[6] == 1:
            return 3


    def getDi(self, action):
        if action[0] == 1:
            return 1
        elif action[1] == 1:
            return 5
        elif action[2] == 1:
            return 2
        elif action[3] == 1:
            return 3
        elif action[4] == 1:
            return 4
        elif action[5] == 1:
            return 5
        elif action[6] == 1:
            return 6
