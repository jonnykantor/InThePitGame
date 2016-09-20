import pygame, math, sys, os
from pygame.locals import *
from random import randint
from Globals import *

class BodyPart(object):
	def __init__(	self, 
					image, 
					starting_position, 
					parent, 
					left_movement_list, 
					right_movement_list, 
					y_shift_list, 
					max_positive_rotation,
					max_negative_rotation,
					rotation_rate):
		"""
		Each BodyPart object will be drawn to a surface contained in the Skeleton class.
		The starting position refers to the position on that surface, relative to the top-left
		corner of that surface. The rotation_angle is used to perform transforms on the original_image, 
		and the resulting rotation will then be stored as current_image

		Each BodyPart may also contain a parent and possibly multiple children depending on the BodyPart's
		place in the skeletal hierarchy

		parent: [BodyPart, x_pos, y_pos] with x_pos, y_pos as ints
		children: [(BodyPart, x_pos, y_pos), (BodyPart, x_pos, y_pos)...] with x_pos, y_pos as ints

		parents can be set as the BodyPart in question is created (provided it's done in hierarchical order)
		
		children will have to be set initially to [] and initialized to a proper list if necessary, preferably
		using the setChildren method. This is somewhat unavoidable, as BodyPart objects may require both a
		parent and children, but if the children objects can be provided (ie: if the child BodyParts are created
		ahead of time), this would necessitate that the parent BodyParts are created later, and thus require the
		parent to be set later instead. As creating hierarchically from the root outwards seems preferable, that's
		what I've gone with.
		
		left_movement_list contains angles that will be used for sequential rotations when the object is facing left
		right_movement_list does the same for movements facing right
		y_shift_list contains values for sequential shifts in the y coordinate position

		max_negative_rotation and max_positive_rotation indicate the maximum amounts of rotation in the negative or
		positive direction that can be performed with respect to the parent's current rotation_angle. This assumes
		that the initial direction is facing leftwards, and the values should be swapped when direction is changed.
		This change should be handled by the Skeleton object containing this BodyPart
		"""
		
		#aesthetic
		self.original_image = image
		self.current_image = image		
		
		#behavior and positions
		self.max_positive_rotation = max_positive_rotation
		self.max_negative_rotation = max_negative_rotation	
		self.rotation_angle = 0
		self.stored_center_pos = self.original_image.get_rect().center
		self.position = starting_position

		#hierarchy
		self.parent = parent #may be None if this BodyPart is the root
		self.children = [] #must be set using setChildren method

		#movements
		self.left_movement_list = left_movement_list		
		self.right_movement_list = right_movement_list
		self.mounted_animation_set = left_movement_list
		self.animation_limit = len(self.left_movement_list)
		self.animation_count = 0
		self.y_shift_list = y_shift_list
		self.y_shift_count = 0
		self.y_shift_limit = len(y_shift_list)

		#alt-movement approach
		self.lower_angle_bound_ammt = max_negative_rotation	#lower_angle_bound_ammt #to be subtracted from current parent[0].rotation_angle to find actual bound
		self.upper_angle_bound_ammt = max_positive_rotation	#upper_angle_bound_ammt #to be added to current parent[0].rotation_angle to find actual bound
		self.rotation_rate = rotation_rate

	def update(self, angle, x_movement, y_movement, isRotationRigid=False):
		"""
		angle: float, indicating degrees, can be any value, positive or negative
		x_movement: int, indicating a shift on the x-axis
		y_movement: int, indicating a shift on the y-axis
		isRotationRigid: bool, indicating that input rotations should be applied to child BodyPart objects
		"""
		#offset declarations						
		parent_bind_point_offset_x = 0
		parent_bind_point_offset_y = 0
		actual_offset_x = 0
		actual_offset_y = 0
		center_offset_x = 0
		center_offset_y = 0

		#rigid rotation and boundary rotation amounts
		rigid_rotation = 0.0
		boundary_rotation = 0.0

		#cosine/sine value calculation need only be done once per limb per update
		#these values will be passed to the rotatePoint function at least once
		cos_val = None
		sin_val = None
		angle_in_radians = None

		if angle != 0: #rotation required
			self.rotation_angle += angle
			#if new rotation_angle violates current angle rules, correct to nearest acceptable value
			if self.parent[0] != None:
				#provided there is a parent object, check if rotation violates bounds
				if (self.rotation_angle) > (self.max_positive_rotation + self.parent[0].rotation_angle):
					ang_diff = self.rotation_angle - (self.max_positive_rotation + self.parent[0].rotation_angle)
					angle -= ang_diff 
					self.rotation_angle = self.max_positive_rotation + self.parent[0].rotation_angle
				elif (self.rotation_angle) < (self.max_negative_rotation + self.parent[0].rotation_angle ):
					ang_diff = self.rotation_angle - (self.max_negative_rotation + self.parent[0].rotation_angle)
					angle -= ang_diff 
					self.rotation_angle = self.max_negative_rotation + self.parent[0].rotation_angle

			angle_in_radians = math.radians(-angle)

			if isRotationRigid: rigid_rotation == angle			
			if self.rotation_angle > 360: self.rotation_angle -= 360
			if self.rotation_angle < -360: self.rotation_angle += 360		
			self.current_image = self.original_image
			self.current_image = pygame.transform.rotate(self.current_image, self.rotation_angle)
			
			#offset calculation to make up for pygame rect size changes
			new_center = self.current_image.get_rect().center
			#get offsets, delta x and y			
			center_offset_x = self.stored_center_pos[0] - new_center[0]
			center_offset_y = self.stored_center_pos[1] - new_center[1]		
			self.stored_center_pos = new_center

			for child in self.children:
				child[1] -= center_offset_x
				child[2] -= center_offset_y			
			
			if self.parent[0] != None:
				self.parent[1] -= center_offset_x
				self.parent[2] -= center_offset_y
				new_parent_bind_point, cos_val, sin_val = rotatePoint((self.parent[1], self.parent[2]), self.stored_center_pos, angle_in_radians, cos_val, sin_val)			
				if new_parent_bind_point != (self.parent[1], self.parent[2]):
					#get offsets for shifting image position so that parent bind points will match up
					parent_bind_point_offset_x = self.parent[1] - new_parent_bind_point[0]
					parent_bind_point_offset_y = self.parent[2] - new_parent_bind_point[1]				
					self.parent[1] = new_parent_bind_point[0]
					self.parent[2] = new_parent_bind_point[1]

			for child in self.children:
				#rotate and correct child bindpoint positions
				new_child_bind_point, cos_val, sin_val = rotatePoint((child[1], child[2]), self.stored_center_pos, angle_in_radians, cos_val, sin_val)
				child[1] = new_child_bind_point[0]
				child[2] = new_child_bind_point[1]
				child_draw_pos = child[0].position
				child_parent_bind_point = (child[0].parent[1] + child_draw_pos[0], child[0].parent[2] + child_draw_pos[1])
				x_child_shift_amount = child_parent_bind_point[0] - (child[1] + self.position[0])
				y_child_shift_amount = child_parent_bind_point[1] - (child[2] + self.position[1])

				#offset shifts resulting from rotations for all children
				#also apply rigid rotation if set to True, and any rotation needed to keep child angle's legal
				if not self.check_isChildRotationLegal(child[0]): rigid_rotation = angle
				child[0].update(	rigid_rotation, 
									center_offset_x + parent_bind_point_offset_x - x_child_shift_amount, 
									center_offset_y + parent_bind_point_offset_y - y_child_shift_amount
								)
		#x/y shift only		
		for child in self.children: child[0].update(0, x_movement, y_movement)

		self.position = (	
							self.position[0] + x_movement + center_offset_x + parent_bind_point_offset_x, 
							self.position[1] + y_movement + center_offset_y  + parent_bind_point_offset_y 
						)
	
	def check_isChildRotationLegal(self, child):
		if (child.rotation_angle) > (child.max_positive_rotation + self.rotation_angle):
			return False
		elif (child.rotation_angle) < (child.max_negative_rotation + self.rotation_angle):
			return False
		else:
			return True
	def getNextAngle(self):
		"""
		An oscilating movement model, returns the next angle to rotate by
		Checks self.rotation_angle to see if it's at one of the rotational bounds; if so, negate self.rotation_rate
		Adds the current self.rotation_rate to self.rotation_angle and checks if the result violates either the lower 
		bound or upper bound, if so, returns the difference between the current self.rotation_angle and the violated bound
		otherwise returns the current rotation rate
		"""
		ret_ang = self.rotation_rate
		#rate negation if necessary, and return new angle
		if self.parent[0] != None:
			if self.rotation_angle == self.upper_angle_bound_ammt + self.parent[0].rotation_angle:
				if self.rotation_rate > 0: self.rotation_rate *= -1	
			elif self.rotation_angle == self.lower_angle_bound_ammt + self.parent[0].rotation_angle:
				if self.rotation_rate < 0: self.rotation_rate *= -1

			if (self.rotation_angle + self.rotation_rate) > (self.upper_angle_bound_ammt + self.parent[0].rotation_angle):
				ret_ang = self.upper_angle_bound_ammt - self.rotation_angle
			elif (self.rotation_angle + self.rotation_rate) < (self.lower_angle_bound_ammt + self.parent[0].rotation_angle):
				ret_ang = self.lower_angle_bound_ammt - self.rotation_angle		

		return ret_ang

	def setChildren(self, children_list):
		"""
		Each item of children_list is a 3-tuple with: (BodyPart, x_pos, y_pos), x_pos & y_pos are ints
		"""
		self.children = children_list

def rotatePoint(point, axis, angle_in_radians, cos_val=None, sin_val=None):
	"""
	given a point and an axis, performs a rotation by first translating the point such that
	the same translation when applied to the axis would place it at the origin, then rotates
	using the rotational matrix:
	[cos(angle_in_radians), -sin(angle_in_radians)] 	* 	[translated_point[0]]
	[sin(angle_in_radians),  cos(angle_in_radians)]			[translated_point[1]]
	Then translates the point by the negation of the original translation, and returns that point
	the function will return the new point location, and the cos_val, sin_val values
	"""
	ret_val = point
	
	#angle_in_radians = math.radians(-angle_in_degrees)

	if cos_val == None: cos_val = math.cos(angle_in_radians)
	if sin_val == None: sin_val = math.sin(angle_in_radians)
	
	ret_val = (ret_val[0] - axis[0], ret_val[1] - axis[1]) #translation
	ret_val = (ret_val[0] * cos_val + ret_val[1] * (-1) * sin_val, ret_val[0] * sin_val + ret_val[1] * cos_val) #rotation
	ret_val = (ret_val[0] + axis[0], ret_val[1] + axis[1]) #negative translation

	return ret_val, cos_val, sin_val

class Skeleton(object):
	UPDATE_TYPE_NEUTRAL = 0
	UPDATE_TYPE_RUN_LEFT = 1
	UPDATE_TYPE_RUN_RIGHT = 2
	def __init__(	self, 
					torso, 
					head, 
					left_upper_arm, 
					right_upper_arm, 
					left_forearm, 
					right_forearm, 
					left_upper_leg,
					right_upper_leg,
					left_lower_leg,
					right_lower_leg,
					alpha_colorkey, 
					initial_draw_order, 
					surface_width, 
					surface_height):
		#BodyParts
		self.head = head
		self.torso = torso
		self.left_upper_arm = left_upper_arm
		self.right_upper_arm = right_upper_arm
		self.left_forearm = left_forearm
		self.right_forearm = right_forearm
		self.left_upper_leg = left_upper_leg
		self.right_upper_leg = right_upper_leg
		self.left_lower_leg = left_lower_leg
		self.right_lower_leg = right_lower_leg

		self.bodyparts = [	self.torso,
							self.head,
							self.left_upper_arm,
							self.right_upper_arm,
							self.left_forearm,
							self.right_forearm,
							self.left_upper_leg,
							self.right_upper_leg,
							self.left_lower_leg,
							self.right_lower_leg	]

		self.image = pygame.Surface((surface_width, surface_height), pygame.SRCALPHA).convert()
		self.width = surface_width
		self.height = surface_height
		
		self.colorkey = alpha_colorkey		
		self.image = self.getImage(initial_draw_order)
		self.image.set_colorkey(alpha_colorkey)

		self.left_face_order = [2, 4, 6, 8, 0, 1, 3, 5, 7, 9]
		self.right_face_order = [3, 5, 7, 9, 0, 1, 2, 4, 6, 8]

		self.onBeat = True
		self.sign = -1

	def update(self, updates, isColliding=False):
		"""
		updates type: list
		should contain 3-tuples, each one comprised as: (float, int, int) - angle, x_movement, y_movement
		"""
		

		if updates == None:
			if not (self.onBeat and isColliding):# or not self.onBeat:
				self.sign = self.sign * -1			
				for index, bodypart in enumerate(self.bodyparts):
					#using mounted movement sets, sort of hard-coded movement
					"""
					bodypart.update(bodypart.mounted_animation_set[bodypart.animation_count], 0, bodypart.y_shift_list[bodypart.y_shift_count])
					bodypart.animation_count += 1
					bodypart.y_shift_count += 1
					if bodypart.y_shift_count >= bodypart.y_shift_limit: bodypart.y_shift_count = 0
					if bodypart.animation_count >= bodypart.animation_limit: bodypart.animation_count = 0				
					"""
					#using alt-movement
					next_angle = bodypart.getNextAngle()
					#if index == 6:
					#	other_next_angle = self.bodyparts[7].getNextAngle()
					#	if (other_next_angle * next_angle) > 0: next_angle = next_angle
					bodypart.update(next_angle, 0, 0)
					
		else:
			for index, bodypart in enumerate(self.bodyparts):
				if updates[index] != None:
					bodypart.update(updates[index][0], updates[index][1], updates[index][2])				

		self.onBeat = not self.onBeat

	def getImage(self, order):
		"""
		update existing Skeleton surface based on order, and return it
		"""

		self.image.fill(self.colorkey)
		for order_index in order:
			self.image.blit(self.bodyparts[order_index].current_image, self.bodyparts[order_index].position)
		
		#DEBUG draw rects at bindpoint positions
		for bodypart in self.bodyparts:
			#child bind points
			for child in bodypart.children:
				color = (255, 100, 255)
				if bodypart == self.bodyparts[0]: color = (50, 50, 255)
				pygame.draw.circle(self.image, color, (int(child[1] + bodypart.position[0]), int(child[2] + bodypart.position[1])), 4, 0)
			#parent bind point
			if bodypart.parent[0] != None:			
				pygame.draw.circle(self.image, (255, 255, 255), (int(bodypart.parent[1] + bodypart.position[0]), int(bodypart.parent[2] + bodypart.position[1])), 4, 2)

			pygame.draw.circle(self.image, (255, 250, 100), (int(bodypart.position[0]), int(bodypart.position[1])), 5, 2)
		return self.image

	def changeDirection(self, direction, direction_obj):
		"""
		shifts bodypart alignments to reflect a change in direction (ie: the character has turned around)
		"""
		for bodypart in self.bodyparts:
			#swap max_positive_rotation and max_negative rotation, and swap sign of both
			temp = bodypart.max_positive_rotation
			bodypart.max_positive_rotation = -bodypart.max_negative_rotation
			bodypart.max_negative_rotation = -temp
			#alt-movement system swaps
			temp = bodypart.upper_angle_bound_ammt
			bodypart.upper_angle_bound_ammt = -bodypart.lower_angle_bound_ammt
			bodypart.lower_angle_bound_ammt = -temp
			bodypart.rotation_rate = -bodypart.rotation_rate

			#reset animation counts and change mounted animation set
			bodypart.animation_count = 0;
			if direction == direction_obj.left:
				bodypart.mounted_animation_set = bodypart.left_movement_list
			elif direction == direction_obj.right:
				bodypart.mounted_animation_set = bodypart.right_movement_list
			if bodypart.rotation_angle != 0:
				bodypart.update(-bodypart.rotation_angle, 0, 0)
					
		if direction == direction_obj.left:			
			
			self.update([	None, 																
							(0, -self.bodyparts[1].original_image.get_width(), 0), 				
							(0, -self.bodyparts[2].original_image.get_width()/2, 0),	
							(0, -self.bodyparts[3].original_image.get_width()/2, 0),	
							None,	
							None,
							(0, -self.bodyparts[6].original_image.get_width()/2, 0),	
							(0, -self.bodyparts[7].original_image.get_width()/2, 0),	
							None,
							None])

		elif direction == direction_obj.right:
			
			self.update([	None, 
							(0, self.bodyparts[1].original_image.get_width(), 0), 
							(0, self.bodyparts[2].original_image.get_width()/2, 0),
							(0, self.bodyparts[3].original_image.get_width()/2, 0),
							None,
							None,
							(0, self.bodyparts[6].original_image.get_width()/2, 0),	
							(0, self.bodyparts[7].original_image.get_width()/2, 0),	
							None,
							None])
		
		#realign torso child-points here
		torso_x_midpoint = self.bodyparts[0].original_image.get_width()/2
		for child in self.bodyparts[0].children:
			child[1] = torso_x_midpoint + (torso_x_midpoint - child[1])

		
def makeSkeleton():
	"""creates images for bodyparts, creates the bodyparts, and then creates the skeleton and returns it"""

	#Loading images is not in the cards just yet, to be written (after being drawn)
	#Currently working out skeleton movement and transforms using colored rects instead - should serve for now	

	head_size = (30, 30)
	arm_up_size = (20, 40)
	forerm_size = (20, 30)
	torso_size = (60, 90)
	leg_up_size = (20, 30)
	leg_low_size = (20, 30)

	torso 	= pygame.Surface(torso_size, pygame.SRCALPHA).convert()
	head 	= pygame.Surface(head_size, pygame.SRCALPHA).convert()	
	l_arm_up= pygame.Surface(arm_up_size, pygame.SRCALPHA).convert()
	r_arm_up= pygame.Surface(arm_up_size, pygame.SRCALPHA).convert()
	l_forerm= pygame.Surface(forerm_size, pygame.SRCALPHA).convert()
	r_forerm= pygame.Surface(forerm_size, pygame.SRCALPHA).convert()
	l_leg_up= pygame.Surface(leg_up_size, pygame.SRCALPHA).convert()
	r_leg_up= pygame.Surface(leg_up_size, pygame.SRCALPHA).convert()
	l_lowleg= pygame.Surface(leg_low_size, pygame.SRCALPHA).convert()
	r_lowleg= pygame.Surface(leg_low_size, pygame.SRCALPHA).convert()

	#initial max positive/negative rotational amounts
	rotation_sets = [	(360.0, -360.0), 
						(90.0, -45.0), 
						(60.0, -60.0), 	(60.0, -60.0), 
						(-30.0, -130.0), 	(-30.0, -130.0), 
						(60.0, -60.0), 	(60.0, -60.0), 
						(100.0, 0.0), 		(100.0, 0.0)	
					]

	rotation_rates = [0, 0, 30, -30, 10, 10, 20, -20, 10, 10]

	limbs = [torso, head, 	l_arm_up, 	r_arm_up, 	l_forerm, 	r_forerm, 	l_leg_up, 	r_leg_up, 	l_lowleg, 	r_lowleg]
			#0		1		2			3			4			5			6			7			8			9
	DARK_GREY		=	(50, 50, 50)
	RED				=	(255, 0, 0)
	GREEN 			=	(0, 255, 0)
	LIGHT_GREEN		= 	(125, 255, 125)
	BLUE 			=	(0, 0, 255)
	LIGHT_BLUE 		=	(125, 125, 255)
	GOLD 			=	(255, 215, 0)
	WHITE 			=	(255, 255, 255)

	torso_position = (arm_up_size[1] + forerm_size[1], arm_up_size[1] + forerm_size[1])

	#these represent the starting draw-positions for the bodypart elements on the skeleton image surface that the skeleton class
	#returns rather than positions on the screen surface. Each one is placed relative to the root BodyPart's position
	start_positions = [	torso_position,																									#torso
						(torso_position[0], torso_position[1] - head_size[1]),															#head
						(torso_position[0] - arm_up_size[0]/2, torso_position[1]),														#upper_arm_left
						(torso_position[0] + torso_size[0] - arm_up_size[0], torso_position[1]),										#upper_arm_right
						(torso_position[0] - arm_up_size[0]/2, torso_position[1] + arm_up_size[1]),										#Forearm_left
						(torso_position[0] + torso_size[0] - arm_up_size[0], torso_position[1] + arm_up_size[1]),						#Forearm_right
						(torso_position[0], torso_position[1] + torso_size[1]), 														#leg_left_up
						(torso_position[0] + torso_size[0] - leg_up_size[0] - leg_up_size[0]/2, torso_position[1] + torso_size[1]),		#leg_left_up
						(torso_position[0], torso_position[1] + torso_size[1] + leg_up_size[1]),										#lower legs
						(torso_position[0] + torso_size[0] - leg_up_size[0] - leg_up_size[0]/2,	torso_position[1] + torso_size[1] + leg_up_size[1])
						]

	limbcols = [RED, GREEN, WHITE, WHITE, GREEN, GREEN, BLUE, GREEN, BLUE, GREEN]
	
	parents = [None, 0, 0, 0, 2, 3, 0, 0, 6, 7]

	
	parent_bind_positions = [	
								(None, None), 
								(head_size[0]/2, head_size[1]), 
								(arm_up_size[0]/2, arm_up_size[0]/2), 
								(arm_up_size[0]/2, arm_up_size[0]/2), 
								(forerm_size[0]/2, 0), 
								(forerm_size[0]/2, 0), 
								(leg_up_size[0]/2, 0), 
								(leg_up_size[0]/2, 0), 
								(leg_low_size[0]/2, 0), 
								(leg_low_size[0]/2, 0)
							]
	children = [[1, 2, 3, 6, 7], [], [4], [5], [], [], [8], [9], [], []]
	children_pos = 	[																									#Torso's children:
					[	
						[1, head_size[0]/2, 0],						 								##head
						[2, 0, arm_up_size[0]/2], 													##left_upper_arm	
						[3, torso_size[0] - arm_up_size[0]/2, arm_up_size[0]/2],				##right upper arm 
						[6,	leg_up_size[0]/2, torso_size[1]], 			  	##left upper leg
						[7, torso_size[0] - leg_up_size[0], torso_size[1]] 	##right upper leg
					 ],	
					[], 		#Head's children
					[[4, arm_up_size[0]/2, arm_up_size[1]]], 									#left_arm_upper
					[[5, arm_up_size[0]/2, arm_up_size[1]]], #right_arm_upper
					[],			#left_arm_lower
					[],			#right_arm_lower
					[[8, leg_up_size[0]/2, leg_up_size[1]]],#left_leg_upper
					[[9, leg_up_size[0]/2, leg_up_size[1]]],	#right_leg_upper
					[],			#left_leg_lower
					[]			#right_leg_lower
				]
	#DECLARE BodyPart OBJECTS HERE:
	parts = []
	for index, limb in enumerate(limbs):
		limb.fill(LIGHT_BLUE)
		limb.set_colorkey(LIGHT_BLUE)
		pygame.draw.rect(limb, limbcols[index], limb.get_rect())
		part_index = parents[index]
		if part_index == None:
			parts.append(BodyPart(limb, start_positions[index], [None, None, None], [0], [0], [0], rotation_sets[index][0], rotation_sets[index][1], 0))
		else:
			parts.append(BodyPart(	limb, 
									start_positions[index], 
									[parts[parents[index]], parent_bind_positions[index][0], parent_bind_positions[index][1]], 
									[0], [0], [0],
									rotation_sets[index][0],
									rotation_sets[index][1],
									rotation_rates[index]
									)
						)
	
	for index, child_positions_list in enumerate(children_pos):
		for inner_index, each_child_pos_list in enumerate(child_positions_list):
			children_pos[index][inner_index][0] = parts[children_pos[index][inner_index][0]]			
		parts[index].setChildren(children_pos[index])	

	parts[6].left_movement_list		=	[-15, -15, -15, 15, 15, 15,  0,  0,  15, 15,  15, -15, -15, -15]
	parts[6].mounted_animation_set 	= 	parts[6].left_movement_list
	parts[6].animation_limit 		= 	len(parts[6].left_movement_list)
	parts[8].left_movement_list		=	[0, 0, 0, 0, 0,  15,   15, 15, 15,  0, -15,  -15,  -15,  -15]
	parts[8].mounted_animation_set 	= 	parts[8].left_movement_list
	parts[8].animation_limit 		= 	len(parts[8].left_movement_list)
	parts[7].left_movement_list		=	[ 0,  15,  15,  15, -15, -15, -15, -15, -15, -15, 0, 15, 15, 15]
	parts[7].mounted_animation_set 	= 	parts[7].left_movement_list
	parts[7].animation_limit 		= 	len(parts[7].left_movement_list)
	parts[9].left_movement_list		=	[ 15,   15, 15, 15,  0, -15,  -15,  -15,  -15,  0, 0, 0, 0, 0]
	parts[9].mounted_animation_set 	= 	parts[9].left_movement_list
	parts[9].animation_limit 		= 	len(parts[9].left_movement_list)

	parts[6].right_movement_list	=	[15, 15, 15, -15, -15, -15,  0,  0,  -15, -15,  -15, 15, 15, 15]
	parts[8].right_movement_list	=	[0, 0, 0, 0, 0,  -15,   -15, -15, -15,  0, 15,  15,  15,  15]
	parts[7].right_movement_list	=	[ 0,  -15,  -15,  -15, 15, 15, 15, 15, 15, 15, 0, -15, -15, -15]
	parts[9].right_movement_list	=	[ -15,   -15, -15, -15,  0, 15,  15,  15,  15,  0, 0, 0, 0, 0]

	parts[2].left_movement_list 	= [10, 5, 5, -5, -5, -10, -20, -10, -5, 5, 10, 20]
	parts[2].mounted_animation_set 	= parts[2].left_movement_list
	parts[2].animation_limit 		= len(parts[2].left_movement_list)
	parts[3].left_movement_list 	= [-20, -10, -5, 5, 10, 20, 10, 5, 5, -5, -5, -10]
	parts[3].mounted_animation_set 	= parts[3].left_movement_list
	parts[3].animation_limit 		= len(parts[3].left_movement_list)
	parts[4].left_movement_list 	= [10, 5, 5, -5, -5, -10, -45, -20, -5, 5, 25, 40]
	parts[4].mounted_animation_set 	= parts[4].left_movement_list
	parts[4].animation_limit 		= len(parts[4].left_movement_list)
	parts[5].left_movement_list 	= [-45, -20, -5, 5, 25, 40, 10, 5, 5, -5, -5, -10]
	parts[5].mounted_animation_set 	= parts[5].left_movement_list
	parts[5].animation_limit 		= len(parts[5].left_movement_list)

	parts[2].right_movement_list 	= [-10, -5, -5, 5, 5, 10, 10, 5, 5, -5, -5, -10]
	parts[3].right_movement_list 	= [10, 5, 5, -5, -5, -10, -10, -5, -5, 5, 5, 10]
	parts[4].right_movement_list 	= [-10, -5, -5, 5, 5, 10, 10, 5, 5, -5, -5, -10]
	parts[5].right_movement_list 	= [10, 5, 5, -5, -5, -10, -10, -5, -5, 5, 5, 10]

	parts[0].y_shift_list = [1, 1, 0, 0, -1, -1, 0, 0]
	parts[0].y_shift_limit = len(parts[0].y_shift_list)

	skeleton = Skeleton(	parts[0], 	#torso
							parts[1], 	#head
							parts[2], 	#up_arm_left
							parts[3], 	#up_arm_right
							parts[4], 	#forearm_left
							parts[5], 	#forearm_right
							parts[6], 	#up_leg_left
							parts[7], 	#up_leg_right
							parts[8],	#low_leg_left
							parts[9],	#low_leg_right
							LIGHT_BLUE, [2, 4, 6, 8, 1, 0, 3, 5, 7, 9], 180, 260)

	return skeleton

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


		self.skeleton = makeSkeleton() #creates Skeleton object for this character, which handles animation


		self.image = self.skeleton.image #set initial image		
		self.pos = starting_position
		self.character_floor = starting_position[1] #used to stop fall motion, essentially locates the 'floor'
		self.facing_direction = 0 #1 is right		
		
		self.rect = self.image.get_rect()		
		self.rect.center = self.pos		
		
		#collision rectangles and stats
		self.bottom_collision_rect = pygame.Rect( self.rect.bottomleft, ( self.rect.width, self.character_floor - self.rect.bottom ) )		
		self.right_side_collision_rect = pygame.Rect( self.rect.topright, (dimsAndLims_obj.right_rect_width, self.rect.height-2) )
		self.left_side_collision_rect = pygame.Rect( (self.rect.left - dimsAndLims_obj.left_rect_width, self.rect.top), self.rect.bottomleft )
		
		self.isCollidingRight = False
		self.isCollidingLeft = False
		self.isCollidingBottom = False

		self.collisionObjectLeft = None
		self.collisionObjectRight = None
		
		#individual counters for individual image list current image position
		
		
		#jump stats
		self.jumpCounter 	= 0
		self.isAirborne 	= False
		self.fall_speed 	= 0
		self.jump_speed 	= 15

		#REMOVE
		self.anim_count = 0
		self.anim_ang = 15
		self.anim_bound = 45
		
	def update(self, direction, left_side_collision_list, right_side_collision_list, bottom_collision_list, direction_obj, dimsAndLims_obj):

		left = direction_obj.left
		right = direction_obj.right
		up = direction_obj.up
		player_left_only = direction_obj.player_left_only
		player_right_only = direction_obj.player_right_only
		nudge_left = direction_obj.nudge_left
		nudge_right = direction_obj.nudge_right

		#collision testing
		collide_left = self.left_side_collision_rect.collidelist(left_side_collision_list) 
		if collide_left > -1: self.collisionObjectLeft = left_side_collision_list[collide_left]
		collide_right = self.right_side_collision_rect.collidelist(right_side_collision_list) 
		if collide_right > -1: self.collisionObjectRight = right_side_collision_list[collide_right]
		collide_bottom = self.bottom_collision_rect.collidelist(bottom_collision_list) 
		
		if collide_left == -1: self.isCollidingLeft = False
		else: self.isCollidingLeft = True
		if collide_right == -1: self.isCollidingRight = False
		else: self.isCollidingRight = True
		if collide_bottom == -1: self.isCollidingBottom = False
		else: self.isCollidingBottom = True			
		
		#jump indicated, not already in the air
		if direction == up and not self.isAirborne:	
			self.jumpCounter = 5					
		
		#if direction == None:
		#	self.skeleton.update(None)
		#	self.image = self.skeleton.getImage(self.skeleton.left_face_order)

		elif direction == left:

			if self.facing_direction == right:
				self.skeleton.changeDirection(direction_obj.left, direction_obj)
				self.facing_direction = left
			self.skeleton.update(None, (self.isCollidingLeft or self.isCollidingRight))
			self.image = self.skeleton.getImage(self.skeleton.left_face_order)
			

		elif direction == right:
			
			if self.facing_direction == left:
				self.skeleton.changeDirection(direction_obj.right, direction_obj)
				self.facing_direction = right
			self.skeleton.update(None, (self.isCollidingLeft or self.isCollidingRight))
			self.image = self.skeleton.getImage(self.skeleton.right_face_order)
			

		##END ANIMATION STUFF				
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
	#action definitions for all AI character objects
	ATTACK_TARGET = 0
	MOVE_FREELY = 1
	WAIT = 2

	def __init__(self, screen, images, starting_position, x_limits, dimsAndLims_obj):
		CharacterObject.__init__(self, screen, images, starting_position, x_limits, dimsAndLims_obj)
		self.action_counter = 0
		self.current_action = None
	
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
				move_speed /= dimsAndLims_obj.move_speed_limit_denom
			if self.x_movement_limit_left == None:				 
				self.pos = (self.pos[0] - move_speed, self.pos[1])
			elif self.x_movement_limit_left - dimsAndLims_obj.x_limit_test_pos < self.pos[0] - move_speed: 
				self.pos = (self.pos[0] - move_speed, self.pos[1])
			else: direction = None
		elif direction == right: 
			if self.isCollidingRight == True:
				move_speed /= dimsAndLims_obj.move_speed_limit_denom
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

		self.action_counter -= 1
		super(AICharacterObject, self).update(direction, left_side_collision_list, right_side_collision_list, bottom_collision_list, direction_obj, dimsAndLims_obj)	
	
	def decideAction(self, targets_list, interrupt_current_action, mid_screen_pos, direction_obj):
		if self.action_counter <= 0 or interrupt_current_action:			
			new_action = [None, None, None] #action, direction, target
			
			#determine next action
			attack_target_chance = 70
			move_freely_chance = 25
			wait_chance = 5
			
			outcome = None
			roll = randint(0, 99)
			if roll < attack_target_chance: outcome = self.ATTACK_TARGET
			elif roll >= attack_target_chance and roll < (attack_target_chance + move_freely_chance): outcome = self.MOVE_FREELY
			else: outcome = self.WAIT
			new_action[0] = outcome

			#if attack_target, choose target, find direction
			if outcome == self.ATTACK_TARGET:
				target_index = randint(0, len(targets_list)-1)
				if targets_list[target_index] == self.rect: target_index -= 1
				new_action[2] = targets_list[target_index]
				new_action[1] = direction_obj.right
				if targets_list[target_index].centerx <= self.rect.centerx: new_action[1] = direction_obj.left

			#determine direction of free movement
			if outcome == self.MOVE_FREELY:
				new_action[1] = direction_obj.right
				if mid_screen_pos <= self.rect.centerx:	new_action[1] = direction_obj.left
				
			self.current_action = new_action
			self.action_counter = 60

class PlayerObject(CharacterObject):	
	def __init__(self, screen, images, starting_position, x_limits, dimsAndLims_obj):
		CharacterObject.__init__(self, screen, images, starting_position, x_limits, dimsAndLims_obj)
	
	def update(self, direction, speed, left_side_collision_list, right_side_collision_list, bottom_collision_list, direction_obj, dimsAndLims_obj):		
		move_speed = speed
		left = direction_obj.left
		right = direction_obj.right
		player_left_only = direction_obj.player_left_only 
		player_right_only = direction_obj.player_right_only
		nudge_left = direction_obj.nudge_left
		nudge_right = direction_obj.nudge_right 


		if self.isCollidingLeft or self.isCollidingRight:
			move_speed /= dimsAndLims_obj.move_speed_limit_denom
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
		elif direction == nudge_left or direction == nudge_right:
			print "NUDGED!"
		super(PlayerObject, self).update(direction, left_side_collision_list, right_side_collision_list, bottom_collision_list, direction_obj, dimsAndLims_obj)


		# each NPC should make decisions on where to move to
		# each decided action should take some time to complete before the next decision is made
		# some outside actions should impact decisions (ie: interrupt or preempt them)

			#each decision should move the npc toward one ore more goals based on preference
			#there should be an element of randomness (ie: lack of rationality, don't always pick the decision with the highest preference)
