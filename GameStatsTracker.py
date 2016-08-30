import pygame
from Text_Object import *
from Globals import *

class GameStatsTracker (object):
	def __init__(	self, 
					starting_beer_level, 
					starting_security_level, 
					starting_points_amount,
					max_points_amount, 
					text_object_argument_list,
					colorkey_color,
					beer_bar_color,
					security_bar_color
					):
		"""
		text object argument list is:
			surface
			text for display
			duration
			textObject type
			all textObject types
			font
			font color
			font_size
			position
			background_color
			colorkey for alpha
			textObject argument vector
		"""
		self.t_o_a_l = text_object_argument_list
		self.update_necessary = False

		self.points_pos = self.t_o_a_l[8]
		self.beer_level_pos = (self.points_pos[0]-100, self.points_pos[1] - 50)
		self.security_level_pos = (self.points_pos[0]-100, self.points_pos[1] - 100)

		self.beer_level = starting_beer_level
		self.security_level = starting_security_level
		self.points_total = starting_points_amount
		self.bar_widths = 15
		
		self.security_bar_surface = pygame.Surface((100, self.bar_widths)).convert()
		self.security_bar_surface.set_alpha(200)
		self.security_bar_surface.set_colorkey(colorkey_color)
		self.security_bar_surface.fill(colorkey_color)
		self.security_bar_surface.fill(security_bar_color, ((0, 0), (self.security_level, self.bar_widths)))
		self.beer_bar_surface = pygame.Surface((100, self.bar_widths)).convert()
		self.beer_bar_surface.set_alpha(200)
		self.beer_bar_surface.set_colorkey(colorkey_color)
		self.beer_bar_surface.fill(colorkey_color)		
		self.beer_bar_surface.fill(beer_bar_color, ((0, 0), (self.beer_level, self.bar_widths)))

		self.beer_counter = 0
		self.beer_counter_limit = 10
		self.security_counter = 0
		self.security_counter_limit = 30
		
		self.max_points_amount = max_points_amount
		self.points_image_sprite = textObject(	self.t_o_a_l[0],
												self.t_o_a_l[1],
												self.t_o_a_l[2],
												self.t_o_a_l[3],
												self.t_o_a_l[4],
												self.t_o_a_l[5],
												self.t_o_a_l[6],
												self.t_o_a_l[7],
												self.t_o_a_l[8],
												self.t_o_a_l[9],
												self.t_o_a_l[10],
												self.t_o_a_l[11])
		self.stats_sprite_group = pygame.sprite.GroupSingle(self.points_image_sprite)

		self.colorkey_color = colorkey_color
		self.beer_bar_color = beer_bar_color
		self.security_bar_color = security_bar_color

	def update(self, beer_adjustment, security_adjustment, points_adjustment):
		
		if not beer_adjustment:
			self.beer_counter += 1
			if self.beer_counter > self.beer_counter_limit:
				self.beer_counter = 0
				beer_adjustment -= 1
		if beer_adjustment < 0:
			self.beer_bar_surface.fill(self.colorkey_color)
		if beer_adjustment:
			self.beer_level += beer_adjustment
			if self.beer_level > 100: self.beer_level = 100
			if self.beer_level < 0: self.beer_level = 0								
			self.beer_bar_surface.fill(self.beer_bar_color, ((0, 0), (self.beer_level, self.bar_widths)))
		
		if not security_adjustment:
			self.security_counter += 1
			if self.security_counter > self.security_counter_limit:
				self.security_counter = 0
				security_adjustment -= 1
		if security_adjustment < 0:
			self.security_bar_surface.fill(self.colorkey_color)
		if security_adjustment: 
			self.security_level += security_adjustment
			if self.security_level > 100: self.security_level = 100
			if self.security_level < 0: self.security_level = 0
			self.security_bar_surface.fill(self.security_bar_color, ((0, 0), (self.security_level, self.bar_widths)))
		
		if points_adjustment: 
			self.points_total += points_adjustment
			self.update_necessary = True

	def draw(self):
		
		if self.update_necessary:
			self.points_image_sprite = textObject(	self.t_o_a_l[0],
													str(self.points_total),
													self.t_o_a_l[2],
													self.t_o_a_l[3],
													self.t_o_a_l[4],
													self.t_o_a_l[5],
													self.t_o_a_l[6],
													self.t_o_a_l[7],
													self.t_o_a_l[8],
													self.t_o_a_l[9],
													self.t_o_a_l[10],
													self.t_o_a_l[11]) 
			self.stats_sprite_group.sprite = self.points_image_sprite
			self.update_necessary = False

		self.stats_sprite_group.draw(self.t_o_a_l[0])
		self.t_o_a_l[0].blit(self.security_bar_surface, self.security_level_pos)
		self.t_o_a_l[0].blit(self.beer_bar_surface, self.beer_level_pos)

	def getTotals(self):
		return self.beer_level, self.security_level, self.points_total