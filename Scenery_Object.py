import pygame
from random import randint
from Globals import *

class ScenerySprite(pygame.sprite.Sprite):
	def __init__(self, screen, image, starting_position):
		pygame.sprite.Sprite.__init__(self)
		self.starting_position = starting_position
		self.screen = screen
		self.image = image
		self.rect = self.image.get_rect(topleft=self.starting_position)

	def update(self, direction, speed, direction_obj):
		if direction == direction_obj.left: self.rect = self.rect.move(speed, 0)
		elif direction == direction_obj.right: self.rect = self.rect.move(-speed, 0)

	def setImage_and_Rect(self, image):
		self.image = image
		self.rect = self.image.get_rect(topleft=self.starting_position) 

class ForegroundSprite(ScenerySprite):
	def __init__(self, screen, image, starting_position):
		ScenerySprite.__init__(self, screen, image, starting_position)

	def update(self, direction, speed, direction_obj):
		super(ForegroundSprite, self).update(direction, speed, direction_obj)

class BackgroundSprite(ScenerySprite):
	def __init__(self, screen, image, starting_position):
		ScenerySprite.__init__(self, screen, image, starting_position)

	def update(self, direction, speed, direction_obj):
		super(BackgroundSprite, self).update(direction, speed, direction_obj)

class AnimatedScenerySprite(ScenerySprite):
	def __init__(self, screen, multi_animation_list, starting_position, starting_animation_index_tuple, inter_frame_delay_max, animation_start_delay):
		"""
		multi_animation_list: 2 dimensional list, each internal list is a list of image-surfaces for a specific animation sequence
		starting_animation_index_tuple: 2-tuple, containing ints; first int refers to animation sequence in multi_animation_list, second int refers to specific image-surface
		"""
		ScenerySprite.__init__(self, screen, multi_animation_list[starting_animation_index_tuple[0]][starting_animation_index_tuple[1]], starting_position)
		self.multi_animation_list = multi_animation_list
		self.start_pos_tuple = starting_animation_index_tuple
		self.animation_count = 0 #len(self.multi_animation_list[self.start_pos_tuple[0]]) - self.start_pos_tuple[1]
		self.current_sequence_and_frame = [self.start_pos_tuple[0], self.start_pos_tuple[1]]
		self.isExecuting = True
		self.frame_delay_set = inter_frame_delay_max
		self.frame_delay_counter = inter_frame_delay_max
		self.animation_delay_start_set = animation_start_delay
		self.animation_delay_start_counter = animation_start_delay

	def getNumAnimations(self):
		"""returns a (int, list) tuple: the number of animation sequences, and each sequence length in a list"""
		return len(self.multi_animation_list), [len(interior_list) for interior_list in self.multi_animation_list]
	
	def update(self, direction, speed, animation_sequence_index, override_animation, direction_obj):
		"""Explicitly alter the position/image of this sprite, animation sequence index refers to the particular sequence to use"""
		super(AnimatedScenerySprite, self).update(direction, speed, direction_obj) #purely directional, not animation related			

		if override_animation and animation_sequence_index != None:
			self.isExecuting = True
			self.animation_delay_start_counter = self.animation_delay_start_set
			self.animation_count = len(self.multi_animation_list[animation_sequence_index])	#reset count to length of current animation sequence			
			self.current_sequence_and_frame[0] = animation_sequence_index #set index for new sequence
			self.current_sequence_and_frame[1] = 0 

		if self.animation_count != 0: #currently in-progress using a previously specified sequence
			self.isExecuting = True
			if self.animation_delay_start_counter > 0:
				self.animation_delay_start_counter -= 1			
			if self.frame_delay_counter > 0:
				self.frame_delay_counter -= 1
			elif self.frame_delay_counter == 0 and self.animation_delay_start_counter == 0:
				self.frame_delay_counter = self.frame_delay_set
				self.animation_count -= 1						
				image = self.multi_animation_list[self.current_sequence_and_frame[0]][self.current_sequence_and_frame[1]]
				self.current_sequence_and_frame[1] += 1
				super(AnimatedScenerySprite, self).setImage_and_Rect(image)
		else:
			self.isExecuting = False			
			if animation_sequence_index != None: #if not None
				self.isExecuting = True
				self.animation_delay_start_counter = self.animation_delay_start_set
				self.animation_count = len(self.multi_animation_list[animation_sequence_index])	#reset count to length of current animation sequence			
				self.current_sequence_and_frame[0] = animation_sequence_index #set index for new sequence
				self.current_sequence_and_frame[1] = 0	#frame for sequence set to 0
				

class AnimatedSceneryAnimationManager(object):
	def __init__(self, spritegroup, list_AnimatedScenerySprites, list_animation_occurence_rates, list_active_reactive_animation_tuples, list_active_reactive_animation_offsets):
		"""
		Intended to schedule animations for the passed in list of AnimatedScenerySprite objects
		using a list of animation occurrence rates (for active animations), and a list of active-reactive relationship tuples
		to determine which reactive animations should fire for which active animations, and with an additional list of offset
		delays for activation of the related reactive animations
		"""
		self.spritegroup = spritegroup
		self.sprites = list_AnimatedScenerySprites
		self.list_animation_occurence_rates = list_animation_occurence_rates
		self.list_active_reactive_animation_tuples = list_active_reactive_animation_tuples
		self.list_active_reactive_animation_offsets = list_active_reactive_animation_offsets
		self.reactive_animation_dictionary = {}
		for tri_tuple in self.list_active_reactive_animation_tuples:
			self.reactive_animation_dictionary[(tri_tuple[0], tri_tuple[1])] = tri_tuple[2]

	def update(self, speed, directions_obj):		
		for index, sprite in enumerate(self.sprites):
			chosen_sequence = None

			if not sprite.isExecuting: #don't bother continuing with choosing an animation sequence if one is already firing
				sequence_roll = randint(0, 99)			
				if self.list_animation_occurence_rates[index]: #determines whether this is an active or reactive sprite

					chosen_sequence = self.searchDropChart(	self.list_animation_occurence_rates[index], 		#drop_chart
															len(self.list_animation_occurence_rates[index])/2,  #starting index
															sequence_roll, 										#value for search
															len(self.list_animation_occurence_rates[index])-1,  #upper index bound
															0, 													#lower index bound
															0, 													#current iteration
															0, 													#default return value
															5)													#max recursions allowed

					if (index, chosen_sequence) in self.reactive_animation_dictionary: #check if updated sprite has a reactive pairing
						reactive_sequence = self.reactive_animation_dictionary[(index, chosen_sequence)]
						#if not self.sprites[reactive_sequence].isExecuting: #check if reactive animation is already firing
						self.sprites[reactive_sequence].update(None, speed, 0, True, directions_obj)

			sprite.update(None, speed, chosen_sequence, False, directions_obj)

	def draw(self, surface):
		self.spritegroup.draw(surface)

	def searchDropChart(self, drop_chart, index, value, upper_ind_b, lower_ind_b, iterat, default=0, max_depth=5):
		iterat += 1
		if max_depth == iterat: return default
		cur_tuple = drop_chart[index]
		if cur_tuple[0] <= value and cur_tuple[1] >= value: 
			return index
		else:
			if cur_tuple[0] > value:
				adjust = (index - lower_ind_b)/2
				if not adjust: adjust = 0
				new_index = adjust + lower_ind_b
				return self.searchDropChart(drop_chart, new_index, value, index, lower_ind_b, iterat)
			elif cur_tuple[1] < value:
				adjust = (upper_ind_b - index)/2
				if not adjust: adjust = 1
				new_index = adjust + index
				return self.searchDropChart(drop_chart, new_index, value, upper_ind_b, index, iterat)
								

class BackgroundSurfacesManager(object):
	def __init__(self, screen, image_list, starting_positions, wrap, scroll_limits, screen_width ):
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
		if self.limits != None: self.limit_test_position = screen_width/2		
		self.background_sprite_group = pygame.sprite.OrderedUpdates()
		for index, image in enumerate(self.images): 
			self.background_sprite_group.add(BackgroundSprite(self.screen, image, self.positions[index]))
			
	def update(self, direction, speed, player_object, direction_obj, dimensions_and_limits_obj):
		"""updates all background sprites uniformly, unless doing so would violate a limit in self.limits""" 
		LEFT = direction_obj.left
		RIGHT = direction_obj.right

		if direction == LEFT:			
			if (self.limits != None): 
				if (self.limits[1] <= (self.limit_test_position + speed)): return dimensions_and_limits_obj.AT_LIMIT_RIGHT, self.x_movement_measure	+ dimensions_and_limits_obj.x_limit_test_pos							

			if player_object.pos[0] == dimensions_and_limits_obj.screen_width/2:	
				self.background_sprite_group.update(direction, speed)			
				self.x_movement_measure += speed						
				if self.limit_test_position != None: self.limit_test_position += speed			

				if self.wrap: #if wrapping is enabled
					if self.x_movement_measure > dimensions_and_limits_obj.screen_width:
						self.x_movement_measure -= dimensions_and_limits_obj.screen_width
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
						target_sprite.update(RIGHT, dimensions_and_limits_obj.screen_width*(len(self.images)))			
			
		elif direction == RIGHT: 
			if (self.limits != None): 
				if (self.limits[0] >= (self.limit_test_position - speed)): return dimensions_and_limits_obj.AT_LIMIT_LEFT, self.x_movement_measure + dimensions_and_limits_obj.x_limit_test_pos

			if player_object.pos[0] == dimensions_and_limits_obj.screen_width/2:
				self.background_sprite_group.update(direction, speed)			
				self.x_movement_measure -= speed			
				
				if self.limit_test_position != None: self.limit_test_position -= speed
				
				if self.wrap: #if wrapping is enabled			
					if self.x_movement_measure < -dimensions_and_limits_obj.screen-width:
						self.x_movement_measure += dimensions_and_limits_obj.screen_width
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
						target_sprite.update(LEFT, dimensions_and_limits_obj.screen_width*(len(self.images)))
		
		return None, self.x_movement_measure + dimensions_and_limits_obj.x_limit_test_pos
	
	def draw(self, screen):
		self.background_sprite_group.draw(screen)