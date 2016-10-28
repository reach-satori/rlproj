

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
				'crude grenade',
				'metal plate',
				'goat leather sandals']

FULL_RACELIST = ['human',
				'anime catgirl',
				'placeholder2',
				'placeholder',
				'placeholder',
				'placeholder',
				'placeholder',
				'placeholder']

FULL_GCLASSLIST = ['warden',
				'placeholder1',
				'placeholder2']



class SkillNode(object):
	def __init__(self, name, tier, leveled, abilities, description, parent):
		self.name = name
		self.tier = tier
		self.leveled = leveled
		self.abilities = abilities
		self.description = description
		self.parent = parent

	def levelup(self):
		self.leveled = True





def get_nodetable(treename):
	if treename == 'combat':
		nodetable = [
		SkillNode(name = 'basic training', tier = 1, leveled = False, abilities = ['kicklaunch'], description = get_node_description('basic training'), parent = []),
		SkillNode(name = 'heavy blades', tier = 2, leveled = False, abilities = [],               description = get_node_description('heavy blades'),   parent = ['basic training'])
		]
	elif treename == 'tech':
		nodetable = [
		SkillNode(name = 'basic training', tier = 1, leveled = False, abilities = [], description = get_node_description('basic training'), parent = [])
		]

	elif treename == 'ritual':
		nodetable = [
		SkillNode(name = 'basic training', tier = 1, leveled = False, abilities = ['kicklaunch'], description = get_node_description('basic training'), parent = [])
		]

	elif treename == 'perks':
		nodetable = [
		SkillNode(name = 'shield focus', tier = 1, leveled = False, abilities = ['shield slam'], description = get_node_description('shield focus'), parent = [])
		]

	return nodetable

def get_node_description(node):
	if node == 'heavy blades':
		return ["KICKS THEIR WITH BIG METAL STICK PLACEHOLDER PLACEHOLDER", 'test test test']
	elif node == 'basic training':
		return['you can kill people better with your hands', 'test test test test']
	elif node == 'shield focus':
		return['shield bonus, shield slam granted']




def ccreation_description(choice):
	if choice == 'empty':
		description = ' '
	elif choice == 'human':
		description = 'A race that once thrived, now driven to the brink of slow destruction. Mostly content to be farmers and traders, although some rare enterprising souls take the sword and venture out. placeholder placeholder placeholder placeholder'
	elif choice == 'warden':
		description = 'generic warrior barbarian, at least until i think about the lore a wee bit lads'
	elif choice == 'anime catgirl':
		description = 'kyaa kawaii nyan'
	return description

def ccreation_stats(choice):
	if choice == 'empty':
		stats = [' ']
	elif choice == 'human':
		stats = ['this is the human statblock', 'it comes as strings in a list','because i dont know how to format it nicely using onlylibtcod','have you seen this console shit', 'seriously, this is bullshit']
	elif choice == 'warden':
		stats = ['more to combat','more to strength', 'more to constitution', 'decent starting weapons']
	elif choice == 'anime catgirl':
		stats = ['we','are', 'here', 'for', 'test', 'purposes']

	return stats


def get_item_description(itemname):
	if itemname == 'scrap metal sword':
		description = ['Scrap metal sword',
				'A sword made out of spare scrap metal.',
				'Metal spurs protrude from the dull blade and veins of rust run across it.',
				"Barely usable as a weapon, but still better than your fists. Just don't cut yourself.",
				'',
				'Damage roll: 2-6',
				'Strength bonus: 30%%',
				'Weight: 10']

	elif itemname == 'crude grenade':
		description = ['Crude grenade',
				'placeholder']

	elif itemname == 'healing salve':
		description = ['Healing salve',
				'placeholder']

	elif itemname == 'pipe gun':
		description = ['Pipe gun',
				'placeholder']

	elif itemname == 'goat leather sandals':
		description = ['Goat leather sandals.',
				'Better than cow leather, surprisingly.',
				'',
				'Dodge bonus: 2',
				'Weight: 2']

	elif itemname == 'metal plate':
		description = ['Strapped metal plate.',
				'A mishapen piece of flat metal with a strap, to hold on to.',
				'Will serve as a shield, for now.',
				'',
				'Armor bonus: 3',
				'Dodge bonus: 2',
				'Weight: 5']

	return description



	