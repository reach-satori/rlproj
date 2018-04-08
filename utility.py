from random import gauss
import math
import libtcodpy as libtcod

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

def obj_to_point(obj):
    return Point(int(obj.x), int(obj.y))

def distance_between(p1, p2): #p1 p2 points
    dx = p1.x - p2.x
    dy = p1.y - p2.y
    return math.sqrt(dx**2 + dy**2)

def normal_randomize(mean,sd): #input mean, sd for gauss distribution

    floatnormal = gauss(float(mean),float(sd)) #output one sample, rounded and non-negative
    if floatnormal <= 1: return 1
    return int(round(floatnormal))


def random_choice(chances_dict):
    #choose one option from dictionary of chances, returning its key
    chances = chances_dict.values()
    strings = chances_dict.keys()
    return strings[random_choice_index(chances)]  

def product(iterable):
    if hasattr(iterable, '__iter__'):
        p = 1
        for n in iterable:
            p *= n
        return p
    else: return iterable


def random_choice_index(chances):  #choose one option from list of chances, returning its index
    #the dice will land on some number between 1 and the sum of the chances
    if chances == []: return 0
    dice = libtcod.random_get_int(0, 0, sum(chances)) #getting a [] from random_choice  < get_random_item_of_depthlevel

 
    #go through all chances, keeping the sum so far
    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w            
 
        #see if the dice landed in the part that corresponds to this choice
        if dice <= running_sum:
            return choice 
        choice += 1
