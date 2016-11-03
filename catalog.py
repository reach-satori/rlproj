from random import choice
import graphical
import libtcodpy as libtcod

SLOTLIST = ['head', 
			'hands', 
			'chest', 
			'right hand', 
			'left hand', 
			'amulet', 
			'left ring', 
			'right ring', 
			'back', 
			'feet']

FULL_STATUSEFFECTLIST = ['maim']


FULL_INAMELIST = ['healing salve', 
				'pipe gun', 
				'scrap metal sword',
				'crude grenade',
				'metal plate',
				'goat leather sandals',
				'kitchen knife',
				'rebar blade']

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

salve_adjs= ['red',
			'blue',
			'green',
			'brown',
			'purple',
			'disgusting',
			'pink',
			'rainbow-coloured'
			'dull',
			'pale',
			'milky',
			'white',
			'sticky',
			'golden',
			'black',
			'smelly',
			'flowery',
			'bronze',
			'metallic',
			'shining',
			'swirling',
			'liquid',
			'rubbery',
			'nearly solid',
			'watery',
			'vibrant',
			'dry',
			'greenish',
			'blueish',
			'sickly',
			'heavy',
			'fuming',
			'steaming',
			'silvery',
			'crusty',
			'flaky',
			'slowly bubbling',
			'hot',
			'sizzling',
			'cold',
			'orange',
			'moldy'
			]
gadget_adjs = ['striped',
			'plastic',
			'red',
			'blue',
			'green',
			'brown',
			'purple',
			'pink',
			'yellow',
			'orange',
			'rusted',
			'moldy',
			'golden',
			'silvery',
			'bronze',
			'shiny',
			'polished',
			'old',
			'decayed',
			'scratched',
			'scuffed',
			'stained',
			'bent',
			'dirty',
			'glossy',
			'matte',
			'gleaming',
			'corroded',
			'deteriorating',
			'worn',
			'rainbow-coloured',
			'antiquated',
			'spotless'
			]


class EqSpecial:
	def __init__(self, owner, enchantlist = []):
		self.owner = owner
		self.enchantlist = get_native_enchants(self)



	



		

class EnchantModule(object):
	def __init__(self, owner, name, value, isnative = False, duration = 0):
		self.isnative = isnative
		self.owner = owner
		self.name = name
		self.value = value
		self.duration = duration
		self.typelist = []


		self.get_typelist()

	def get_typelist(self):
		typelist = []
		if self.name == 'str bonus': 
			self.typelist.append('on atk bonus')
		if self.name == 'maim chance':
			self.typelist.append('on atk bonus')
			self.typelist.append('status applier')




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

def get_status_startfunction(status):
	if status.name == 'maim':
		return graphical.FloatingText(status.affected.owner, status.name, libtcod.violet)

def get_status_stepfunction(status):
	pass

def get_native_enchants(eqspecial): #must return list of EnchantModule objects
	nativelist = []
	#   eqspecial.equipment.gameobj.name
	if eqspecial.owner.owner.name == "rebar blade":
		nativelist.append(EnchantModule(eqspecial, 'str bonus', 0.45, True))
		nativelist.append(EnchantModule(eqspecial, 'maim chance', 0.3, True, duration = 30))
	elif eqspecial.owner.owner.name == 'scrap metal sword':
		nativelist.append(EnchantModule(eqspecial, 'str bonus', 0.25, True))
		nativelist.append(EnchantModule(eqspecial, 'maim chance', 0.25, True, duration = 20))
	elif eqspecial.owner.owner.name == 'kitchen knife':
		nativelist.append(EnchantModule(eqspecial, 'multiattack', 0.25, True))

	return nativelist



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

def random_salve_name(salve):
	global salve_adjs
	if 0 < salve.depth_level <= 4:
		adjnum = 1
	elif 4 < salve.depth_level <= 9:
		adjnum = 2
	else: adjnum = 3

	adjlist = []
	for index in range(adjnum):
		adj = choice(salve_adjs)
		adjlist.append(adj)
		salve_adjs.remove(adj)

	name = 'a ' + ', '.join(adjlist) + ' salve'

	return name

def random_gadget_name(gadget):
	global gadget_adjs
	if 0 < gadget.depth_level <= 4:
		adjnum = 1
	elif 4 < gadget.depth_level <= 9:
		adjnum = 2
	else: adjnum = 3

	adjlist = []
	for index in range(adjnum):
		adj = choice(gadget_adjs)
		adjlist.append(adj)
		gadget_adjs.remove(adj)

	name = 'a ' + ', '.join(adjlist) + ' ' + choice(['thingamajig', 'doodad', 'doohickey', 'thingamabob', 'gadget', 'device', 'gizmo', 'apparatus', 'contraption', 'widget'])

	return name






def get_item_description(item):

	if item.owner.name == 'scrap metal sword':
		description = [
					'Scrap metal sword',
					'A sword made out of spare scrap metal.',
					'Metal spurs protrude from the dull blade and veins of rust run across it.',
					"Barely usable as a weapon, but still better than your fists. Just don't cut yourself."
					]
		if item.identified: description + [
		'',
		'Damage roll: ' + str(item.base_dmg[0]) + '-' + str(item.base_dmg[1]),
		'Strength bonus: ' + str(item.special.on_atk_bonus['str bonus']*100) + '%%',
		'Weight: ' + str(item.weight)
		]

	elif item.owner.name == 'rebar blade':
		description = [
					'Rebar blade',
					'A massive, thick piece of rebar, with one end sharpened into a blade.',
					"The other end has a strap of leather tied around it, to protect the wielder's hand.",
					"Quite heavy. You can't use it with only one hand."
					]
		if item.identified: description + [
		'',
		'Damage roll: ' + str(item.base_dmg[0]) + '-' + str(item.base_dmg[1]),
		"Special: This item has a chance to maim on hit, severely impairing the target's movement.",
		'Strength bonus: ' + str(item.special.on_atk_bonus['str bonus']*100) + '%%',
		'Weight: ' + str(item.weight)
		]

	elif item.owner.name == 'kitchen knife':
		description = [
					'Kitchen knife',
					"Ordinary light knife you'd find in any kitchen. This one is sharp and clean.",
					"Not exactly made for combat, but it'll do the job."
					]
		if item.identified: description + [
		'',
		'Damage roll: ' + str(item.base_dmg[0]) + '-' + str(item.base_dmg[1]),
		'Special: This item can multiattack.',
		'Weight: ' + str(item.weight)
		]

	elif item.owner.name == 'crude grenade':
		description = [
		        'Crude grenade',
				'placeholder'
				]

	elif item.owner.name == 'healing salve':
		description = [
		        'Healing salve',
				'placeholder'
				]

	elif item.owner.name == 'pipe gun':
		description = [
		        'A crude pipe gun.',
				'An explosive charge attached to the end of scavenged brass tubing,',
				'which is filled with nails and metal bits. Good for one use.',
				'',
				'Damage: 20',
				'Range: 6',
				'Weight: ' + str(item.weight)
				]

	elif item.owner.name == 'goat leather sandals':
		description = [
		        'Goat leather sandals.',
				'Comfortable and better than cow leather, surprisingly.']
		if item.identified: description + [
				'',
				'Dodge bonus: ' + str(item.equipment.dodge_bonus),
				'Weight: ' + str(item.weight)
				]

	elif item.owner.name == 'metal plate':
		description = [
		        'Strapped metal plate.',
				'A mishapen piece of flat metal with a strap, to hold on to.',
				'Will serve well enough as a shield, for now.']
		if item.identified: description + [
				'',
				'Armor bonus: ' + str(item.equipment.armor_bonus),
				'Dodge bonus: ' + str(item.equipment.dodge_bonus),
				'Weight: ' + str(item.weight)
				]




	if item.itemtype == 'salve' and not item.identified:
		description = [
		        'An unknown salve.',
				'A strange gel-like substance inside a container.',
				'Who knows what it could do?'
				]

	if item.itemtype == 'gadget' and not item.identified:
		description = [
		        'An unknown gadget.',
				'Some kind of machine or tool, currently beyond your understanding.',
				'Who knows what it could do?'
				] 

	return description

