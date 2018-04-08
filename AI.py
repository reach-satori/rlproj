import libtcodpy as libtcod
from utility import *
#AI is a simple FSM so far
#transition is pass_into, check for transition is check_for_stateswap, an 'active' state gets executed in the take_turn method every turn

class DumbAI(object): #ai module belonging to GameObj, state switches around but always gets executed in take_turn method
    def __init__(self, owner, gldir):
        self.gldir = gldir
        self.owner = owner
        self.state = SimpleIdle(self, gldir)

        self.last_state = self.state
        self.timer_since_swap = 0
        self.extrainfo = None
        
    def take_turn(self):
        self.state.check_for_stateswap()
        self.timer_since_swap += 1
        self.state.execute()


class AIState(object):# Base Class
    def __init__(self, ai, gldir):
        self.ai = ai
        self.gldir = gldir
        self.owner = self.ai.owner
        self.action = ''
        self.target = None
        self.cost = 0

    def check_for_stateswap(self):
        raise ValueError('wooawowaaaow override this in branch classes') #override this in branch classes
    def execute(self):
        raise ValueError('wooawowaaaow override this in branch classes') #override this in branch classes

    def determine_cost(self):
        cost = self.owner.fighter.speed
        for stati in self.owner.fighter.status:
            if stati.name == 'maim' and self.action == 'move': cost += 70
            if stati.name == 'slow': cost += int(round(stati.power*1.25))
        return cost

    def pass_into(self, newstate):
        self.ai.last_state = self
        self.ai.timer_since_swap = 0
        self.ai.state = newstate(self.ai, self.gldir)
        self.ai.state.execute()



class SimpleIdle(AIState): #stands there
    def execute(self):
        while True:
            monster = self.owner
            self.cost = self.determine_cost()

            if self.cost > monster.fighter.energy: return
            monster.fighter.energy -= self.cost

    def check_for_stateswap(self):
        monster = self.owner
        if libtcod.map_is_in_fov(self.gldir.fov_map, monster.x, monster.y): 
            self.pass_into(SimpleAttack)

class SimpleAttack(AIState): #walks up and hits
    def execute(self):
        while True:

            self.formulate_turn()
            monster = self.owner


            if self.cost > monster.fighter.energy: return


            monster.fighter.energy -= self.cost
            if self.action == 'move':
                monster.move_astar((self.target))
            elif self.action == 'attack':
                monster.fighter.attack(self.target)

    def formulate_turn(self):
        monster = self.owner

        if monster.distance_to(self.gldir.player) >= 2:
            self.action = 'move'
            self.target = obj_to_point(self.gldir.player)
            self.cost = self.determine_cost()

        elif self.gldir.player.fighter.hp >= 0:
            self.action = 'attack'
            self.target = self.gldir.player
            self.cost = self.determine_cost()

    def check_for_stateswap(self):
        monster = self.owner
        if not libtcod.map_is_in_fov(self.gldir.fov_map, monster.x, monster.y):    
            self.pass_into(SimpleSearch)

class SimpleSearch(AIState): #walks up to where player was last seen
    def execute(self):
        while True:
            monster = self.owner
            self.action = 'move'
            self.target = self.ai.last_state.target
            self.cost = self.determine_cost()

            if self.cost > monster.fighter.energy: return
            monster.fighter.energy -= self.cost

            if self.action == 'move':
                monster.move_astar(self.target)

    def check_for_stateswap(self):
        monster = self.owner
        if libtcod.map_is_in_fov(self.gldir.fov_map, monster.x, monster.y): 
            self.pass_into(SimpleAttack)
        if self.ai.timer_since_swap > 7 or (self.owner.x, self.owner.y) == (self.target.x, self.target.y): 
            self.pass_into(SimpleIdle)




