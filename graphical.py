from math import pi, acos, hypot, ceil, sqrt
import libtcodpy as libtcod


activeeffects = []

class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y

class EffectCon(object):
	def __init__(self, width, height, duration = 0):
		self.width = width
		self.height = height
		self.duration = duration
		self.maxduration = duration
		self.console = libtcod.console_new(width, height)

class FloatingText(EffectCon):
	def __init__(self, origin, text, color, duration = 8):
		width = len(text)
		height = 6
		EffectCon.__init__(self, width, height, duration) #duration in frames?? not sure how this is gonna work
		libtcod.console_set_default_foreground(self.console, color)

		self.text = text.upper() + '!'
		self.origin = origin
		self.color = color
		self.blitx = int(origin.camx - ceil(float(width)/2))
		self.blity = origin.camy - (height - 1)
		
		activeeffects.append(self)

	def draw(self):

		libtcod.console_clear(self.console)#perhaps set it up later so it only clears when it changes
		percent_through = (float(self.duration)/self.maxduration)

		ypos = int(round(lerp(0, self.height, percent_through))) - 1
		libtcod.console_print_ex(self.console, 0, ypos, libtcod.BKGND_NONE, libtcod.LEFT, self.text)
		libtcod.console_blit(self.console, 0, 0, 0, 0, 0, self.blitx, self.blity, 1, 0)
		libtcod.console_flush()


		self.duration -= 1

class PlainAreaEffect(EffectCon):
	def __init__(self, tilelist, fadetime, color1, color2):
		self.tilelist = tilelist
		self.color1 = color1
		self.color2 = color2
		allx = map(lambda tile: tile.x, self.tilelist)
		ally = map(lambda tile: tile.y, self.tilelist)
		minx = min(allx)
		maxx = max(allx)
		miny = min(ally)
		maxy = max(ally)
		self.blitx = minx
		self.blity = miny
		width = maxx - minx + 1
		height = maxy - miny + 1
		EffectCon.__init__(self, width, height, fadetime)

		libtcod.console_set_key_color(self.console, libtcod.silver)
		libtcod.console_set_default_background(self.console, libtcod.silver)#key color

		idx = [0, self.maxduration]
		col = [self.color1, self.color2]
		self.colormap = libtcod.color_gen_map(col, idx)



		newcoordlist = []
		for tile in self.tilelist:
			newcoordlist.append((tile.x - minx, tile.y - miny))
		self.con_coords = newcoordlist

		activeeffects.append(self)


	def draw(self):
		
		for x in range(self.width+1):
			for y in range(self.height+1):
				if (x, y) in self.con_coords:
					libtcod.console_set_char_background(self.console, x, y, self.colormap[self.maxduration - self.duration], flag=libtcod.BKGND_SET)
				else:
					libtcod.console_set_char_background(self.console, x, y, libtcod.silver, flag=libtcod.BKGND_SET)
		libtcod.console_blit(self.console, 0, 0, 0, 0, 0, self.blitx, self.blity, 0, 0.5)
		self.duration -= 1






class LineHandler(EffectCon):
	def __init__(self, origin, end, color, char= '', sleep = 50, duration = 0):#origin and end must be GameObj, otherwise have camx, camy attributes
	# duration 0 means 1 frame draw
		width, height = width_height_from_twopts(origin, end)
		EffectCon.__init__(self, width, height, duration)
		self.origin = origin
		self.end = end
		self.char = char
		self.color = color
		self.sleep = sleep
		libtcod.console_set_default_foreground(self.console, self.color)

		self.line = createline(origin, end)

		############################################
		activeeffects.append(self)

	def draw(self):#sleep is in miliseconds


		if self.char == '': self.char = determine_projchar(self.origin, self.end)#can't put functions in the definition line apparently, so its here instead
		
		libtcod.console_set_default_foreground(self.console, self.color)
		for point in self.line:
			libtcod.console_put_char(self.console,int(point.x), int(point.y), self.char, libtcod.BKGND_NONE)

		lastpoint = self.line[-1]
		libtcod.console_put_char(self.console, int(lastpoint.x), int(lastpoint.y), 9, libtcod.BKGND_NONE)
		libtcod.console_blit(self.console, 0, 0, 0, 0, 0, min(self.origin.camx, self.end.camx), min(self.origin.camy, self.end.camy), 1, 0)
		libtcod.console_flush()

		libtcod.sys_sleep_milli(self.sleep)

def get_increments(*args):
	if len(args) == 4:
		origin = Point(args[0],args[1])
		target = Point(args[2], args[3])
	elif len(args) == 2:
		origin = args[0]
		target = args[1]

	if origin.x == target.x and origin.y == target.y: return 0, 0

	if origin.x == target.x: dx = 0
	elif origin.y == target.y: dy = 0

	if target.x > origin.x: dx = 1
	elif target.x < origin.x: dx = -1

	if target.y > origin.y: dy = 1
	elif target.y < origin.y: dy = -1

	return int(dx), int(dy)



def render_effects():
	global activeeffects
	for effect in activeeffects:
		if effect.duration == 0: 
			activeeffects.remove(effect)
			# libtcod.console_delete(effect.console)
		else: effect.draw()

def console_from_twopts(origin, end):
	width = abs(max(origin.x, end.x) - min(origin.x, end.x)) + 1
	height = abs(max(origin.y, end.y) - min(origin.y, end.y)) + 1

	return libtcod.console_new(width, height)

def width_height_from_twopts(origin, end):
	width = abs(max(origin.x, end.x) - min(origin.x, end.x)) + 1
	height = abs(max(origin.y, end.y) - min(origin.y, end.y)) + 1
	return width, height


def createline(origin_obj, end_obj):
	origin = Point(origin_obj.x, origin_obj.y)
	end = Point(end_obj.x, end_obj.y)
	conorigin, conend = points_to_conpoints(origin, end)

	interpoints = []

	n = float(diagonal_distance(conorigin, conend))
	step = float(0)
	while step <= n:
		factor = step/ (n)
		interpoints.append(round_point(lerp_point(conorigin, conend, factor)))
		step += 1

	return interpoints
	


def round_point(p):
    return Point(round(p.x), round(p.y));


def lerp(start, end, t):
	return start + (t*(end-start))


def points_to_conpoints(p1, p2):
	newp1 = p1                            #
	newp2 = p2                            #
#                                         #
	dx = abs(p1.x - p2.x)                 #
	dy = abs(p1.y - p2.y)                 #
	minx = min(p1.x, p2.x)                #
	maxx = max(p1.x, p2.x)                #   this function maps any 2 points to extremum points in a separate grid
	miny = min(p1.y, p2.y)                #   kind of like removing a rectangular section defined by 2 diagonal points, setting the top left to 0,0 and then returning
	maxy = max(p1.y, p2.y)                #   the new coordinates
#                                         #   this is necessary because i'm using separate consoles to draw graphical effects, which makes things a lot easier
	for newp in (newp1,newp2):           #
		if newp.x == minx: newp.x = 0   #   the effect is that the graphical effect that needs to be drawn and its size are known, but not where it should be drawn in the root console
		if newp.y == miny: newp.y = 0   #   that will be determined in another module and not here (because I don't know how to fuck with that stuff(yet))
		if newp.x == maxx: newp.x = dx  #
		if newp.y == maxy: newp.y = dy  #
#                                         #


	return (newp1, newp2)


def determine_projchar(p1, p2):                         #                                         
	if p1.y == p2.y: return '-'                         #                                         
	elif p1.x == p2.x: return '|'                       #                                       
	elif p1.y > p2.y:                                   #                     t           t       
		lower = p1                                      #                     |          /           
		upper = p2                                      #                     |   "|"   /            
	elif p2.y > p1.y:                                   #                     | 20 deg /             
		lower = p2                                      #                     |       /              
		upper = p1                                      #                     |      /     "/"       
#                                                       #                     |     /    50 deg      
	dy = lower.y - upper.y                              #                     |    /                 
	dx = lower.x - upper.x                              #           idem      |   /          ___---t      
	dist = hypot(dx, dy)                                #                     |  /     __----             
	theta = acos(float(dx/dist)) * 180 / pi             #                     | / ___--     20 deg "-" 
#                                                       #     ________________o---________________t
	if 160 <= theta < 180 or 0 < theta <= 20: return '-'#
	elif 110 <= theta < 160: return '/'                 #    takes point with bigger y as lower than does acos to find angle
	elif 70 <= theta < 110: return '|'                  #
	else: return '\\'                                   #
#                                                       #



def lerp_point(p1, p2, t):
	newx = lerp(p1.x, p2.x, t)
	newy = lerp(p1.y, p2.y, t)
	point = Point(newx, newy)
	return point

def line(p1, p2):
	points = []
	step = 0
	n = diagonal_distance(p1, p2)
	for step in range(n+1):
		t = step / n
		points.append(lerp_point(p1, p2, t))

def diagonal_distance(p1, p2):
	dx = p1.x - p2.x
	dy = p1.y - p2.y
	return max(abs(dx), abs(dy))
