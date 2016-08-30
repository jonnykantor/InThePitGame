import pygame, math, sys, os
from pygame.locals import *
from random import randint
from Globals import *

class CharacterObject(pygame.sprite.Sprite):
	def __init__(self, screen, images, starting_position, x_limits, dimsAndLims_obj):
		"""Super class for player and non-player characters in the game
		CharacterObject class is mainly to handle animation and collision 
		detectionrather than repositioning of pc/npc objects - except for 
		vertical movement (jumping)"""
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
		self.character_floor = starting_position[1] #used to stop fall motion, essentially locates the 'floor'
		self.facing_direction = 1 #1 is right		
		
		self.rect = self.image.get_rect()		
		self.rect.center = self.pos		
		
		#image lists by direction
		self.left_images 	= self.images[:LEFT_3	+ 1	]		
		self.right_images 	= self.images[LEFT_3 	+ 1	:RIGHT_3 	+ 1	]
		#currently only using left/right animations
		'''
		self.idle_images 	= self.images[right_3	+ 1 :IDLE_3 	+ 1	]				
		self.up_images 		= self.images[IDLE_3 	+ 1	:up_3 		+ 1	]
		self.down_images 	= self.images[up_3 		+ 1	:DOWN_3 	+ 1	]
		'''
		
		#collision rectangles and stats
		self.bottom_collision_rect = pygame.Rect( self.rect.bottomleft, ( self.rect.width, self.character_floor - self.rect.bottom ) )		
		self.right_side_collision_rect = pygame.Rect( self.rect.topright, (dimsAndLims_obj.right_rect_width, self.rect.height-2) )
		self.left_side_collision_rect = pygame.Rect( (self.rect.left - dimsAndLims_obj.left_rect_width, self.rect.top), self.rect.bottomleft )
		
		self.isCollidingRight = False
		self.isCollidingLeft = False
		self.isCollidingBottom = False

		self.collisionObjectLeft = -1
		self.collisionObjectRight = -1
		
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
		
	def update(self, direction, left_side_collision_list, right_side_collision_list, bottom_collision_list, direction_obj, dimsAndLims_obj):

		left = direction_obj.left
		right = direction_obj.right
		up = direction_obj.up
		player_left_only = direction_obj.player_left_only
		player_right_only = direction_obj.player_right_only
		nudge_left = direction_obj.nudge_left
		nudge_right = direction_obj.nudge_right

		collide_left = self.left_side_collision_rect.collidelist(left_side_collision_list) 
		if collide_left > -1: self.collisionObjectLeft = left_side_collision_list[collide_left]
		collide_right = self.right_side_collision_rect.collidelist(right_side_collision_list) 
		if collide_right > -1: self.collisionObjectRight = right_side_collision_list[collide_right]
		collide_bottom = self.bottom_collision_rect.collidelist(bottom_collision_list) 
		
		#test for collisions
		if collide_left == -1: self.isCollidingLeft = False
		else: self.isCollidingLeft = True
		if collide_right == -1: self.isCollidingRight = False
		else: self.isCollidingRight = True
		if collide_bottom == -1: self.isCollidingBottom = False
		else: self.isCollidingBottom = True			
		#jump indicated, not already in the air
		if direction == up and not self.isAirborne:	
			self.jumpCounter = 5					
		
		if direction == left:
			self.facing_direction = left
			if self.left_ind == 15: self.left_ind = 0 
			else: self.left_ind += 1
			self.image = self.left_images[self.left_ind/5]					
		elif direction == right:
			self.facing_direction = right
			if self.right_ind == 15: self.right_ind = 0
			else: self.right_ind += 1
			self.image = self.right_images[self.right_ind/5]		
		#check jumpCounter and increment y-pos if necessary
		elif self.jumpCounter > 0:			
			self.isAirborne = True
			self.jumpCounter -= 1
			self.pos = (self.pos[0], self.pos[1]-self.jump_speed*self.jumpCounter)						
		#airborne from jump, or simply above the floor height, and not colliding with anything below
		elif self.isAirborne or self.pos[1] < self.character_floor:
							
			#extending collision rectangle from bottom of self.rect up to current fall_speed
			if collide_bottom != -1:				
				if ( abs(self.rect.bottom - bottom_collision_list[collide_bottom].top) ) <= ( self.fall_speed + 2 ):
					self.isCollidingBottom = True
					self.isAirborne = False
					self.fall_speed = 0
					self.pos = (self.pos[0], bottom_collision_list[collide_bottom].top - self.rect.height/2 - 1)							
			
			if self.pos[1] < self.character_floor:
				self.fall_speed += 2
				self.pos = (self.pos[0], self.pos[1]+self.fall_speed)

		#somehow below the floor, move back to floor	
		if self.pos[1] > self.character_floor: 
			self.isAirborne = False
			self.fall_speed = 0
			self.pos = (self.pos[0], self.character_floor)
				
		self.rect = self.image.get_rect()
		self.rect.center = self.pos		
		
		#re-set collision rects based on new character object self.rect location
		self.bottom_collision_rect = pygame.Rect( self.rect.bottomleft, ( self.rect.width, self.fall_speed ) ) 
		self.right_side_collision_rect = pygame.Rect( self.rect.topright, (dimsAndLims_obj.right_rect_width, self.rect.height-2) )
		self.left_side_collision_rect = pygame.Rect( (self.rect.left - dimsAndLims_obj.left_rect_width, self.rect.top), (dimsAndLims_obj.left_rect_width, self.rect.height-2) )		
	
class AICharacterObject(CharacterObject):
	def __init__(self, screen, images, starting_position, ai_type, x_limits, dimsAndLims_obj):
		CharacterObject.__init__(self, screen, images, starting_position, x_limits, dimsAndLims_obj)
		self.char_type = ai_type
	
	def update(self, direction, speed, left_side_collision_list, right_side_collision_list, bottom_collision_list, direction_obj, dimsAndLims_obj):
		move_speed = speed
		left = direction_obj.left
		right = direction_obj.right
		player_left_only = direction_obj.player_left_only
		player_right_only = direction_obj.player_right_only
		nudge_left = direction_obj.nudge_left
		nudge_right = direction_obj.nudge_right

		if direction == left:
			if self.isCollidingLeft == True: 
				move_speed /= 5
			if self.x_movement_limit_left == None:				 
				self.pos = (self.pos[0] - move_speed, self.pos[1])
			elif self.x_movement_limit_left - dimsAndLims_obj.x_limit_test_pos < self.pos[0] - move_speed: 
				self.pos = (self.pos[0] - move_speed, self.pos[1])
			else: direction = None
		elif direction == right: 
			if self.isCollidingRight == True:
				move_speed /= 5
			if self.x_movement_limit_right == None: 
				self.pos = (self.pos[0] + move_speed, self.pos[1])
			elif self.x_movement_limit_right + dimsAndLims_obj.x_limit_test_pos > self.pos[0] + move_speed: 
				self.pos = (self.pos[0] + move_speed, self.pos[1])
			else: direction = None
		elif direction == player_left_only: 
			self.pos = (self.pos[0] + move_speed, self.pos[1])
			direction = None			
		elif direction == player_right_only: 
			self.pos = (self.pos[0] - move_speed, self.pos[1])
			direction = None
		elif direction == nudge_left:
			if self.x_movement_limit_left - dimsAndLims_obj.x_limit_test_pos < self.pos[0] - speed:
				self.pos = (self.pos[0] - speed, self.pos[1])
			direction = None #possibly pass NUDGE up to super for animation later?
		elif direction == nudge_right:
			if self.x_movement_limit_right + dimsAndLims_obj.x_limit_test_pos > self.pos[0] + speed:
				self.pos = (self.pos[0] + speed, self.pos[1])
			direction = None #possibly pass NUDGE up to super for animation later?		

		super(AICharacterObject, self).update(direction, left_side_collision_list, right_side_collision_list, bottom_collision_list, direction_obj, dimsAndLims_obj)	
	
class PlayerObject(CharacterObject):	
	def __init__(self, screen, images, starting_position, x_limits, dimsAndLims_obj):
		CharacterObject.__init__(self, screen, images, starting_position, x_limits, dimsAndLims_obj)
	
	def update(self, direction, speed, left_side_collision_list, right_side_collision_list, bottom_collision_list, direction_obj, dimsAndLims_obj):		
		move_speed = speed
		left = direction_obj.left
		right = direction_obj.right
		player_left_only = direction_obj.player_left_only 
		player_right_only = direction_obj.player_right_only 


		if self.isCollidingLeft or self.isCollidingRight:
			move_speed /= 5
		if direction == left:			
			if self.pos[0] > dimsAndLims_obj.screen_width/2 + move_speed:
				self.pos = (self.pos[0] - move_speed, self.pos[1])				
			elif self.pos[0] > dimsAndLims_obj.screen_width/2:
				self.pos = (dimsAndLims_obj.screen_width/2, self.pos[1])
		elif direction == right:
			if self.pos[0] < dimsAndLims_obj.screen_width/2 - move_speed:
				self.pos = (self.pos[0] + move_speed, self.pos[1])				
			elif self.pos[0] < dimsAndLims_obj.screen_width/2:
				self.pos = (dimsAndLims_obj.screen_width/2, self.pos[1])
		elif direction == player_left_only:
			if self.pos[0] - move_speed > move_speed:
				self.pos = (self.pos[0] - move_speed, self.pos[1])
				direction = left
		elif direction == player_right_only:
			if self.pos[0] + move_speed < dimsAndLims_obj.screen_width-move_speed:
				self.pos = (self.pos[0] + move_speed, self.pos[1])
				direction = right
		super(PlayerObject, self).update(direction, left_side_collision_list, right_side_collision_list, bottom_collision_list, direction_obj, dimsAndLims_obj)
