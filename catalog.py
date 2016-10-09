

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
				"Barely usable as a weapon, but still better than your fists. Just don't cut yourself."]

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

def get_item_special(itemname):
	if itemname == 'scrap metal sword':
		special = 'str bonus'
		value = 0.3

	else: return ['empty',None, None]

	return [itemname, special, value]



