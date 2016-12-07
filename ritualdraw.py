from utility import *
import libtcodpy as libtcod
import graphical
from floodfill import enclosed_space_processing
from messages import *


class RitualDraw(object): #each drawing main body is represented by this
	def __init__(self, originx, originy, gamemap, gldir):
		self.length = 1
		self.originx = originx
		self.originy = originy
		self.player = gldir.player
		self.gamemap = gamemap
		self.drawdir = gldir.drawdir
		self.objects = gldir.game_objs
		self.drawntile_list = []
		self.game_msgs = gldir.game_msgs
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
		print shape
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
					message("The " + dude.name + " is blasted by a wave of energy!", libtcod.green, self.game_msgs)
			if glyph.special.char == 265:
				for dude in affected:
					dude.fighter.receive_status('DoT', 7, power = power)
					message('The '+ dude.name + "'s flesh starts to decay!", libtcod.green, self.game_msgs)
			if glyph.special.char == 266:
				for dude in affected:
					dude.fighter.receive_status('slow', int(round(float(power)/2)), power = power)
					message('The '+ dude.name + "'s movements become dull!", libtcod.green, self.game_msgs)

		for tile in self.drawntile_list:
			tile.special.char = "'"
		self.spent = True
		self.drawdir.drawinglist.remove(self)

	def get_affected(self):
		shape = self.determine_shape()
		tilecoords = map(lambda tile: (tile.x, tile.y), self.get_affected_tiles())
		affected = []
		for obj in self.objects:
			if (obj.x, obj.y) in tilecoords: affected.append(obj)

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

		elif shape == 'enclosed' or shape == 'diamond':
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


	def diamond_test(self):
		w, h = self.get_dimensions()
		all_x = map(lambda tile: tile.x, self.drawntile_list)
		all_y = map(lambda tile: tile.y, self.drawntile_list)
		if w != h: return False
		if w % 2 != 0: return False

		boundingbox = Rect(min(all_x), min(all_y), w, h)

		full_diamondtiles = []
		for i in range(w/2 + 1):
			tile1 = self.gamemap[boundingbox.x1 + i][boundingbox.y1 + w/2 - i]
			tile2 = self.gamemap[boundingbox.x1 + i][boundingbox.y1 + w/2 + i]
			tile3 = self.gamemap[boundingbox.x1 + w/2 + i][boundingbox.y1 + i]
			tile4 = self.gamemap[boundingbox.x1 + w/2 + i][boundingbox.y1 + w - i]
			full = [tile1, tile2, tile3, tile4]
			full_diamondtiles += full

		return set(full_diamondtiles) == set(self.drawntile_list)

	def focus_cross_test(self): #creates a focus cross (X) from the bounding box and tests if the actual drawing is the exact same
		w, h = self.get_dimensions()
		all_x = map(lambda tile: tile.x, self.drawntile_list)
		all_y = map(lambda tile: tile.y, self.drawntile_list)
		if w != h: return False

		boundingbox = Rect(min(all_x), min(all_y), w, h)
		diag1 = [self.gamemap[boundingbox.x1+i][boundingbox.y1+i] for i in range(w+1)]
		diag2 = [self.gamemap[boundingbox.x2-i][boundingbox.y1+i] for i in range(w+1)]


		full_crosstiles = diag1 + diag2

		return set(full_crosstiles) == set(self.drawntile_list)


	def aoe_cross_test(self):
		w, h = self.get_dimensions()
		all_x = map(lambda tile: tile.x, self.drawntile_list)
		all_y = map(lambda tile: tile.y, self.drawntile_list)
		if w != h: return False
		if w % 2 != 0: return False

		boundingbox = Rect(min(all_x), min(all_y), w, w)
		vert = [self.gamemap[boundingbox.x1 + w/2][boundingbox.y1 + i] for i in range(w+1)]
		hori = [self.gamemap[boundingbox.x1 + i][boundingbox.y1 + h/2] for i in range(w+1)]


		full_crosstiles = vert + hori

		return set(full_crosstiles) == set(self.drawntile_list)

	def determine_shape(self):
		if len(self.drawntile_list) <= 4: return 'linear'

		aoe_cross = self.aoe_cross_test()
		focus_cross = self.focus_cross_test()
		diamond = self.diamond_test()

		if aoe_cross == True and focus_cross == False and diamond == False: return 'aoe cross'
		elif aoe_cross == False and focus_cross == False and diamond == True: return 'diamond'
		elif aoe_cross == False and focus_cross == True and diamond == False: return 'focus cross'

		enclosed_coords = enclosed_space_processing(self.drawntile_list)

		if not enclosed_coords: return 'linear'
		else: return 'enclosed' 
		

			
	def merge(self, other_drawing):

		duplicates_removed = filter(lambda x: x not in self.drawntile_list, other_drawing.drawntile_list)
		self.drawntile_list += duplicates_removed
		self.drawdir.drawinglist.remove(other_drawing)

	def get_dimensions(self):
		xcoords = map(lambda tile: tile.x, self.drawntile_list)
		ycoords = map(lambda tile: tile.y, self.drawntile_list)
		height = (max(ycoords) - min(ycoords))
		width = (max(xcoords) - min(xcoords))

		return width, height