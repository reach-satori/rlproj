import libtcodpy as libtcod
from utility import *
from AI import AIState
from collections import deque
from messages import message
from math import sqrt




class DogAI(object): #ai module belonging to GameObj, state switches around but always gets executed in take_turn method
	def __init__(self, owner, gldir):
		self.gldir = gldir
		self.owner = owner
		self.currentnoise = 0
		self.state = DogIdle(self, gldir)
		self.hplog = deque([], 4)
		self.hplog.append(self.owner.fighter.hp)
		self.gothit = False

		self.last_state = self.state
		self.timer_since_swap = 0
		self.extrainfo = None


		
	def take_turn(self):
		self.state.check_for_stateswap()
		self.currentnoise = libtcod.heightmap_get_value(self.gldir.noisemap, self.owner.x, self.owner.y)

		if self.owner.fighter.hp != self.hplog[-1]:
			self.hplog.append(self.owner.fighter.hp)  #checks if hp has changed
			self.gothit = True

		else self.gothit = False


		self.timer_since_swap += 1
		self.state.execute()

	def count_dogs(self):
		dogs = filter(lambda x: x.ai and isinstance(x.ai, DogAI), self.gldir.game_objs)
		dogcounter = 0
		for dog in dogs:
			if dog.distance_to(self.owner) < 10: dogcounter += 1

		return dogcounter


class DogIdle(AIState):
	def execute(self):
		monster = self.owner
		while True:

			self.cost = self.determine_cost()
			if self.cost > monster.fighter.energy: return

			monster.fighter.energy -= self.cost

	def check_for_stateswap(self):
		monster = self.owner
		if libtcod.map_is_in_fov(self.gldir.fov_map, monster.x, monster.y): 
			if self.ai.count_dogs() > 3: 
				self.pass_into(DogAttack)
			else: 
				self.pass_into(DogBark)

class DogBark(AIState):
	def execute(self):
		monster = self.owner
		self.target = obj_to_point(self.gldir.player)
		while True:
			
			self.cost = self.determine_cost()
			if self.cost > monster.fighter.energy: return

			monster.fighter.energy -= self.cost
			self.gldir.create_noise(self.owner, 5)

	def check_for_stateswap(self):
		monster = self.owner
		n_of_dogs = self.ai.count_dogs()

		if self.ai.gothit:
			self.pass_into(DogAttack)
			return

		if not libtcod.map_is_in_fov(self.gldir.fov_map, monster.x, monster.y):
			self.pass_into(DogChase)
			return

class DogAttack(AIState):
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
				

	def check_for_stateswap(self):
		if not libtcod.map_is_in_fov(self.gldir.fov_map, monster.x, monster.y):
			self.pass_into(DogChase)
			return


class DogChase(AIState): #walks up to where player was last seen
	def execute(self):
		monster = self.owner
		while True:
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
			if self.ai.count_dogs() > 3: 
				self.pass_into(DogAttack)
			else: 
				self.pass_into(DogBark)

		if self.ai.timer_since_swap > 10:
			self.pass_into(DogIdle)
