

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
		factor = step/ (n+1)
		interpoints.append(round_point(lerp_point(corigin, cend, factor)))
		step += 1

	return interpoints
	


def round_point(p):
    return Point(round(p.x), round(p.y));


def lerp(start, end, t):
	return start + (t*(end-start))


def points_to_conpoints(p1, p2):
	newp1 = p1
	newp2 = p2

	dx = abs(p1.x - p2.x)
	dy = abs(p1.y - p2.y)
	minx = min(p1.x, p2.x)
	maxx = max(p1.x, p2.x)
	miny = min(p1.y, p2.y)
	maxy = max(p1.y, p2.y)

	for point in (newp1,newp2):
		if point.x == minx: point.x = 0
		if point.y == miny: point.y = 0
		if point.x == maxx: point.x = dx
		if point.y == maxy: point.y = dy



	return (newp1, newp2)

def determine_direction(origin, end):
	if end.x == origin.x and end.y == origin.y: return 'samesquare'
	if end.x > origin.x and end.y > origin.y:
		return 'to bottom-right'
	elif end.x < origin.x and end.y < origin.y:
		return 'to top-left'
	elif end.x > origin.x and end.y < origin.y:
		return 'to top-right'
	elif end.x < origin.x and end.y > origin.y:
		return 'to bottom-left'
	elif end.x == origin.x:
		if end.y > origin.y: return 'down'
		else: return 'up'
	elif end.y == origin.x:
		if end.x > origin.x: return 'right'
		else: return 'left'


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
