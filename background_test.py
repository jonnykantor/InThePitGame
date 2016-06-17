import pygame, math, sys
import os
from pygame.locals import *
from random import randint
from sys import argv

class CharacterObject(pygame.sprite.Sprite):
	def __init__(self, screen, images, starting_position):
		pygame.sprite.Sprite.__init__(self)
		
		self.screen = screen
		self.images = images
		self.image = images[IDLE_0]		
		self.pos = starting_position		
		
		self.rect = self.image.get_rect()		
		self.rect.center = self.pos		
		
		#image lists by direction
		self.left_images 	= self.images[:IDLE_3 	+ 1	]		
		self.right_images 	= self.images[IDLE_3 	+ 1	:LEFT_3 	+ 1	]
		'''
		self.idle_images 	= self.images[				:IDLE_3 	+ 1	]		
		self.left_images 	= self.images[IDLE_3 	+ 1	:LEFT_3 	+ 1	]		
		self.right_images 	= self.images[LEFT_3 	+ 1	:RIGHT_3 	+ 1	]
		self.up_images 		= self.images[RIGHT_3 	+ 1	:UP_3 		+ 1	]
		self.down_images 	= self.images[UP_3 		+ 1	:DOWN_3 	+ 1	]
		'''
		
		#collision rectangles and stats
		self.bottom_collision_rect = pygame.Rect( self.rect.bottomleft, ( self.rect.width, FLOOR_HEIGHT - self.rect.bottom ) )		
		self.right_side_collision_rect = pygame.Rect( self.rect.topright, (RIGHT_RECT_WIDTH, self.rect.height-2) )
		self.left_side_collision_rect = pygame.Rect( (self.rect.left - LEFT_RECT_WIDTH, self.rect.top), self.rect.bottomleft )
		
		self.isCollidingRight = False
		self.isCollidingLeft = False
		self.isCollidingBottom = False
		
		#individual indices for individual image lists
		self.idle_ind 	= 0
		self.left_ind 	= 0
		self.right_ind 	= 0
		self.up_ind 	= 0
		self.down_ind 	= 0
		
		#jump stats
		self.jumpCounter 	= 0
		self.isAirborne 	= False
		self.fall_speed 	= 0
		self.jump_speed 	= 10
		
	def update(self, direction):
		
		collide_left = self.left_side_collision_rect.collidelist([x.rect for x in EVERY_CHARACTER_SPRITE_GROUP])
		collide_right = self.right_side_collision_rect.collidelist([x.rect for x in EVERY_CHARACTER_SPRITE_GROUP])
		collide_bottom = self.bottom_collision_rect.collidelist([x.rect for x in FOREGROUND_SPRITE_GROUP])
		
		if collide_left == -1: self.isCollidingLeft = False
		else: self.isCollidingLeft = True
		if collide_right == -1: self.isCollidingRight = False
		else: self.isCollidingRight = True
		if collide_bottom == -1: self.isCollidingBottom = False
		else: self.isCollidingBottom = True			
		
		if direction == UP and not self.isAirborne:	
			self.jumpCounter = 5			
		elif direction == DOWN:	
			#not using down yet
			pass		
		
		if direction == LEFT:
			self.right_ind = 0			
			if collide_left == -1:
				self.isCollidingLeft = False
				#update image for animation
				if self.left_ind == 15: self.left_ind = 0 
				else: self.left_ind += 1
				self.image = self.left_images[self.left_ind/5]					
			else: #colliding left				
				self.isCollidingLeft = True
		elif direction == RIGHT:
			self.left_ind = 0
			if collide_right == -1:
				self.isCollidingRight = False
				#update image for animation
				if self.right_ind == 15: self.right_ind = 0
				else: self.right_ind += 1
				self.image = self.right_images[self.right_ind/5]		
			else: #colliding right
				self.isCollidingRight = True
			
		elif self.jumpCounter > 0:			
			self.isAirborne = True
			self.jumpCounter -= 1
			self.pos = (self.pos[0], self.pos[1]-self.jump_speed*self.jumpCounter)			
			
		elif self.isAirborne or self.pos[1] < FLOOR_HEIGHT:
							
			#extending collision rectangle for object from self.rect.bottom to y = 400			
			if collide_bottom != -1:				
				if ( abs(self.rect.bottom - [x.rect for x in FOREGROUND_SPRITE_GROUP][collide_bottom].top) ) <= ( self.fall_speed + 2 ):
					self.isCollidingBottom = True
					self.isAirborne = False
					self.fall_speed = 0
					self.pos = (self.pos[0], [x.rect for x in FOREGROUND_SPRITE_GROUP][collide_bottom].top - self.rect.height/2 - 1)							
			
			if self.pos[1] < FLOOR_HEIGHT:
				self.fall_speed += 2
				self.pos = (self.pos[0], self.pos[1]+self.fall_speed)
			
		if self.pos[1] > FLOOR_HEIGHT: 
			self.isAirborne = False
			self.fall_speed = 0
			self.pos = (self.pos[0], FLOOR_HEIGHT)
				
		self.rect = self.image.get_rect()
		self.rect.center = self.pos		
		
		self.bottom_collision_rect = pygame.Rect( self.rect.bottomleft, ( self.rect.width, self.fall_speed ) ) 
		self.right_side_collision_rect = pygame.Rect( self.rect.topright, (RIGHT_RECT_WIDTH, self.rect.height-2) )
		self.left_side_collision_rect = pygame.Rect( (self.rect.left - LEFT_RECT_WIDTH, self.rect.top), (LEFT_RECT_WIDTH, self.rect.height-2) )
	
class AICharacterObject(CharacterObject):
	def __init__(self, screen, images, starting_position):
		CharacterObject.__init__(self, screen, images, starting_position)
	
	def update(self, direction):		
		if direction == LEFT and self.isCollidingLeft == False: self.pos = (self.pos[0] - 10, self.pos[1])
		elif direction == RIGHT and self.isCollidingRight == False: self.pos = (self.pos[0] + 10, self.pos[1])
		elif direction == PLAYER_LEFT_ONLY: 
			self.pos = (self.pos[0] + 10, self.pos[1])
			direction = None
		elif direction == PLAYER_RIGHT_ONLY: 
			self.pos = (self.pos[0] - 10, self.pos[1])
			direction = None
		super(AICharacterObject, self).update(direction)	
	
class PlayerObject(CharacterObject):
	def __init__(self, screen, images, starting_position):
		CharacterObject.__init__(self, screen, images, starting_position)
	
	def update(self, direction):
		super(PlayerObject, self).update(direction)

class ForegroundSurfaceSprite(pygame.sprite.Sprite):
	def __init__(self, screen, image, starting_position):
		pygame.sprite.Sprite.__init__(self)
		self.screen = screen
		self.image = image
		self.rect = self.image.get_rect(topleft=starting_position)
		
	def update(self, direction, speed):
		if direction == LEFT: self.rect = self.rect.move(speed, 0)
		elif direction == RIGHT: self.rect = self.rect.move(-speed, 0)

class ForegroundSurfaces():
	def __init__(self, screen, images, starting_positions):
		self.screen = screen		
		self.scenery_surfaces = images
		self.scenery_rects = []		

		for index, surface in enumerate(self.scenery_surfaces):
			self.scenery_rects.append( surface.get_rect().move(starting_positions[index]) )		
			
			
	def updatePos(self, direction, speed):
	
		if direction == LEFT:			
			self.scenery_rects = [x.move(speed, 0) for x in self.scenery_rects]			
		elif direction == RIGHT:
			self.scenery_rects = [x.move(-speed, 0) for x in self.scenery_rects]			
		
	def drawForegroundSurfaces(self):		
		for i in range(len(self.scenery_surfaces)):
			if self.scenery_rects[i].left < (SCREEN_WIDTH + SCREEN_WIDTH/2) and self.scenery_rects[i].right > ((-1) * SCREEN_WIDTH/2 ):
				self.screen.blit(self.scenery_surfaces[i], self.scenery_rects[i])

class BackgroundSurfaces(): #needs to be updated to handle a dynamic number of background images
	def __init__(self, screen):
		self.screen = SCREEN
		self.panel_order = [0, 1, 2, 3, 4]
		self.panel_x_pos = [ (-1)*SCREEN_WIDTH*2, (-1)*SCREEN_WIDTH, 0, SCREEN_WIDTH, SCREEN_WIDTH*2]
		self.surfaces = []
		path = ASSETS_PATH
		for i in range(5):			
			fn = 'b' + str(i+1) + '.jpg'
			full_path = os.path.join(path, fn)
			surf = pygame.image.load(full_path).convert()
			self.surfaces.append(surf)
	
	def updatePos(self, direction, speed):
		"""
		direction type is int using RIGHT or LEFT
		speed type is int
		determines change in position per call
		"""
		if direction == LEFT: 
			self.panel_x_pos = [x+speed for x in self.panel_x_pos]
			if self.panel_x_pos[0] >= (-1)*SCREEN_WIDTH: 
				self.panel_order = self.panel_order[1:] + self.panel_order[:1]
				self.panel_x_pos = [x-SCREEN_WIDTH for x in self.panel_x_pos]
		elif direction == RIGHT: 
			self.panel_x_pos = [x-speed for x in self.panel_x_pos]
			if self.panel_x_pos[0] < (-1)*SCREEN_WIDTH*3:
				self.panel_order = self.panel_order[-1:] + self.panel_order[:-1]
				self.panel_x_pos = [x+SCREEN_WIDTH for x in self.panel_x_pos]
				
	def drawBackgrounds(self):
		for index, surface in enumerate(self.surfaces):
			if abs( self.panel_x_pos[self.panel_order[index]] ) < SCREEN_WIDTH + 100:
				self.screen.blit(surface, (self.panel_x_pos[self.panel_order[index]], 0))			
	
def loadImages(path, f_names):
	"""returns a list of pygame.Surface objects, loaded from images at 'path' having a name in the 'f_names' list"""
	ret_surfaces = []
	for f_name in f_names:		
		ret_surfaces.append( pygame.image.load(os.path.join(path, f_name)).convert_alpha() )
	return ret_surfaces

if __name__ == "__main__": #Globals
	
	##directions for movement
	LEFT = 0
	RIGHT = 1
	DOWN = 2
	UP = 3
	#next two are to avoid animation of non-player objects 
	#when they are only moving due to player movement
	PLAYER_LEFT_ONLY = 4 
	PLAYER_RIGHT_ONLY = 5
	##/directions for movement

	##colors
	GREY = (128, 128, 128)
	RED = (255, 0, 0)
	GREEN = (0, 255, 0)
	BLUE = (0, 0, 255)
	LIGHT_BLUE = (125, 125, 255)
	##/colors

	##speeds
	BACKGROUND_SPEED = 10
	FOREGROUND_SPEED = 8
	##/speeds

	##collision rect widths
	LEFT_RECT_WIDTH = 5
	RIGHT_RECT_WIDTH = 5
	##

	##universal scenery heights
	#remember that (0, 0) in pygame is the top-left corner; y > 0 is below this point
	FLOOR_HEIGHT = 400
	##

	##image array layout keys
	#IDLE
	IDLE_0 	= 0
	IDLE_1 	= 1
	IDLE_2 	= 2
	IDLE_3 	= 3
	#LEFT
	LEFT_0 	= 4
	LEFT_1 	= 5
	LEFT_2 	= 6
	LEFT_3 	= 7
	#RIGHT
	RIGHT_0 = 8
	RIGHT_1 = 9
	RIGHT_2 = 10
	RIGHT_3 = 11
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
	
	##SCREEN surface attributes
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
	##
	
	
	##loading images for objects	
	foreground_surfaces = loadImages( ASSETS_PATH, FOREGROUND_ASSET_FNAMES )
	player_object_surfaces = loadImages( ASSETS_PATH, PLAYER_ASSET_FNAMES )
	AI_character_object_surfaces = loadImages( ASSETS_PATH, AI_CHARACTER_ASSET_FNAMES )
	##
	
	##instatiate objects
	BACKGROUND = BackgroundSurfaces(SCREEN)	#old, should be switched to sprites
	FOREGROUND = ForegroundSurfaces(SCREEN, foreground_surfaces, FOREGROUND_ASSET_POSITIONS) #old, should be switched to sprites
	
	FOREGROUND_SPRITE_GROUP = pygame.sprite.Group()
	for index, forg_surf in enumerate(foreground_surfaces):
		FOREGROUND_SPRITE_GROUP.add(ForegroundSurfaceSprite(SCREEN, forg_surf, FOREGROUND_ASSET_POSITIONS[index]))
	
	PLAYER = PlayerObject(SCREEN, player_object_surfaces, (SCREEN_WIDTH/2, FLOOR_HEIGHT))
	PLAYER_SPRITE_GROUP = pygame.sprite.Group()
	PLAYER_SPRITE_GROUP.add(PLAYER)
	
	AI_CHARACTER = AICharacterObject(SCREEN, AI_character_object_surfaces, (SCREEN_WIDTH/3, FLOOR_HEIGHT))
	AI_CHARACTER_2 = AICharacterObject(SCREEN, AI_character_object_surfaces, (SCREEN_WIDTH/3 + randint(-50, 50), FLOOR_HEIGHT))
	AI_CHARACTER_3 = AICharacterObject(SCREEN, AI_character_object_surfaces, (SCREEN_WIDTH/3 + randint(-50, 50), FLOOR_HEIGHT))
	AI_CHARACTER_4 = AICharacterObject(SCREEN, AI_character_object_surfaces, (SCREEN_WIDTH/3 + randint(-50, 50), FLOOR_HEIGHT))
	
	AI_CHARACTER_SPRITE_GROUP = pygame.sprite.Group()
	
	AI_CHARACTER_SPRITE_GROUP.add(AI_CHARACTER)	
	AI_CHARACTER_SPRITE_GROUP.add(AI_CHARACTER_2)
	AI_CHARACTER_SPRITE_GROUP.add(AI_CHARACTER_3)
	AI_CHARACTER_SPRITE_GROUP.add(AI_CHARACTER_4)
		
	EVERY_CHARACTER_SPRITE_GROUP = pygame.sprite.Group()
	EVERY_CHARACTER_SPRITE_GROUP.add(PLAYER)
	EVERY_CHARACTER_SPRITE_GROUP.add(AI_CHARACTER)
	EVERY_CHARACTER_SPRITE_GROUP.add(AI_CHARACTER_2)
	EVERY_CHARACTER_SPRITE_GROUP.add(AI_CHARACTER_3)
	EVERY_CHARACTER_SPRITE_GROUP.add(AI_CHARACTER_4)
	##	
	
	##ai character rand action vars, temporary
	ai_rand_act = 0
	char_action = 2	
	
if __name__ == "__main__": #main loop	
	while 1:
		time_elapsed = CLOCK.tick(30)
				
		#SCREEN.fill((0,0,0)) #not necessary currently as entire background is drawn to with no transparency
		
		event_list = pygame.event.get()
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
				for rect in FOREGROUND.scenery_rects:					
					if rect.collidepoint(m_x_pos, m_y_pos):
						print "yep"						
		
		if LEFT_KEY_DOWN and PLAYER.isCollidingLeft == False: 
			PLAYER_SPRITE_GROUP.update(LEFT)
			BACKGROUND.updatePos(LEFT, BACKGROUND_SPEED)
			#FOREGROUND.updatePos(LEFT, FOREGROUND_SPEED)
			FOREGROUND_SPRITE_GROUP.update(LEFT, FOREGROUND_SPEED)
			AI_CHARACTER_SPRITE_GROUP.update(PLAYER_LEFT_ONLY)
		if RIGHT_KEY_DOWN and PLAYER.isCollidingRight == False: 
			PLAYER_SPRITE_GROUP.update(RIGHT)
			BACKGROUND.updatePos(RIGHT, BACKGROUND_SPEED)
			#FOREGROUND.updatePos(RIGHT, FOREGROUND_SPEED)
			FOREGROUND_SPRITE_GROUP.update(RIGHT, FOREGROUND_SPEED)			
			AI_CHARACTER_SPRITE_GROUP.update(PLAYER_RIGHT_ONLY)
			
		#character random action		
		jump_action = randint(0, 125)
		if ai_rand_act == 0: 
			char_action = randint(0, 2)
			if char_action == 2: ai_rand_act = 15
			else: ai_rand_act = randint(5, 10)
		else: ai_rand_act -= 1
		if char_action == 2: 
			AI_CHARACTER_SPRITE_GROUP.update(None)
			if jump_action == 5: AI_CHARACTER_SPRITE_GROUP.update(UP)
		else: 
			AI_CHARACTER_SPRITE_GROUP.update(char_action)
			if jump_action == 5: AI_CHARACTER_SPRITE_GROUP.update(UP)		
		AI_CHARACTER_SPRITE_GROUP.update(None)
		#/character random action		
		
		PLAYER_SPRITE_GROUP.update(None)		
		BACKGROUND.drawBackgrounds()		
		pygame.draw.rect(SCREEN, GREY, ((0, FLOOR_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT-FLOOR_HEIGHT)) )		
		
		AI_CHARACTER_SPRITE_GROUP.draw(SCREEN)		
		PLAYER_SPRITE_GROUP.draw(SCREEN)		
		
		#FOREGROUND.drawForegroundSurfaces()
		FOREGROUND_SPRITE_GROUP.draw(SCREEN)
		
		#display new frame
		pygame.display.flip()