from utility import *
import libtcodpy as libtcod
import graphical
from floodfill import enclosed_space_processing


class RitualDraw(object): #each drawing main body is represented by this
	def __init__(self, originx, originy, player, gamemap, objects, drawdir):
		self.length = 1
		self.originx = originx
		self.originy = originy
		self.player = player
		self.gamemap = gamemap
		self.drawdir = drawdir
		self.objects = objects
		self.drawntile_list = []
		self.concluded = False
		self.spent = False

	def get_glyphs(self):
		glyphtile_list = filter(lambda tile: tile.special.name == 'glyph', self.drawntile_list)
		return glyphtile_list


	def add_drawntile(self, tile): #list of gamemap tiles involved
		self.drawntile_list.append(tile)

	def diagonal_exception(self): #i refuse to explain this, in fact i refuse to even look at it anymore
		for tile in self.drawntile_list:
			x = tile.x
			y = tile.y
			if self.gamemap[x+1][y].special and self.gamemap[x][y+1].special:
				if self.gamemap[x+1][y] not in self.drawntile_list and self.gamemap[x][y+1] not in self.drawntile_list:
					if self.gamemap[x+1][y].special.name in ['glyph', 'drawing'] and self.gamemap[x][y+1].special.name in ['glyph', 'drawing']:
						if self.gamemap[x+1][y+1] in self.drawntile_list:
							if self.gamemap[x+1][y].get_drawing() == self.gamemap[x][y+1].get_drawing():
								self.merge(self.gamemap[x][y+1].get_drawing())
								return

			if self.gamemap[x-1][y].special and self.gamemap[x][y+1].special:
				if self.gamemap[x-1][y] not in self.drawntile_list and self.gamemap[x][y+1] not in self.drawntile_list:
					if self.gamemap[x-1][y].special.name in ['glyph', 'drawing'] and self.gamemap[x][y+1].special.name in ['glyph', 'drawing']:
						if self.gamemap[x-1][y+1] in self.drawntile_list:
							if self.gamemap[x-1][y].get_drawing() == self.gamemap[x][y+1].get_drawing():
								self.merge(self.gamemap[x][y+1].get_drawing())
								return


	def evoke(self):
		self.diagonal_exception()

		self.drawntile_list = list(set(self.drawntile_list)) #glyphs were duplicating if they were placed in junctions of merged drawings for some reason, this fixes it
		power = 10
		glyphs = self.get_glyphs()
		affected = self.get_affected()
		shape = self.determine_shape()
		graphichandler = graphical.PlainAreaEffect(self.get_affected_tiles(), fadetime = 5, color1 = libtcod.white, color2 = libtcod.black)

		if shape == 'focus cross':
			if len(self.drawntile_list) % 4 == 0: size = len(self.drawntile_list)/4
			else:size = (len(self.drawntile_list)-1)/4
			power += 7*size

		elif shape == 'enclosed': power += 7
		power += self.player.rtree.level*2

		for glyph in glyphs:
			if glyph.special.char == 264:
				for dude in affected:
					if dude.fighter: dude.fighter.take_damage(int(round(power*1.5)))
					message("The " + dude.name + " is blasted by a wave of energy!")
			if glyph.special.char == 265:
				for dude in affected:
					dude.fighter.receive_status('DoT', 7, power = power)
					message('The '+ dude.name + "'s flesh starts to decay!")
			if glyph.special.char == 266:
				for dude in affected:
					dude.fighter.receive_status('slow', int(round(float(power)/2)), power = power)
					message('The '+ dude.name + "'s movements become dull!")

		for tile in self.drawntile_list:
			tile.special.char = "'"
		self.spent = True
		self.drawdir.drawinglist.remove(self)

	def get_affected(self):
		shape = self.determine_shape()

		affected = []
		if shape in ['aoe cross', 'focus cross']: center = self.get_center()

		if shape == 'focus cross' and center == None:
			for tile in self.drawntile_list:
				if self.gamemap[tile.x+1][tile.y] in self.drawntile_list and self.gamemap[tile.x][tile.y+1] in self.drawntile_list:
					center = tile # not really center, this is some fuckery that had to be solved with X crosses involving even numbers
					break  #but i dont feel like explaining it all so whatever

			for obj in self.objects:
				if obj.fighter and (obj.x, obj.y) in [(center.x, center.y),(center.x+1, center.y),(center.x, center.y+1),(center.x+1, center.y+1)]:
					affected.append(obj)

		elif shape == 'focus cross':
			for obj in self.objects:
					if obj.fighter and obj.distance_to(center) < 2: 
						affected.append(obj)

		elif shape == 'aoe cross':
			size = (len(self.drawntile_list) - 1)/4 #size is the length of each "arm" on the cross
			for obj in self.objects:
				if obj.fighter and obj.distance_to(center) <= size: 
					affected.append(obj)

		elif shape == 'linear':
			affected_coords = [(tile.x, tile.y) for tile in self.drawntile_list]
			for obj in self.objects:
				if obj.fighter and (obj.x, obj.y) in affected_coords:
					affected.append(obj)

		elif shape == 'enclosed':
			enclosed_coords = enclosed_space_processing(self.drawntile_list)
			line_coords = [(tile.x, tile.y) for tile in self.drawntile_list]
			for obj in self.objects:
				if obj.fighter and ((obj.x, obj.y) in enclosed_coords or (obj.x, obj.y) in line_coords):
					affected.append(obj)

		return affected

	def get_affected_tiles(self):
		shape = self.determine_shape()
		affected = []
		if shape in ['aoe cross', 'focus cross']: center = self.get_center()
		if shape == 'focus cross' and center == None:
			for tile in self.drawntile_list:
				if self.gamemap[tile.x+1][tile.y] in self.drawntile_list and self.gamemap[tile.x][tile.y+1] in self.drawntile_list:
					affected += [self.gamemap[tile.x+1][tile.y], self.gamemap[tile.x][tile.y], self.gamemap[tile.x][tile.y+1], self.gamemap[tile.x+1][tile.y+1]]

		elif shape == 'focus cross':
			cx = center.x
			cy = center.y
			for x in range(cx - 1, cx + 2):
				for y in range(cy - 1, cy + 2):
					affected.append(self.gamemap[x][y])

		elif shape == 'aoe cross':
			size = (len(self.drawntile_list) - 1)/4 #size is the length of each "arm" on the cross
			cx = center.x
			cy = center.y
			for x in range(cx - size, cx + size + 1):
				for y in range(cy - size, cy + size + 1):
					if distance_between(Point(x, y), center) <= size: affected.append(self.gamemap[x][y])

		elif shape == 'linear':
			affected += self.drawntile_list
		elif shape == 'enclosed':
			affected += self.drawntile_list
			enclosed_coords = enclosed_space_processing(self.drawntile_list)
			for x,y in enclosed_coords:
				affected.append(self.gamemap[x][y]) 
		return affected

	def get_center(self):
		center = None

		for tile in self.drawntile_list:
			x, y = tile.x, tile.y
			if tile.special.char == 197:
				if (self.gamemap[x+1][y] in self.drawntile_list) and (self.gamemap[x-1][y] in self.drawntile_list) and (self.gamemap[x][y+1] in self.drawntile_list) and (self.gamemap[x][y-1] in self.drawntile_list): # plus-shaped central tile
					center = tile
					break
			elif tile.special.char == 190:
				if self.gamemap[x+1][y+1] in self.drawntile_list and self.gamemap[x+1][y-1] in self.drawntile_list and self.gamemap[x-1][y+1] in self.drawntile_list and self.gamemap[x-1][y-1] in self.drawntile_list: # 'X shaped central tile'
					center = tile
					break

		return center

	def focus_cross_test(self): #creates a focus cross (X) from the bounding box and tests if the actual drawing is the exact same
		all_x = map(lambda tile: tile.x, self.drawntile_list)
		all_y = map(lambda tile: tile.y, self.drawntile_list)
		w = max(all_x) - min(all_x)
		h = max(all_y) - min(all_y)
		boundingbox = Rect(min(all_x), min(all_y), w, h)
		diag1 = [self.gamemap[boundingbox.x1+i][boundingbox.y1+i] for i in range(w+1)]
		diag2 = [self.gamemap[boundingbox.x2-i][boundingbox.y1+i] for i in range(w+1)]
		selfdiag1 = []
		selfdiag2 = []
		for tile in diag1:
			if tile in self.drawntile_list:
				selfdiag1.append(tile)
			else: return False
		for tile in diag2:
			if tile in self.drawntile_list:
				selfdiag2.append(tile)
			else: return False

		full_crosstiles = selfdiag1 + selfdiag2
		if set(full_crosstiles) == set(self.drawntile_list):
			return True
		else: return False






	def determine_shape(self): #what an ugly piece of code
		width, height = self.get_dimensions()
		aoe_cross = True
		focus_cross = True
		diamond = True
		nonglyphs = filter(lambda x: x.special.name == 'drawing', self.drawntile_list)
		charlist = map(lambda x: x.special.char, nonglyphs)
		if width == height: #only for this type of ritual drawing

			for char in charlist: #first, filter by size and characters
				if char not in [15, 196, 197, 179]:
					aoe_cross = False
				if char not in [15, 188, 189, 190]:
					focus_cross = False
				if char not in [15, 209, 210, 211, 212, 190, 188, 189]:
					diamond = False

			center_tile = self.get_center()
			if center_tile is None:
				aoe_cross = False
			elif center_tile.special.char == 188:
				aoe_cross = False
				diamond = False
			elif center_tile.special.char == 197:
				focus_cross = False
				diamond = False

			print aoe_cross, focus_cross, diamond
		 	#check for symmetry
			all_x = map(lambda tile: tile.x, self.drawntile_list)
			all_y = map(lambda tile: tile.y, self.drawntile_list)
			minx = min(all_x)
			miny = min(all_y)
			center_coord = Point(round(minx+float(width)/2 - 1), round(miny + float(height)/2 - 1))
			left_of_center = filter(lambda tile: tile.x < center_coord.x, self.drawntile_list)
			right_of_center = filter(lambda tile: tile.x > center_coord.x, self.drawntile_list)
			above_center = filter(lambda tile: tile.y < center_coord.y, self.drawntile_list)
			below_center = filter(lambda tile: tile.y > center_coord.y, self.drawntile_list)

			print len(left_of_center), len(right_of_center), len(above_center), len(below_center)
			if not len(left_of_center) == len(right_of_center) == len(above_center) == len(below_center):
				aoe_cross = False
				focus_cross = False
				diamond = False

			if self.focus_cross_test(): #the way it's done inside that method is much better than this filtering-down crap, perhaps i'll refactor it all into the same format later
				aoe_cross = False #in focus_cross_test i get the bounding box and draw out what would be the correct figure, then compare the two sets of tiles
				focus_cross = True
				diamond = False


		else: 
			aoe_cross = False
			focus_cross = False
			diamond = False

		if aoe_cross == True and focus_cross == False and diamond == False: return 'aoe cross'
		elif aoe_cross == False and focus_cross == False and diamond == True: return 'diamond'
		elif aoe_cross == False and focus_cross == True and diamond == False: return 'focus cross'

		enclosed_coords = enclosed_space_processing(self.drawntile_list)
		if not enclosed_coords: return 'linear'
		else: return 'enclosed' 
		

			
	def merge(self, inactive_drawing):
		global drawdir

		duplicates_removed = filter(lambda x: x not in self.drawntile_list, inactive_drawing.drawntile_list)
		self.drawntile_list += duplicates_removed
		drawdir.drawinglist.remove(inactive_drawing)

	def get_dimensions(self):
		xcoords = map(lambda tile: tile.x, self.drawntile_list)
		ycoords = map(lambda tile: tile.y, self.drawntile_list)
		height = (max(ycoords) - min(ycoords)) + 1
		width = (max(xcoords) - min(xcoords)) + 1

		return width, height