import pygame, math, sys, os
from pygame.locals import *
from random import randint
from sys import argv

class CharacterObject(pygame.sprite.Sprite):
	def __init__(self, screen, images, starting_position, x_limits=None):
		pygame.sprite.Sprite.__init__(self)
		
		self.x_movement_limit_left = None
		self.x_movement_limit_right = None
		if x_limits != None:
			self.x_movement_limit_left = x_limits[0]
			self.x_movement_limit_right = x_limits[1]
			
		self.screen = screen
		self.images = images
		self.image = images[0]		
		self.pos = starting_position		
		
		self.rect = self.image.get_rect()		
		self.rect.center = self.pos		
		
		#image lists by direction
		self.left_images 	= self.images[:LEFT_3	+ 1	]		
		self.right_images 	= self.images[LEFT_3 	+ 1	:RIGHT_3 	+ 1	]
		#currently only using left/right animations
		'''
		self.idle_images 	= self.images[RIGHT_3	+ 1 :IDLE_3 	+ 1	]				
		self.up_images 		= self.images[IDLE_3 	+ 1	:UP_3 		+ 1	]
		self.down_images 	= self.images[UP_3 		+ 1	:DOWN_3 	+ 1	]
		'''
		
		#collision rectangles and stats
		self.bottom_collision_rect = pygame.Rect( self.rect.bottomleft, ( self.rect.width, FLOOR_HEIGHT - self.rect.bottom ) )		
		self.right_side_collision_rect = pygame.Rect( self.rect.topright, (RIGHT_RECT_WIDTH, self.rect.height-2) )
		self.left_side_collision_rect = pygame.Rect( (self.rect.left - LEFT_RECT_WIDTH, self.rect.top), self.rect.bottomleft )
		
		self.isCollidingRight = False
		self.isCollidingLeft = False
		self.isCollidingBottom = False
		
		#individual counters for individual image list current image position
		self.idle_ind 	= 0
		self.left_ind 	= 0
		self.right_ind 	= 0
		self.up_ind 	= 0
		self.down_ind 	= 0
		
		#jump stats
		self.jumpCounter 	= 0
		self.isAirborne 	= False
		self.fall_speed 	= 0
		self.jump_speed 	= 15
		
	def update(self, direction):
		
		collide_left = self.left_side_collision_rect.collidelist([x.rect for x in EVERY_CHARACTER_SPRITE_GROUP])
		collide_right = self.right_side_collision_rect.collidelist([x.rect for x in EVERY_CHARACTER_SPRITE_GROUP])
		collide_bottom = self.bottom_collision_rect.collidelist([x.rect for x in FOREGROUND_SPRITE_GROUP])
		
		#test for collisions
		if collide_left == -1: self.isCollidingLeft = False
		else: self.isCollidingLeft = True
		if collide_right == -1: self.isCollidingRight = False
		else: self.isCollidingRight = True
		if collide_bottom == -1: self.isCollidingBottom = False
		else: self.isCollidingBottom = True			
		
		#jump indicated, not already in the air
		if direction == UP and not self.isAirborne:	
			self.jumpCounter = 5					
		
		if direction == LEFT:
			self.right_ind = 0			
			if collide_left == -1: #if not colliding to the left
				self.isCollidingLeft = False
				#update image for animation
				if self.left_ind == 15: self.left_ind = 0 
				else: self.left_ind += 1
				self.image = self.left_images[self.left_ind/5]					
			else: #colliding left				
				self.isCollidingLeft = True
		elif direction == RIGHT:
			self.left_ind = 0
			if collide_right == -1: #if not colliding tot he right
				self.isCollidingRight = False
				#update image for animation
				if self.right_ind == 15: self.right_ind = 0
				else: self.right_ind += 1
				self.image = self.right_images[self.right_ind/5]		
			else: #colliding right
				self.isCollidingRight = True
		
		#direction != left, direction != right, upward movement required from jump
		elif self.jumpCounter > 0:			
			self.isAirborne = True
			self.jumpCounter -= 1
			self.pos = (self.pos[0], self.pos[1]-self.jump_speed*self.jumpCounter)			
			
		#airborne from jump, or simply above the floor height, and not colliding with anything below
		elif self.isAirborne or self.pos[1] < FLOOR_HEIGHT:
							
			#extending collision rectangle from bottom of self.rect up to current fall_speed
			if collide_bottom != -1:				
				if ( abs(self.rect.bottom - [x.rect for x in FOREGROUND_SPRITE_GROUP][collide_bottom].top) ) <= ( self.fall_speed + 2 ):
					self.isCollidingBottom = True
					self.isAirborne = False
					self.fall_speed = 0
					self.pos = (self.pos[0], [x.rect for x in FOREGROUND_SPRITE_GROUP][collide_bottom].top - self.rect.height/2 - 1)							
			
			if self.pos[1] < FLOOR_HEIGHT:
				self.fall_speed += 2
				self.pos = (self.pos[0], self.pos[1]+self.fall_speed)
				
		#somehow below the floor, move back to floor	
		if self.pos[1] > FLOOR_HEIGHT: 
			self.isAirborne = False
			self.fall_speed = 0
			self.pos = (self.pos[0], FLOOR_HEIGHT)
				
		self.rect = self.image.get_rect()
		self.rect.center = self.pos		
		
		#re-set collision rects based on new character object self.rect location
		self.bottom_collision_rect = pygame.Rect( self.rect.bottomleft, ( self.rect.width, self.fall_speed ) ) 
		self.right_side_collision_rect = pygame.Rect( self.rect.topright, (RIGHT_RECT_WIDTH, self.rect.height-2) )
		self.left_side_collision_rect = pygame.Rect( (self.rect.left - LEFT_RECT_WIDTH, self.rect.top), (LEFT_RECT_WIDTH, self.rect.height-2) )		
	
class AICharacterObject(CharacterObject):
	def __init__(self, screen, images, starting_position, ai_type = 0):
		CharacterObject.__init__(self, screen, images, starting_position)
		self.char_type = ai_type
	
	def update(self, direction):
		move_speed = BACKGROUND_SPEED
		if direction == LEFT and self.isCollidingLeft == False: 					
			self.pos = (self.pos[0] - move_speed, self.pos[1])
		elif direction == RIGHT and self.isCollidingRight == False: 			
			self.pos = (self.pos[0] + move_speed, self.pos[1])
		elif direction == PLAYER_LEFT_ONLY: 
			self.pos = (self.pos[0] + move_speed, self.pos[1])
			direction = None
		elif direction == PLAYER_RIGHT_ONLY: 
			self.pos = (self.pos[0] - move_speed, self.pos[1])
			direction = None
		super(AICharacterObject, self).update(direction)	
	
class PlayerObject(CharacterObject):
	def __init__(self, screen, images, starting_position):
		CharacterObject.__init__(self, screen, images, starting_position)
	
	def update(self, direction):		
		move_speed = BACKGROUND_SPEED
		if direction == LEFT:
			if self.pos[0] > SCREEN_WIDTH/2 + move_speed:
				self.pos = (self.pos[0] - move_speed, self.pos[1])				
			elif self.pos[0] > SCREEN_WIDTH/2:
				self.pos = (SCREEN_WIDTH/2, self.pos[1])
		elif direction == RIGHT:
			if self.pos[0] < SCREEN_WIDTH/2 - move_speed:
				self.pos = (self.pos[0] + move_speed, self.pos[1])				
			elif self.pos[0] < SCREEN_WIDTH/2:
				self.pos = (SCREEN_WIDTH/2, self.pos[1])
		elif direction == PLAYER_LEFT_ONLY:
			self.pos = (self.pos[0] - move_speed, self.pos[1])
			direction = LEFT
		elif direction == PLAYER_RIGHT_ONLY:
			self.pos = (self.pos[0] + move_speed, self.pos[1])
			direction = RIGHT		
		super(PlayerObject, self).update(direction)

class textObject(pygame.sprite.Sprite):
	def __init__(self, screen, text, duration, type, font, font_color, font_size, position, back_color=None):
		pygame.sprite.Sprite.__init__(self)		
		self.screen = screen
		self.font = pygame.font.SysFont(font, font_size)
		self.font_image = self.font.render(text, False, BLACK).convert()				
		self.rect = self.font_image.get_rect()	
		size = (self.rect.right + 6, self.rect.bottom + 6)
		self.image = pygame.Surface(size, pygame.SRCALPHA).convert()
		self.image.fill(WHITE)
		self.image.blit(self.font_image, self.rect.topleft)
		self.image.blit(self.font_image, (self.rect.left+6, self.rect.top))
		self.image.blit(self.font_image, (self.rect.left, self.rect.top+6))
		self.image.blit(self.font_image, (self.rect.left+6, self.rect.top+6))
		self.font_image = self.font.render(text, False, GOLD).convert()
		self.image.blit(self.font_image, (self.rect.left+3, self.rect.top+3))				
		self.rect = self.rect.move(position)		
		self.rect.center = position		
		self.type = type

		self.image.set_colorkey(WHITE)
		
		self.font_color = font_color
		self.font_size = font_size
		self.back_color = back_color
		self.duration = duration
		
		
		
	def update(self):
		
		if self.type == POINTS_FADING:			
			self.image.set_alpha(self.image.get_alpha()-10)
			self.rect.top = self.rect.top - 5
			self.duration -= 1			
					
class ScenerySprite(pygame.sprite.Sprite):
	def __init__(self, screen, image, starting_position):
		pygame.sprite.Sprite.__init__(self)
		self.screen = screen
		self.image = image
		self.rect = self.image.get_rect(topleft=starting_position)

	def update(self, direction, speed):
		if direction == LEFT: self.rect = self.rect.move(speed, 0)
		elif direction == RIGHT: self.rect = self.rect.move(-speed, 0) 

class ForegroundSprite(ScenerySprite):
	def __init__(self, screen, image, starting_position):
		ScenerySprite.__init__(self, screen, image, starting_position)

	def update(self, direction, speed):
		super(ForegroundSprite, self).update(direction, speed)

class BackgroundSprite(ScenerySprite):
	def __init__(self, screen, image, starting_position):
		ScenerySprite.__init__(self, screen, image, starting_position)

	def update(self, direction, speed):
		super(BackgroundSprite, self).update(direction, speed)	

class BackgroundSurfacesManager(object):
	def __init__(self, screen, image_list, starting_positions, wrap=True, scroll_limits=None ):
		"""
		Managing object for the sprite.Group for all background surfaces.		
		"""
		self.screen = screen
		self.images = image_list 
		self.image_order = range(len(image_list)) 	#in case of wrap=True, will form a circular list, indicating which image will be drawn in what order
		self.positions = starting_positions 		#list of tuples [(x-coord, y-coord),...]		
		self.limits = scroll_limits 				#tuple of 2 x-values (left-limit, right-limit)
		self.wrap = wrap 							#if true: background is circular in nature - will wrap back around
		self.limit_test_position = None
		self.x_movement_measure = 0 				
		if self.limits != None: self.limit_test_position = SCREEN_WIDTH/2		
		self.background_sprite_group = pygame.sprite.Group()
		for index, image in enumerate(self.images): 
			self.background_sprite_group.add(BackgroundSprite(self.screen, image, self.positions[index]))
			
	def update(self, direction, speed):
		"""updates all background sprites uniformly, unless doing so would violate a limit in self.limits""" 
		if direction == LEFT:			
			if (self.limits != None): 
				if (self.limits[1] <= (self.limit_test_position + speed)): return AT_LIMIT_RIGHT, self.x_movement_measure								

			if PLAYER.pos[0] == SCREEN_WIDTH/2:	
				self.background_sprite_group.update(direction, speed)			
				self.x_movement_measure += speed						
				if self.limit_test_position != None: self.limit_test_position += speed
			
				if self.wrap: #if wrapping is enabled
					if self.x_movement_measure > SCREEN_WIDTH:
						self.x_movement_measure -= SCREEN_WIDTH
						#get sprite with largest x-pos
						sprite_x_pos = None
						target_sprite = None
						for sprite in self.background_sprite_group:
							if sprite_x_pos == None: 
								sprite_x_pos = sprite.rect.x
								target_sprite = sprite
							elif sprite_x_pos < sprite.rect.x: 
								sprite_x_pos = sprite.rect.x
								target_sprite = sprite
						#farthest right sprite found, cycle
						target_sprite.update(RIGHT, SCREEN_WIDTH*(len(self.images)))			
			
		elif direction == RIGHT: 
			if (self.limits != None): 
				if (self.limits[0] >= (self.limit_test_position - speed)): return AT_LIMIT_LEFT, self.x_movement_measure

			if PLAYER.pos[0] == SCREEN_WIDTH/2:
				self.background_sprite_group.update(direction, speed)			
				self.x_movement_measure -= speed			
				
				if self.limit_test_position != None: self.limit_test_position -= speed
				
				if self.wrap: #if wrapping is enabled			
					if self.x_movement_measure < -SCREEN_WIDTH:
						self.x_movement_measure += SCREEN_WIDTH
						#get sprite with largest x-pos
						sprite_x_pos = None
						target_sprite = None
						for sprite in self.background_sprite_group:
							if sprite_x_pos == None: 
								sprite_x_pos = sprite.rect.x
								target_sprite = sprite
							elif sprite_x_pos > sprite.rect.x: 
								sprite_x_pos = sprite.rect.x
								target_sprite = sprite
						#farthest left sprite found, cycle
						target_sprite.update(LEFT, SCREEN_WIDTH*(len(self.images)))
		
		return None, self.x_movement_measure
	
	def draw(self, screen):
		self.background_sprite_group.draw(screen)			
	
def loadImages(path, f_names):
	"""returns a list of pygame.Surface objects, loaded from images at 'path' having a name in the 'f_names' list"""
	ret_surfaces = []
	for f_name in f_names:		
		ret_surfaces.append( pygame.image.load(os.path.join(path, f_name)).convert_alpha() )
	return ret_surfaces
	
def event_LeftKeyPress():
	global X_LIMIT_TEST_POS
	background_left_limit_hit, X_LIMIT_TEST_POS = BACKGROUND_SURFACE_MANAGER.update(LEFT, BACKGROUND_SPEED)
	
	if not background_left_limit_hit and PLAYER.pos[0] == SCREEN_WIDTH/2:
		
		PLAYER_SPRITE_GROUP.update(LEFT)	 
		FOREGROUND_SPRITE_GROUP.update(LEFT, FOREGROUND_SPEED)
		AI_CHARACTER_SPRITE_GROUP.update(PLAYER_LEFT_ONLY)
	else:
		PLAYER_SPRITE_GROUP.update(PLAYER_LEFT_ONLY)	
	
def event_RightKeyPress():
	global X_LIMIT_TEST_POS
	background_right_limit_hit, X_LIMIT_TEST_POS = BACKGROUND_SURFACE_MANAGER.update(RIGHT, BACKGROUND_SPEED)
		
	if not background_right_limit_hit and PLAYER.pos[0] == SCREEN_WIDTH/2:  
		PLAYER_SPRITE_GROUP.update(RIGHT)	
		FOREGROUND_SPRITE_GROUP.update(RIGHT, FOREGROUND_SPEED)			
		AI_CHARACTER_SPRITE_GROUP.update(PLAYER_RIGHT_ONLY)
	else:
		PLAYER_SPRITE_GROUP.update(PLAYER_RIGHT_ONLY)	
	
def eventHandler(event_list):
	"""
	eventHandler takes a pygame.event.get() list and handles every event in the list	 
	"""
	global LEFT_KEY_DOWN
	global RIGHT_KEY_DOWN
	global CURR_FONT
	for event in event_list:		
		#KEYPRESS EVENTS
		if event.type == pygame.QUIT: sys.exit(0)			
		if hasattr(event, 'key'):				
			down = event.type == KEYDOWN		
			if event.key == K_ESCAPE and not down: sys.exit(0)
			elif event.key == K_LEFT:
				if down: LEFT_KEY_DOWN = True						
				else: LEFT_KEY_DOWN = False
			elif event.key == K_RIGHT:
				if down: RIGHT_KEY_DOWN = True
				else: RIGHT_KEY_DOWN = False
			elif event.key == K_SPACE and down:					
				PLAYER_SPRITE_GROUP.update(UP)			
		
		if event.type == MOUSEMOTION: 
			m_x_pos, m_y_pos = event.pos
		elif event.type == MOUSEBUTTONUP:
			m_x_pos, m_y_pos = event.pos
			#TESTING TEXT - NOT PERMANENT, TO BE REMOVED						
			create_And_AddTextSpriteToGroup("123456789", 20, POINTS_FADING, "impact", GOLD, 40, (m_x_pos, m_y_pos), None, TEXT_SPRITE_GROUP_POINTS) 			
			
			#/TESTING
	
	if LEFT_KEY_DOWN and PLAYER.isCollidingLeft == False: 
		event_LeftKeyPress()
	if RIGHT_KEY_DOWN and PLAYER.isCollidingRight == False: 
		event_RightKeyPress()
				
def updateAllGroups(sprite_groups_list):
	"""All sprite groups in the list are given their basic per-frame update"""
	for group in sprite_groups_list:
		group.update(None)
		
	spriteUpdateAndRemove_Text(TEXT_SPRITE_GROUP_POINTS)

def drawAllSprites(draw_list, surface):
	"""All objects in the draw_list have their draw method called"""
	for item in draw_list:
		item.draw(surface)
		
def debug_drawRects(rect_list):
	for rect in rect_list:
		pygame.draw_rect(SCREEN, BLUE, rect)
		
def AI_behavior_handler(AI_Character_list):
	global ai_rand_act
	global char_action	
	for index, ai_character in enumerate(AI_Character_list):		
		isJumping = randint(0, 125)		
		if ai_rand_act[index] == 0:
			char_action[index] = randint(0, 2)			
			if char_action[index] == 2: ai_rand_act[index] = 15
			else: ai_rand_act[index] = randint(5, 10)
		else: ai_rand_act[index] -= 1
		if char_action[index] == 2:
			ai_character.update(None)
			if isJumping == randint(0, 125): ai_character.update(UP)
		else:			
			ai_character.update(char_action[index])
			if isJumping == randint(0, 125): ai_character.update(UP)	
			
def create_And_AddTextSpriteToGroup(text, duration, type, font, font_color, font_size, position, back_color, sprite_group):
	text_sprite = textObject(SCREEN, text, duration, type, font, font_color, font_size, position, back_color)	
	sprite_group.add(text_sprite)	

def spriteUpdateAndRemove_Text(text_sprite_group):
	for sprite in text_sprite_group.sprites():
		if sprite.duration == 0:
			text_sprite_group.remove(sprite)		
	text_sprite_group.update()
				
if __name__ == "__main__": #Globals
	
	##directions for movement
	LEFT = 0
	RIGHT = 1
	DOWN = 2
	UP = 3
	#next two are to avoid animation of non-player objects 
	#when they are only moving relative to player object movement
	PLAYER_LEFT_ONLY = 4 
	PLAYER_RIGHT_ONLY = 5
	##/directions for movement

	##colors
	GREY = (128, 128, 128)
	RED = (255, 0, 0)
	GREEN = (0, 255, 0)
	BLUE = (0, 0, 255)
	LIGHT_BLUE = (125, 125, 255)
	BLACK = (0, 0, 0)
	GOLD = (255, 215, 0)
	WHITE = (255, 255, 255)
	##/colors
	
	##
	#NOTE: THESE FONTS DO NOT WORK:
	#anything ending in 'bold' (FONT_LIST[CURR_FONT][-4:] == "bold")	
	#anything ending in 'italic' (FONT_LIST[CURR_FONT][-6:] == "italic")
	#cambria
	#yugothic
	FONT_LIST = pygame.font.get_fonts()
	CURR_FONT = 0
	FONT_LIMIT = len(FONT_LIST)
	##
	
	##TextObj types
	POINTS_FADING = 0
	##

	##speeds
	BACKGROUND_SPEED = 10
	FOREGROUND_SPEED = 8
	##/speeds

	##collision rect widths - these are for character/player object extended collision rectangles
	LEFT_RECT_WIDTH = 5
	RIGHT_RECT_WIDTH = 5
	##

	##universal scenery heights
	#remember that (0, 0) in pygame is the top-left corner; y > 0 is below this point
	FLOOR_HEIGHT = 400
	##

	##image array layout keys	
	#LEFT
	LEFT_0 	= 0
	LEFT_1 	= 1
	LEFT_2 	= 2
	LEFT_3 	= 3
	#RIGHT
	RIGHT_0 = 4
	RIGHT_1 = 5
	RIGHT_2 = 6
	RIGHT_3 = 7
	#IDLE
	IDLE_0 	= 8
	IDLE_1 	= 9
	IDLE_2 	= 10
	IDLE_3 	= 11
	#UP
	UP_0 	= 12
	UP_1 	= 13
	UP_2 	= 14
	UP_3 	= 15
	#DOWN
	DOWN_0 	= 16
	DOWN_1 	= 17
	DOWN_2 	= 18
	DOWN_3 	= 19
	##
	
	##AI states
	DEFAULT_AI_TYPE = 0 #debugging ai type
	##
	
	##SCREEN surface attributes/objects (and also the Clock)
	SCREEN_WIDTH = 800
	SCREEN_HEIGHT = 600	
	SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	SCREEN_RECT = SCREEN.get_rect()
	CLOCK = pygame.time.Clock()		
	##
	
	##Bools for determining whether a key is held down
	LEFT_KEY_DOWN = False
	RIGHT_KEY_DOWN = False
	##
	
	##art assets and asset arrays
	#These should probably all be moved to a separate text file and processed programmatically 
	#to avoid unncessary bulk in the code as asset amounts rise
	
	ASSETS_PATH = r'art_assets/'
	
	PLAYER_ASSET_FNAMES = [
	'death_sprite_left_1.png',
	'death_sprite_left_2.png',
	'death_sprite_left_3.png',
	'death_sprite_left_4.png',
	'death_sprite_right_1.png',
	'death_sprite_right_2.png',
	'death_sprite_right_3.png',
	'death_sprite_right_4.png'
	]
	
	AI_CHARACTER_ASSET_FNAMES = [
	'red_death_sprite_left_1.png',
	'red_death_sprite_left_2.png',
	'red_death_sprite_left_3.png',
	'red_death_sprite_left_4.png',
	'red_death_sprite_right_1.png',
	'red_death_sprite_right_2.png',
	'red_death_sprite_right_3.png',
	'red_death_sprite_right_4.png'
	]

	FOREGROUND_ASSET_FNAMES = [
	'vending.png', 
	'vending.png', 
	'vending.png', 
	'vending.png',
	'vending.png', 
	'vending.png', 
	'vending.png', 
	'vending.png',
	'vending.png', 
	'vending.png', 
	'vending.png', 
	'vending.png',
	'vending.png', 
	'vending.png', 
	'vending.png', 
	'vending.png']
	
	FOREGROUND_ASSET_POSITIONS = [
	(650, 400),
	(100, 200),
	(500, 300),
	(0, 600),
	(600, 0),
	(400, 400),
	(800, 400),
	(800, 600),
	(300, 500),
	(0, 200),
	(-500, 300),
	(-1000, 600),
	(1600, 0),
	(1400, 400),
	(-800, 400),
	(1800, 600)]
	
	BACKGROUND_ASSET_FNAMES = [
	'b1.jpg',
	'b2.jpg',
	'b3.jpg',
	'b4.jpg',
	'b5.jpg']	
	##
	
	## Screen side limits
	#note that this limit is when the background screen will stop scrolling
	#the player character will still be at the screen mid-point, and AI
	#characters move independent of background coords
	X_SCROLL_LIMIT_LEFT = -SCREEN_WIDTH/2
	X_SCROLL_LIMIT_RIGHT = SCREEN_WIDTH + SCREEN_WIDTH/2
	X_SCROLL_LIMITS = (X_SCROLL_LIMIT_LEFT, X_SCROLL_LIMIT_RIGHT)
	X_PLAYER_MOVE_LIMIT = (0, SCREEN_WIDTH)
	AT_LIMIT_LEFT = 1 #left-side of background limit has been reached
	AT_LIMIT_RIGHT = 2 #right-side of background limit has been reached
	X_LIMIT_TEST_POS = SCREEN_WIDTH/2
	##
		
	##loading images for objects	
	foreground_surfaces 			= loadImages( ASSETS_PATH, FOREGROUND_ASSET_FNAMES )
	background_surfaces 			= loadImages( ASSETS_PATH, BACKGROUND_ASSET_FNAMES )
	player_object_surfaces 			= loadImages( ASSETS_PATH, PLAYER_ASSET_FNAMES )
	AI_character_object_surfaces 	= loadImages( ASSETS_PATH, AI_CHARACTER_ASSET_FNAMES )
	##
	
	##instatiate sprite and sprite group objects
	TEXT_SPRITE_GROUP_POINTS = pygame.sprite.Group()
	BACKGROUND_SURFACE_MANAGER = BackgroundSurfacesManager(SCREEN, background_surfaces, [(-1600, 0), (-800, 0), (0, 0), (800, 0), (1600, 0)], True, (-2000, 2800) )		
	FOREGROUND_SPRITE_GROUP = pygame.sprite.Group()
	for index, forg_surf in enumerate(foreground_surfaces):
		FOREGROUND_SPRITE_GROUP.add(ForegroundSprite(SCREEN, forg_surf, FOREGROUND_ASSET_POSITIONS[index]))
	
	PLAYER = PlayerObject(SCREEN, player_object_surfaces, (SCREEN_WIDTH/2, FLOOR_HEIGHT))
	PLAYER_SPRITE_GROUP = pygame.sprite.Group()
	PLAYER_SPRITE_GROUP.add(PLAYER)
	
	AI_CHARACTER_SPRITE_GROUP = pygame.sprite.Group()
	for i in range(4): AI_CHARACTER_SPRITE_GROUP.add( AICharacterObject(SCREEN, AI_character_object_surfaces, (SCREEN_WIDTH/3 + randint(-50, 50), FLOOR_HEIGHT))) 		
	EVERY_CHARACTER_SPRITE_GROUP = AI_CHARACTER_SPRITE_GROUP.copy()
	EVERY_CHARACTER_SPRITE_GROUP.add(PLAYER)
	##	
	
	##ai character rand action vars, temporary
	ai_rand_act = [0] * len(AI_CHARACTER_SPRITE_GROUP)	
	char_action = [2] * len(AI_CHARACTER_SPRITE_GROUP)
	
if __name__ == "__main__": #game loop
	pygame.init()
	while 1:
		time_elapsed = CLOCK.tick(30)
		
		event_list = pygame.event.get()
		eventHandler(event_list)			
		
		AI_behavior_handler(AI_CHARACTER_SPRITE_GROUP)
		
		updateAllGroups([AI_CHARACTER_SPRITE_GROUP, PLAYER_SPRITE_GROUP])		
		
		BACKGROUND_SURFACE_MANAGER.draw(SCREEN) #should be added to drawAllSprites once a sprite floor is added
		#temp floor
		pygame.draw.rect(SCREEN, GREY, ((0, FLOOR_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT-FLOOR_HEIGHT)) )				
		#/temp floor
		drawAllSprites([AI_CHARACTER_SPRITE_GROUP, PLAYER_SPRITE_GROUP, FOREGROUND_SPRITE_GROUP, TEXT_SPRITE_GROUP_POINTS], SCREEN)				
		
		#for sprite in TEXT_SPRITE_GROUP_POINTS.sprites():
		#	pygame.draw.rect(SCREEN, BLUE, sprite.rect)
		
		#display new frame
		pygame.display.flip()