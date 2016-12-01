from random import gauss
import math

class Rect:
	def __init__(self, x, y, w, h):
		self.x1 = x
		self.y1 = y
		self.x2 = x+w
		self.y2 = y+h


	def center(self):
		center_x = (self.x1+self.x2)/2
		center_y = (self.y1+self.y2)/2
		return (center_x,center_y)

	def intersect(self,other):
		return (self.x1 <= other.x2 and self.x2 >= other.x1 and self.y1 <= self.y2 and self.y2 >= other.y1)
		#check if rectangle intersects with another one


class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y


def distance_between(p1, p2): #p1 p2 points
	dx = p1.x - p2.x
	dy = p1.y - p2.y
	return math.sqrt(dx**2 + dy**2)
	
def normal_randomize(mean,sd): #input mean, sd for gauss distribution

	floatnormal = gauss(float(mean),float(sd)) #output one sample, rounded and non-negative
	if floatnormal <= 1: return 1
	return int(round(floatnormal))