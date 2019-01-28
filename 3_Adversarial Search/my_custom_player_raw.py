
from sample_players import DataPlayer
import random, math, copy


class CustomPlayer(DataPlayer):
    """ Implement your own agent to play knight's Isolation

    The get_action() method is the only *required* method. You can modify
    the interface for get_action by adding named parameters with default
    values, but the function MUST remain compatible with the default
    interface.

    **********************************************************************
    NOTES:
    - You should **ONLY** call methods defined on your agent class during
      search; do **NOT** add or call functions outside the player class.
      The isolation library wraps each method of this class to interrupt
      search when the time limit expires, but the wrapper only affects
      methods defined on this class.

    - The test cases will NOT be run on a machine with GPU access, nor be
      suitable for using any other machine learning techniques.
    **********************************************************************
    """
    def get_action(self, state):
        """ Employ an adversarial search technique to choose an action
        available in the current state calls self.queue.put(ACTION) at least

        This method must call self.queue.put(ACTION) at least once, and may
        call it as many times as you want; the caller is responsible for
        cutting off the function after the search time limit has expired.

        See RandomPlayer and GreedyPlayer in sample_players for more examples.

        **********************************************************************
        NOTE:
        - The caller is responsible for cutting off search, so calling
          get_action() from your own code will create an infinite loop!
          Refer to (and use!) the Isolation.play() function to run games.
        **********************************************************************
        """
        # TODO: Replace the example implementation below with your own search
        #       method by combining techniques from lecture
        #
        # EXAMPLE: choose a random move without any search--this function MUST
        #          call self.queue.put(ACTION) at least once before time expires
        #          (the timer is automatically managed for you)
        import random
        #self.queue.put(random.choice(state.actions()))

        #self.queue.put(self.alpha_beta_search(state, depth=10))
        #self.queue.put(self.NegamaxAlphaBeta(state, depth = 3))


        if state.ply_count < 2:
            return self.queue.put(random.choice(state.actions()))

        best_move = (-1, -1)
        try:
            depth = 0
            while True:
                move = self.queue.put(self.alpha_beta_search(state, depth))
                if move == (-1,-1):
                    #print('Search Depth Completed =', depth,'\n')
                    return best_move
                else:
                    best_move = move
                depth +=1
        except:
            # return the best move from the last completed search iteration
            print('Search Depth Completed =', depth,'\n')
            return best_move

        '''
        if state.ply_count < 2:
            return self.queue.put(random.choice(state.actions()))
        else:
            try:
                depth = 0
                while True:
                    move = self.queue.put(self.alpha_beta_search(state, depth))
                    #move = self.queue.put(self.alpha_beta_search(state))
                    if move == (-1,-1):
                        return best_move
                    else:
                        best_move = move
                    depth +=1
            except:
                # return the best move from the last completed search iteration
                return best_move
        ####################################################
        if state.ply_count < 2:
            self.queue.put(random.choice(state.actions()))
        else:
            depth_limit = 5
            for depth in range(1, depth_limit + 1):
                best_move = self.alpha_beta_search(state, depth)
            self.queue.put(best_move)
        '''



    def min_value(self, state, alpha, beta, depth):
        if state.terminal_test():
            return state.utility(self.player_id)
        if depth <= 0:
            return self.score(state)
            #return self.score2(state)
        v = float("inf")
        for a in state.actions():
            v = min(v, self.max_value(state.result(a), alpha, beta, depth-1))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v


    def max_value(self, state, alpha, beta, depth):
        if state.terminal_test():
            return state.utility(self.player_id)
        if depth <= 0:
            return self.score(state)
            #return self.score2(state)
        v = float("-inf")
        for a in state.actions():
            v = max(v, self.min_value(state.result(a), alpha, beta, depth-1))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def alpha_beta_search(self, state, depth=3):
        alpha=float("-inf")
        beta=float("inf")
        best_score = float("-inf") #or val = float("-inf")
        best_move = (-1,-1) # or action = (-1, -1)
        for a in state.actions():
            v = self.min_value(state.result(a), alpha, beta, depth-1)
            alpha = max(alpha, v)
            if v > best_score: #orginally v>=best_score
                best_score = v
                best_move = a
        return best_move


    def score(self, state): #Baseline
        own_loc = state.locs[self.player_id]
        opp_loc = state.locs[1 - self.player_id]
        own_liberties = state.liberties(own_loc)
        opp_liberties = state.liberties(opp_loc)
        return len(own_liberties) - len(opp_liberties)

    def score2(self, state):
        own_loc = state.locs[self.player_id]
        own_liberties = state.liberties(own_loc)
        return len(own_liberties)

    def custom_heuristic_1(self, state):
        #It works!
        own_loc = state.locs[self.player_id]
        opp_loc = state.locs[1 - self.player_id]
        own_liberties = state.liberties(own_loc)
        opp_liberties = state.liberties(opp_loc)
        my_moves = len(own_liberties)
        opponent_moves = len(opp_liberties)
        score = my_moves**2 - 1.8*(opponent_moves**2)
        if my_moves ==0:
            return float("-inf")
        elif opponent_moves ==0:
            return float("inf")
        else:
            return score

        '''
        #own_loc = state.locs[self.player_id]
        #opp_loc = state.locs[1 - self.player_id]
        #own_liberties = state.liberties(own_loc)
        #opp_liberties = state.liberties(opp_loc)
        #return len(own_liberties)**2 - 1.8*len(opp_liberties)**2
        #######################################################
        if state.terminal_test():
            return state.utility(self.player_id)
        my_moves = len(state.actions(self.player_id))
        opponent_moves = len(state.actions(1-self.player_id))
        score = my_moves * my_moves - 1.8 * opponent_moves * opponent_moves
        return score
        '''

    def custom_heuristic_2(self, state):
        #Get a larger value if position in already blocking opp moves
        own_loc = state.locs[self.player_id]
        opp_loc = state.locs[1 - self.player_id]
        own_liberties = state.liberties(own_loc)
        opp_liberties = state.liberties(opp_loc)
        my_moves = len(own_liberties)
        opponent_moves = len(opp_liberties)
        score = 0

        if my_moves ==0:
            return float("-inf")
        elif opponent_moves ==0:
            return float("inf")
        else:
            for pos in own_liberties:
                if pos in opp_liberties:
                    score +=5
            #if own_loc in opp_liberties:
            #    score +=5
            score += my_moves - opponent_moves
            return score

        '''
        if state.terminal_test():
            return state.utility(self.player_id)
        score = 0.0
        move = state.locs[self.player_id]
        opp_moves = state.actions(1 - self.player_id)
        if move in opp_moves:
            score += 5
        own_moves = len(state.actions(self.player_id))
        opp_moves = len(state.actions(1 - self.player_id))
        score += float(own_moves - opp_moves)
        return score
        '''

    def custom_heuristic_3(self, state):
        #Get a larger value if position in already blocking opp moves
        own_loc = state.locs[self.player_id]
        opp_loc = state.locs[1 - self.player_id]
        own_liberties = state.liberties(own_loc)
        opp_liberties = state.liberties(opp_loc)
        my_moves = len(own_liberties)
        opponent_moves = len(opp_liberties)
        score = 0

        if my_moves ==0:
            return float("-inf")
        elif opponent_moves ==0:
            return float("inf")
        else:
            #for pos in own_liberties:
            #    if pos in opp_liberties:
            #        score +=5
            if own_loc in opp_liberties:
                score +=5
            score += my_moves - opponent_moves
            return score
        '''
        'looks ahead'
        own_loc = state.locs[self.player_id]
        opp_loc = state.locs[1 - self.player_id]
        own_liberties = state.liberties(own_loc)
        opp_liberties = state.liberties(opp_loc)
        my_moves = len(own_liberties)
        opponent_moves = len(opp_liberties)
        for move in own_liberties:
            _g = state.result(move)
            my_moves += len(_g.liberties(state.locs[self.player_id]))
        for move in opp_liberties:
            _g = state.result(move)
            opponent_moves += len(_g.liberties(state.locs[1-self.player_id]))
        if my_moves ==0:
            return float("-inf")
        elif opponent_moves ==0:
            return float("inf")
        else:
            return my_moves - opponent_moves
        ###########################################
        #if state.terminal_test():
        #    return state.utility(self.player_id)
        my_moves = state.actions(self.player_id)
        my_moves_len = len(my_moves)
        opp_moves = state.actions(1-self.player_id)
        opp_moves_len = len(opp_moves)
        for move in my_moves:
            _g = state.result(move)
            my_moves_len += len(_g.actions(self.player_id))
        for move in opp_moves:
            _g = state.result(move)
            opp_moves_len += len(_g.actions(1-self.player_id))
        score = float(my_moves_len - opp_moves_len)
        return score
        '''

    def custom_heuristic_4(self, state):
        #works
        own_loc = state.locs[self.player_id]
        opp_loc = state.locs[1 - self.player_id]
        own_liberties = state.liberties(own_loc)
        opp_liberties = state.liberties(opp_loc)
        my_moves = 18*len(own_liberties)
        opponent_moves = len(opp_liberties)
        if my_moves ==0:
            return float("-inf")
        elif opponent_moves ==0:
            return float("inf")
        else:
            return my_moves - opponent_moves
    '''
    def NegamaxAlphaBeta(self, state, depth=3):
        #if self.timer() < self.time_limit:
        #    pass
        alpha=float("-inf")
        beta=float("inf")
        best_score = float("-inf")
        best_move = (-1,-1)
        if depth ==0 or state.terminal_test():
            return state.utility(self.player_id)
        for a in state.actions():
            v = -1*self.min_value(state.result(a), -1*alpha, -1*beta, depth-1)
            alpha = max(alpha,v)
            if v >= best_score:
                best_score = v
                best_move = a
            if alpha >=beta:
                break
        return best_move
        '''
