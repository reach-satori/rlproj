import libtcodpy as libtcod
import math
import textwrap
import shelve
import catalog
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

class Equipment:
	def __init__(self, slot, power_bonus = 0, armor_bonus = 0, dodge_bonus = 0):
		self.slot = slot
		self.is_equipped = False
		self.power_bonus = power_bonus
		self.dodge_bonus = dodge_bonus
		self.armor_bonus = armor_bonus

	def equip(self):
		#equip object and show a message about it
		self.is_equipped = True
		message('Equipped ' + self.owner.name + ' on your ' + self.slot + '.', libtcod.light_green)

	def dequip(self):
		if not self.is_equipped: return
		self.is_equipped = False
		message('Unequipped ' + self.owner.name + ' from ' + self.slot + '.', libtcod.light_yellow)

	def equip_options(self):
		options = ['Examine', 'Unequip', 'Drop']
		index = menu('Choose an action: ', options, 50)
		if index == 0:#examine
			self.owner.item.examine()

		elif index == 1:#unequip
			self.unequip()

		elif index == 2: #drop (and unequip)
			self.unequip()
			self.owner.item.drop()


class Item:
	def __init__(self, weight, depth_level = 1, use_function = None):
		self.weight = weight
		self.use_function = use_function
		self.depth_level = depth_level

	def pick_up(self):
		if len(inventory)>=26:
			message('Your inventory is full')
		else:
			inventory.append(self.owner)  # inventory has objects, not item
			objects.remove(self.owner)
			message('You picked up a ' + self.owner.name + '!', libtcod.green)

	def use(self):
		if self.use_function == None:
			message('The' + self.owner.name + 'cannot be used.')
		else:
			if self.use_function() != 'cancelled':  #conditions for persistent/charge-based consumables go here
				inventory.remove(self.owner)

	def drop(self):
		#add to the map and remove from the player's inventory. also, place it at the player's coordinates
		objects.append(self.owner)
		inventory.remove(self.owner)
		self.owner.x = player.x
		self.owner.y = player.y
		message('You dropped a ' + self.owner.name + '.', libtcod.yellow)

	def examine(self):
		itemname = self.owner.name
		text = catalog.get_item_description(itemname)

		textbox(text)

	def item_options(self):
		options = ['Examine', 'Drop', 'Use']
		index = menu('Choose an action: ', options, 50)
		if index == 0:#examine
			self.examine()

		if index == 1: #drop
			self.drop()

		if index == 2: #use
			self.use()




class Fighter:
	def __init__(self, hp, armor, dodge, power, xp,  death_function = None):
		self.max_hp = hp
		self.hp = hp
		self.base_armor = armor
		self.base_dodge = dodge
		self.base_power = power
		self.death_function = death_function
		self.xp = xp

	def take_damage(self,damage):
		if damage > 0:
			self.hp -= damage
			if self.hp < 0:
				player.fighter.xp += self.xp
				function = self.death_function
				if function is not None:
					function(self.owner)

	def attack(self, target):
		damage = self.power - target.fighter.armor
		if damage > 0:
			message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
			target.fighter.take_damage(damage)
		else:
			message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')

	def heal(self, amount):
		self.hp += amount
		if self.hp > self.max_hp:
			self.hp = self.max_hp

	@property
	def power(self):
		bonus = sum(equipment.power_bonus for equipment in get_all_equipped(self.owner))
		return self.base_power + bonus

	@property
	def armor(self):  #return actual defense, by summing up the bonuses from all equipped items
		bonus = sum(equipment.armor_bonus for equipment in get_all_equipped(self.owner))
		return self.base_armor + bonus

	@property
	def dodge(self):  #return actual defense, by summing up the bonuses from all equipped items
		bonus = sum(equipment.dodge_bonus for equipment in get_all_equipped(self.owner))
		return self.base_dodge + bonus
 
	@property
	def max_hp(self):  #return actual max_hp, by summing up the bonuses from all equipped items
		bonus = sum(equipment.max_hp_bonus for equipment in get_all_equipped(self.owner))
		return self.base_max_hp + bonus
	



class DumbMonster:
	def take_turn(self):
		monster = self.owner

		if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
			if monster.distance_to(player) >= 2:
				monster.move_towards(player.x, player.y)

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

class Tile:
	def __init__(self, blocked, block_sight = None):
		self.blocked = blocked
		self.explored = False

		#blocks sight by default if blocks movement (standard wall)
		if block_sight is None:	self.block_sight = blocked
		
class Object:
	def __init__(self,x, y, char, name, color, blocks = False, fighter = None, ai = None, item = None, ignore_fov = False, equipment = None):
		self.x = x
		self.y = y
		self.char = char
		self.color = color
		self.blocks = blocks
		self.name = name
		self.ignore_fov = ignore_fov


		self.item = item
		if self.item:
			self.item.owner = self

		self.equipment = equipment
		if self.equipment:
			self.equipment.owner = self

		self.fighter = fighter
		if self.fighter:
			self.fighter.owner = self

		self.ai = ai
		if self.ai:
			self.ai.owner = self

	def move(self, dx, dy):
		if not is_blocked(self.x+dx, self.y+dy):
			self.x += dx
			self.y += dy

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

def normal_randomize(mean,sd): #input mean, sd for gauss distribution
	floatnormal = gauss(float(mean),float(sd)) #output one sample, rounded and non-negative
	if floatnormal < 1: floatnormal = 1
	return int(round(floatnormal))




def main_menu():

	while not libtcod.console_is_window_closed():
		#show options and wait for the player's choice
		choice = menu('', ['Play a new game', 'Continue last game', 'Quit'], 24)

		if choice == 0:  #new game
			initialize_player()
			character_creation()
			clear_screen()
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
	lovemessage = ['the game begins','go fuck yourself','go fuck yourself','go fuck yourself','go fuck yourself','go fuck yourself','go fuck yourself']
	textbox(lovemessage)
	#OPTIONAL STUFF

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
			player.fighter.power += 1
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
	global dungeon_level

	message('You descend further into the bowels of the earth.', libtcod.dark_violet)
	clear_screen()
	make_map()
	initialize_fov()
	dungeon_level += 1



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

			if key_char == 'e':
				if key.shift: # E (SHIFT E) prompts you to equip an item
					chosen_equipment = action_equip_menu('Choose an item to equip:\n')
					if chosen_equipment is None:
						msgbox('You have no equippable items in your inventory.')
					else:
						chosen_equipment.equip()

				else: # e shows equipped items
					chosen_item = equipment_menu('Press a key for more options, or any other to cancel.\n')
					if chosen_item is None:
						pass
					elif chosen_item is 'empty':
						msgbox('No item there! Press E to equip something.')
					else:
						chosen_item.equip_options()
					


			if key_char == 'i':
				#show the inventory
				chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
				if chosen_item is not None:
					chosen_item.item_options()

			if key_char == 'd':
				#show the inventory; if an item is selected, drop it
				chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
				if chosen_item is not None:
					chosen_item.drop()

			if key_char == '.':
				if player.x == stairs.x and player.y == stairs.y:
					next_level()
				else:
					message("You can't go down here!")

			if key_char == 'c':
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

def create_item_rngtable(dungeon_level = 1): # this gonna get modified to shit before this is over
	output_items = []					# returns list of (OBJECT)items to spawn in a dungeon level by calling get_random_item on a normal distribution of depthlevels
	mean_items = 7 + dungeon_level  * 3

	number_of_items = normal_randomize(mean_items, dungeon_level ** 0.5)
	for index in range(number_of_items):
		item_depthlevel = normal_randomize(dungeon_level, 0.5 * dungeon_level)
		randomized_item = get_random_item_of_depthlevel(item_depthlevel)
		output_items.append(randomized_item)

	return output_items

def get_items_of_depthlevel(desired_depth = 1):
	itemlist = get_full_item_list() # gets all the items of a desired depth level RETURNS ITEM OBJECTS
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
			objects.append(items_to_place[i])
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
			if not visible:
				if map[x][y].explored:
					if wall:
						libtcod.console_put_char_ex(con, x, y, '#', color_dark_wall, libtcod.black)
					else:
						libtcod.console_put_char_ex(con, x, y, '.', color_dark_ground, libtcod.black )
			elif visible:
				if wall:
					libtcod.console_put_char_ex(con, x, y, '#', color_light_wall, libtcod.black)
				else:
					libtcod.console_put_char_ex(con, x, y, '.', color_light_ground, libtcod.black )
				map[x][y].explored = True

	libtcod.console_set_default_foreground(con, libtcod.white)
	libtcod.console_set_default_background(panel, libtcod.black)
	libtcod.console_clear(panel)

	render_bar(1, 1, BAR_WIDTH, 'Health', player.fighter.hp, player.fighter.max_hp, libtcod.dark_red, libtcod.darkest_red) # display health
	libtcod.console_print_ex(panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon level ' + str(dungeon_level))  #display dungeon level

	player.send_to_front() #always draw player
	for object in objects:
		object.draw()


	#print game messages, one line at a time
	y = 1
	for (line, color) in game_msgs:
		libtcod.console_set_default_foreground(panel,color)
		libtcod.console_print_ex(panel,MSG_X, y, libtcod.BKGND_NONE, libtcod. LEFT, line)
		y += 1




	#blits the content of the 'con' console to the root console
	libtcod.console_blit(con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0, 0)
	#blits the content of the 'panel' console to the root console
	libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

def clear_screen():
	clearer = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
	for y in range(SCREEN_HEIGHT):
		for x in range(SCREEN_WIDTH):
			libtcod.console_put_char_ex(clearer, x, y, ' ', libtcod.black, libtcod.black)
			libtcod.console_blit(clearer,0,0,0,0,0,0,0)

def create_room(room):
	global map
	for x in range(room.x1+1,room.x2):
		for y in range(room.y1+1,room.y2):
			map[x][y].blocked = False
			map[x][y].block_sight = False

# def roll_nds(n,s):	# as in roll n d4, n d6, etc
# 	result_list = []
# 	for i in n:
# 		result_list.append(libtcod.random_get_int(0, 1, s))

# 	return result_list




def random_choice_index(chances):  #choose one option from list of chances, returning its index
	#the dice will land on some number between 1 and the sum of the chances
	dice = libtcod.random_get_int(0, 1, sum(chances))
 
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
	return strings[random_choice_index(chances)]

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
	if name == 'healing salve':
		item_component = Item(weight = 0.5, depth_level = 1, use_function = pot_heal)
		item = Object(x, y, '!', 'healing salve', libtcod.violet, None, None, None, item = item_component)
	elif name == 'pipe gun':
		item_component = Item(weight = 1, depth_level = 2, use_function = consumable_pipegun)
		item = Object(x ,y, '?', 'pipe gun', libtcod.light_blue, None, None, None, item = item_component)
	elif name == 'crude grenade':
		item_component = Item(weight = 1, depth_level = 2, use_function = consumable_crudenade)
		item = Object(x, y, '?', 'crude grenade', libtcod.dark_red, None, None, None, item = item_component)
	elif name == 'scrap metal sword':
		item_component = Item(weight = 10, depth_level = 2)
		equipment_component = Equipment(slot='right hand')
		item = Object(x, y, '/', 'scrap metal sword', libtcod.desaturated_blue, item = item_component, equipment=equipment_component)

	return item

def generate_monster(name, x, y):
	if name == 'rat':
		fighter_component = Fighter(hp = 10, armor = 0, dodge = 2, power = 3, xp = 10, death_function = monster_death)
		ai_component = DumbMonster()
		monster = Object(x, y, 'r', 'rat', libtcod.desaturated_green, blocks = True, fighter = fighter_component, ai = ai_component)
	elif name == 'nasty rat':
		fighter_component = Fighter(hp = 15, armor = 1, dodge = 2, power = 4, xp = 25, death_function = monster_death)
		ai_component = DumbMonster()
		monster = Object(x, y, 'r', 'nasty rat', libtcod.red, blocks = True, fighter = fighter_component, ai = ai_component)

	return monster





def place_objects(room):
	num_monsters = libtcod.random_get_int(0,0,MAX_ROOM_MONSTERS)

	for i in range(num_monsters):
		x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
		y = libtcod.random_get_int(0, room.y1+1, room.y2-1)
		if not is_blocked(x,y):
	###################### MONSTER RNG SHIT #######################
	#REDO LATER WITH FANCY PDFs
			monster_chance = {'rat': 80, 'nasty rat': 20}
			choice = random_choice(monster_chance)
			monster = generate_monster(choice,x,y)
	###################### MONSTER RNG SHIT #######################
			objects.append(monster)

	x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
	y = libtcod.random_get_int(0, room.y1+1, room.y2-1)


	# objects.append(item)
	# item.send_to_back()

def is_blocked(x,y):
	if map[x][y].blocked:
		return True
	
	for object in objects:
		if object.blocks and object.x == x and object.y == y:
			return True

	return False

def player_move_or_attack(dx,dy):
	global fov_recompute

	x = player.x + dx
	y = player.y + dy

	target = None
	for object in objects:
		if object.fighter and object.x == x and object.y == y:
			target = object
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

def inventory_menu(header):
	if len(inventory) == 0:
		options = ['You have NOTHING!']
	else:
		options = []
		for item in inventory:
			text = item.name
			#show additional information, in case it's equipped
			if item.equipment and item.equipment.is_equipped:
				text = text + ' (on ' + item.equipment.slot + ')'
			options.append(text)

	index = menu(header, options, INVENTORY_WIDTH)

	if index is None or len(inventory) == 0: return None
	return inventory[index].item # RETURNS ITEM - RETURNS ITEM

def action_equip_menu(header):
	options = []
	output_item = []
	for item in inventory:
		if item.equipment and item.equipment.is_equipped == False:
			options.append(item.name)
			output_item.append(item)

	if len(options) == 0:
		return None
	else:
		index = menu(header, options, INVENTORY_WIDTH)

	return output_item[index].equipment

def equipment_menu(header):
	options = []
	outputitem = []
	check = False
	for slot in catalog.SLOTLIST:
		equipment = get_equipped_in_slot(slot)
		if equipment == None:
			outputitem.append('empty')
			options.append(slot + ':     - ')
		else:
			outputitem.append(equipment)# RETURNS EQUIPMENT COMPONENT INSTANCE
			options.append(slot + ':    ' + equipment.owner.name)



#Loops through objects for equipped item in a slot, returning 'empty' if there is none
				
	index = menu(header, options, INVENTORY_WIDTH)

	if index is None: return None
	elif outputitem[index] == 'empty': return 'empty'
	elif outputitem[index] != 'empty': return outputitem[index]


def textbox(lines): # takes text as a list of (str)lines and displays it
	width = 0
	for line in lines:
		if len(line) > width:
			width = len(line)

	width += 6
	height = len(lines) + 4
	window = libtcod.console_new(width, height)


	# libtcod.console_print_rect_ex(window,0,0, width, height, libtcod.BKGND_NONE, libtcod.LEFT)

	y = 2
	for line in lines:
		libtcod.console_print_rect_ex(window, 3, y, width, height, libtcod.BKGND_DEFAULT, libtcod.LEFT, line)
		y += 1

	x = SCREEN_WIDTH/2 - width/2
	y = SCREEN_HEIGHT/2 - height/2
	libtcod.console_print_frame(window,0, 0, width, height, clear=False, flag=libtcod.BKGND_DEFAULT)
	libtcod.console_blit(window,0,0,width,height,0,x,y,1.0,1.0)
	libtcod.console_flush()
	ignore = libtcod.console_wait_for_keypress(True)



def character_creation():
	width = (SCREEN_WIDTH*2)/3+1
	height = SCREEN_HEIGHT/2
	menu_selection = libtcod.console_new(width, height)
	##################RACERACERACERACERACERACERACE##########################
	letter_index = ord('a')
	y = 2
	x = 2
	for option_text in catalog.FULL_RACELIST:
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
	key_char = chr(key.c)

	if key_char == 'a':
		race_description_box('human')
		charstat_box()

	key = libtcod.console_wait_for_keypress(True)

	if key == libtcod.KEY_ENTER:
		pass

		


	#######################################################################

def race_description_box(race):
	width = SCREEN_WIDTH/3 - 2 
	height = SCREEN_HEIGHT/2

	description_box = libtcod.console_new(width, height)
	libtcod.console_set_alignment(description_box, libtcod.CENTER)
	text = catalog.race_description(race)
	libtcod.console_print_rect(description_box, width/2, height*2/3, width, height, text)
	libtcod.console_print_frame(description_box,0, 0, width, height, clear=False, flag=libtcod.BKGND_DEFAULT)

	libtcod.console_blit(description_box, 0, 0, 0, 0, 0, (width*2)+2, 0)
	libtcod.console_flush()


def charstat_box():
	width = SCREEN_WIDTH -6
	height = SCREEN_HEIGHT/2 -2
	statsbox = libtcod.console_new(width, height)
	libtcod.console_print_frame(statsbox,0, 0, width, height, clear=False, flag=libtcod.BKGND_DEFAULT)
	for i in range(1,5):
		libtcod.console_print_ex(statsbox, 1, i*2, libtcod.BKGND_NONE, libtcod.LEFT, 'PLACEHOLDER PLACEHOLDER PLACEHOLDER PLACEHOLDER PLACEHOLDER')
		libtcod.console_print_ex(statsbox, 63, 2, libtcod.BKGND_NONE, libtcod.LEFT, 'Press Enter to confirm selection.')

	libtcod.console_blit(statsbox, 0, 0, 0, 0, 0, 2, height + 2)
	libtcod.console_flush()



def menu(header, options, width):
	if len(options) > 26:
		raise ValueError('Cannot have a menu with more than 26 options.')
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
		return index
	return None

def msgbox(message, width=50):
	menu(message, [], width)

def initialize_player():
	global player
	fighter_component = Fighter(hp=30, armor = 3, dodge = 3, power=3, xp = 0, death_function = player_death)
	player = Object(0,0, '@', 'player', libtcod.white, blocks = True, fighter = fighter_component)
	player.lvl = 1

def target_tile(max_range = None):
	global objects

	message('Choose a target - ESC to cancel.', libtcod.red)
	targeter = Object(player.x, player.y, '+', 'targeter', libtcod.red,ignore_fov = True)
	objects.append(targeter)
	targeter.send_to_front()

	while True:
		render_all()
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
 
def target_monster(max_range=None):
	#returns a clicked monster inside FOV up to a range, or None if right-clicked
	while True:
		(x, y) = target_tile(max_range)
		if x is None:  #player cancelled
			return None

	#return the first clicked monster, otherwise continue looping
		for obj in objects:
			if obj.x == x and obj.y == y and obj.fighter and obj != player:
				return obj

def clear_game():
	global objects, map, inventory

	for object in objects:
		object.clear()
		objects.remove(object)
	for item in inventory:
		inventory.remove(item)

	clear_screen()


def new_game():
	global player, game_msgs, game_state, inventory, dungeon_level
	
	
	dungeon_level = 1
	make_map()
	initialize_fov()

	game_state = 'playing'
	inventory = []

	#create the list of game messages and their colors, starts empty
	game_msgs = []
	dungeon_level = 1 






def pot_heal():
	if player.fighter.hp == player.fighter.max_hp:
		message('You are at full health already!')
		return 'cancelled'

	message('Your wounds start to feel better.')
	player.fighter.heal(POTHEAL_AMOUNT)

def consumable_pipegun():
	monster = target_monster(5)
	if monster is None:
		return 'cancelled'
	else:
		message('The slug strikes the ' + monster.name + ' with a loud thunder! The damage is '+ str(LIGHTNING_DAMAGE) + ' hit points.', libtcod.light_blue)
		monster.fighter.take_damage(LIGHTNING_DAMAGE)

def consumable_crudenade():
	(x, y) = target_tile()
	if x is None: return 'cancelled'
	message('The grenade explodes, burning everything within ' + str(FIREBALL_RADIUS) + ' tiles!', libtcod.orange)

	for obj in objects:  #damage every fighter in range, including the player
		if obj.distance(x, y) <= FIREBALL_RADIUS and obj.fighter:
			message('The ' + obj.name + ' gets burned for ' + str(FIREBALL_DAMAGE) + ' hit points.', libtcod.orange)
			obj.fighter.take_damage(FIREBALL_DAMAGE)




libtcod.console_set_custom_font('terminal8x12_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)



main_menu()













