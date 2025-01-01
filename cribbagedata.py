import random 
import scoring
import time
import datetime
import sys
import argparse
import re
import os



#initialize the card itself for easy access
class Deck:
    
    def __init__(self):
        self.cards = []
        self.suits = {
            'hearts': {'name': 'hearts', 'symbol': '♥'}, #♥
            'diamonds': {'name': 'diamonds', 'symbol': '♦'}, #♦
            'clubs': {'name': 'clubs', 'symbol': '♣'}, #♣
            'spades': {'name': 'spades', 'symbol': '♠'} #♠


        }
        self.ranks = {
            'A': {'symbol' : 'A', 'value': 1, 'rank': 1}
            ,'2': {'symbol' : '2', 'value': 2, 'rank': 2}
            ,'3': {'symbol' : '3', 'value': 3, 'rank': 3}
            ,'4': {'symbol' : '4', 'value': 4, 'rank': 4}
            ,'5': {'symbol' : '5', 'value': 5, 'rank': 5}
            ,'6': {'symbol' : '6', 'value': 6, 'rank': 6}
            ,'7': {'symbol' : '7', 'value': 7, 'rank': 7}
            ,'8': {'symbol' : '8', 'value': 8, 'rank': 8}
            ,'9': {'symbol' : '9', 'value': 9, 'rank': 9}
            ,'10': {'symbol' : '10', 'value': 10, 'rank': 10}
            ,'J': {'symbol' : 'J', 'value': 10, 'rank': 11}
            ,'Q': {'symbol' : 'Q', 'value': 10, 'rank': 12}
            ,'K': {'symbol' : 'K', 'value': 10, 'rank': 13}
        }

        for suit in self.suits:
            for rank in self.ranks: #double for loop :)
                # self.cards.append(Card(suit,suit_symbol,rank,rank_value))
                self.cards.append(Card(rank=self.ranks[rank], suit=self.suits[suit]))
    
    def shuffle(self):
        random.shuffle(self.cards)
    def draw(self):
        return self.cards.pop()
    def cut(self):
        return self.cards.pop(int(len(self.cards)/2))
    

    def __str__(self):
        deckStr = ""
        for card in self.cards:
            deckStr += str(card) + " "
        return deckStr

class Card:
    def __init__ (self,suit,rank):
        self.suit = suit
        self.rank = rank
        # self.symbol = symbol
        # self.value = value
        self.tupl = (str(rank['symbol']), str(suit))

    def __str__(self):
        return str(self.rank['symbol'] + self.suit['symbol'])
    
    def get_value(self):
        return self.rank['value']
    def get_suit(self):
        return self.suit['name']
    def get_rank(self):
        return self.rank['rank']

#what are we finding out? best card combinations? i dont remember... 
#lets start with coding automated cribbage hands (one at a time)

class CribbageGame:

    MAX_SCORE = 121
    CRIB_SIZE = 4   
    GO_SIZE = 31

    def __init__(self,players,file_path,maximumScore):
        self.players = players
        self.file_path = file_path
        self.maxScore = maximumScore if maximumScore is not None else float('inf')
        # self.dealer = players[0]


    def extractScore(self,line):
        match = re.search(r'T(\d+)S',line)
        return int(match.group(1)) if match else float('inf')

    def insert_sorted_line(self,new_line,finalScore):
        tempFilePath = self.file_path + '.tmp'

        with open(self.file_path, 'r', encoding='utf-8') as input_file, open(tempFilePath, 'w', encoding='utf-8') as output_file:
            inserted = False
            for line in input_file:
                exisiting_score = self.extractScore(line)

                if not inserted and finalScore < exisiting_score:
                    output_file.write(f"T{finalScore}{new_line}\n")
                    inserted = True
                output_file.write(line)
            if not inserted:
                output_file.write(f"T{finalScore}{new_line}\n")
        
        os.replace(tempFilePath,self.file_path)


    def oneRoundTest(self):
        dealer = self.players[0]
        r = CribbageRound(self,dealer)
        r.play()

    def multiRoundTest(self,roundCount):
        roundCount = roundCount
        dealer = self.players[0]
        for round in range(roundCount):

            r = CribbageRound(self,dealer)
            roundOutput = r.play()
            player1score,player2score = self.players[0].getScoreInt(),self.players[1].getScoreInt()
            finalString = f"{roundOutput}&{player1score}/{player2score}"
            # print(f"round {round+1} {roundOutput}&{self.players[0].getScore()}/{self.players[1].getScore()}")
            totalScore = int(player1score + player2score)
            if totalScore <= self.maxScore:
                self.insert_sorted_line(new_line=finalString,finalScore=totalScore)


            pass



class CribbageRound:
    def __init__(self,game,dealer):
        self.deck = Deck()
        self.game = game
        #create two hands for gameplay
        self.hands = {player: [] for player in self.game.players}
        self.table = []
        self.crib = []
        self.starter = None
        self.dealer = dealer
        self.nondealer = [p for p in self.game.players if p!= dealer][0]

        self.testString = ""

    
    
    def __str__(self):
        strings = []
        strings.append(f"\n Crib is... {[str(card) for card in self.crib]}")
        for player,hands in self.hands.items():
            # strings.append(f"Player {player}'s hand : {[str(card) for card in hands]}")
            strings.append(f"scores for player {player} : {player.getScore()}")
        return "\n".join(strings)
    
    
    #shuffle and distrubute cards




    def _deal(self):
        self.deck.shuffle()

        cardsPerPlayer = 6 # to hand, 2 to crib, 4 to play
        
        for _ in range (cardsPerPlayer):
            for p in self.game.players:
                self.hands[p].append(self.deck.draw())

        # print(self.hands)


    def get_table_value(self, startIndex):


        return sum(i['card'].get_value() for i in self.table[startIndex:]) if self.table else 0

    def scoreChecker(self,cardSequence):
        score = 0
        scoreScenarios = [scoring.ExactlyEqualsN(n=15), scoring.ExactlyEqualsN(n=31),
                          scoring.HasPairTripleQuad(),scoring.HasStraight_DuringPlay()]
        for scenario in scoreScenarios:
            s, desc, = scenario.check(cardSequence[:])
            score += s
            # print("Score " + desc) if desc else None
            return score

    def scoreHandChecker(self,cards):
        score = 0
        scoreScenarios = [scoring.CountCombinationsEqualToN(n=15), scoring.HasPairTripleQuad(), 
                          scoring.HasStraight_InHand(), scoring.HasFlush()]
        for scenario in scoreScenarios:
            s, desc = scenario.check(cards[:])
            score += s
            # print(desc) if desc else None
        return score
    def jackChecker(self,cards,starterCard):
        score = 0
        for card in cards:
            if card.get_rank() == 11:
                if card.get_suit() == starterCard.get_suit():
                    score += 1
                    # print(f"score given for having a matching jack {card.get_suit()} and {starterCard.get_suit()}")
        
        return score






    #cut deck and play!
    def play(self):
        #shuffle deck!!!
        self.deck.shuffle()

        #DEAL THE CARDS DUMBASS
        self._deal()

        #take 2 cards to send to crib
        #iterate between both players to choose crib cards (this case 2)
        for p,hand in self.hands.items():
            cards_to_crib = p.selectCribCards(hand)
            self.crib += cards_to_crib
            for card in cards_to_crib:
                self.hands[p].remove(card)
            # print([str(card) for card in cards_to_crib]) #enable this for checking what is in the crib
        

        #cut deck
        self.starter = self.deck.cut()
        self.testString += f"S{self.starter}/"

        # print(f"Starter card is... {self.starter}")

        #print hands of both players

        #score player hands now for testing
        for p in self.game.players:
            p.resetScore()
            score = self.scoreHandChecker(cards = self.hands[p] + [self.starter])
            score += self.jackChecker(cards = self.hands[p], starterCard= self.starter)
            p.increasePoints(score)

            # print(f"{p} points = {score}")



        #begin play!

        #iterate between each player to complete play randomly

        if(self.starter.get_rank() == 11):
            # print(f"point given for jack starter")
            self.dealer.increasePoints(2)
        
        activePlayers = [self.dealer, self.nondealer]
        while sum([len(v) for v in self.hands.values()]):
            startindex = len(self.table)
            while activePlayers:
                for p in activePlayers:
                    
                    # print(f"table contents " )
                    card = p.selectCardsToPlay(hand = self.hands[p], table=self.table[startindex:], 
                                               crib = self.crib)
                    #possible bug, not counting exactly 31... 
                    if card.get_value() + self.get_table_value(startindex) > 31 or card is None:
                        activePlayers.remove(p)
                    else:
                        
                        if self.get_table_value(startindex) > 0:
                            self.testString += ("/")

                        self.table.append({'player':p, 'card':card})
                        self.testString += (f"{p}{card}") # Pikaboo

                        self.hands[p].remove(card)
                        if not self.hands[p]:
                            activePlayers.remove(p)
                        
                        tabelValue = self.get_table_value(startindex)
                        # print("Player %s plays %s for %d" %(str(p), str(card), tabelValue))
                        self.testString += (str(tabelValue)) # Pikaboo

                        score = self.scoreChecker(cardSequence=[move['card'] for move in self.table[startindex:]])


                        if score:
                            playerIndex = self.game.players.index(p)
                            self.game.players[playerIndex].increasePoints(score)

                            self.testString += ("+") # Pikaboo
                        # self.testString += ("/") # Pikaboo

            
            if len(activePlayers) == 0: #gives last player 1 point for being the last player
                playerofLastCard = self.table[-1]['player']
                playerIndex = self.game.players.index(playerofLastCard)

                score = 1
                # print(f"{playerofLastCard} finished the run")
                activePlayers = [p for p in self.game.players if p!= playerofLastCard and self.hands[p]]
                if self.hands[playerofLastCard]:

                    activePlayers += [playerofLastCard]
                if self.get_table_value(startindex) == 31:
                    score += 1
                    self.testString += ("+") # Pikaboo
                
                self.game.players[playerIndex].increasePoints(score)
                self.testString += ("+") # Pikaboo
                
        #crib scoring
        # print (f"crib scoring")
        score = self.scoreHandChecker(cards =(self.crib + [self.starter]))
        if score:
            playerIndex = self.game.players.index(self.dealer)
            self.game.players[playerIndex].increaseCribPoints(score)
        
        self.testString += "%"
        for card in self.crib:
            self.testString += str(card)

        return self.testString
        # print(self)
        

            


class randomPlayer:
    def __init__(self,name):
        self.points = 0
        self.name = name
        self.cribPoints = 0

    def __str__(self):
        return self.name
    def selectCribCards(self,hand):
        return random.sample(hand,2)
    
    def selectCardsToPlay(self,hand,table,crib):
        return random.choice(hand)
    
    def increasePoints(self,points):
        self.points += points
    def getScore(self):
        return str(self.points+self.cribPoints)
        # return f"hand : {self.points}. crib : {self.cribPoints}. total : {self.points + self.cribPoints}."
    def getScoreInt(self):
        return int(self.points + self.cribPoints)
    def increaseCribPoints(self,points):
        self.cribPoints += points
    def resetScore(self):
        self.points = 0
        self.cribPoints = 0


def main():
    # testDeck = Deck()
    # print(testDeck)
    #initalize random players for well... randomness

    begin = time.time()


    player1 = randomPlayer("D")
    player2 = randomPlayer("R")
    players = [player1,player2]
    game = CribbageGame(players=players)
    game.multiRoundTest(100)
    
    end = time.time()

    print(f"total time {end-begin} ")
    # print(game)



    #time for a test of a "endless run" that outputs scores to a file

    #first, create a way to see if the score is worth printing (jared will know)
    #second, create a way to send a 1 line text to a file with all containing information
        #hands present on both players
        #starter card
        #order placed
        #and crib
        #ending with total points
    




if __name__ == '__main__':
    

    parser = argparse.ArgumentParser(description="Runs Cribbage Random Rounds")
    parser.add_argument('num_rounds', nargs="?", help="Number of rounds to play", type=int)
    parser.add_argument('max_value', nargs="?", help="Max score number to insert", type=int)
    parser.add_argument("-c","--clear",action="store_true", help="Clears output file before starting")
    args = parser.parse_args()

    if args.num_rounds is None:
        # while True:
        #     userInput = input("Number of rounds : ")
        #     try:
        #         n = int(userInput)
        #         break
        #     except ValueError:
        #         print(f"Please add a valid integer")
        n = 0
    else:
        n = args.num_rounds

    if args.max_value is None:
        maxSort = float('inf')
    else:
        maxSort = args.max_value
    

    fileName = f"cribbageRoundTester.csv"


    if args.clear:
        open(fileName, 'w').close()

    player1 = randomPlayer("D")
    player2 = randomPlayer("R")
    players = [player1,player2]
    # fileName =
    begin = time.time()

    game = CribbageGame(players=players,file_path=fileName,maximumScore=maxSort)
    game.multiRoundTest(n)
    
    end = time.time()

    print(f"total time {end-begin} ")


    # main()