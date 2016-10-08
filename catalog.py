

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
				'placeholder2']

FULL_CLASSLIST = ['warden',
				'placeholder1',
				'placeholder2']








def race_description(race):
	if race == 'human':
		description = 'A race that once thrived, now driven to the brink of slow destruction. Mostly content to be farmers and traders, although some rare enterprising souls take the sword and venture out. placeholder placeholder placeholder placeholder'
		return description



def get_item_description(itemname):
	if itemname == 'scrap metal sword':
		return ['Scrap metal sword',
				'A sword made out of spare scrap metal.',
				'Metal spurs protrude from the dull blade and veins of rust run across it.',
				"Barely usable as a weapon, but still better than your fists. Just don't cut yourself."]

	elif itemname == 'crude grenade':
		return ['Crude grenade',
				'placeholder']

	elif itemname == 'healing salve':
		return ['Healing salve',
				'placeholder']

	elif itemname == 'pipe gun':
		return ['Pipe gun',
				'placeholder']
