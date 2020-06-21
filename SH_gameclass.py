import random

class SH_game:


    def __init__(self, players):
        presidential_powers = [['None','None','Examine','Kill','Kill','None'],['None','Identity','President','Kill','Kill','None'],['Identity','Identity','President','Kill','Kill','None']]
        fs_nr = 1 + int((len(players)-5)/2)
        lib_nr = 3 + int((len(players)-4)/2)
        roles = ['hitler'] + ['fascist']*fs_nr + ['liberal']*lib_nr
        random.shuffle(players)
        random.shuffle(roles)
        self._players = dict(zip(players, roles))
        random.shuffle(players)
        self._player_order = list(players)
        self._next_presidents = players
        self._presidential_powers = presidential_powers[fs_nr -1]


        #ingame variables
        self._passed_policies = [0,0]
        #self._passed_policies = [0,0]
        self._draw_pile = ['fascist']*11 + ['liberal']*6
        random.shuffle(self._draw_pile)
        self._discard_pile = list()
        self._rejected_governments = 0
        self._nominated_chancellor = None
        self._last_government = [None]*2
        self._investigated = list()

    def return_party(self,player):
        if self._players[player] == 'liberal':
            return 'liberal'
        else:
            return 'fascist'

    def return_president(self):
        return self._next_presidents[0]

    def return_chancellor(self):
        return self._nominated_chancellor

    def return_players(self):
        return self._players.keys()

    def return_presidential_power(self):
        return self._presidential_powers[self._passed_policies[1]-1]

    def return_investigate_candidates(self):
        res = list()
        for x in self._players.keys():
            if x in self._investigated:
                continue
            if is_president(x):
                continue
            res.append(x)
        return res

    def return_other_players(self):
        res = list()
        for x in self._players.keys():
            if x != self._next_presidents[0]:
                res.append(x)
        return res

    def investigate(self,player):
        self._investigated.append(player)
        return self.return_party(player)


    def is_hitler(self,player):
        if self._players[player] == 'hitler':
            return True
        else:
            return False


    def return_chancellor_candidates(self):
        res = list(self._players.keys())
        res.remove(self._next_presidents[0])
        if self._last_government[1] == None:
            return res
        else:
            if self._last_government[1] != self._next_presidents[0]:
                try:
                    res.remove(self._last_government[1])
                except:
                    pass
            if(len(self._players.keys()) > 5):
                try:
                    res.remove(self._last_government[0])
                except:
                    pass
        return res


    def list_next_presidents(self):
       return self._next_presidents


    def is_president(self, player):
        if self._next_presidents[0] == player:
            return True
        else:
            return False

    def is_chancellor(self, player):
        if self._nominated_chancellor == player:
            return True
        else:
            return False

    def is_fascist(self,player):
        if self._players[player] == 'fascist':
            return True
        else:
            return False


    def was_not_in_last_government(self,player):
        return player in self._last_government


    def reshuffle_deck(self):
        self._draw_pile += self._discard_pile
        random.shuffle(self._draw_pile)
        self._discard_pile = list()

    #return all fascists and hitler
    def show_fascists(self):
        res = [list(),list()]
        for x in self._players.keys():
            if (self._players[x] == 'fascist'):
                res[0].append(x)
        for x in self._players.keys():
            if (self._players[x] == 'hitler'):
                res[1].append(x)
        return res


    def nominate_chancellor(self,player):
        self._nominated_chancellor = player


    def discard_card(self,card):
        self._discard_pile.append(card)


    def fascist_policy_victory(self):
        if self._passed_policies[1] >= 6:
            return True
        else:
            return False


    def liberal_policy_victory(self):
        if self._passed_policies[0] >= 5:
            return True
        else:
            return False


    def pass_policy(self,policy):
        if (policy == 'fascist'):
            self._passed_policies[1] += 1
        elif (policy == 'liberal'):
            self._passed_policies[0] += 1


    #Insert the vote as a list
    def enter_vote(self, vote):
        hitler_won = False
        if(sum(vote) > len(self._players)/2):
            if self.is_hitler(self._nominated_chancellor) and self._passed_policies[1] >= 3:
               hitler_won = True
            self.make_chancellor()
            return(True, hitler_won,False)
        else:
            policy_auto_passed = self.reject_chancellor()
            return(False,False,policy_auto_passed)


    #make a new player chancellor
    def make_chancellor(self):
        self._rejected_governments = 0
        self._last_government[0] = self.return_president()
        self._last_government[1] = self.return_chancellor()


    def change_government(self):
        self._nominated_chancellor = None
        last = self._next_presidents[0]
        self._next_presidents.remove(last)
        if not last in self._next_presidents: # Bc of Presidential Power
            self._next_presidents.append(last)


    #make a new player chancellor
    def reject_chancellor(self):
        self.change_government()
        self._rejected_governments += 1
        if (self._rejected_governments >= 3):
            self._rejected_governments = 0
            if(len(self._draw_pile) < 3):
                self.reshuffle_deck()
            x = self._draw_pile.pop(0)
            self.pass_policy(x)
            return True
        return False



    #draw policies and return the policies and the president
    def draw_policies(self):
        if(len(self._draw_pile) < 3):
            self.reshuffle_deck()
        drawn_policies = [self._draw_pile.pop(0),self._draw_pile.pop(0),self._draw_pile.pop(0)]

        return (drawn_policies)


    def choose_president(self, player):
        self._next_presidents.insert(1,player)


    def examine_policies(self):
        if(len(self._draw_pile) < 3):
            self.reshuffle_deck()
        drawn_policies = [self._draw_pile[0],self._draw_pile[1],self._draw_pile[2]]

        return (drawn_policies)

    def kill(self,player):
        hitler_lost = self.is_hitler(player)
        self._players.pop(player)
        self._next_presidents.remove(player)
        return hitler_lost
