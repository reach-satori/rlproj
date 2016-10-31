from math import pi, acos, hypot

class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y





def createline(origin_obj, end_obj):
	origin = Point(origin_obj.x, origin_obj.y)
	end = Point(end_obj.x, end_obj.y)
	corigin, cend = points_to_conpoints(origin, end)

	interpoints = []

	n = float(diagonal_distance(corigin, cend))
	step = float(0)
	while step <= n:
		factor = step/ (n)
		interpoints.append(round_point(lerp_point(corigin, cend, factor)))
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
	for point in (newp1,newp2):           #
		if point.x == minx: point.x = 0   #   the effect is that the graphical effect that needs to be drawn and its size are known, but not where it should be drawn in the root console
		if point.y == miny: point.y = 0   #   that will be determined in another module and not here (because I don't know how to fuck with that stuff(yet))
		if point.x == maxx: point.x = dx  #
		if point.y == maxy: point.y = dy  #
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
