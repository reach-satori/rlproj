from sett import *
import libtcodpy as libtcod

class Camera(object):
	def __init__(self, w = CAMERA_WIDTH, h = CAMERA_HEIGHT, x=0, y=0, player = None, fov_map = None, gamemap = None, con = None):
		self.width = w
		self.height = h
		self.x = x
		self.y = y
		self.player = player
		self.fov_map = fov_map
		self.gamemap = gamemap
		self.con = con

	def reset_position(self, coord = 'both'):

		if coord == 'xreset' or coord == 'both': self.x = self.player.x - self.width/2 # less than 0 type errors get dont happen because of setter properties
		if coord == 'yreset' or coord == 'both': self.y = self.player.y - self.height/2 # centers camera on self.self.player
		libtcod.console_clear(self.con)



	def check_for_posreset(self, xdiff = FREEMOVE_WIDTH, ydiff = FREEMOVE_HEIGHT):
		centerx, centery = self.center
		if (self.player.x > centerx + xdiff or self.player.x < centerx - xdiff) and (self.player.y > centery + ydiff or self.player.y < centery - ydiff): #the ugliest code
			return 'both'

		if self.player.x > centerx + xdiff: return 'xreset'  
		elif self.player.x < centerx - xdiff: return 'xreset'
#                                                       
		if self.player.y > centery + ydiff: return 'yreset'  
		elif self.player.y < centery - ydiff: return 'yreset'
														

		return False

	def camera_render(self):
		if self.check_for_posreset(): self.reset_position(self.check_for_posreset())

		for camy in range(self.height):
			mapy = self.y + camy
			for camx in range(self.width):
				mapx = self.x + camx

				visible = libtcod.map_is_in_fov(self.fov_map, mapx, mapy)
				wall = self.gamemap[mapx][mapy].block_sight
				special = self.gamemap[mapx][mapy].special
				if not visible:
					if self.gamemap[mapx][mapy].explored:
						if wall:
							libtcod.console_put_char_ex(self.con, camx, camy, '#', color_dark_wall, libtcod.black)           #
						else:                                                                                     #
							libtcod.console_put_char_ex(self.con, camx, camy, '.', color_dark_ground, libtcod.black)         # OK this looks bad but it's quite simple actually, i'm sure it could be written more elegantly with abs or something
						if special and wall:                                                                      # basically there are 3 nested rectangles: the biggest beingthe actual map where objects interact and the game happens, the second is the camera, which gets rendered to con in camera_render method
							libtcod.console_put_char_ex(self.con, camx, camy, special.char, color_dark_wall, libtcod.black)  # the third is a phantom FREEMOVE square which is checked in check_for_posreset and all it does is center the camera position (separately for x and y) when the self.player walks outside of it
						elif special and not wall:                                                                 #most of the complexity is just in juggling coordinates between camera and map, but it more or less comes down to : 
							libtcod.console_put_char_ex(self.con, camx, camy, special.char, color_dark_ground, libtcod.black) #mapcoord = camera_origin_coord + current_camera_coord: that's those mapx and mapy variables. works like poschengband camera
				else: #it's visible
					if wall:
						libtcod.console_put_char_ex(self.con, camx, camy, '#', color_light_wall, libtcod.black)
					else:
						libtcod.console_put_char_ex(self.con, camx, camy, '.', color_light_ground, libtcod.black)
					if special:
						libtcod.console_put_char_ex(self.con, camx, camy, special.char, special.foreground, special.background)
					self.gamemap[mapx][mapy].explored = True




	@property
	def center(self):
		centerx = self.x + self.width/2
		centery = self.y + self.height/2
		return centerx, centery

	@property
	def x2(self):
		return self.x + self.width

	@property
	def y2(self):
		return self.y + self.height
	
	

	@property
	def x(self):
		return self._x

	@property
	def y(self):
		return self._y
	
	@x.setter
	def x(self, value):
		if value < 0: value = 0
		if value > MAP_WIDTH - self.width: value = MAP_WIDTH - self.width
		self._x = value

	@y.setter
	def y(self, value):
		if value < 0: value = 0
		if value > MAP_HEIGHT - self.height: value = MAP_HEIGHT - self.height
		self._y = value




def render_all(fov_map, fov_recompute, objects, game_msgs, player, camera, panel, con, dungeon_level):#globals used: fov_map, fov_recompute, objects, game_msgs, player, camera, panel, con

	if fov_recompute:
		fov_recompute = False
		libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)
				
	camera.camera_render()

	for obj in objects:
		if obj.in_camera(): obj.draw()

	player.draw()
	for obj in objects:
		if obj.name == 'targeter': obj.draw()

	#blits the content of the 'con' console to the root console
	libtcod.console_blit(con, 0, 0, CAMERA_WIDTH, CAMERA_HEIGHT, 0, 0, 0)
	libtcod.console_set_default_background(panel, libtcod.black)
	libtcod.console_clear(panel)
	#print game messages, one line at a time
	y = 1
	for (line, color) in game_msgs:
		libtcod.console_set_default_foreground(panel,color)
		libtcod.console_print_ex(panel,MSG_X, y, libtcod.BKGND_NONE, libtcod. LEFT, line)
		y += 1

	render_bar(1, 1, BAR_WIDTH, 'Health', player.fighter.hp, player.fighter.max_hp, libtcod.dark_red, libtcod.darkest_red, panel) # display health
	libtcod.console_print_ex(panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon level ' + str(dungeon_level))  #display dungeon level

	
	#blits the content of the 'panel' console to the root console
	libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color, panel):
	bar_width = int(float(value) / maximum * total_width)

	libtcod.console_set_default_background(panel, back_color)
	libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)


	libtcod.console_set_default_background(panel, bar_color)
	if bar_width > 0:
		libtcod.console_rect(panel,x,y,bar_width, 1, False, libtcod.BKGND_SCREEN)

	libtcod.console_set_default_foreground(panel, libtcod.white)
	libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER, name + ': ' + str(value) + '/' + str(maximum))