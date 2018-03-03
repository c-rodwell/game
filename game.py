import random

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
        while self.outcome(current_state) is None:
            current_player_num = current_state.current_player_num
            current_player = self.getplayer(current_player_num)
            chosen_move = None
            while not (chosen_move in self.allowed_moves(current_state, current_player_num)):
                chosen_move = current_player.pick_move(self, self.visible_info(current_state, current_player_num))
            current_state = self.move(current_state, current_player_num, chosen_move)
        self.display(current_state) #show the ending state - do I ever not want to do that?
        return self.outcome(current_state) #could call this one less time if we remembered value from the while condition

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

class FingerGame(Game): #for now assume 2 players
    def __init__(self, params):
        super().__init__(params)
        self.handsperplayer = params['hands per player'] if 'hands per player' in params else 2
        self.outnumber = parmas['out number'] of 'out number' in params else 6
    def allowed_moves(self, state, playernum): #public - if you're not allowed to see opponents allowed moves, pass an incomplete state
        #could pass this info to player or just to check legal moves
        #(does it need player arg, since state should include which player to move?)
        valid_adds = [(otherplayer, myhand, opponentshand)
                for otherplayer in players for myhand in range (1,self.handsperplayer+1) for opponentshand in range(1, self.handsperplayer+1)
                if otherplayer != playernum ]#and myhand is not zero and opponents 
        valid_splits = ['split '+str(handnum) for handnum in range(1, self.handsperplayer+1) ] #if that hand is even and there is an open space
    def move(self, state, player, move): #public
        #hit - add the number from your hand to opponents hand
        #split - put half your hand into your open hand
        #now it is the next player's turn

    def outcome(self, state):
        #if all but one player has all 0: that player gets +1, others get -1
        #make a tie for looped games?
        #else None

    def display(self, state):
        #show the gamestate
        return
    
class fingergameHumanPlayer(HumanPlayer):
    def pick_move(self, game, state):
        return

class MinMaxFingerGamePlayer(MinMaxSearchPlayer):
    def represent_state(self, game, state):
        return (state.current_player_num, tuple(state.board[0]), tuple(state.board[1]), tuple(state.board[2])) #tuple can be a key, but not list
    def heuristic(self, game, state):
        return 0 #that is the default
    
#Tictactoe setup
##emptyboard = [[0,0,0],[0,0,0],[0,0,0]]
##player1 = MinMaxTicTacToePlayer({'number':1, 'max depth':2, 'show moves':True})
##player2 = tictactoeHumanPlayer({'number':2})
##players = {1:player1, 2:player2}
##tictactoestart=tictactoeState(emptyboard, 1)
##game = tictactoeGame({'starting state':tictactoestart, 'players': players})
##scores = game.play()

#finger game setup
startinghands = {1:[1,1],2:[1,1]}
player1 = fingergameHumanPlayer({'number':1})
player2 = MinMaxFingerGamePlayer({'number':2, 'max depth':3, 'show moves':True})
players = {1:player1, 2:player2}
startingstate = fingergameState(startinghands,1)
game=FingerGame({'starting state':startingstate, 'players': players})

