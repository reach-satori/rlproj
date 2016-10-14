

SLOTLIST = ['head', 
			'hands', 
			'armour', 
			'right hand', 
			'left hand', 
			'amulet', 
			'left ring', 
			'right ring', 
			'backpack', 
			'boots']

FULL_INAMELIST = ['healing salve', 
				'pipe gun', 
				'scrap metal sword',
				'crude grenade']

FULL_RACELIST = ['human',
				'placeholder1',
				'placeholder2',
				'placeholder',
				'placeholder',
				'placeholder',
				'placeholder',
				'placeholder']

FULL_GCLASSLIST = ['warden',
				'placeholder1',
				'placeholder2']

combattable = [

					]

class SkillNode(object):
	def __init__(self, name, level, leveled, abilities, description):
		self.name = name
		self.level = level
		self.leveled = leveled
		self.name = name
		self.abilities = abilities
		self.description = description

def get_nodetable(treename):
	if treename == 'combat':
		nodetable = [

		SkillNode(name = 'basic training', level = 1, leveled = False, abilities = ['kicklaunch'], description = node_description('basic training')),
		SkillNode(name = 'heavy blades', level = 2, leveled = False, abilities = [], description = node_description('heavy blades'))
		]
	elif treename == 'tech':
		nodetable = []

	elif treename == 'ritual':
		nodetable = []

	return nodetable

def node_description(node):
	if node == 'kicklaunch':
		return ["KICKS THEIR ASS FOR 3 TILES PLACEHOLDER PLACEHOLDER"]
	if node == 'basic training':
		return['placeholder placeholder']




def ccreation_description(choice):
	if choice == 'empty':
		description = ' '
	elif choice == 'human':
		description = 'A race that once thrived, now driven to the brink of slow destruction. Mostly content to be farmers and traders, although some rare enterprising souls take the sword and venture out. placeholder placeholder placeholder placeholder'
	elif choice == 'warden':
		description = 'generic warrior barbarian, at least until i think about the lore a wee bit lads'
	return description

def ccreation_stats(choice):
	if choice == 'empty':
		stats = [' ']
	elif choice == 'human':
		stats = ['this is the human statblock', 'it comes as strings in a list','because i dont know how to format it nicely using onlylibtcod','have you seen this console shit', 'seriously, this is bullshit']
	elif choice == 'warden':
		stats = ['more to combat','more to strength', 'more to constitution', 'decent starting weapons']

	return stats


def get_item_description(itemname):
	if itemname == 'scrap metal sword':
		description = ['Scrap metal sword',
				'A sword made out of spare scrap metal.',
				'Metal spurs protrude from the dull blade and veins of rust run across it.',
				"Barely usable as a weapon, but still better than your fists. Just don't cut yourself.",
				'',
				'Damage roll: 2-6',
				'Strength bonus: 30%%']

	elif itemname == 'crude grenade':
		description = ['Crude grenade',
				'placeholder']

	elif itemname == 'healing salve':
		description = ['Healing salve',
				'placeholder']

	elif itemname == 'pipe gun':
		description = ['Pipe gun',
				'placeholder']

	return description

def get_item_special(item): #take item's object and returns dictionary with {'special_name':special_value} (special value is 0 if not applicable)
	specialdict = {}
	if item.owner.name == 'scrap metal sword':
		specialdict['str bonus'] = 0.3  # gives item a .str_bonus attribute on equip, which then gets checked at attack in the power property of the fighter
	
	
	#to clarify how specials work, since it's a mess and i don't know how to make it better:
	#whenever an item gets equipped, it checks this spot and gets a property added in the apply_special method(called inside equip)
	#which is in turn used for whatever purpose wherever it's needed by way of me manually adding it
	#it's gonna be really horrible and give me a headache i'me sure, but i'm new at programmin and don't know how else to do it
	#I suppose I could make categories for specials, but that's a little restricting and I'm gonna have to open it up again
	#when I want to make an item do something unique anyway so

	#at least i can catalogue here exactly what each special does and where the code is
	
	return specialdict



	