import random
import math

class Game: #rules of the game
        #players
        #current_state
        #starting_state  - do I define that here or pass it to play?

    def __init__(self, params): #private
        self.starting_state = params['starting state']
        self.players = params['players'] #use a dictionary
        self.playernumbers = self.players.keys()#could call this whenever

    def getplayer(self, playernum): #private
        return self.players[playernum]
    
    def allowed_moves(self, state, playernum): #public - if you're not allowed to see opponents allowed moves, pass an incomplete state
        #could pass this info to player or just to check legal moves
        #(does it need player arg, since state should include which player to move?)
        return []
    
    def move(self, state, player, move): #public
        #return the resulting state, does not change current state
        #(does it need player arg, since state should include which player to move?)
        #how to represent a move? could be int position on list of allowed moves, or other form specific to game
        #check if move in allowed_moves(state)? not necessary if move is an index on allowed_moves list
        return state

    def outcome(self, state): #public
        #None if game is not finished, or list of each player's score
        #calling this should not affect the state since ai will use it
        return None

    def display(self, state): #public
        #show the gamestate
        return
        
    def visible_info(self, state, playernum): #private
        #show that player whatever they can see about the game state
        return state #that will work for complete information games
        #for incomplete info games - return an altered gamestate. that way it always returns a gamestate
    
    def play(self): #private. don't need players and starting state param here if set in init
        current_state = self.starting_state
        #try:
        while self.outcome(current_state) is None:
            current_player_num = current_state.current_player_num
            current_player = self.getplayer(current_player_num)
            chosen_move = None
            legal_moves = self.allowed_moves(current_state, current_player_num)
            while chosen_move not in legal_moves:
                chosen_move = current_player.pick_move(self, self.visible_info(current_state, current_player_num))
            current_state = self.move(current_state, current_player_num, chosen_move)
        self.display(current_state) #show the ending state - do I ever not want to do that?
        return self.outcome(current_state) #could call this one less time if we remembered value from the while condition
        # except Exception:
        #     print("error at state: ")
        #     self.display(current_state)

    #the other player's number, for 2-player only. 1->2, 2->1
    def otherplayer(self, playernum):
        return 1 if playernum == 2 else 2

#current state of the game
class Gamestate: 
    def __init__(self, current_player_num):
        self.current_player_num = current_player_num
    def copy(self):
        return
    #current_player

class Player:
    def __init__(self, params):
        self.mynumber = params['number']
        self.showmoves = params['show moves'] if 'show moves' in params else True
    def pick_move(self, game, state): #should this pass allowed moves list too?
        return game.allowed_moves(state, self.mynumber)[0] #default

#____general player implementations_____
                                 
class HumanPlayer(Player):
    def move(self, game, state):
        display(state)
##      display allowed moves
##      prompt for which move
##      return that move
    def display(self, state):
        #show the game state however a human player likes it
        return

class RandomPlayer(Player):
    def pick_move(self, game, state):
        return random.choice(game.allowed_moves(state, self.mynumber))

class MinMaxSearchPlayer(Player):
    def __init__(self, params):
        super().__init__(params)
        self.maxdepth = params['max depth'] if 'max depth' in params else 0
        self.memorized_states = {} #key = state, value = (value of the state, best move)
        self.debug = params['debug'] if 'debug' in params else False
        
    def pick_move(self, game, state):
        if self.showmoves:
            game.display(state)
        return self.evaluate(game, state, self.maxdepth)['best move']

    def represent_state(self, game, state):
        #represent state so that states equivalent in the game are the same even if different gamestate objects, but states not equivlent in the game are different
        return state

    def heuristic(self, game, state):
        #approximate value of the state when we don't want to think ahead
        return 0
    
    def evaluate(self, game, state, depth):
        representation = self.represent_state(game, state)
        if self.debug: print ('evaluating state: ' + str(representation) + " at depth " + str(depth))
        if representation in self.memorized_states and self.memorized_states[representation]['good to depth'] >= depth: #so it can evaluate again. but what if entry is None?
            if self.debug: print('returned from memorized states: '+str(self.memorized_states[representation]))
            return self.memorized_states[representation]
        else:
            self.memorized_states[representation] = None #to prevent looping, put it in memorized states. when value is none, that should not be considered as an option.
            outcome = game.outcome(state)
            value, bestmove, goodtodepth = None, None, None
            if outcome is not None:
                if self.debug: print("reached end of game with outcome "+str(outcome))
                value, bestmove, goodtodepth = outcome[self.mynumber], None, float('Inf')
            elif depth == 0:
                value, bestmove, goodtodepth = self.heuristic(game, state), None, depth # not sure what move, do a random one?
                if self.debug: print("reached depth 0, evaluated heuristic as "+str(value))
            else:
                if self.debug: print('considering different moves')
                #minmax - I will do best move for me, opponents will do move worst for me.
                #or maybe opponent will do move which is best for them. but then we would have to evaluate from their perspective too. only matters for non zero-sum
                current = state.current_player_num
                allowed = game.allowed_moves(state, current)
                resulting_values = {}
                for choice in allowed:
                    resulting_state = game.move(state, current, choice)
                    evaluation = self.evaluate(game, resulting_state, depth-1) #will have value, best move, good to depth
                    if evaluation is not None: #None means don't consider that as move, for example to avoid loops or illegal state we missed
                        resulting_values[choice]=evaluation
                if self.debug: print('resulting_values = '+str(resulting_values))
                if (current == self.mynumber):
                    #value = max([d['value'] for d in resulting_values.values()] #this way doesn't use bestmove
                    bestmove = max(resulting_values.keys(), key = lambda x: resulting_values[x]['value'])
                    value = resulting_values[bestmove]['value']
                else:
                    value = min([d['value'] for d in resulting_values.values()])
                    #what is bestmove? probably doesn't matter when it isn't our turn
                #good to what depth? recursively, min depth resulting states are good to. equivalently - inf if all are inf, otherwise depth
                #could make more sophisticated eg if one state has a winning move, it's winning to any depth without considering other options
                goodtodepth = min([resulting_values[choice]['good to depth'] for choice in allowed])+1
            result = {'value': value, 'best move': bestmove, 'good to depth': goodtodepth}
            self.memorized_states[representation] = result
            if self.debug: print ('evaluated state: ' + str(representation) + ' at depth ' + str(depth)+': returning '+str(result))
            return result
    
#___tic tac toe classes_____

#copy array of arrays by value, assuming values in sub-array are value types
def gridofvaluescopy(board):
    return [row.copy() for row in board]

#and if those are objects which also need copying, double pass through
def gridofobjectscopy(board):
    return [[item.copy() for item in row] for row in board]

class tictactoeState(Gamestate):
    def __init__(self, board, current_player_num):
        self.board=board
        self.current_player_num = current_player_num
    def copy(self):
        #copied_board = [self.board[0].copy(),self.board[1].copy(),self.board[2].copy()] #to make sure nothing is linked
        copied_board = gridofvaluescopy(self.board)
        return tictactoeState(copied_board, self.current_player_num)

class tictactoeGame(Game):
    #def __init__(self, state, players): default is just to set state and players, and scores all zero
    #starting_state = [[0,0,0],[0,0,0],[0,0,0]] - 0 if not taken, put in each player's number in that spot when taken
    def allowed_moves(self, state, playernum): #take (a,b) pairs as a move - then we have to verify it's allowed
        return [(a,b) for a in [1,2,3] for b in [1,2,3] if state.board[a-1][b-1]== 0]

    def move(self, state, playernum, choice):  
        #new gamestate resulting from that move, without changing the old one - that's useful for ai
        new_state = state.copy()
        if choice in self.allowed_moves(state, playernum):
            new_state.board[choice[0]-1][choice[1]-1] = playernum
            new_state.current_player_num = (2 if playernum == 1 else 1) #would need different logic if more players or repeat turns
        return new_state

    def rows(self, state):
        board = state.board
        return [[board[0][0],board[0][1],board[0][2]],
        [board[1][0],board[1][1],board[1][2]],
        [board[2][0],board[2][1],board[2][2]],
        [board[0][0],board[1][0],board[2][0]],
        [board[0][1],board[1][1],board[2][1]],
        [board[0][2],board[1][2],board[2][2]],
        [board[0][0],board[1][1],board[2][2]],
        [board[0][2],board[1][1],board[2][0]]]

    def outcome(self, state):
        #three in a row wins
        for row in self.rows(state):
            if ((row[0] != 0) and (row[0] == row[1] == row[2])):
                winner = row[0]
                #return [(1 if playernum == winner else -1) for playernum in self.playernumbers] #should game have a list of valid player nums?
                return {p:(1 if p == winner else -1) for p in self.playernumbers}
        #no more moves - tie
        space_remaining = False
        for row in self.rows(state):
            if 0 in row:
                space_remaining = True
        if not space_remaining:
            return {p:0 for p in self.playernumbers}
        return None
                
    #def visible_info(self, state, player): default is to return state

    #put this it in game so we can show the game. or could just leave it in human player
    def display(self, state):
        board = state.board
        print(str(board[0][0]) + " " + str(board[0][1]) + " " +str(board[0][2]) +"\n"
            + str(board[1][0]) + " " + str(board[1][1]) + " " +str(board[1][2]) +"\n"
            + str(board[2][0]) + " " + str(board[2][1]) + " " +str(board[2][2]) +"\n"
            + self.status_string(state))#"player "+str(state.current_player_num)+" to move\n")

    def status_string(self,state):
        outcome = self.outcome(state)
        if outcome is None:
            return "player "+str(state.current_player_num)+" to move\n"
        return "game over. scores: "+str(outcome)

    #def play(self): default is to loop while not finished, ask again if the move was illegal

class tictactoeHumanPlayer(HumanPlayer):
    def pick_move(self, game, state):
        game.display(state)
        allowed = ['1','2','3']
        a,b = None, None
        while (a not in allowed or b not in allowed):
            try:
                print ("enter your move as 2 digits from 1-3, for example 31")
                a,b = input()
            except:
                continue
        return (int(a), int(b))

class MinMaxTicTacToePlayer(MinMaxSearchPlayer):
    def represent_state(self, game, state):
        return (state.current_player_num, tuple(state.board[0]), tuple(state.board[1]), tuple(state.board[2])) #tuple can be a key, but not list
    def heuristic(self, game, state):
        #number of two in a rows I have
        mytwos = [r for r in game.rows(state) if
                  ( (r[0] == r[1] == self.mynumber) or (r[0] == r[2] == self.mynumber) or (r[1] == r[2] == self.mynumber))]
        #print('heuristic: ' + str(len(mytwos)) + ' 2 in a row for state '+str(self.represent_state(game,state)))
        return len(mytwos)/5

#finger game
class fingergameState(Gamestate):

    def __init__(self, hands, current_player_num):
        self.hands=hands
        self.current_player_num = current_player_num

    def copy(self):
        #copied_board = [self.board[0].copy(),self.board[1].copy(),self.board[2].copy()] #to make sure nothing is linked
        copied_board = gridofvaluescopy(self.board)
        return fingergameState(copied_board, self.current_player_num)

    def hand_is_empty(self, playernum, handnum):
        return self.hands[playernum][handnum] == 0

    # return the player's hand number which is empty, or None if the player has no empty hand
    # index will start for 1 so can do "if player_empty_hand(num)" to see if None
    def player_empty_hand(self, playernum):
        #return 0 in self.hands[playernum].values()
        hands = self.hands[playernum]
        for handnum in hands:
            if hands[handnum] == 0:
                return handnum
        return None

    #players not elminated from the game yet: have some nonzero hands
    def remaining_players(self):
        remaining_nums = []
        #the hand of all zero for whatever length - is there a simpler dictionary constructor?
        all_zeros_hands = {}
        hands_per_player = len(self.hands[1]) #this is a param in FingerGame - share from there?
        for i in range(1, 1+hands_per_player):
            all_zeros_hands[i]=0
        for player in self.hands:
            if self.hands[player] != all_zeros_hands:
                remaining_nums.append(player)
        return remaining_nums

    def remaining_players_alt(self):
        remaining_nums = []
        #the hand of all zero for whatever length - is there a simpler dictionary constructor?
        for player in self.hands:
            for hand_num in self.hands[player]:
                if self.hands[player][hand_num] != 0:
                    remaining_nums.append(player)
                    break #continue the outer loop on first nonzero - don't keep looking at the other hands of that player
                #remaining_nums.append(player)
        return remaining_nums


class FingerGame(Game): #for now assume 2 players

    def __init__(self, params):
        super().__init__(params)
        self.handsperplayer = params['hands per player'] if 'hands per player' in params else 2
        self.outnumber = parmas['out number'] if 'out number' in params else 6
        #self.numplayers = 2 #could make a param

    def allowed_moves(self, state, playernum): #public - if you're not allowed to see opponents allowed moves, pass an incomplete state
        #could pass this info to player or just to check legal moves
        #(does it need player arg, since state should include which player to move?)
        hand_nums = range(1, self.handsperplayer+1)
        #add own nonzero hand to opponent's nonzero hand
        valid_adds = [("hit", otherplayer, myhand, opponentshand)
                for otherplayer in self.players for myhand in hand_nums for opponentshand in hand_nums
                if otherplayer != playernum #no hitting own hand
                and not state.hand_is_empty(otherplayer, opponentshand) #no hitting opponents empty hand
                and not state.hand_is_empty(playernum, myhand)] #no hitting with own empty hand
        #split own nonzero, even hand in half. needs another open space
        valid_splits = [('split', handnum) for handnum in range(1, self.handsperplayer+1)
                        if not state.hand_is_empty(playernum, handnum)
                        and state.hands[playernum][handnum] %2 == 0
                        and state.player_empty_hand(playernum)]
        return valid_adds + valid_splits

    # hit - add the number from your hand to opponents hand. if over limit, it goes to 0.
    # split - put half your even, nonempty hand into your other empty hand
    # then it is the next player's turn - no repeat moves
    def move(self, state, player, move): #public
        next_state = state.copy()
        if move[0] == "hit":
            hit, otherplayer, myhand, opponentshand = move
            new_value = next_state.hands[otherplayer][opponentshand] + next_state.hands[player][myhand]
            if new_value >= self.outnumber:
                new_value = 0
            next_state.hands[otherplayer][opponentshand] = new_value
        elif move[0] == "split":
            split, handnum = move
            open_hand = next_state.player_empty_hand(player)
            half_val = next_state.hands[player][handnum] / 2
            next_state.hands[player][handnum] = half_val
            next_state.hands[player][open_hand] = half_val
        return next_state

    #if all but one player has all 0: that player gets +1, others get -1
    #make a tie for looped games? -> tie by repetition count or something -> need to use the whole history?
    #else None - not finished yet
    def outcome(self, state):
        remaining = state.remaining_players()
        if len(remaining) > 1:
            return None
        elif len(remaining) == 1:
            scores = {}
            for playernum in self.playernumbers:
                if playernum in remaining:
                    scores[playernum] = +1
                else:
                    scores[playernum] = -1
            return scores
        else:
            #should not get 0 or negative
            raise Exception("error - 0 or negative players remaining")

    def display(self, state):
        #show the gamestate:
        #     hand 1   hand 2     ...hand k
        #p1   1         1           1
        #p2   1         2           3
        #...
        #pn   0         4           2

        #but usually just 2 players?

        #print the top line

        # or crude version: just list the hands.
        print(state)

    
class fingergameHumanPlayer(HumanPlayer):
    def pick_move(self, game, state):
        return

class MinMaxFingerGamePlayer(MinMaxSearchPlayer):
    def represent_state(self, game, state):
        return (state.current_player_num, tuple(state.board[0]), tuple(state.board[1]), tuple(state.board[2])) #tuple can be a key, but not list
    def heuristic(self, game, state):
        return 0 #that is the default

#mancala game

#board structure:
#+---+---+---+---+---+---+---+---+
#|   | 1 | 2 | 3 | 4 | 5 | 6 |   |
#| 0 |---+---+---+---+---+---| 0 |
#|   | 6 | 5 | 4 | 3 | 2 | 1 |   |
#+---+---+---+---+---+---+---+---+
#
#represent as [row1,row2] where each row has index 0-6, 0 is the store

class mancalaState(Gamestate):
    def __init__(self, board, current_player_num):
        self.board=board #board is a 2d array of integers
        self.current_player_num = current_player_num
    def copy(self):
        copied_board = gridofvaluescopy(self.board)
        return mancalaState(copied_board, self.current_player_num)

class mancalaGame(Game): #for now assume 2 players
    def __init__(self, params):
        super().__init__(params) #default params - starting state, players

    #moves - number from 1 to 6 indicating which of your piles you pick up - only from own side and not the store
    def allowed_moves(self, state, playernum): #public - if you're not allowed to see opponents allowed moves, pass an incomplete state. does it need playernum arg?
        return [n for n in range(1,7) if state.board[playernum-1][n] > 0] 
      
    def move(self, state, player, move): #move is an integer 1-6
        if move in self.allowed_moves(state, player):
            newstate = state.copy()
            numstones = state.board[player-1][move]
            currentside = player
            currentindex = move
            newstate.board[player-1][move] = 0 #pick up all the stones there. should there be a setter method?
            nextplayer = self.otherplayer(player) #player who will go next - usually that is the other player
            while numstones > 0:
                currentside, currentindex = self.nextspace(currentside, currentindex, player) #go to next spot, drop 1 stone there
                newstate.board[currentside-1][currentindex] += 1
                numstones -=1
            #special rules for where the last stone drops
            if currentindex == 0: #landed in your own store - go again
                nextplayer = player
            elif currentside == player and newstate.board[currentside-1][currentindex] == 1: #land in empty spot (now has 1) on your own side - take stones from opposite spot
                oppositeside, oppositeindex = self.otherplayer(player), 7 - currentindex
                newstate.board[player-1][0] += newstate.board[oppositeside-1][oppositeindex]
                newstate.board[oppositeside-1][oppositeindex] = 0
            #now we have nextplayer - by default other player, or current player if they landed on their store
            #but if one player has no legal move, their turn is skipped - go to the other one.
            #if neither has a move, game is over and we don't care whose turn it is
            newstate.current_player_num = nextplayer
            if len(self.allowed_moves(newstate, nextplayer))==0:
                newstate.current_player_num = self.otherplayer(nextplayer)
            return newstate
        return state #only for invalid move, ask again
        
    #game is over when no more moves allowed. player with most stones wins, or tie if equal
    def outcome(self, state):
        if len(self.allowed_moves(state, 1)) > 0 or len(self.allowed_moves(state, 2)) > 0:
            return None
        #minmax player wants to maximize own outcome - so usually give +1 for win, 0 for tie, -1 for loss
        #but we can try giving them score for how many they get also - should give similar behavior since player's scores sum to constant
        #only difference should be that they try to win by as much as possible or lose by as little as possible (does this make calculations harder?)
        player1score = state.board[0][0]
        player2score = state.board[1][0]
        return {1: player1score, 2: player2score}
        #regular way - +1 to one with more, -1 to one with less, or 0 both if tied

    def display(self, state):
        #+---+---+---+---+---+---+---+---+
        #|   | 1 | 2 | 3 | 4 | 5 | 6 |   |
        #| 0 |---+---+---+---+---+---| 0 |
        #|   | 6 | 5 | 4 | 3 | 2 | 1 |   |
        #+---+---+---+---+---+---+---+---+
        toplegend ='moves:1   2   3   4   5   6      \n'
        side =     '+---+---+---+---+---+---+---+---+\n'
##        top =    '|   | 1 | 2 | 3 | 4 | 5 | 6 |   |\n'
##        middle = '| 0 |---+---+---+---+---+---| 0 |\n'
##        bottom = '|   | 6 | 5 | 4 | 3 | 2 | 1 |   |\n'
        botlegend ='moves:6   5   4   3   2   1      \n'

        top = '|'.join(['|   ']+[self.centeredstring(state.board[1][i],3) for i in range(1,7)]+['   |'])+'\n'
        middle = '|'+self.centeredstring(state.board[1][0],3)+'|---+---+---+---+---+---|'+self.centeredstring(state.board[0][0],3)+'|\n'
        bottom = '|'.join(['|   ']+[self.centeredstring(state.board[0][i],3) for i in range(6,0,-1)]+['   |'])+'\n'

        playerstr = "\nplayer "+str(state.current_player_num)+"'s turn:\n"
        if state.current_player_num == 2:
            print(playerstr+toplegend+side+top+middle+bottom+side)
        else:
            print(playerstr+side+top+middle+bottom+side+botlegend)
    
    #mancala specific methods
    def centeredstring(self, num, totalwidth):
        s = str(num)
        beforenum = math.floor((totalwidth - len(s))/2)
        afternum = math.ceil((totalwidth - len(s))/2)
        beforestr = ''.join([' ' for x in range(beforenum)])
        afterstr = ''.join([' ' for x in range(afternum)])
        return beforestr+s+afterstr

    #what space do you go into after current space? depends on which player.
    #represent current space as which player's side (1,2) and position (0 to 6), return in same format
    #mancala - current player goes into their own store but not opponent's store
    def nextspace(self, whoseside, index, whoseturn):
        if index > 1:
            return (whoseside, index-1) #advance 1 spot along the row
        elif index == 1: #last in row - go to store if it is your own, otherwise go to other row
            if whoseside == whoseturn:
                return (whoseside, 0)
            else:
                return (self.otherplayer(whoseside), 6)
        else: #index is 0 - always go to other row
            return (self.otherplayer(whoseside), 6) #after store is other players side

    #number of the other player, for 2 player game assuming players 1 and 2
    #TODO generalize this to rotating list of players, put it in game class
    def otherplayer(self, playernum):
        return 1 if playernum ==2 else 2
    
class mancalaHumanPlayer(HumanPlayer):
    def pick_move(self, game, state):
        game.display(state)
        allowed = ['1','2','3','4','5','6'] #these are all possible moves. should we check which are actually available here?
        move = None
        while move not in allowed:
            try:
                print ("player "+str(self.mynumber)+": enter your move as the index from 1 to 6")
                move = input()
            except:
                continue
        return int(move)

class MinMaxMancalaPlayer(MinMaxSearchPlayer):
    def represent_state(self, game, state):
        return (state.current_player_num, tuple(state.board[0]), tuple(state.board[1])) #tuple can be a key, but not list
    def heuristic(self, game, state):
        return 0

class smarterMinMaxMancalaPlayer(MinMaxMancalaPlayer):
    def heuristic(self, game, state):
        return state.board[self.mynumber-1][0] - state.board[game.otherplayer(self.mynumber)-1][0] #difference of store amounts
    
#Tictactoe setup
def tic_tac_toe_demo():
    emptyboard = [[0,0,0],[0,0,0],[0,0,0]]
    player1 = MinMaxTicTacToePlayer({'number':1, 'max depth':2, 'show moves':True})
    player2 = tictactoeHumanPlayer({'number':2})
    players = {1:player1, 2:player2}
    tictactoestart=tictactoeState(emptyboard, 1)
    game = tictactoeGame({'starting state':tictactoestart, 'players': players})
    scores = game.play()

#finger game setup
def finger_game_demo():
    startinghands = {1:[1,1],2:[1,1]}
    player1 = fingergameHumanPlayer({'number':1})
    player2 = fingergameHumanPlayer({'number': 2})

    #player2 = MinMaxFingerGamePlayer({'number':2, 'max depth':3, 'show moves':True})
    players = {1:player1, 2:player2}
    startingstate = fingergameState(startinghands,1)
    game=FingerGame({'starting state':startingstate, 'players': players})
    scores=game.play()

#mancala setup
def mancala_demo():
    startingboard = [[0,4,4,4,4,4,4],[0,4,4,4,4,4,4]]
    #player1 = mancalaHumanPlayer({'number':1})
    player2 = mancalaHumanPlayer({'number':2})
    player1 = smarterMinMaxMancalaPlayer({'number':1, 'max depth':3, 'show moves':True})
    #player2 = MinMaxMancalaPlayer({'number': 2, 'max depth': 6, 'show moves': True})
    #player2 = smarterMinMaxMancalaPlayer({'number':2, 'max depth':8, 'show moves':True})
    players = {1:player1, 2:player2}
    startingstate = mancalaState(startingboard,1)
    game=mancalaGame({'starting state':startingstate, 'players': players})
    scores=game.play()
    print(scores)

if __name__ == "__main__":
    #mancala_demo()
    finger_game_demo()