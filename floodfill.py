import random

class Point(object):
	def __init__(self, x, y, tagged):
		self.x = x
		self.y = y
		self.tagged = tagged

def recursive_fill(grid, x, y):
	if not grid[x][y].tagged:
		grid[x][y].tagged = True

		if y > 0:
			recursive_fill(grid,x,y-1)
		if y < len(grid[x]) - 1:
			recursive_fill(grid,x,y+1)
		if x > 0:
			recursive_fill(grid,x-1,y)
		if x < len(grid) - 1:
			recursive_fill(grid,x+1,y)

	
	

def enclosed_space_processing(tilelist):
	x_list = [tile.x for tile in tilelist]
	y_list = [tile.y for tile in tilelist]
	normalized_tilelist = [Point(tile.x, tile.y, True) for tile in tilelist]
	for tile in normalized_tilelist:
		tile.x -= min(x_list)
		tile.y -= min(y_list)
	coordlist = [(point.x, point.y) for point in normalized_tilelist]





	height = max(y_list) - min(y_list) + 1
	width = max(x_list) - min(x_list) + 1 #height and width of the bounding box for the drawing, +1 so they are in tile units (all tiles in one Y coord results in a height of 1 rather than 0)

	grid = [[Point(x, y, False)
		for y in range(height + 2)] #create the expanded bounding box (one extra tile of empty (untagged) space to each side) for a width and height of +2
			for x in range(width + 2)]

	for x in range(width+2): #tag the input tiles (moved 1 space diagonally to the SE)
		for y in range(height+2):
			if (x, y) in coordlist: grid[x+1][y+1].tagged = True


#========================================#
	recursive_fill(grid, 0, 0)
#========================================#
	enclosed = []
	for x in range(width+2):  #currently this only tests if an enclosed space exists somewhere, it does not account for, say, enclosed spaces with a 'tail'
		for y in range(height+2):
			if not grid[x][y].tagged: enclosed.append((x+min([tile.x for tile in tilelist])-1, y+min([tile.y for tile in tilelist])-1))

	return enclosed











