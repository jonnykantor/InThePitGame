import pygame
from Globals import *

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
			
	def update(self, direction, speed, player_object):
		"""updates all background sprites uniformly, unless doing so would violate a limit in self.limits""" 
		if direction == LEFT:			
			if (self.limits != None): 
				if (self.limits[1] <= (self.limit_test_position + speed)): return AT_LIMIT_RIGHT, self.x_movement_measure								

			if player_object.pos[0] == SCREEN_WIDTH/2:	
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

			if player_object.pos[0] == SCREEN_WIDTH/2:
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