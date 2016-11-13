import libtcodpy as libtcod
import math
import textwrap
import shelve
import catalog
import graphical
from random import gauss, uniform

#TODO: big todos:
#TODO: Graphical effects(floating text, floating numbers maybe, blood, buff effects)##floating text done
#TODO: map generation
#TODO: some actual interesting enemies, AI
#TODO: staves, ranged weapons, polearms, cudgels
#TODO: more weapons, more enemies, more consumables
#TODO: fill out skill, perk trees
#TODO: subskill system***

#window size
SCREEN_WIDTH = 120
SCREEN_HEIGHT = 60


#map size
MAP_WIDTH = 160
MAP_HEIGHT = 150

CAMERA_WIDTH = 80
CAMERA_HEIGHT = 50
FREEMOVE_WIDTH = 15
FREEMOVE_HEIGHT = 10

#GUI parameters
BAR_WIDTH = 20
PANEL_HEIGHT = 10
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1

#map gen parameters
MAX_ROOM_MONSTERS = 3
ROOM_MAX_SIZE = 25  # ALL TO BE CHANGED LATER OF COURSE
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

class DrawingDir(object): #singleton drawdir
	def __init__(self): #keeps record of ritual drawings on the ground that are not yet activated, since I want the player to be able to have multiple of them set up at once
		self.drawinglist = []


class RitualDraw(object): #each drawing main body is represented by this
	def __init__(self, originx, originy):
		self.length = 1
		self.originx = originx
		self.originy = originy
		self.drawntile_list = []
		self.concluded = False


	def add_drawntile(self, tile): #list of gamemap tiles involved
		self.drawntile_list.append(tile)




class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y



class PlayerActionReport(object): #singleton, director
	def __init__(self, action = None, x1 = None, y1 = None, x2 = None, y2 = None, objects = None, action_extra = None, takes_turn = True):
		self.action = action
		self.action_extra = action_extra   #
		self.takes_turn = takes_turn       #
#ACTIONS: move, attack, start drawing, stop drawing, drop item, equip item, use item

		self.x1 = x1                       #This object reports on the last action taken by the player, as well as keeping a record of the last 50 actions in a list(number decided in add_to_recorder),
		self.y1 = y1                       #Remember to add a director update call to every player action that takes a turn
		self.x2 = x2                       #
		self.y2 = y2                       #
		self.objects = objects             #
		self.recorder = []                 #

	def __dir__(self):
		return ['action', 'x1', 'y1', 'y2', 'x2', 'objects', 'action_extra', 'takes_turn']

	def update(self, **kwargs):#kwarg keywords must be attributes. This function updates the director singleton with the attributes passed, then sets all of its other attributes to standard values defined at the bottom(or none if there are no defaults)
		global director
		for keyword, value in kwargs.iteritems():
			setattr(self, keyword, value)

		attrlist = [attr for attr in dir(self)]
		setnone = filter(lambda x: x not in kwargs, [attr for attr in dir(self)])
		for attrname in setnone:
			try: setattr(self, attrname, None)
			except: raise ValueError('Something has gone wrong with the game director. Check what got passed through director.update', attrname, setnone, dir(self))

		if 'takes_turn' not in kwargs: self.takes_turn = True
		if 'x1' not in kwargs: self.x1 = player.x
		if 'y1' not in kwargs: self.y1 = player.y

		self.add_to_recorder()

	def add_to_recorder(self):
		record_dict = {}
		for attribute in dir(self):
			record_dict[attribute] = self.__dict__[attribute]
		self.recorder.append(record_dict)
		if len(self.recorder) > 50: self.recorder.pop(0) #rolling list







class SkillTree:
	def __init__(self, stype, level = 0):
		self.stype = stype
		self.level = level
		self.nodetable = catalog.get_nodetable(stype)

	def get_node_from_name(self, name):
		for node in self.nodetable:
			if node.name == name: return node


	def get_available_nodes(self):
		available_nodes = []
		for node in self.nodetable:
			if (node.parent == [] or node.parent == '' or check_if_node_leveled(self, node.parent)) and not node.leveled: 
				available_nodes.append(node)
		if available_nodes == []: textbox('No nodes to select.')
		else: return available_nodes



	def node_select(self):
		width = SCREEN_WIDTH
		height = SCREEN_HEIGHT
		ended = False

		skillbox = libtcod.console_new(width, height)
		options = self.get_available_nodes()
		letter_index = ord('a')
		y=2
		libtcod.console_print_frame(skillbox,0, 0, width, height, clear=False, flag=libtcod.BKGND_DEFAULT) #god i hate making menus

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
				if pass_perk_requirements(node) and (node.parent == [] or node.parent == '' or check_if_node_leveled(self, node.parent)) and not node.leveled: 
					available_nodes.append(node)
		if available_nodes == []: textbox('No nodes to select.')
		else: return available_nodes



#SKILL TREE DATA STRUCTURE:
#One SkillTree (perktree inherited for perks) object for each type (combat, tech, ritual, perks), each containing appropriate nodetable objects gotten from the catalog
#abilities are passed on to the player in the Player's abilities property whenever they are called (getter decorator)
#haven't done passive bonuses yet



class Ccreation: #singleton, ccreation
#character creation code is a bit of a mess here, but it should be understandable if you go through it line by line
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
			#initalize player later here
			
		#return Player(self.chosenrace, self.chosengclass,)

	def statbox(self,choice): # draws stat box(bottom half)
		width = SCREEN_WIDTH -6
		height = SCREEN_HEIGHT/2 -2

		statsbox = libtcod.console_new(width, height)
		libtcod.console_print_frame(statsbox,0, 0, width, height, clear=False, flag=libtcod.BKGND_DEFAULT)
		try: statblock = catalog.ccreation_stats(choice) ## text for the statblock, comes in a list of strings
		except: statblock = ["this description hasn't been written yet!"]
		for line in statblock:
			libtcod.console_print_ex(statsbox, 1, statblock.index(line)+1,libtcod.BKGND_NONE, libtcod.LEFT, line)
		libtcod.console_print_ex(statsbox, 1, 60, libtcod.BKGND_NONE, libtcod.LEFT, 'Press enter to accept selection')

		libtcod.console_blit(statsbox, 0, 0, 0, 0, 0, 2, height + 2) #creates and prints to the statbox that takes up the lower half of the screen in char creation

	def descriptionbox(self,choice): #draws description box (top right)
		width = SCREEN_WIDTH/3 - 2 
		height = SCREEN_HEIGHT/2

		description_box = libtcod.console_new(width, height)
		libtcod.console_set_alignment(description_box, libtcod.CENTER)
		try: text = catalog.ccreation_description(choice)  # remove this try clause when i no longer have placeholder classes/racest/etc
		except: text = "this description hasn't been written yet!"
		libtcod.console_print_rect(description_box, width/2+2, height*2/3, width-5, height, text)
		libtcod.console_print_frame(description_box,0, 0, width, height, clear=False, flag=libtcod.BKGND_DEFAULT)

		libtcod.console_blit(description_box, 0, 0, 0, 0, 0, (width*2)+2, 0) #creates and prints to the description box that takes up the upper left side of the screen in char creation

	def choicebox(self):
		width = (SCREEN_WIDTH*2)/3+1
		height = SCREEN_HEIGHT/2
		menu_selection = libtcod.console_new(width, height)                                       #
		letter_index = ord('a')                                                                   #
		y = 2                                                                                     #
		x = 2                                                                                     #
		if self.stage == 'race select':                                                           #
			requested_list = catalog.FULL_RACELIST                                                #
		elif self.stage == 'class select':                                                        #
			requested_list = catalog.FULL_GCLASSLIST                                              #
#                                                                                                 # all menu creation stuff copy pasta-ed from menu method
		for option_text in requested_list:                                                        #
			text = ' ' + chr(letter_index) +'  -  ' + option_text                                 #
			libtcod.console_print_ex(menu_selection, x, y, libtcod.BKGND_NONE, libtcod.LEFT, text)#
#                                                                                                 #
			y += 2                                                                                #
			if y > SCREEN_HEIGHT/2 - 1:                                                           #
				x += 8                                                                            #
				y = 2                                                                             #
			letter_index += 1                                                                     #

		libtcod.console_print_frame(menu_selection,0, 0, width, height, clear=False, flag=libtcod.BKGND_DEFAULT)
		libtcod.console_blit(menu_selection,0,0,0,0,0,2,0)
		libtcod.console_flush()

		key = libtcod.console_wait_for_keypress(True)


		if key.vk == libtcod.KEY_ENTER:
			if self.stage == 'race select':  # this is where the stage cycling takes place

				if self.chosenrace == 'empty': 
					msgbox("You haven't chosen a race.")
					return 'empty'
				self.stage = 'class select'
				return self.chosenrace

			elif self.stage == 'class select':
				if self.chosengclass == 'empty': 
					msgbox("You haven't chosen a class.")
					return 'empty'	
				self.stage = 'skill select'
				return self.chosengclass
		

		index = key.c - ord('a')
		if index >= 0 and index < len(requested_list): 
			return requested_list[index] ### returns the name of the chosen class or race or whatever as per catalog list
		else: return 'empty'



	




class Equipment:
	def __init__(self, owner, slot, base_dmg = [0,0], armor_bonus = 0, dodge_bonus = 0, twohand = False):
		self.slot = slot
		self.owner = owner
		self.is_equipped = False
		self.base_dmg = base_dmg
		self.dodge_bonus = dodge_bonus
		self.armor_bonus = armor_bonus
		self.twohand = twohand
		self.special = None


		self.add_base_specials()

	def equip(self,equipper):
		#equip object and show a message about it
		if equipper == 'player':
			if self.twohand and get_equipped_in_slot('left hand'): 
				message("The " + self.owner.name + ' requires both hands to use.')
				return
				
			if get_equipped_in_slot(self.slot):
				get_equipped_in_slot(self.slot).unequip()
			self.is_equipped = True
			message('Equipped ' + self.owner.item.dname + ' on your ' + self.slot + '.', libtcod.light_green)
			director.update(action = 'equip item', object_s = self.owner)


	def unequip(self):

		if not self.is_equipped: return
		self.is_equipped = False
		message('Unequipped ' + self.owner.item.dname + ' from ' + self.slot + '.', libtcod.light_yellow)
		director.update(action = 'unequip item', object_s = self.owner)

	def equip_options(self): #upon getting chosen from the equipment menu
		options = ['Examine', 'Unequip', 'Drop']
		index = menu('Choose an action: ', options, 50)
		if index == 0:
			self.owner.item.examine()
			return 'examine'

		elif index == 1:
			self.unequip()
			return 'unequip'

		elif index == 2: #drop (and unequip)
			self.unequip() # this is redundant because it's in the item drop method but i'm gonna leave it here, just in case
			self.owner.item.drop()
			return 'drop'

	def roll_dmg(self):
		if self.base_dmg == [0,0]: return 0
		else:
			return libtcod.random_get_int(0, self.base_dmg[0], self.base_dmg[1])

	def add_base_specials(self):
		self.special = catalog.EqSpecial(owner = self)


	def apply_on_atk_bonus(self, origin, target):

		bonusdmg = Dmg(0, 1, 0)
		if self.special:
			for enchant in self.special.enchantlist: #cycles through EnchantModules
				
				if enchant.name == 'str bonus':
					bonusdmg.add(origin.stats['strength'] * enchant.value)
				elif enchant.name == 'maim chance':
					if libtcod.random_get_float(0,0,1) <= enchant.value:
						target.fighter.receive_status('maim', enchant.duration)
						message('Your attack maims the enemy!', libtcod.light_blue)

		return bonusdmg





class Item:
	def __init__(self, owner, weight = 0, depth_level = 1, use_function = None, itemtype = 'gadget'):
		self.weight = weight
		self.owner = owner
		self.use_function = use_function
		self.depth_level = depth_level
		self.identified = False
		self.already_seen = False
		self.itemtype = itemtype
		if itemtype == 'trinket': self.identified = True
		#possible itemtypes: equipment, salve, gadget, trinket, heavy blade, light blade,


	def pick_up(self):
		if len(inventory)>=26:
			message('Your inventory is full')
			return False
		elif sum([item.item.weight for item in inventory]) > player.max_weight:
			message("You're carrying too much already!")
			return False
		else:
			inventory.append(self.owner)  # inventory has objects, not item
			objects.remove(self.owner)
			message('You picked up ' + self.dname + '!', libtcod.green)
			director.update(action = 'pick up item', object_s = self.owner)
			return True

	def use(self):
		if self.use_function == None:
			message('The ' + self.owner.name + ' cannot be used.')
		else:
			if self.use_function() != 'cancelled':  #conditions for persistent/charge-based consumables go here
				inventory.remove(self.owner)
				director.update(action = 'use item', object_s = self.owner)

	def drop(self):
		#add to the map and remove from the player's inventory. also, place it at the player's coordinates
		objects.insert(0,self.owner)
		inventory.remove(self.owner)
		if self.owner.equipment and self.owner.equipment.is_equipped: self.owner.equipment.unequip()
		self.owner.x = player.x
		self.owner.y = player.y
		message('You dropped a ' + self.dname + '.', libtcod.yellow)
		director.update(action = 'drop item', object_s = self.owner)

	def examine(self):
		text = catalog.get_item_description(self)
		director.update(action = 'examine item', object_s = self.owner, takes_turn = False)

		textbox(text)

	def item_options(self):
		options = ['Examine', 'Drop', 'Use']
		index = menu('Choose an action: ', options, 50)
		if index == 0:#examine
			self.examine()
			return 'examine'

		if index == 1: #drop
			self.drop() 
			return 'drop'

		if index == 2: #use
			self.use() 
			return 'use'

	@property
	def dname(self):#short for display name
		global namekeeper
		if self.owner.name in namekeeper:
			self.already_seen = True


		if not self.identified:
			if self.itemtype == 'equipment' or self.itemtype == 'heavy blade' or self.itemtype == 'light blade' or self.itemtype == 'polearm' or self.itemtype == 'staff' or self.itemtype == 'cudgel':
				unidname = 'an unidentified ' + self.owner.name
			elif self.itemtype == 'salve': 
				if not self.already_seen:
					unidname = catalog.random_salve_name(self)
					namekeeper[self.owner.name] = unidname
				else: unidname = namekeeper[self.owner.name]
			elif self.itemtype == 'gadget':
				if not self.already_seen:
					unidname = catalog.random_gadget_name(self)
					namekeeper[self.owner.name] = unidname
				else: unidname = namekeeper[self.owner.name]
			return unidname

		else: return self.owner.name

class StatusEffect(object): #TODO: STACKING BEHAVIOUR FOR STATUS EFFECTS
	def __init__(self, name, duration, affected):
		self.name = name
		self.duration = duration
		if duration == 0: self.duration = -1
		self.affected = affected

	def activate(self):
		if self.duration == 0:
			self.terminate()
		else:
			self.status_stepfunction()

	def terminate(self):
		self.affected.status.remove(self)

	def status_startfunction(self):
		if self.name == 'maim':
			return graphical.FloatingText(self.affected.owner, self.name, libtcod.violet)


	def status_stepfunction(self):
		if self.name == 'drawing': 
			drawing_function(self)


		self.duration -= 1



class Fighter:
	def __init__(self, hp, armor, power, xp,  death_function = None, depth_level = 1):
		self.max_hp = hp
		self.hp = hp
		self.base_armor = armor
		self.base_power = power
		self.death_function = death_function
		self.depth_level = depth_level
		self.xp = xp
		self.state = 'normal'
		self.status = []

		self.dodge = 0 # enemies don't usually dodge atm, so this is a hacky fix to make monsters able to attack other monsters


	def take_damage(self,damage):
		if isinstance(damage, Dmg): damage = damage.resolve()
		if damage > 0:
			self.hp -= damage
			if self.hp < 0:
				player.fighter.xp += self.xp
				function = self.death_function
				if function is not None:
					function(self.owner)

	def receive_status(self, statusname, duration):
		status = StatusEffect(statusname, duration, self)
		self.status.append(status)

	def attack(self, target):
		

		if isinstance(self.owner, Player):
			multiattack = get_multiattack_number()

			for i in range(multiattack):

				if not target.fighter: break #if target dies in between multiattacks, exit loop

				damage = self.power()
				for equip in get_all_equipped(self.owner):#equivalent to global player
					damage.add(equip.apply_on_atk_bonus(self.owner, target))
				finaldmg = damage.resolve()
				finaldmg -= target.fighter.armor

				if finaldmg < 0: finaldmg = 0

				message('You attack the ' + target.name + ' for ' + str(int(round(finaldmg))) + ' hit points.')
				target.fighter.take_damage(finaldmg)
			director.update(action = 'attack', x2 = target.x, y2 = target.y)

		else:
			if libtcod.random_get_int(0, 1, 100) > int(round(target.dodge * 1.3)):
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
			flat_bonus = 3
			equiproll = 0
			multiplicative_component = 0
			for equip in equipments: 
				equiproll += equip.roll_dmg()

			combat_flatbonus = ctree.level * 2
			flat_bonus += combat_flatbonus
			multiplicative_component += equiproll
			return Dmg(multiplicative_component, product(multipliers), flat_bonus)

		else:
			return normal_randomize(self.base_power, self.base_power/10)


	@property
	def armor(self):  #return actual defense, by summing up the bonuses from all equipped items
		bonus = sum(int(math.ceil(equipment.armor_bonus/2)) for equipment in get_all_equipped(self.owner))
		return self.base_armor + bonus
 
	@property
	def max_hp(self):  #return actual max_hp, by summing up the bonuses from all equipped items
		bonus = sum(equipment.max_hp_bonus for equipment in get_all_equipped(self.owner))
		return self.base_max_hp + bonus

                     # exemple: if attackn == 3.4, it does 3 attacks always and has a 40% chance of doing an additional attack for a total of 4

class Dmg:
	def __init__(self, multiplicative, multiplier = 1, flat = 0):
		self.multiplicative = multiplicative
		self.multiplier = multiplier
		self.flat = flat

	def add(self, *args):
		if len(args) == 3:
			self.multiplicative += args[0]
			self.multiplier *= args[1]
			self.flat += args[2]
		elif len(args) == 1:
			damage = args[0]
			if isinstance(damage, Dmg): # if argument is another damage instance, adds them together
				self.multiplicative += damage.multiplicative
				self.multiplier *= damage.multiplier
				self.flat += damage.flat
			elif type(damage) == float  or type(damage) == int:	# if argument is just a number, adds it as multiplicative
				self.multiplicative += damage

	def resolve(self):
		return self.multiplicative * self.multiplier + self.flat



class DumbMonster:  # basic AI
	def take_turn(self):
		monster = self.owner
		if monster.fighter.state == 'skip turn':
			monster.fighter.state == 'normal'
			return

		if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
			if monster.distance_to(player) >= 2 and len(monster.fighter.status) > 0:
				for status in monster.fighter.status:
					if status.name == 'maim' and status.duration % 2 == 0:
						monster.move_astar(player)

			elif monster.distance_to(player) >= 2:
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

class Camera(object):
	def __init__(self, w = CAMERA_WIDTH, h = CAMERA_HEIGHT, x=0, y=0):
		self.width = w
		self.height = h
		self.x = x
		self.y = y

	def reset_position(self, coord = 'both'):

		if coord == 'xreset' or coord == 'both': self.x = player.x - self.width/2 # less than 0 type errors get dont happen because of setter properties
		if coord == 'yreset' or coord == 'both': self.y = player.y - self.height/2 # centers camera on player
		libtcod.console_clear(con)



	def check_for_posreset(self, xdiff = FREEMOVE_WIDTH, ydiff = FREEMOVE_HEIGHT):
		centerx, centery = self.center
		if (player.x > centerx + xdiff or player.x < centerx - xdiff) and (player.y > centery + ydiff or player.y < centery - ydiff): #the ugliest code
			return 'both'

		if player.x > centerx + xdiff: return 'xreset'  
		elif player.x < centerx - xdiff: return 'xreset'
#                                                       
		if player.y > centery + ydiff: return 'yreset'  
		elif player.y < centery - ydiff: return 'yreset'
                                                        

		return False

	def camera_render(self):
		if self.check_for_posreset(): self.reset_position(self.check_for_posreset())

		for camy in range(self.height):
			mapy = self.y + camy
			for camx in range(self.width):
				mapx = self.x + camx

				visible = libtcod.map_is_in_fov(fov_map, mapx, mapy)
				wall = gamemap[mapx][mapy].block_sight
				special = gamemap[mapx][mapy].special
				if not visible:
					if gamemap[mapx][mapy].explored:
						if wall:
							libtcod.console_put_char_ex(con, camx, camy, '#', color_dark_wall, libtcod.black)           #
						else:                                                                                     #
							libtcod.console_put_char_ex(con, camx, camy, '.', color_dark_ground, libtcod.black)         # OK this looks bad but it's quite simple actually, i'm sure it could be written more elegantly with abs or something
						if special and wall:                                                                      # basically there are 3 nested rectangles: the biggest beingthe actual map where objects interact and the game happens, the second is the camera, which gets rendered to con in camera_render method
							libtcod.console_put_char_ex(con, camx, camy, special.char, color_dark_wall, libtcod.black)  # the third is a phantom FREEMOVE square which is checked in check_for_posreset and all it does is center the camera position (separately for x and y) when the player walks outside of it
						elif special and not wall:                                                                 #most of the complexity is just in juggling coordinates between camera and map, but it more or less comes down to : 
							libtcod.console_put_char_ex(con, camx, camy, special.char, color_dark_ground, libtcod.black) #mapcoord = camera_origin_coord + current_camera_coord: that's those mapx and mapy variables. works like poschengband camera
				else: #it's visible
					if wall:
						libtcod.console_put_char_ex(con, camx, camy, '#', color_light_wall, libtcod.black)
					else:
						libtcod.console_put_char_ex(con, camx, camy, '.', color_light_ground, libtcod.black)
					if special:
						libtcod.console_put_char_ex(con, camx, camy, special.char, special.foreground, special.background)
					gamemap[mapx][mapy].explored = True


	@property
	def center(self):
		centerx = self.x + self.width/2
		centery = self.y + self.height/2
		return centerx, centery

	@property
	def x2(self):
	    return self.x + self.width

	@property
	def y2(self):
	    return self.y + self.height
	
	

	@property
	def x(self):
		return self._x

	@property
	def y(self):
		return self._y
	
	@x.setter
	def x(self, value):
		if value < 0: value = 0
		if value > MAP_WIDTH - self.width: value = MAP_WIDTH - self.width
		self._x = value

	@y.setter
	def y(self, value):
		if value < 0: value = 0
		if value > MAP_HEIGHT - self.height: value = MAP_HEIGHT - self.height
		self._y = value


class SpTile:
	def __init__(self, name, char = None, foreground = None, background = None, onwalk_effect = None):
		self.name = name# 
		self.char = char                                                                        # 
		self.foreground = foreground                                                            # 
		self.background = background                                                            # 
		self.onwalk_effect = onwalk_effect                                                      # sptile is a component, similar to how equipment, items, fighter etc works
#                                                                                               # added to Tile
	def apply_onwalk(self, walker):                                                             # 
		if self.onwalk_effect and walker.fighter:                                               # 
			for effect in self.onwalk_effect:                                                   # 
				if effect == 'damage': walker.fighter.take_damage(self.onwalk_effect['damage']) # 

class Tile:
	def __init__(self, blocked, block_sight = None, special = None):
		self.blocked = blocked
		self.explored = False
		self.special = special

		#blocks sight by default if blocks movement (standard wall)
		if block_sight is None:	self.block_sight = blocked
		


		


class GameObj(object):
	def __init__(self, x, y, char, name, color, blocks = False, fighter = None, ai = None, ignore_fov = False, equipment = None, item = None):
		self.x = x
		self.y = y
		self.char = char
		self.color = color
		self.blocks = blocks
		self.name = name
		self.equipment = equipment
		self.item = item
		self.ignore_fov = ignore_fov



		if self.name in catalog.FULL_INAMELIST: self.get_item_components()



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
				libtcod.map_set_properties(fov, x1, y1, not gamemap[x1][y1].block_sight, not gamemap[x1][y1].blocked)
 
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
				if gamemap[self.x][self.y].special and gamemap[self.x][self.y].special.onwalk_effect:
					gamemap[self.x][self.y].special.apply_onwalk(self)
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
			if isinstance(self, Player):
				director.update(action = 'move', x1 = self.x-dx, y1 = self.y-dy, x2 = self.x, y2 = self.y)

		if gamemap[self.x][self.y].special and gamemap[self.x][self.y].special.onwalk_effect:
			gamemap[self.x][self.y].special.apply_onwalk(self)




	def in_camera(self):
		if camera.x <= self.x <= camera.x2 and camera.y <= self.y <= camera.y2: return True
		else: return False


	def unblocked_move(self, dx, dy):
		self.x += dx
		self.y += dy

	def draw(self):
		if (libtcod.map_is_in_fov(fov_map, self.x, self.y) or self.ignore_fov):
			libtcod.console_set_default_foreground(con, self.color)
			libtcod.console_put_char_ex(con, self.camx, self.camy, self.char, self.color, libtcod.black)

	def clear(self):
		libtcod.console_put_char_ex(con, self.camx, self.camy, ' ', libtcod.white,libtcod.black)

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

	def get_item_components(self):
		if self.name == 'healing salve':  #only basic stats go here, for special functions and descriptions go to catalog
			self.item = Item(self, weight = 0.5, depth_level = 2, use_function = pot_heal, itemtype = 'salve')
			colorchoice = check_colorkeeper(self.name)
		
		elif self.name == 'pipe gun':
			self.item = Item(self, weight = 2, depth_level = 2, use_function = consumable_pipegun, itemtype = 'gadget')
			colorchoice = check_colorkeeper(self.name)

		elif self.name == 'crude grenade':
			self.item = Item(self, weight = 1, depth_level = 2, use_function = consumable_crudenade, itemtype = 'gadget')
			colorchoice = check_colorkeeper(self.name)
			
		elif self.name == 'scrap metal sword':
			self.item = Item(self, weight = 7, depth_level = 2, itemtype = 'heavy blade')
			self.equipment = Equipment(self, slot='right hand', base_dmg = [5,7])
			
		elif self.name == 'rebar blade':
			self.item = Item(self, weight = 20, depth_level = 2,itemtype = 'heavy blade')
			self.equipment = Equipment(self, slot = 'right hand', base_dmg = [10,13],  twohand = True)
			
		elif self.name == 'kitchen knife':
			self.item = Item(self, weight = 4, depth_level = 1, itemtype = 'light blade')
			self.equipment = Equipment(self, slot='right hand', base_dmg = [3,4])
			
		elif self.name == 'metal plate':
			self.item = Item(self, weight = 5, depth_level = 2)#weapons need itemtype, but armor can just get a slot check
			self.equipment = Equipment(self, slot='left hand', armor_bonus = 3, dodge_bonus = 2)
			
		elif self.name == 'goat leather sandals':
			self.item = Item(self, weight = 2, depth_level = 2)
			self.equipment = Equipment(self, slot='feet', dodge_bonus = 2)

		elif self.name == "someone's memento":
			self.item = Item(self, weight = 0.5, depth_level = 2, itemtype = 'trinket')






	@property
	def camx(self):
		camx = self.x - camera.x
		return camx
	@property
	def camy(self):
		camy = self.y - camera.y
		return camy
	
	



class Player(GameObj):#player is inherited because it's easier since it has one instance, but other stuff is usually components
	def __init__(self, race = 'human', gclass = 'warden', stats = {'strength':5,'constitution':5,'agility':5,'intelligence':5,'attunement':5}, perks = []):
		fighter_component = Fighter(hp=30, armor = 3, power=3, xp = 0, death_function = player_death) #changed later through ccreation
		GameObj.__init__(self,0,0, '@', 'player', libtcod.white, blocks = True, fighter = fighter_component)
		self.race = race #only player-exclusive stats should go here if possible
		self.gclass = gclass #gclass for game class
		self.stats = stats
		self.perks = perks
		self.lvl = 1
		#self.abilities

		############################################################################
		#########################   ABILITY  DEFINITIONS               #############
		############################################################################

	def abl_kicklaunch(self): #return true if went through, false if its cancelled
		target = random_adj_target()
		if target == None:
			message('Nobody to kick!')
			return False
			
		dx, dy = graphical.get_increments(self, target)
		dmg = self.fighter.power(multipliers = [0.5])
		dmg = dmg.resolve()
		target.fighter.take_damage(dmg)
		message('You put all your strength behind a mighty kick, dealing ' + str(int(round(dmg))) + ' damage.', libtcod.light_red)
		
		if push(self, target, 3) < 3: message('The ' + target.name + ' slams into something violently!') 
		director.update(action = 'use ability', action_extra = 'kicklaunch', x2 = target.x, y2 = target.y)
		return True
# 		# ABILITY DISTANCE NUMBER

	def abl_fling_trinket(self, chosen_trinket = None):
		if not chosen_trinket: chosen_trinket = inventory_menu('Choose a trinket to throw:', itemtype = 'trinket') #so you can arrive here through 't' throw or 'a' ability > fling trinket..... remember inventory_menu returns None if it's cancelled
		if not chosen_trinket: return
		
	def abl_consume_trinket(self, chosen_trinket = None):
		if not chosen_trinket: chosen_trinket = inventory_menu('Choose a trinket to consume:', itemtype = 'trinket') #so you can arrive here through 't' throw or 'a' ability > fling trinket..... remember inventory_menu returns None if it's cancelled

	def abl_toggle_drawing(self):
		if 'drawing' not in [stati.name for stati in self.fighter.status]:
			player.fighter.receive_status('drawing', 0)
			director.update(action = 'start drawing')
			drawing = RitualDraw(self.x, self.y)
			drawdir.drawinglist.append(drawing)
			message("You start chanting and drawing the runes of mystery.")

		elif director.action == "start drawing":#activating and deactivating right away draws glyphs rather than lines, this block is cleaning up activation in this event
			active_drawing = filter(lambda x: not x.concluded, drawdir.drawinglist)
			drawdir.drawinglist.remove(active_drawing[0]) #adding a glyph does not add a new drawing to drawdir, it just modifies one tile in the main body of another drawing
			wanted_status = filter(lambda x: x.name == 'drawing', self.fighter.status) #little bit of copypasted code, but this way is more readable i think
			wanted_status[0].terminate() #there can only be one drawing status online anyway - tying it to a single toggle key makes sure of it

			playertile = gamemap[player.x][player.y] #just so it's easier to write and read - points to the tile the player is standing on
			if (playertile.special and playertile.special.name not in ['drawing', 'glyph']) or not playertile.special:
				message('You can only draw a glyph on top of ritual lines.')
				return 'didnt-take-turn'
			else:
				director.update(action = 'draw glyph')
				if glyph_draw_menu() == 'didnt-take-turn': return 'didnt-take-turn'
				return

		else:
			wanted_status = filter(lambda x: x.name == 'drawing', self.fighter.status)
			wanted_status[0].terminate() #there can only be one drawing status online anyway - tying it to a single toggle key makes sure of it
			wanted_drawing = filter(lambda x: not x.concluded, drawdir.drawinglist) #only one drawing should be "not concluded" at any one time. It means the main body is still in the process of being drawn - glyphs are only character changes and are checked on activation
			wanted_drawing[0].concluded = True  #it's a closed loop together with the drawing status so there should be no problems
			return 'didnt-take-turn'



	@property
	def abilities(self):
		abilitylist = []
		for tree in (ctree, ttree, rtree, ptree):
			for node in tree.nodetable:
				if node.abilities != None and node.leveled:
					abilitylist += node.abilities
		self._abilities = abilitylist
		return self._abilities

	@property
	def max_weight(self):
		maxweight = self.stats['strength'] * 40
		return maxweight

	@property
	def dodge(self):
		dodge = self.stats['agility']
		dodge += sum([equip.dodge_bonus for equip in get_all_equipped(player)])
		dodgepercentage = self.stats['agility'] * 14 / 100
		dodge *= dodgepercentage
		return dodge
	
	


def tree_lvlup():
	options = ['Combat', 'Tech', 'Ritual']

	while True:
		index = menu('Choose skill tree', options, SCREEN_WIDTH)
		if index is None or index not in [0,1,2]: continue
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
		choice = menu('Welcome.', ['Play a new game', 'Continue last game', 'Quit'], 24)

		if choice == 0:  #new game
			ccreation = Ccreation()
			ccreation.run_creation()

			
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
	file['gamemap'] = gamemap
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
	global gamemap, objects, player, inventory, game_msgs, game_state, dungeon_level, stairs

	file = shelve.open('savegame', 'r')
	gamemap = file['gamemap']
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
		

		for object in objects:
			if object.fighter and len(object.fighter.status) > 0:
				for stati in object.fighter.status:
					stati.activate()

		render_all()			

		player_action = handle_keys()

		graphical.render_effects() #render effects have to be here because effects depend on object locatons, leading to wrong-looking offsets

		if game_state == 'playing' and player_action != 'didnt-take-turn':  # remember to have checks for timed buffs and things like that here, otherwise things will become shitty
			for object in objects:
				if object.ai:
					object.ai.take_turn()


		if player_action == 'exit':
			save_game()
			clear_game()
			break

def check_lvlup():
	lvlup_xp = LEVEL_UP_BASE + (player.lvl * LEVEL_UP_FACTOR) #bug: dying in the same frame you level up
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

	if slot == 'left hand':                     #
		wep = get_equipped_in_slot('right hand')# twohander special case
		if wep and wep.twohand: return wep      #



	return

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
	global dungeon_level
	dungeon_level += 1
	message('You descend further into the bowels of the earth.', libtcod.dark_violet)
	make_map()
	libtcod.console_clear(con)

	initialize_fov()
	
def handle_keys():
	global key
	key_char = chr(key.c)
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
			director.update(action = 'wait')

		elif key_char == 'g':
				for obj in objects:
					if obj.x == player.x and obj.y == player.y and obj.item:
						if obj.item.pick_up(): pass
						else: return 'didnt-take-turn'


		elif key_char == 'd' and not key.shift:
			#show the inventory; if an item is selected, drop it
			chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
			if chosen_item:
				chosen_item.drop()
			else: return 'didnt-take-turn'

		elif key_char == 'd' and key.shift:
			if player.abl_toggle_drawing() == "didnt-take-turn": return 'didnt-take-turn'

		elif key_char == 'e':
			if key.shift: # E (SHIFT E) prompts you to equip an item
				chosen_equipment = action_equip_menu('Choose an item to equip:\n')
				if chosen_equipment is None:
					return 'didnt-take-turn'
				else:
					chosen_equipment.equip('player')

			else: # e shows equipped items
				chosen_item = equipment_menu('Press a key for more options, or any other to cancel.\n')
				if chosen_item is None:
					return 'didnt-take-turn'
				elif chosen_item == 'empty':
					msgbox('No item there! Press E to equip something.')
					return 'didnt-take-turn'
				else:
					chosen_action = chosen_item.equip_options()
					if chosen_action == 'examine': return 'didnt-take-turn'

		elif key_char == 'z':
			abil = ability_menu()
			if not abil: return 'didnt-take-turn'

		elif key_char == 'a':
			chosen_item = inventory_menu('Press the key next to an item to use it.\n')
			if chosen_item is not None:
				chosen_item.use()
			else:
				return 'didnt-take-turn'

		elif key_char == 'i':
			#show the inventory
			chosen_item = inventory_menu('Press the key next to an item for more options, or any other to cancel.\n')
			if chosen_item is not None:
				chosen_action = chosen_item.item_options()
				if chosen_action == 'examine': return 'didnt-take-turn'
			else: return 'didnt-take-turn'
		elif chr(key.c) == ']':
			raise ValueError(director.action)
		else:
			if key_char == '.' and key.shift:
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

def check_if_node_leveled(tree, node_s):

		if type(node_s) is list:
			for name in node_s:
				chknode = tree.get_node_from_name(name)
				if not chknode.leveled: return False
			return True

		elif type(node_s) is str:
			if not tree.get_node_from_name(node_s): return False
			else: return True

def ability_menu(): #returns ability name if ability goes through, None if its cancelled
	ability_choices = [ability for ability in player.abilities]
	if ability_choices != []:
		choice = menu('Choose an ability.', ability_choices, SCREEN_WIDTH/2)
	else: 
		msgbox("You don't have any abilities yet.")
		return

	if choice is not None: 
		return activate_ability(ability_choices[choice]) #activates ability if its not cancelled, then returns ability name or None depending on whether it got cancelled
	else: return

def activate_ability(abil_name): #returns abil name if not cancelled, None otherwise
	completed = False
	if abil_name == 'kicklaunch':
		if player.abl_kicklaunch(): completed = True
	elif abil_name == 'fling trinket':
		if player.abl_fling_trinket(): completed = True
	elif abil_name == 'consume trinket':
		if player.abl_consume_trinket(): completed = True

	if completed == True: return abil_name

def glyph_draw_menu():
	#glyph_choices = something something from rtree
	glyph_choices = ['&' , '$']
	choice = menu('Choose a glyph to draw.', glyph_choices, SCREEN_WIDTH/2)

	if choice is not None:
		draw_glyph(glyph_choices[choice])
	else: return 'didnt-take-turn'

def draw_glyph(glyph):
	glyphtile = gamemap[player.x][player.y]
	if glyphtile.special and glyphtile.special.name == 'drawing':
		glyphtile.special.char = glyph
		glyphtile.special.name = 'glyph'
	else: message("You can't draw a glyph here.")







def make_map():
	global gamemap, objects, stairs, player

	gamemap = [[Tile(True)
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
	stairs = GameObj(new_x,new_y,'>', 'stairs', libtcod.white, ignore_fov = True)
	objects.append(stairs)
	stairs.send_to_back()

	place_items_in_level()

def create_item_rngtable(depth_level = 1): # this gonna get modified to shit before this is over
	output_items = []					# returns list of (OBJECT)items to spawn by calling get_random_item on a normal distribution of depthlevels
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

	

				
	camera.camera_render()

	for obj in objects:
		if obj.in_camera(): obj.draw()

	player.draw()
	for obj in objects:
		if obj.name == 'targeter': obj.draw()

	#blits the content of the 'con' console to the root console
	libtcod.console_blit(con, 0, 0, CAMERA_WIDTH, CAMERA_HEIGHT, 0, 0, 0)



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

def clear_screen(): #this is slow, usually you will want libtcod.console_clear instead
	clearer = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
	for y in range(SCREEN_HEIGHT):
		for x in range(SCREEN_WIDTH):
			libtcod.console_put_char_ex(con, x, y, ' ', color_dark_wall, libtcod.black)
			libtcod.console_blit(clearer,0,0,0,0,0,0,0)

def create_room(room):
	global gamemap
	for x in range(room.x1+1,room.x2):
		for y in range(room.y1+1,room.y2):
			gamemap[x][y].blocked = False
			gamemap[x][y].block_sight = False

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
	global gamemap
	for x in range(min(x1,x2),max(x1,x2)+1):
		gamemap[x][y].blocked = False
		gamemap[x][y].block_sight = False

def create_v_tunnel(y1,y2,x):
	global gamemap
	for y in range(min(y1,y2),max(y1,y2)+1):
		gamemap[x][y].blocked = False
		gamemap[x][y].block_sight = False

def check_colorkeeper(name):
	global colorkeeper
	if name not in colorkeeper:
		colorchoice = libtcod.Color(libtcod.random_get_int(0,30,255),libtcod.random_get_int(0,30,255),libtcod.random_get_int(0,30,255))
		colorkeeper[name] = colorchoice
	else: colorchoice = colorkeeper[name]
	return colorchoice


def generate_item(name, x, y): #RETURNS HIGHEST OBJECT, NOT ITEM OR EQUIP COMPONENT #to add a new item, it has to be added here, to get_item_components, to catalog.FULL_INAMELIST, to descriptions in catalog
	if name == 'healing salve':  #only basic stats go here, for special functions and descriptions go to catalog
		colorchoice = check_colorkeeper(name)
		item = GameObj(x, y, '!', name, colorchoice, None, None, None,)

	elif name == 'pipe gun':
		colorchoice = check_colorkeeper(name)
		item = GameObj(x, y, '?', name, colorchoice, None, None, None )

	elif name == 'crude grenade':
		colorchoice = check_colorkeeper(name)
		item = GameObj(x, y, '?', name, colorchoice, None, None, None )

	elif name == 'scrap metal sword':
		item = GameObj(x, y, '/', name, libtcod.desaturated_blue )

	elif name == 'rebar blade':
		item = GameObj(x, y, '/', name, libtcod.darkest_green )

	elif name == 'kitchen knife':
		item = GameObj(x, y, '/', name, libtcod.darker_sepia, ignore_fov = True)

	elif name == 'metal plate':
		item = GameObj(x, y, '[', name, libtcod.light_grey )

	elif name == 'goat leather sandals':
		item = GameObj(x, y, '[', name, libtcod.lighter_azure )

	elif name == "someone's memento":
		item = GameObj(x,y, '*', name, libtcod.gold)

	return item

def generate_tile(name):
	if name == 'jagged rock':
		special_component = SpTile(name, ',', libtcod.white, libtcod.black, onwalk_effect = {'damage':2})
		tile = Tile(False, None, special_component)
	return tile

def generate_monster(name, x, y):
	if name == 'crazed mutt':
		fighter_component = Fighter(hp = 30, armor = 0, power = 4, xp = 10, death_function = monster_death, depth_level = 1)
		ai_component = DumbMonster()
		monster = GameObj(x, y, 'd', name, libtcod.lighter_red, blocks = True, fighter = fighter_component, ai = ai_component)
	elif name == 'mad hermit':
		fighter_component = Fighter(hp = 15, armor = 1, power = 6, xp = 25, death_function = monster_death, depth_level = 1)
		ai_component = DumbMonster()
		monster = GameObj(x, y, 'h', name, libtcod.lighter_red, blocks = True, fighter = fighter_component, ai = ai_component)

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

	x = libtcod.random_get_int(0, room.x1+1, room.x2-1) #+1 -1 because it has to exclude the walls
	y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

def is_blocked(x,y):
	if gamemap[x][y].blocked:
		return True
	
	for obj in objects:
		if obj.blocks and obj.x == x and obj.y == y:
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
			libtcod.map_set_properties(fov_map, x, y, not gamemap[x][y].block_sight, not gamemap[x][y].blocked)



def inventory_menu(header, itemtype = None):
	inv = filter(lambda x: not x.equipment or x.equipment not in get_all_equipped(player), inventory)

	if itemtype:
		inv = filter(lambda x: x.item.itemtype == itemtype, inv)

	if len(inv) == 0:
		options = ['You have NOTHING!']
	else:
		options = []
		for item in inv:
				text = item.item.dname
				options.append(text)

	index = menu(header, options, INVENTORY_WIDTH)
	if index is None or len(inv) == 0: return
	return inv[index].item # RETURNS ITEM COMPONENT

def action_equip_menu(header):
	options = []
	output_item = []
	inv = filter(lambda x: x.equipment != None, inventory)
	inv = filter(lambda x: x.equipment not in get_all_equipped(player), inv)
	for item in inv:
		options.append(item.item.dname)
		output_item.append(item)

	if len(options) == 0:
		msgbox('Nothing to equip.')
		return
	else:
		index = menu(header, options, INVENTORY_WIDTH)

	if index is None: return
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

	if index is None: return
	elif outputitem[index] == 'empty': return 'empty'
	elif outputitem[index] != 'empty': return outputitem[index] # RETURNS EQUIPMENT COMPONENT INSTANCE

def textbox(lines): # takes text as a list of (str)lines and displays it
	width = 0
	if type(lines) == list:
		width = map(lambda x: len(x), lines)
		width = max(width)
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
	height = len(options) + header_height + 2

	window = libtcod.console_new(width, height)
	libtcod.console_print_frame(window,0,0,width,height,clear=False, flag=libtcod.BKGND_DEFAULT)

	libtcod.console_set_default_foreground(window, libtcod.white)
	if options != []:
		libtcod.console_print_rect_ex(window, 1, 0, width-1, height, libtcod.BKGND_NONE, libtcod.LEFT, header)
	else:
		libtcod.console_print_rect_ex(window, 1, 1, width-1, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

	y = header_height
	letter_index = ord('a')
	for option_text in options:
		text = '(' + chr(letter_index) + ') ' + option_text
		libtcod.console_print_ex(window, 1, y, libtcod.BKGND_NONE, libtcod.LEFT, text)

		y += 1
		letter_index += 1

	x = SCREEN_WIDTH/2 - width/2
	y = SCREEN_HEIGHT/2 - height/2
	libtcod.console_blit(window,0,0,width,height,0,x,y,1.0,1.0)

	libtcod.console_flush()
	key = libtcod.console_wait_for_keypress(True)

	index = key.c - ord('a')
	libtcod.console_clear(window)
	libtcod.console_blit(window,0,0,0,0,0,x,y,1.0,1.0)
	if index >= 0 and index < len(options): return index

	return


def msgbox(message, width=50):
	menu(message, [], width)


def target_tile(max_range = None):
	global objects

	message('Choose a target - ESC to cancel.', libtcod.red)
	targeter = GameObj(player.x, player.y, '+', 'targeter', libtcod.red,ignore_fov = True)
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
			continue

		elif (keyb.vk == libtcod.KEY_ENTER and libtcod.map_is_in_fov(fov_map, targeter.x, targeter.y) and (max_range is None or player.distance_to(targeter) <= max_range)):

			targeter.clear()
			objects.remove(targeter)
			return (targeter.x, targeter.y)

		elif (keyb.vk == libtcod.KEY_ENTER and not libtcod.map_is_in_fov(fov_map, targeter.x, targeter.y)):
			message('You cannot target there!', libtcod.grey)


		else:
			targeter.clear()
			objects.remove(targeter)
			return (None, None)

def closest_monster(max_range):
	#find closest enemy, up to a maximum range, and in the player's FOV
	closest_enemy = None
	closest_dist = max_range + 1  #start with (slightly more than) maximum

	for obj in objects:
		if obj.fighter and not obj == player and libtcod.map_is_in_fov(fov_map, obj.x, obj.y):
		#calculate distance between this object and the player
			dist = player.distance_to(obj)
			if dist < closest_dist:  #it's closer, so remember it
				closest_enemy = obj
				closest_dist = dist
	return closest_enemy

def random_adj_target():
	adjacents = []
	for obj in objects:
		if obj.distance_to(player) < 2 and obj.fighter and not obj == player: adjacents.append(obj)

	if adjacents == []: 
		return
	else: 
		choice = libtcod.random_get_int(0,0,len(adjacents)-1)

	return adjacents[choice]


 
def target_monster(max_range=None):
	
	while True:
		(x, y) = target_tile(max_range)
		if x is None:  #player cancelled
			return

	
		for obj in objects:
			if obj.x == x and obj.y == y and obj.fighter and obj != player:
				return obj

		message('Nothing to target there!', libtcod.grey)

def clear_game():
	global objects, inventory

	for obj in objects:
		obj.clear()
		objects.remove(obj)
	for item in inventory:
		inventory.remove(item)

	clear_screen()

def new_game():
	global player, game_msgs, game_state, inventory, dungeon_level, namekeeper, colorkeeper, camera, director, drawdir

	player = Player()
	dungeon_level = 1
	director = PlayerActionReport()
	drawdir = DrawingDir()
	inventory = []
	namekeeper = {}
	colorkeeper = {}
	game_msgs = []


	make_map()

	camera = Camera()

	initialize_fov()

	game_state = 'playing'

	item = generate_item('pipe gun', 0, 0)
	inventory.append(item)


	


def push(origin, target, distance):#only usable for 1 tile distance between target and origin, because i'd need a line algorhithm for longer distance pushes (so it's not just a vertical, horizontal or perfectly diagonal line)
	if origin.distance_to(target) <= 2: #can expand it later
		dx, dy = graphical.get_increments(origin, target)
		for i in range(1, distance+1):
			if not is_blocked(target.x+dx, target.y+dy):
				target.x += dx
				target.y += dy
			elif i < distance: return i # return where it got blocked
		return distance

def pot_heal():
	if player.fighter.hp == player.fighter.max_hp:
		message('You are at full health already!')
		return 'cancelled'

	message('Your wounds start to feel better.')
	player.fighter.heal(POTHEAL_AMOUNT)

# def draw_laser(origin, end, char, color): #origin and end must be GameObj(or otherwise also have camx, camy attributes)
# 	line = graphical.createline(origin, end)

# 	linecon = graphical.console_from_twopts(origin, end)
# 	libtcod.console_set_default_foreground(linecon, color)
# 	for point in line:
# 		libtcod.console_put_char(linecon,int(point.x), int(point.y), char, libtcod.BKGND_NONE)

# 	libtcod.console_blit(linecon, 0, 0, 0, 0, 0, min(origin.camx, end.camx), min(origin.camy, end.camy), 1, 0)
# 	libtcod.console_flush()

# 	libtcod.sys_sleep_milli(50)

#OLD CODE: This functionality has been transferred to the graphical module


def consumable_pipegun():
	monster = target_monster(6)
	if monster is None:
		return 'cancelled'
	else:
		message('The slug explodes out of the flimsy gun with a loud thunder and strikes the ' + monster.name + '! The damage is '+ str(LIGHTNING_DAMAGE) + ' hit points.', libtcod.light_blue)
		# draw_laser(player, monster, graphical.determine_projchar(player, monster), libtcod.light_blue)
		graphical.LineHandler(player, monster, libtcod.light_blue)
		# lineffect.draw(libtcod.light_blue) #it's in the init method now, not sure if i should keep it there


		monster.fighter.take_damage(1)
		monster.fighter.receive_status('maim', 30)
		

def consumable_crudenade():
	x, y = target_tile()
	if x is None: return 'cancelled'

	message('The grenade explodes, spraying everything within ' + str(FIREBALL_RADIUS) + ' tiles with shrapnel!', libtcod.orange)

	for obj in objects:  #damage every fighter in range, including the player
		if obj.distance(x, y) <= FIREBALL_RADIUS and obj.fighter:
			if libtcod.map_is_in_fov(fov_map, obj.x, obj.y): message('The ' + obj.name + ' gets burned for ' + str(FIREBALL_DAMAGE) + ' hit points.', libtcod.orange)
			obj.fighter.take_damage(FIREBALL_DAMAGE)


def pass_node_requirements(node):
	if node == 'shield focus':
		if ctree.level >= 1: return True
	else: return False

def get_multiattack_number():
	attackn = 0
	for equip in get_all_equipped(player):
		for enchant in equip.special.enchantlist: 
			if enchant.name == 'multiattack': attackn += enchant.value

	attackn *= player.stats['agility']/5
	attackn += 1
######################
	if uniform(math.floor(attackn), math.ceil(attackn)) > attackn:#
		return int(math.floor(attackn))                           # if attackn is not an integer(as it usually wont be), this bit of code just takes a uniform probability on the decimal part
	else: return int(math.ceil(attackn))     

def drawing_function(self):
	if director.action == 'move':
		x, y = director.x1, director.y1
		prevtile = None
		if gamemap[x][y].special and gamemap[x][y].special.name == 'drawing': prevtile = gamemap[x][y].special.char

		character = determine_drawchar(prevtile)
		drawntile = SpTile(name = 'drawing', char = character, foreground = libtcod.white)
		
		if not gamemap[x][y].special: 
			gamemap[x][y].special = drawntile
			drawing = filter(lambda x: not x.concluded, drawdir.drawinglist)
			drawing[0].add_drawntile(gamemap[x][y])

def determine_orientation(dxl, dyl):
	orient = ''
	if dxl == 1 and dyl == 0:
		orient = 'from w'
	elif dxl == 1 and dyl == -1:
		orient = 'from sw'
	elif dxl == 1 and dyl == 1:
		orient = 'from nw'

	elif dxl == -1 and dyl == 0:
		orient = 'from e'
	elif dxl == -1 and dyl == -1:
		orient = 'from se'
	elif dxl == -1 and dyl == 1:
		orient = 'from ne'

	elif dxl == 0 and dyl == 1:
		orient = 'from n'
	elif dxl == 0 and dyl == -1:
		orient = 'from s'

	return orient

def determine_drawchar(prevchar):

	if director.action == 'move': x1, x2, y1, y2 = director.x1, director.x2, director.y1, director.y2
	lastmove = get_last_move_action()
	dxl, dyl = graphical.get_increments(lastmove['x1'], lastmove['y1'], lastmove['x2'], lastmove['y2'])
	dx, dy = graphical.get_increments(x1, y1, x2, y2)
	lorient = determine_orientation(dxl, dyl) #last orientation
	corient = determine_orientation(dx, dy)	#current orientation
	char = 'E' #for error
	if director.action == 'move':
		if (lorient == 'from w' and corient == 'from s') or (lorient == 'from n' and corient == 'from e') : char = 180
		elif (lorient == 'from w' and corient == 'from n') or (lorient == 'from s' and corient == 'from e'): char = 183
		elif (lorient == 'from s' and corient == 'from w') or (lorient == 'from e' and corient == 'from n'): char = 182 #these are (rounded) 90deg corners
		elif (lorient == 'from n' and corient == 'from w') or (lorient == 'from e' and corient == 'from s'): char = 181

		elif (lorient == 'from sw' and corient == 'from w') or (lorient == 'from e' and corient == 'from ne'): char = 200
		elif (lorient ==  'from nw' and corient == 'from w') or (lorient == 'from e' and corient == 'from se'): char = 199
		elif (lorient ==  'from w' and corient == 'from sw') or (lorient == 'from ne' and corient == 'from e'): char = 198
		elif (lorient ==  'from w' and corient == 'from nw') or (lorient == 'from se' and corient == 'from e'): char = 201 #135deg corners (center - diag)
		elif (lorient ==  'from n' and corient == 'from ne') or (lorient == 'from sw' and corient == 'from s'): char = 202
		elif (lorient ==  'from nw' and corient == 'from n') or (lorient == 'from s' and corient == 'from se'): char = 205
		elif (lorient ==  'from ne' and corient == 'from n') or (lorient == 'from s' and corient == 'from sw'): char = 204
		elif (lorient ==  'from n' and corient == 'from nw') or (lorient == 'from se' and corient == 'from s'): char = 203


		elif dyl == 0 and dy == 0: char = 196 #straight lines :horizontal
		elif dxl == 0 and dx == 0: char = 179 #vertical

		elif (lorient ==  'from se' and corient == 'from se') or (lorient == 'from nw' and corient == 'from nw'): char = 189 #diagonals
		elif (lorient ==  'from ne' and corient == 'from ne') or (lorient == 'from sw' and corient == 'from sw'): char = 188

		elif (lorient ==  'from se' and corient == 'from ne') or (lorient == 'from sw' and corient == 'from nw'): char = 211
		elif (lorient ==  'from nw' and corient == 'from sw') or (lorient == 'from ne' and corient == 'from se'): char = 209
		elif (lorient ==  'from ne' and corient == 'from nw') or (lorient == 'from se' and corient == 'from sw'): char = 210 #90deg diagonal 'beaks'
		elif (lorient ==  'from nw' and corient == 'from ne') or (lorient == 'from sw' and corient == 'from se'): char = 212

		elif (lorient ==  'from w' and corient == 'from ne') or (lorient == 'from sw' and corient == 'from e'): char = 256
		elif (lorient ==  'from sw' and corient == 'from n') or (lorient == 'from s' and corient == 'from ne'): char = 257
		elif (lorient ==  'from s' and corient == 'from nw') or (lorient == 'from se' and corient == 'from n'): char = 262
		elif (lorient ==  'from e' and corient == 'from nw') or (lorient == 'from se' and corient == 'from w'): char = 263
		elif (lorient ==  'from e' and corient == 'from sw') or (lorient == 'from ne' and corient == 'from w'): char = 261
		elif (lorient ==  'from n' and corient == 'from sw') or (lorient == 'from ne' and corient == 'from s'): char = 260  #45deg diagonal 'beaks'
		elif (lorient ==  'from nw' and corient == 'from s') or (lorient == 'from n' and corient == 'from se'): char = 259
		elif (lorient ==  'from nw' and corient == 'from e') or (lorient == 'from w' and corient == 'from se'): char = 258
# I hope to eventually come up with a non-retarded way to do this, perhaps involving binary representations
	return char

def get_last_move_action():
	for i in range(len(director.recorder)-2, 0, -1):
		if director.recorder[i]['action'] == 'move':
			return director.recorder[i]



libtcod.console_set_custom_font('Terminus.png', libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=17)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
libtcod.sys_set_fps(LIMIT_FPS)
libtcod.console_map_ascii_codes_to_font(256, 16, 0, 16)
con = libtcod.console_new(CAMERA_WIDTH, CAMERA_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
main_menu()













