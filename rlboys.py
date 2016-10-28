import libtcodpy as libtcod
import math
import textwrap
import shelve
import catalog
import graphical
from random import gauss



#window size
SCREEN_WIDTH = 120
SCREEN_HEIGHT = 60


#map size
MAP_WIDTH = 80
MAP_HEIGHT = 50

#GUI parameters
BAR_WIDTH = 20
PANEL_HEIGHT = 10
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1

#map gen parameters
MAX_ROOM_MONSTERS = 3
ROOM_MAX_SIZE = 10  # ALL TO BE CHANGED LATER OF COURSE
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
 
LIMIT_FPS = 20  #20 frames-per-second maximum
FOV_ALGO = 0  #default FOV algorithm
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10
INVENTORY_WIDTH = SCREEN_WIDTH - 10
CHARACTER_SCREEN_WIDTH = 40

LIGHTNING_DAMAGE = 20 
LIGHTNING_RANGE = 5
FIREBALL_DAMAGE = 12
FIREBALL_RADIUS = 4
POTHEAL_AMOUNT = 10

LEVEL_UP_BASE = 50
LEVEL_UP_FACTOR = 75
LEVEL_SCREEN_WIDTH = 40



color_dark_wall = libtcod.Color(0, 0, 100)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_wall = libtcod.Color(130, 110, 50)
color_light_ground = libtcod.Color(200, 180, 50)





class SkillTree:
	def __init__(self, stype, level = 0):
		self.stype = stype
		self.level = level
		self.nodetable = catalog.get_nodetable(stype)

	def get_node_from_name(self, name):
		for node in self.nodetable:
			if node.name == name: return node
			else: raise ValueError('Skill list node that does not exist requested!')

	def get_available_nodes(self):
		available_nodes = []
		for node in self.nodetable:
			if (node.parent == [] or node.parent == '' or self.check_if_node_leveled(node.parent)) and node.leveled == False: 
				available_nodes.append(node)
		if available_nodes == []: textbox('No nodes to select.')
		else: return available_nodes

	def check_if_node_leveled(self, node_s):

		if type(node_s) is list:
			for name in node_s:
				chknode = self.get_node_from_name(name)
				if not chknode.leveled: return False
			return True

		elif type(node_s) is str:
			if not self.get_node_from_name(node_s): return False
			else: return True

	def node_select(self):
		width = SCREEN_WIDTH
		height = SCREEN_HEIGHT
		ended = False

		skillbox = libtcod.console_new(width, height)
		options = self.get_available_nodes()
		letter_index = ord('a')
		y=2
		libtcod.console_print_frame(skillbox,0, 0, width, height, clear=False, flag=libtcod.BKGND_DEFAULT)

		for node in options:
			text = ' ' + chr(letter_index) +'  -  ' + node.name
			libtcod.console_print_ex(skillbox, 2, y, libtcod.BKGND_NONE, libtcod.LEFT, text)

			y += 2
			letter_index += 1
		libtcod.console_blit(skillbox,0,0,0,0,0,0,0)
		libtcod.console_flush()
		choice = False
		while True:
			libtcod.console_flush()

			key = libtcod.console_wait_for_keypress(True)
			if key.vk == libtcod.KEY_ENTER:
				if choice:
					choice.levelup()
					return True
				else:
					textbox('No node chosen.')
					continue
			elif key.vk == libtcod.KEY_ESCAPE:
				return
			index = key.c - ord('a')
			choice = options[index]
			self.node_description(choice)
			

		
	def node_description(self, node):
		width = SCREEN_WIDTH -6
		height = SCREEN_HEIGHT/2 -2

		skillcon = libtcod.console_new(width, height)
		libtcod.console_print_frame(skillcon,0, 0, width, height, clear=False, flag=libtcod.BKGND_DEFAULT)
		description = catalog.get_node_description(node.name) ## 
		for line in description:
			libtcod.console_print_ex(skillcon, 1, description.index(line)+1,libtcod.BKGND_NONE, libtcod.LEFT, line)
		libtcod.console_print_ex(skillcon, 1, 60, libtcod.BKGND_NONE, libtcod.LEFT, 'Press enter to accept selection')

		libtcod.console_blit(skillcon, 0, 0, 0, 0, 0, 2, height + 2) 

	@property
	def level(self):
		maxlvl = 0
		for node in self.nodetable:
			if node.leveled and node.tier > maxlvl: maxlvl = node.tier  #tree level is = to highest skill node tier

		return maxlvl
	
class PerkTree(SkillTree):
	def get_available_nodes(self):
		for node in self.nodetable:
				if pass_perk_requirements(node) and (node.parent == [] or node.parent == '' or self.check_if_node_leveled(node.parent)) and node.leveled == False: 
					available_nodes.append(node)
		if available_nodes == []: textbox('No nodes to select.')
		else: return available_nodes



#SKILL TREE DATA STRUCTURE:
#One SkillTree (perktree inherited for perks) object for each type (combat, tech, ritual, perks), each containing appropriate nodetable objects gotten from the catalog
#abilities are passed on to the player in the Player's abilities property whenever they are called (getter decorator)
#haven't done passive bonuses yet



class Ccreation:

	def __init__(self, stage = 'race select', chosenrace = 'empty', chosengclass = 'empty', chosenperk = 'empty'):
		self.stage = stage
		self.chosenrace = chosenrace
		self.chosengclass = chosengclass
		self.chosenperk = chosenperk

	def run_creation(self):
		global ptree, ctree, ttree, rtree 
		ctree = SkillTree('combat', 1)
		ttree = SkillTree('tech', 0)
		rtree = SkillTree('ritual', 0)
		ptree = PerkTree('perks', 0)

		while self.stage != 'complete':
			if self.stage == 'race select':
				self.descriptionbox(self.chosenrace) 
				self.statbox(self.chosenrace)
				self.chosenrace = self.choicebox()
			elif self.stage == 'class select': #loops between this and choicebox until creation is done
				self.descriptionbox(self.chosengclass)
				self.statbox(self.chosengclass)
				self.chosengclass = self.choicebox()
			elif self.stage == 'skill select':
				tree_lvlup()
				self.stage = 'complete'
				clear_screen()
			# elif self.stage == 'perk select':
			
			
		#return Player(self.chosenrace, self.chosengclass,)

	def statbox(self,choice):
		width = SCREEN_WIDTH -6
		height = SCREEN_HEIGHT/2 -2

		statsbox = libtcod.console_new(width, height)
		libtcod.console_print_frame(statsbox,0, 0, width, height, clear=False, flag=libtcod.BKGND_DEFAULT)
		statblock = catalog.ccreation_stats(choice) ## text for the statblock, comes in a list of strings
		for line in statblock:
			libtcod.console_print_ex(statsbox, 1, statblock.index(line)+1,libtcod.BKGND_NONE, libtcod.LEFT, line)
		libtcod.console_print_ex(statsbox, 1, 60, libtcod.BKGND_NONE, libtcod.LEFT, 'Press enter to accept selection')

		libtcod.console_blit(statsbox, 0, 0, 0, 0, 0, 2, height + 2) #creates and prints to the statbox that takes up the lower half of the screen in char creation

	def descriptionbox(self,choice):
		width = SCREEN_WIDTH/3 - 2 
		height = SCREEN_HEIGHT/2

		description_box = libtcod.console_new(width, height)
		libtcod.console_set_alignment(description_box, libtcod.CENTER)
		text = catalog.ccreation_description(choice)
		libtcod.console_print_rect(description_box, width/2+2, height*2/3, width-5, height, text)
		libtcod.console_print_frame(description_box,0, 0, width, height, clear=False, flag=libtcod.BKGND_DEFAULT)

		libtcod.console_blit(description_box, 0, 0, 0, 0, 0, (width*2)+2, 0) #creates and prints to the description box that takes up the upper left side of the screen in char creation

	def choicebox(self):
		width = (SCREEN_WIDTH*2)/3+1
		height = SCREEN_HEIGHT/2
		menu_selection = libtcod.console_new(width, height)
		letter_index = ord('a')
		y = 2
		x = 2
		if self.stage == 'race select':
			requested_list = catalog.FULL_RACELIST
		elif self.stage == 'class select':
			requested_list = catalog.FULL_GCLASSLIST

		for option_text in requested_list:
			text = ' ' + chr(letter_index) +'  -  ' + option_text
			libtcod.console_print_ex(menu_selection, x, y, libtcod.BKGND_NONE, libtcod.LEFT, text)

			y += 2
			if y > SCREEN_HEIGHT/2 - 1:
				x += 8
				y = 2
			letter_index += 1

		libtcod.console_print_frame(menu_selection,0, 0, width, height, clear=False, flag=libtcod.BKGND_DEFAULT)
		libtcod.console_blit(menu_selection,0,0,0,0,0,2,0)
		libtcod.console_flush()

		key = libtcod.console_wait_for_keypress(True)

		if key.vk == libtcod.KEY_ENTER and self.stage == 'race select':   # this is where the stage cycling takes place
			self.stage = 'class select'
			return self.chosenrace

		elif key.vk == libtcod.KEY_ENTER and self.stage == 'class select':
			self.stage = 'skill select'
			return self.chosengclass

		index = key.c - ord('a')
		if index >= 0 and index < len(requested_list): 
			return requested_list[index] ### returns the name of the chosen class or race or whatever as per catalog list
		return None


		
class Player(object):
	def __init__(self, race = 'human', gclass = 'warden', stats = {'strength':5,'constitution':5,'agility':5,'intelligence':5,'attunement':5}, dodge = 0, perks = []):
		self.race = race #only player-exclusive stats should go here if possible
		self.gclass = gclass #gclass for game class
		self.stats = stats
		self.dodge = dodge
		self.perks = perks
		#self.abilities

	@property
	def abilities(self):
		abilitylist = []
		for tree in (ctree, ttree, rtree, ptree):
			for node in tree.nodetable:
				if node.abilities != None and node.leveled:
					abilitylist += node.abilities
		self._abilities = abilitylist
		return self._abilities

	@abilities.setter
	def abilities(self):
		return self.abilities

class EqSpecial:
	def __init__(self, on_atk_bonus = {}):
		self.on_atk_bonus = on_atk_bonus #here i'm gonna add all every different 'type' of item special. Some will probably change things on attack, some on the character, and so on.

	def apply_on_atk_bonus(self, origin, target):
		if self.on_atk_bonus:
			bonusdmg = Dmg(0, [1], 0)
			for bonus in self.on_atk_bonus:
				if bonus == 'str bonus':
					bonusdmg.add(origin.player.stats['strength'] * self.on_atk_bonus['str bonus'], [1], 0)

		return bonusdmg


class Equipment:
	def __init__(self, slot, base_dmg = [0,0], armor_bonus = 0, dodge_bonus = 0, special = EqSpecial()):
		self.slot = slot
		self.is_equipped = False
		self.base_dmg = base_dmg
		self.dodge_bonus = dodge_bonus
		self.armor_bonus = armor_bonus
		self.special = special

		if self.special:
			self.special.owner = self

	def equip(self,equipper):
		#equip object and show a message about it
		if equipper == 'player':
			self.is_equipped = True
			message('Equipped ' + self.owner.item.dname + ' on your ' + self.slot + '.', libtcod.light_green)


	def unequip(self):
		if not self.is_equipped: return
		self.is_equipped = False
		message('Unequipped ' + self.owner.item.dname + ' from ' + self.slot + '.', libtcod.light_yellow)

	def equip_options(self): #upon getting chosen from the equipment menu
		options = ['Examine', 'Unequip', 'Drop']
		index = menu('Choose an action: ', options, 50)
		if index == 0:#examine
			self.owner.item.examine()

		elif index == 1:#unequip
			self.unequip()

		elif index == 2: #drop (and unequip)
			self.unequip()
			self.owner.item.drop()

	def roll_dmg(self):
		if self.base_dmg == [0,0]: return 0
		else:
			return libtcod.random_get_int(0, self.base_dmg[0], self.base_dmg[1])



class Item:
	def __init__(self, weight, depth_level = 1, use_function = None, itemtype = 'gadget'):
		self.weight = weight
		self.use_function = use_function
		self.depth_level = depth_level
		self.identified = False
		self.already_seen = False
		self.itemtype = itemtype
		#possible itemtypes: equipment, salve, gadget, trinket


	def pick_up(self):
		if len(inventory)>=26:
			message('Your inventory is full')
		else:
			inventory.append(self.owner)  # inventory has objects, not item
			objects.remove(self.owner)
			message('You picked up ' + self.dname + '!', libtcod.green)

	def use(self):
		if self.use_function == None:
			message('The' + self.owner.name + 'cannot be used.')
		else:
			if self.use_function() != 'cancelled':  #conditions for persistent/charge-based consumables go here
				inventory.remove(self.owner)

	def drop(self):
		#add to the map and remove from the player's inventory. also, place it at the player's coordinates
		objects.insert(0,self.owner)
		inventory.remove(self.owner)
		if self.owner.equipment and self.owner.equipment.is_equipped: self.owner.equipment.unequip()
		self.owner.x = player.x
		self.owner.y = player.y
		message('You dropped a ' + self.dname + '.', libtcod.yellow)

	def examine(self):
		text = catalog.get_item_description(self)

		textbox(text)

	# def name_for_display(self):
	# 	if not self.identified:
	# 		if self.owner.equipment: 
	# 			unidname = 'an unidentified ' + self.owner.name
	# 			return unidname
	# 		elif 'salve' in self.owner.name:
	# 			return catalog.random_salve_name(self)
# replaced by property dname

	def item_options(self):
		options = ['Examine', 'Drop', 'Use']
		index = menu('Choose an action: ', options, 50)
		if index == 0:#examine
			self.examine()

		if index == 1: #drop
			self.drop()

		if index == 2: #use
			self.use()

	@property
	def dname(self):
		global namekeeper
		if self.owner.name in namekeeper:
			self.already_seen = True


		if not self.identified:
			if self.itemtype == 'equipment': 
				unidname = 'an unidentified ' + self.owner.name
			elif self.itemtype == 'salve': 
				if not self.already_seen:
					unidname = catalog.random_salve_name(self)
					namekeeper[self.owner.name] = unidname
				else: unidname = namekeeper[self.owner.name]
			else: return self.owner.name
			return unidname

class Fighter:
	def __init__(self, hp, armor, power, xp,  death_function = None, state = ['normal']):
		self.max_hp = hp
		self.hp = hp
		self.base_armor = armor
		self.base_power = power
		self.death_function = death_function
		self.xp = xp
		self.state = state


	def take_damage(self,damage):
		if isinstance(damage, Dmg): damage = damage.resolve()
		elif damage > 0:
			self.hp -= damage
			if self.hp < 0:
				player.fighter.xp += self.xp
				function = self.death_function
				if function is not None:
					function(self.owner)

	def attack(self, target):
		if self.owner.player:
			damage = self.power()
			for equip in get_all_equipped(self.owner):#equivalent to global player
				if equip.special.on_atk_bonus:
					damage.objadd(equip.special.apply_on_atk_bonus(self.owner, target))
			finaldmg = damage.resolve()
			finaldmg -= target.fighter.armor
			if finaldmg > 0:
				message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(int(round(finaldmg))) + ' hit points.')
				target.fighter.take_damage(finaldmg)
			else:
				message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')

		else:
			if libtcod.random_get_int(0, 1, 100) > int(round(target.player.dodge * 1.3)):
				damage = self.power() - target.fighter.armor
				if damage > 0:
					message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(int(round(damage))) + ' hit points.')
					target.fighter.take_damage(damage)
				else:
					message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')
			else: message(self.owner.name.capitalize() + ' misses ' + target.name + ' completely!', libtcod.lightest_green)


	def heal(self, amount):
		self.hp += amount
		if self.hp > self.max_hp:
			self.hp = self.max_hp

	def power(self, multipliers = [1]):

		if self.owner is player:

			equipments = get_all_equipped(self.owner)
			flat_bonus = 0
			equiproll = 0
			multiplicative_component = 0
			for equip in equipments: 
				equiproll += equip.roll_dmg()

			combat_flatbonus = ctree.level * 2
			flat_bonus += combat_flatbonus
			multiplicative_component += equiproll
			return Dmg(multiplicative_component, product(multipliers), flat_bonus)

		else:
			return self.base_power

																			

	@property
	def armor(self):  #return actual defense, by summing up the bonuses from all equipped items
		bonus = sum(int(math.ceil(equipment.armor_bonus/2)) for equipment in get_all_equipped(self.owner))
		return self.base_armor + bonus
 
	@property
	def max_hp(self):  #return actual max_hp, by summing up the bonuses from all equipped items
		bonus = sum(equipment.max_hp_bonus for equipment in get_all_equipped(self.owner))
		return self.base_max_hp + bonus
	
class Dmg:
	def __init__(self, multiplicative, multiplier = [1], flat = 1):
		self.multiplicative = multiplicative
		if not hasattr(multiplier, '__iter__'): self.multiplier = [multiplier]
		else: self.multiplier = multiplier
		self.flat = flat

	def add(self, multiplicative, multiplier, flat):
		self.multiplicative += multiplicative
		self.multiplier += multiplier
		self.flat += flat

	def objadd(self, dmgobj):
		self.multiplicative += dmgobj.multiplicative
		self.multiplier += dmgobj.multiplier
		self.flat += dmgobj.flat

	def resolve(self):
		return (self.multiplicative * product(self.multiplier)) + self.flat



class DumbMonster:  # basic AI
	def take_turn(self):
		monster = self.owner
		if 'skip turn' in monster.fighter.state:
			monster.fighter.state.remove('skip turn')
			return

		if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
			if monster.distance_to(player) >= 2:
				monster.move_astar(player)


			elif player.fighter.hp >= 0:
				monster.fighter.attack(player)



class Rect:
	def __init__(self, x, y, w, h):
		self.x1 = x
		self.y1 = y
		self.x2 = x+w
		self.y2 = y+h

	def center(self):
		center_x = (self.x1+self.x2)/2
		center_y = (self.y1+self.y2)/2
		return (center_x,center_y)

	def intersect(self,other):
		return (self.x1 <= other.x2 and self.x2 >= other.x1 and self.y1 <= self.y2 and self.y2 >= other.y1)
		#check if rectangle intersects with another one

class SpTile:
	def __init__(self, char = None, foreground = None, background = None, onwalk_effect = None):
		self.char = char
		self.foreground = foreground
		self.background = background
		self.onwalk_effect = onwalk_effect

	def apply_onwalk(self, walker):
		if self.onwalk_effect and walker.fighter:
			for effect in self.onwalk_effect:
				if effect == 'damage': walker.fighter.take_damage(self.onwalk_effect['damage'])

class Tile:
	def __init__(self, blocked, block_sight = None, special = None):
		self.blocked = blocked
		self.explored = False
		self.special = special

		#blocks sight by default if blocks movement (standard wall)
		if block_sight is None:	self.block_sight = blocked
		



class Object:
	def __init__(self,x, y, char, name, color, blocks = False, fighter = None, ai = None, item = None, ignore_fov = False, equipment = None, player = None):
		self.x = x
		self.y = y
		self.char = char
		self.color = color
		self.blocks = blocks
		self.name = name
		self.ignore_fov = ignore_fov
		self.player = player




		self.equipment = equipment
		if self.equipment:
			self.equipment.owner = self

		self.item = item
		if self.item:
			self.item.owner = self
			if self.equipment: self.item.itemtype = 'equipment'

		self.fighter = fighter
		if self.fighter:
			self.fighter.owner = self

		self.ai = ai
		if self.ai:
			self.ai.owner = self

	def move_astar(self, target):
		#Create a FOV map that has the dimensions of the map
		fov = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
 
		#Scan the current map each turn and set all the walls as unwalkable
		for y1 in range(MAP_HEIGHT):
			for x1 in range(MAP_WIDTH):
				libtcod.map_set_properties(fov, x1, y1, not map[x1][y1].block_sight, not map[x1][y1].blocked)
 
		#Scan all the objects to see if there are objects that must be navigated around
		#Check also that the object isn't self or the target (so that the start and the end points are free)
		#The AI class handles the situation if self is next to the target so it will not use this A* function anyway   
		for obj in objects:
			if obj.blocks and obj != self and obj != target:
				#Set the tile as a wall so it must be navigated around
				libtcod.map_set_properties(fov, obj.x, obj.y, True, False)
 
		#Allocate a A* path
		#The 1.41 is the normal diagonal cost of moving, it can be set as 0.0 if diagonal moves are prohibited
		my_path = libtcod.path_new_using_map(fov, 1.41)
 
		#Compute the path between self's coordinates and the target's coordinates
		libtcod.path_compute(my_path, self.x, self.y, target.x, target.y)
 
		#Check if the path exists, and in this case, also the path is shorter than 25 tiles
		#The path size matters if you want the monster to use alternative longer paths (for example through other rooms) if for example the player is in a corridor
		#It makes sense to keep path size relatively low to keep the monsters from running around the map if there's an alternative path really far away        
		if not libtcod.path_is_empty(my_path) and libtcod.path_size(my_path) < 25:
			#Find the next coordinates in the computed full path
			x, y = libtcod.path_walk(my_path, True)
			if x or y:
				#Set self's coordinates to the next path tile
				self.x = x
				self.y = y
				if map[self.x][self.y].special and map[self.x][self.y].special.onwalk_effect:
					map[self.x][self.y].special.apply_onwalk(self)
		else:
			#Keep the old move function as a backup so that if there are no paths (for example another monster blocks a corridor)
			#it will still try to move towards the player (closer to the corridor opening)
			self.move_towards(target.x, target.y)  
 
		#Delete the path to free memory
		libtcod.path_delete(my_path)

	def move(self, dx, dy):
		if not is_blocked(self.x+dx, self.y+dy):
			self.x += dx
			self.y += dy

		if map[self.x][self.y].special and map[self.x][self.y].special.onwalk_effect:
			map[self.x][self.y].special.apply_onwalk(self)





	def unblocked_move(self, dx, dy):
		self.x += dx
		self.y += dy

	def draw(self):
		if (libtcod.map_is_in_fov(fov_map, self.x, self.y) or self.ignore_fov):
			libtcod.console_set_default_foreground(con, self.color)
			libtcod.console_put_char_ex(con, self.x, self.y, self.char, self.color, libtcod.black)

	def clear(self):
		libtcod.console_put_char_ex(con, self.x, self.y, ' ', libtcod.white,libtcod.black)

	def move_towards(self, target_x, target_y):
		#vector from this object to the target, and distance
		dx = target_x - self.x
		dy = target_y - self.y
		distance = math.sqrt(dx ** 2 + dy ** 2)

		#normalize it to length 1 (preserving direction), then round it and
		#convert to integer so the movement is restricted to the map grid
		dx = int(round(dx / distance))
		dy = int(round(dy / distance))
		self.move(dx, dy)

	def distance_to(self, other):
		#return the distance to another object
		dx = other.x - self.x
		dy = other.y - self.y
		return math.sqrt(dx ** 2 + dy ** 2)

	def distance(self,x,y):
		return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

	def send_to_back(self):
		global objects
		objects.remove(self)
		objects.insert(0, self)

	def send_to_front(self):
		global objects
		objects.remove(self)
		objects.append(self)


		############################################################################
		#########################   ABILITY  DEFINITIONS(for player)   #############
		############################################################################

	def abl_kicklaunch(self):
		target = random_adj_target()

		dx = 0
		dy = 0

		if target == None:
			message('Nobody to kick!')
			return

		if self.y < target.y:
			dy = 3
		elif self.y > target.y:
			dy = -3

		if self.x < target.x:
			dx = 3
		elif self.x > target.x:
			dx = -3

		dmg = self.fighter.power(multipliers = [0.5])
		dmg = dmg.resolve()
		target.fighter.take_damage(dmg)
		message('You put all your strength behind a mighty kick, dealing ' + str(int(round(dmg))) + ' damage.', libtcod.light_red)
		##########################################################################################
		##########moves object (dx, dy) units, stopping and displaying a slam message if they hit something
		if abs(dx) == abs(dy) and abs(dx) > 1:
			for i in range(1,abs(max(dx,dy))):
				if not is_blocked(target.x + int(math.copysign(1, dx)), target.y + int(math.copysign(1, dy))): 
					target.x += int(math.copysign(1, dx))
					target.y += int(math.copysign(1, dy))
				else: 
					message('The ' + target.name + ' slams into something violently!')
					return

		elif dx == 0 and abs(dy) > 1:
			for i in range(1,abs(dy)):
				if not is_blocked(target.x, target.y + int(math.copysign(1, dy))):
					target.y += int(math.copysign(1, dy))
				else:
					message('The ' + target.name + ' slams into something violently!')
					return
			

		elif dy == 0 and abs(dx) > 1:
			for i in range(1,abs(dx)):
				if not is_blocked(target.x + int(math.copysign(1, dx)), target.y):
					target.x += int(math.copysign(1, dx))
				else:
					message('The ' + target.name + ' slams into something violently!')
					return

		#####################


def tree_lvlup():
	options = ['Combat', 'Tech', 'Ritual']

	while True:
		index = menu('Choose skill tree', options, SCREEN_WIDTH)
		if index is None: continue
		elif index is 0:
			if ctree.node_select(): break
		elif index is 1:
			if ttree.node_select(): break
		elif index is 2:
			if rtree.node_select(): break



def normal_randomize(mean,sd): #input mean, sd for gauss distribution

	floatnormal = gauss(float(mean),float(sd)) #output one sample, rounded and non-negative
	if floatnormal <= 1: return 1
	return int(round(floatnormal))

def main_menu():
	global con

	while not libtcod.console_is_window_closed():
		#show options and wait for the player's choice
		choice = menu('', ['Play a new game', 'Continue last game', 'Quit'], 24)

		if choice == 0:  #new game
			ccreation = Ccreation()
			ccreation.run_creation()

			initialize_player()
			libtcod.console_clear(con)
			new_game()
			play_game()
		if choice == 1:  #load last game
			try:
				load_game()
			except:
				msgbox('\n No saved game to load.\n', 24)
				continue
			play_game()
		elif choice == 2:  #quit
			break

def save_game():
	#open a new empty shelve (possibly overwriting an old one) to write the game data
	file = shelve.open('savegame', 'n')
	file['map'] = map
	file['objects'] = objects
	file['player_index'] = objects.index(player)  #index of player in objects list
	file['inventory'] = inventory
	file['game_msgs'] = game_msgs
	file['game_state'] = game_state
	file['dungeon_level'] = dungeon_level
	file['stairs_index'] = objects.index(stairs)
	file.close()
 
def load_game():
	#open the previously saved shelve and load the game data
	global map, objects, player, inventory, game_msgs, game_state, dungeon_level, stairs

	file = shelve.open('savegame', 'r')
	map = file['map']
	objects = file['objects']
	player = objects[file['player_index']]  #get index of player in objects list and access it
	inventory = file['inventory']
	game_msgs = file['game_msgs']
	game_state = file['game_state']
	dungeon_level = file['dungeon_level']
	stairs = objects[file['stairs_index']]
	file.close()

	initialize_fov()

def play_game():
	global key, mouse

	player_action = None
	key = libtcod.Key()
	mouse = libtcod.Mouse()

	render_all()
	lovemessage = ['the game begins','some kind of lore goes here',"but for now its a placeholder","placeholder placeholder"]
	textbox(lovemessage)

	while not libtcod.console_is_window_closed():


		libtcod.console_flush() # draws the screen
		for object in objects:
			object.clear()

		check_lvlup()


		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS,key,mouse)
		render_all()


		player_action = handle_keys()
		if game_state == 'playing' and player_action != 'didnt-take-turn':
			for object in objects:
				if object.ai:
					object.ai.take_turn()


		if player_action == 'exit':
			save_game()
			clear_game()
			break

def check_lvlup():
	lvlup_xp = LEVEL_UP_BASE + (player.lvl * LEVEL_UP_FACTOR)
	if player.fighter.xp >= lvlup_xp:
		player.lvl += 1
		player.fighter.xp -= lvlup_xp
		message('Your battle skills grow stronger! You reached level ' + str(player.lvl) + '!', libtcod.yellow)

		choice = None
		while choice == None:  #keep asking until a choice is made
			choice = menu('Level up! Choose a stat to raise:\n',
				['Constitution (+20 HP, from ' + str(player.fighter.max_hp) + ')',
				'Strength (+1 attack, from ' + str(player.fighter.power) + ')',
				'Agility (+1 armor, from ' + str(player.fighter.armor) + ')'], LEVEL_SCREEN_WIDTH)

		if choice == 0:
			player.fighter.max_hp += 20
			player.fighter.hp += 20
		elif choice == 1:
			pass
		elif choice == 2:
			player.fighter.armor += 1

def get_equipped_in_slot(slot):  #returns the equipment in a slot, or None if it's empty
	for obj in inventory:
		if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
			return obj.equipment
	return None

def get_all_equipped(obj):  #returns a list of equipped items
	if obj == player:
		equipped_list = []
		for item in inventory:
			if item.equipment and item.equipment.is_equipped:
				equipped_list.append(item.equipment)
		return equipped_list
	else:
		return []  #other objects have no equipment

def next_level():
	global dungeon_level, con
	dungeon_level += 1
	message('You descend further into the bowels of the earth.', libtcod.dark_violet)
	make_map()
	libtcod.console_clear(con)

	initialize_fov()
	
def handle_keys():
	global key

	if key.vk == libtcod.KEY_ENTER and key.lalt:
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

	elif key.vk == libtcod.KEY_ESCAPE:

		return 'exit' # exit game

	#movement
	if game_state == 'playing':

		if key.vk == libtcod.KEY_KP8:
			player_move_or_attack(0,-1)

		elif key.vk == libtcod.KEY_KP2:
			player_move_or_attack(0,1)

		elif key.vk == libtcod.KEY_KP4:
			player_move_or_attack(-1,0)

		elif key.vk == libtcod.KEY_KP6:
			player_move_or_attack(1,0)

		elif key.vk == libtcod.KEY_KP9:
			player_move_or_attack(1,-1)

		elif key.vk == libtcod.KEY_KP7:
			player_move_or_attack(-1,-1)

		elif key.vk == libtcod.KEY_KP1:
			player_move_or_attack(-1,1)

		elif key.vk == libtcod.KEY_KP3:
			player_move_or_attack(1,1)

		elif key.vk == libtcod.KEY_KP5:
			pass

		else:
			key_char = chr(key.c)
			############################ ENTER OTHER KEY COMMANDS HERE WITH if key_char == blahblah
			#if key_char == chr(key.i):
			#	inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
			if key_char == 'g':
				for object in objects:
					if object.x == player.x and object.y == player.y and object.item:
						object.item.pick_up()

			elif key_char == 'e':
				if key.shift: # E (SHIFT E) prompts you to equip an item
					chosen_equipment = action_equip_menu('Choose an item to equip:\n')
					if chosen_equipment is None:
						msgbox('Unable to equip.')
					else:
						chosen_equipment.equip('player')

				else: # e shows equipped items
					chosen_item = equipment_menu('Press a key for more options, or any other to cancel.\n')
					if chosen_item is None:
						pass
					elif chosen_item is 'empty':
						msgbox('No item there! Press E to equip something.')
					else:
						chosen_item.equip_options()

			# elif key_char == ']':
			# 	raise ValueError(get_equipped_in_slot('right hand').is_equipped)

			elif key_char == 'z':
				ability_choices = [ability for ability in player.player.abilities]
				choice = menu('Press a key for an ability, or any other to cancel.', ability_choices, SCREEN_WIDTH/2)

				if choice is not None:
					if ability_choices[choice] == 'kicklaunch':
						player.abl_kicklaunch()

			elif key_char == 'a':
				chosen_item = inventory_menu('Press the key next to an item to use it.\n')
				if chosen_item is not None:
					chosen_item.use()
					


			elif key_char == 'i':
				#show the inventory
				chosen_item = inventory_menu('Press the key next to an item for more options, or any other to cancel.\n')
				if chosen_item is not None:
					chosen_item.item_options()

			elif key_char == 'd':
				#show the inventory; if an item is selected, drop it
				chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
				if chosen_item is not None:
					chosen_item.drop()

			elif key_char == '.' and key.shift:
				if player.x == stairs.x and player.y == stairs.y:
					next_level()
				else:
					message("You can't go down here!")

			elif key_char == 'c':
				#show character information
				level_up_xp = LEVEL_UP_BASE + player.lvl * LEVEL_UP_FACTOR
				msgbox('Character Information\n\nLevel: ' + str(player.lvl) + '\nExperience: ' + str(player.fighter.xp) +
					'\nExperience to level up: ' + str(level_up_xp) + '\n\nMaximum HP: ' + str(player.fighter.max_hp) +
					'\nAttack: ' + str(player.fighter.power) + '\nDefense: ' + str(player.fighter.armor), CHARACTER_SCREEN_WIDTH)


			return 'didnt-take-turn'

def make_map():
	global map, objects, stairs, player

	map = [[Tile(True)
		for y in range(MAP_HEIGHT)]
			for x in range(MAP_WIDTH)]

	rooms = []
	objects = [player]
	num_rooms = 0
	for r in range(MAX_ROOMS):
		w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
		h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)

		x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
		y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)

		new_room = Rect(x,y,w,h)

		failed = False
		for other_room in rooms:
			if new_room.intersect(other_room):
				failed = True
				break

		if not failed:
			create_room(new_room)
			place_objects(new_room)
			(new_x,new_y) = new_room.center()

			if num_rooms == 0:
				player.x = new_x
				player.y = new_y

			else:
				(prev_x,prev_y) = rooms[num_rooms-1].center()
				if libtcod.random_get_int(0,0,1) == 1:
					create_h_tunnel(prev_x, new_x, prev_y)
					create_v_tunnel(prev_y, new_y, new_x)
				else:
					create_v_tunnel(prev_y, new_y, new_x)
					create_h_tunnel(prev_x, new_x, prev_y)

			rooms.append(new_room)
			num_rooms += 1
	stairs = Object(new_x,new_y,'>', 'stairs', libtcod.white, ignore_fov = True)
	objects.append(stairs)
	stairs.send_to_back()

	place_items_in_level()

def create_item_rngtable(depth_level = 1): # this gonna get modified to shit before this is over
	output_items = []					# returns list of (OBJECT)items to spawn in a dungeon level by calling get_random_item on a normal distribution of depthlevels
	mean_items = 7 + depth_level  * 3

	maxdepth = 1
	for iobj in get_full_item_list():
		if iobj.item.depth_level > maxdepth: maxdepth = iobj.item.depth_level

	number_of_items = normal_randomize(mean_items, mean_items * 0.5) # chooses number of items to be created in a given dungeonlvl
	if number_of_items <= 5: number_of_items = 5
	for index in range(number_of_items):
		item_depthlevel = normal_randomize(depth_level, 0.5 ** depth_level) # for each item, chooses a depth level in a gauss curve

		if item_depthlevel > maxdepth: item_depthlevel = maxdepth

		randomized_item = get_random_item_of_depthlevel(item_depthlevel) 
		output_items.append(randomized_item)

	return output_items

def get_items_of_depthlevel(desired_depth = 1):
	itemlist = get_full_item_list() # gets all the items of a desired depth level -- RETURNS ITEM OBJECTS
	depth_items = []
	for item_obj in itemlist:
		if item_obj.item.depth_level == desired_depth:
			depth_items.append(item_obj)
	return depth_items

def get_random_item_of_depthlevel(desired_depth = 1):
	itemlist = get_items_of_depthlevel(desired_depth)
	itemdict = {}
	for item in itemlist:
		itemdict[item.name] = 1 # can change this later with an item rarity attribute in object.item to weight it

	choice = random_choice(itemdict)
	choice = generate_item(choice,0,0)
	return choice # returns the item OBJECT (ITEM.OWNER)

def place_items_in_level():
	global objects
	i = 0
	items_to_place = create_item_rngtable(dungeon_level)
	while i < len(items_to_place):
		x = libtcod.random_get_int(0, 1, MAP_WIDTH-1)
		y = libtcod.random_get_int(0, 1, MAP_HEIGHT-1)
		if not is_blocked(x,y):
			items_to_place[i].x = x
			items_to_place[i].y = y
			objects.insert(0, items_to_place[i])
			i += 1

def get_full_item_list():
	itemlist = []
	for itemname in catalog.FULL_INAMELIST:
		item_obj = generate_item(itemname,0,0)
		itemlist.append(item_obj)
	return itemlist

def render_all():
	global fov_map, color_dark_wall, color_light_wall
	global color_dark_ground, color_light_ground
	global fov_recompute

	if fov_recompute:
		fov_recompute = False
		libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

	for y in range(MAP_HEIGHT):
		for x in range(MAP_WIDTH):
			visible = libtcod.map_is_in_fov(fov_map, x, y)
			wall = map[x][y].block_sight
			special = map[x][y].special
			if not visible:
				if map[x][y].explored:
					if wall:
						libtcod.console_put_char_ex(con, x, y, '#', color_dark_wall, libtcod.black)
					else:
						libtcod.console_put_char_ex(con, x, y, '.', color_dark_ground, libtcod.black)
					if special and wall:
						libtcod.console_put_char_ex(con, x, y, special.char, color_dark_wall, libtcod.black)
					elif special and not wall:
						libtcod.console_put_char_ex(con, x, y, special.char, color_dark_ground, libtcod.black)

			else: #it's visible
				if wall:
					libtcod.console_put_char_ex(con, x, y, '#', color_light_wall, libtcod.black)
				else:
					libtcod.console_put_char_ex(con, x, y, '.', color_light_ground, libtcod.black)
				if special:
					libtcod.console_put_char_ex(con, x, y, special.char, special.foreground, special.background)


				map[x][y].explored = True


	for object in objects:
		object.draw()

	player.draw()

	#blits the content of the 'con' console to the root console
	libtcod.console_blit(con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0, 0)


	libtcod.console_set_default_background(panel, libtcod.black)
	libtcod.console_clear(panel)
	#print game messages, one line at a time
	y = 1
	for (line, color) in game_msgs:
		libtcod.console_set_default_foreground(panel,color)
		libtcod.console_print_ex(panel,MSG_X, y, libtcod.BKGND_NONE, libtcod. LEFT, line)
		y += 1

	render_bar(1, 1, BAR_WIDTH, 'Health', player.fighter.hp, player.fighter.max_hp, libtcod.dark_red, libtcod.darkest_red) # display health
	libtcod.console_print_ex(panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon level ' + str(dungeon_level))  #display dungeon level

	
	#blits the content of the 'panel' console to the root console
	libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

def clear_screen():
	clearer = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
	for y in range(SCREEN_HEIGHT):
		for x in range(SCREEN_WIDTH):
			libtcod.console_put_char_ex(con, x, y, ' ', color_dark_wall, libtcod.black)
			libtcod.console_blit(clearer,0,0,0,0,0,0,0)

def create_room(room):
	global map
	for x in range(room.x1+1,room.x2):
		for y in range(room.y1+1,room.y2):
			map[x][y].blocked = False
			map[x][y].block_sight = False

def random_choice_index(chances):  #choose one option from list of chances, returning its index
	#the dice will land on some number between 1 and the sum of the chances
	if chances == []: return 0
	dice = libtcod.random_get_int(0, 0, sum(chances)) #getting a [] from random_choice  < get_random_item_of_depthlevel

 
	#go through all chances, keeping the sum so far
	running_sum = 0
	choice = 0
	for w in chances:
		running_sum += w         
 
		#see if the dice landed in the part that corresponds to this choice
		if dice <= running_sum:
			return choice 
		choice += 1


def random_choice(chances_dict):
	#choose one option from dictionary of chances, returning its key
	chances = chances_dict.values()
	strings = chances_dict.keys()
	return strings[random_choice_index(chances)]  #here lies a bug that took a newbie a full beautiful sunday to squash, rip in piss

def create_h_tunnel(x1,x2,y):
	global map
	for x in range(min(x1,x2),max(x1,x2)+1):
		map[x][y].blocked = False
		map[x][y].block_sight = False

def create_v_tunnel(y1,y2,x):
	global map
	for y in range(min(y1,y2),max(y1,y2)+1):
		map[x][y].blocked = False
		map[x][y].block_sight = False

def generate_item(name, x, y): #RETURNS HIGHEST OBJECT, NOT ITEM OR EQUIP COMPONENT
	if name == 'healing salve':  #only basic stats go here, for special functions and descriptions go to catalog
		item_component = Item(weight = 0.5, depth_level = 1, use_function = pot_heal, itemtype = 'salve')
		item = Object(x, y, '!', name, libtcod.violet, None, None, None, item = item_component)
	elif name == 'pipe gun':
		item_component = Item(weight = 1, depth_level = 2, use_function = consumable_pipegun, itemtype = 'gadget')
		item = Object(x, y, '?', name, libtcod.light_blue, None, None, None, item = item_component)
	elif name == 'crude grenade':
		item_component = Item(weight = 1, depth_level = 2, use_function = consumable_crudenade, itemtype = 'gadget')
		item = Object(x, y, '?', name, libtcod.dark_red, None, None, None, item = item_component)
	elif name == 'scrap metal sword':
		item_component = Item(weight = 10, depth_level = 1)
		special_component = EqSpecial(on_atk_bonus = {'str bonus':0.3})
		equipment_component = Equipment(slot='right hand', base_dmg = [2,6], special = special_component)
		item = Object(x, y, '/', name, libtcod.desaturated_blue, item = item_component, equipment=equipment_component)
	elif name == 'metal plate':
		item_component = Item(weight = 5, depth_level = 2)
		equipment_component = Equipment(slot='left hand', armor_bonus = 3, dodge_bonus = 2)
		item = Object(x, y, '[', name, libtcod.light_grey, item = item_component, equipment=equipment_component)
	elif name == 'goat leather sandals':
		item_component = Item(weight = 2, depth_level = 2)
		equipment_component = Equipment(slot='boots', dodge_bonus = 2)
		item = Object(x, y, '[', name, libtcod.dark_sepia, item = item_component, equipment=equipment_component)

	return item

def generate_tile(name, x, y):
	if name == 'jagged rock':
		special_component = SpTile(',', libtcod.white, libtcod.black, onwalk_effect = {'damage':2})
		tile = Tile(False, None, special_component)
	return tile

def generate_monster(name, x, y):
	if name == 'crazed mutt':
		fighter_component = Fighter(hp = 10, armor = 0, power = 4, xp = 10, death_function = monster_death)
		ai_component = DumbMonster()
		monster = Object(x, y, 'd', name, libtcod.lighter_red, blocks = True, fighter = fighter_component, ai = ai_component)
	elif name == 'mad hermit':
		fighter_component = Fighter(hp = 15, armor = 1, power = 6, xp = 25, death_function = monster_death)
		ai_component = DumbMonster()
		monster = Object(x, y, 'h', name, libtcod.lighter_red, blocks = True, fighter = fighter_component, ai = ai_component)

	return monster

def place_objects(room):
	num_monsters = libtcod.random_get_int(0,0,MAX_ROOM_MONSTERS)

	for i in range(num_monsters):
		x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
		y = libtcod.random_get_int(0, room.y1+1, room.y2-1)
		if not is_blocked(x,y):
	###################### MONSTER RNG SHIT #######################
	#REDO LATER WITH FANCY PDFs
			monster_chance = {'crazed mutt': 80, 'mad hermit': 20}
			choice = random_choice(monster_chance)
			monster = generate_monster(choice,x,y)
	###################### MONSTER RNG SHIT #######################
			objects.append(monster)

	x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
	y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

def is_blocked(x,y):
	if map[x][y].blocked:
		return True
	
	for object in objects:
		if object.blocks and object.x == x and object.y == y:
			return True

	return False

def product(iterable):
	if hasattr(iterable, '__iter__'):
		p = 1
		for n in iterable:
			p *= n
		return p
	else: return iterable

def player_move_or_attack(dx,dy):
	global fov_recompute

	x = player.x + dx
	y = player.y + dy

	target = None
	for obj in objects:
		if obj.fighter and obj.x == x and obj.y == y:
			target = obj
			break


	if target is not None:
		player.fighter.attack(target)
	else:
		player.move(dx,dy)
		fov_recompute = True

def player_death(player):

	global game_state
	message('You died')
	game_state = 'dead'

	player.char = '%'
	player.color = libtcod.dark_red

def monster_death(monster):
	message('The ' + monster.name + ' dies, gurgling blood.')
	monster.char = '%'
	monster.color = libtcod.dark_red
	monster.blocks = False
	monster.fighter = None
	monster.ai = None
	monster.name = 'remains of ' + monster.name
	monster.send_to_back()

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
	bar_width = int(float(value) / maximum * total_width)

	libtcod.console_set_default_background(panel, back_color)
	libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)


	libtcod.console_set_default_background(panel, bar_color)
	if bar_width > 0:
		libtcod.console_rect(panel,x,y,bar_width, 1, False, libtcod.BKGND_SCREEN)

	libtcod.console_set_default_foreground(panel, libtcod.white)
	libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER, name + ': ' + str(value) + '/' + str(maximum))

def message(new_msg, color = libtcod.white):
	new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

	for line in new_msg_lines:
		if len(game_msgs) == MSG_HEIGHT:
			del game_msgs[0]

		game_msgs.append( (line, color) )

def initialize_fov():
	global fov_recompute, fov_map
	fov_recompute = True
	fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)

	for y in range(MAP_HEIGHT):
		for x in range(MAP_WIDTH):
			libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)

def displayinv():
	return filter(lambda x: x.equipment not in get_all_equipped(player), inventory)

def inventory_menu(header):
	inv = displayinv()

	if len(inv) == 0:
		options = ['You have NOTHING!']
	else:
		options = []
		for item in inv:
				text = item.item.dname
				options.append(text)

	index = menu(header, options, INVENTORY_WIDTH)

	if index is None or len(inv) == 0: return None
	return inv[index].item # RETURNS ITEM - RETURNS ITEM

def action_equip_menu(header):
	options = []
	output_item = []
	inv = displayinv()
	for item in inv:
		if item.equipment and item.equipment.is_equipped == False:
			options.append(item.item.dname)
			output_item.append(item)

	if len(options) == 0:
		return None
	else:
		index = menu(header, options, INVENTORY_WIDTH)

	if index is None: return None
	return output_item[index].equipment

def equipment_menu(header):
	options = []
	outputitem = []
	check = False
	for slot in catalog.SLOTLIST: #Loops through objects for equipped item in a slot, returning 'empty' if there is none
		equipment = get_equipped_in_slot(slot)
		if equipment == None:
			outputitem.append('empty')
			options.append(slot + ':     - ')
		else:
			outputitem.append(equipment)
			options.append(slot + ':    ' + equipment.owner.item.dname)	

	index = menu(header, options, INVENTORY_WIDTH)

	if index is None: return None
	elif outputitem[index] == 'empty': return 'empty'
	elif outputitem[index] != 'empty': return outputitem[index] # RETURNS EQUIPMENT COMPONENT INSTANCE

def textbox(lines): # takes text as a list of (str)lines and displays it
	width = 0
	if type(lines) is list:
		for line in lines:
			if len(line) > width:
				width = len(line)
	else:
		width = len(lines)

	width += 6
	height = len(lines) + 4
	if type(lines) is not list:
		height = 5

	window = libtcod.console_new(width, height)

	y = 2
	if type(lines) is list:
		for line in lines:
			libtcod.console_print_rect_ex(window, 3, y, width, height, libtcod.BKGND_DEFAULT, libtcod.LEFT, line)
			y += 1

	else:
		libtcod.console_print_rect_ex(window, 1, y, width, height, libtcod.BKGND_DEFAULT, libtcod.LEFT, lines)

	x = SCREEN_WIDTH/2 - width/2
	y = SCREEN_HEIGHT/2 - height/2
	libtcod.console_print_frame(window,0, 0, width, height, clear=False, flag=libtcod.BKGND_DEFAULT)
	libtcod.console_blit(window,0,0,width,height,0,x,y,1.0,1.0)
	libtcod.console_flush()
	ignore = libtcod.console_wait_for_keypress(True)

	libtcod.console_clear(window)
	libtcod.console_blit(window,0,0,width,height,0,x,y,1.0,1.0)
	

def menu(header, options, width):
	if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')
	header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
	height = len(options) + header_height

	window = libtcod.console_new(width, height)

	libtcod.console_set_default_foreground(window, libtcod.white)
	libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)


	y = header_height
	letter_index = ord('a')
	for option_text in options:
		text = '(' + chr(letter_index) + ') ' + option_text
		libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)

		y += 1
		letter_index += 1

	x = SCREEN_WIDTH/2 - width/2
	y = SCREEN_HEIGHT/2 - height/2
	libtcod.console_blit(window,0,0,width,height,0,x,y,1.0,1.0)

	libtcod.console_flush()
	key = libtcod.console_wait_for_keypress(True)

	index = key.c - ord('a')
	if index >= 0 and index < len(options): 
		libtcod.console_clear(window)
		return index
	return None


def msgbox(message, width=50):
	menu(message, [], width)

def initialize_player():
	global player
	player_component = Player()
	fighter_component = Fighter(hp=30, armor = 3, power=3, xp = 0, death_function = player_death)
	player = Object(0,0, '@', 'player', libtcod.white, blocks = True, fighter = fighter_component, player = player_component)
	player.lvl = 1

def target_tile(max_range = None):
	global objects

	message('Choose a target - ESC to cancel.', libtcod.red)
	targeter = Object(player.x, player.y, '+', 'targeter', libtcod.red,ignore_fov = True)
	objects.append(targeter)
	

	while True:

		render_all()
		targeter.send_to_front()
		targeter.clear()
		libtcod.console_flush()
		keyb = libtcod.console_wait_for_keypress(True)
	
		

		if keyb.vk == libtcod.KEY_KP8:
			targeter.unblocked_move(0,-1)

		elif keyb.vk == libtcod.KEY_KP2:
			targeter.unblocked_move(0,1)

		elif keyb.vk == libtcod.KEY_KP4:
			targeter.unblocked_move(-1,0)

		elif keyb.vk == libtcod.KEY_KP6:
			targeter.unblocked_move(1,0)

		elif keyb.vk == libtcod.KEY_KP9:
			targeter.unblocked_move(1,-1)

		elif keyb.vk == libtcod.KEY_KP7:
			targeter.unblocked_move(-1,-1)

		elif keyb.vk == libtcod.KEY_KP1:
			targeter.unblocked_move(-1,1)

		elif keyb.vk == libtcod.KEY_KP3:
			targeter.unblocked_move(1,1)

		elif keyb.vk == libtcod.KEY_KP5:
			pass

		elif (keyb.vk == libtcod.KEY_ENTER and libtcod.map_is_in_fov(fov_map, targeter.x, targeter.y) and (max_range is None or player.distance_to(targeter) <= max_range)):

			targeter.clear()
			objects.remove(targeter)
			return (targeter.x, targeter.y)

		elif (keyb.vk == libtcod.KEY_ENTER and not libtcod.map_is_in_fov(fov_map, targeter.x, targeter.y)):
			message('You cannot target there!', libtcod.grey)


		elif keyb.vk == libtcod.KEY_ESCAPE:
			targeter.clear()
			objects.remove(targeter)
			return (None, None)

def closest_monster(max_range):
	#find closest enemy, up to a maximum range, and in the player's FOV
	closest_enemy = None
	closest_dist = max_range + 1  #start with (slightly more than) maximum

	for object in objects:
		if object.fighter and not object == player and libtcod.map_is_in_fov(fov_map, object.x, object.y):
		#calculate distance between this object and the player
			dist = player.distance_to(object)
			if dist < closest_dist:  #it's closer, so remember it
				closest_enemy = object
				closest_dist = dist
	return closest_enemy

def random_adj_target():
	adjacents = []
	for object in objects:
		if object.distance_to(player) < 2 and object.fighter and not object == player: adjacents.append(object)

	if adjacents == []: 
		return None
	else: 
		choice = libtcod.random_get_int(0,0,len(adjacents)-1)

	return adjacents[choice]


 
def target_monster(max_range=None):
	
	while True:
		(x, y) = target_tile(max_range)
		if x is None:  #player cancelled
			return None

	
		for obj in objects:
			if obj.x == x and obj.y == y and obj.fighter and obj != player:
				return obj

		message('Nothing to target there!', libtcod.grey)

def clear_game():
	global objects, inventory

	for object in objects:
		object.clear()
		objects.remove(object)
	for item in inventory:
		inventory.remove(item)

	clear_screen()

def new_game():
	global player, game_msgs, game_state, inventory, dungeon_level, namekeeper
	
	dungeon_level = 1
	make_map()
	initialize_fov()

	game_state = 'playing'
	inventory = []
	namekeeper = {}

	#create the list of game messages and their colors, starts empty
	game_msgs = []

	

def pot_heal():
	if player.fighter.hp == player.fighter.max_hp:
		message('You are at full health already!')
		return 'cancelled'

	message('Your wounds start to feel better.')
	player.fighter.heal(POTHEAL_AMOUNT)

def draw_laser(origin, end, char, color):
	line = graphical.createline(origin, end)

	linecon = console_from_twopts(origin, end)
	libtcod.console_set_default_foreground(linecon, color)
	for point in line:
		libtcod.console_put_char(linecon,int(point.x), int(point.y), char, libtcod.BKGND_NONE)

	libtcod.console_blit(linecon, 0, 0, 0, 0, 0, min(origin.x, end.x), min(origin.y, end.y), 1, 0)
	libtcod.console_flush()

	libtcod.sys_sleep_milli(50)

def console_from_twopts(origin, end):
	width = abs(max(origin.x, end.x) - min(origin.x, end.x)) + 1
	height = abs(max(origin.y, end.y) - min(origin.y, end.y)) + 1

	return libtcod.console_new(width, height)

def consumable_pipegun():
	monster = target_monster(20)
	if monster is None:
		return 'cancelled'
	else:
		message('The slug explodes out of the flimsy gun with a loud thunder and strikes the ' + monster.name + '! The damage is '+ str(LIGHTNING_DAMAGE) + ' hit points.', libtcod.light_blue)
		monster.fighter.take_damage(LIGHTNING_DAMAGE)
		draw_laser(player, monster, graphical.determine_projchar(player, monster), libtcod.light_blue)

def consumable_crudenade():
	(x, y) = target_tile()
	if x is None: return 'cancelled'
	message('The grenade explodes, spraying everything within ' + str(FIREBALL_RADIUS) + ' tiles with shrapnel!', libtcod.orange)

	for obj in objects:  #damage every fighter in range, including the player
		if obj.distance(x, y) <= FIREBALL_RADIUS and obj.fighter:
			message('The ' + obj.name + ' gets burned for ' + str(FIREBALL_DAMAGE) + ' hit points.', libtcod.orange)
			obj.fighter.take_damage(FIREBALL_DAMAGE)


def pass_node_requirements(node):
	if node == 'shield focus':
		if ctree.level >= 1: return True
	else: return False




libtcod.console_set_custom_font('terminal10x16_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)




main_menu()













