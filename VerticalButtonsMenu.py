import pygame, sys
from pygame.locals import *
from Globals import *
from Text_Object import *
from random import randint

class VerticalButtonsMenu(object):
	def __init__(	self,
					surface, 						#surface that menu will be blitted to
					text_for_buttons,				#text list, each item is the content of one button
					commands_for_buttons,			#integer list, each item corresponds to a command in the menu_commands object
					font,							#string name of a pygame.SysFont
					font_size,
					background_image,				#type is surface. Set to None to instead use background_fill_color
					background_fill_color, 			#the surface will be filled with this color background if there is no background image provided
					button_border_and_font_color, 	
					button_background_color,
					button_alpha_colorkey_color,	#take care that there is no overlap between the button and selected button colors
					button_border_size,				
					button_corner_radius, 
					button_stack_alignment,			#the stack is vertical, alignment is one of LEFT, RIGHT or CENTER
					is_button_size_equalized,		#if True, all buttons are set to the same size as the largest button (determined by size of the font image)
					selected_color_font_and_border, #font/border color for the button when the mouse is hovering over it
					selected_color_background,					
					non_interactive_text_object_args,							
					):		
		
		self.surface = surface
		self.surface_size = (self.surface.get_width(), self.surface.get_height())
		self.button_text_array = text_for_buttons
		self.commands = commands_for_buttons
		self.font = pygame.font.SysFont(font, font_size)
		self.background_color = background_fill_color
		self.button_border_and_font_color = button_border_and_font_color
		self.button_background_color = button_background_color
		self.button_alpha_colorkey_color = button_alpha_colorkey_color
		self.button_border_size = button_border_size
		self.button_corner_radius = button_corner_radius
		self.button_stack_alignment = button_stack_alignment		
		self.is_button_size_equalized = is_button_size_equalized
		self.selected_color_font_and_border = selected_color_font_and_border
		self.selected_color_background = selected_color_background
		self.non_int_elmnt_sprite_group = pygame.sprite.OrderedUpdates()

		#set up background image
		
		if background_image == None:			
			self.background = pygame.Surface((self.surface_size[0], self.surface_size[1]), pygame.SRCALPHA).convert()
			self.background.fill(self.background_color)
			self.background.set_alpha(200)
		else:
			self.background = background_image

		#instantiate text_objects for the creation of non-interactive elements		
		for args in non_interactive_text_object_args:
			self.non_int_elmnt_sprite_group.add(	textObject(	self.surface,	
																args[0],	#text = string of text to be displayed
																args[1],	#duration = integer
																args[2],	#text_obj_type = see Globals.py for various types
																args[3], 	#all text_obj types
																args[4],	#font = string indicating the name of a valid font for pygame.font.SysFont
																args[5],	#font_color = see Globals.py for various colors
																args[6],	#font_size = integer
																args[7],	#position = (x, y) integer tuple
																args[8],	#back_color = default None, otherwise used where necessary
																args[9],	#colorkey_color = used for alpha adjustments
																args[10],))	#argument_vector: should be a list of whatever extra arguments are needed	




		#instantiate font surfaces for the creation of buttons
		self.largest_height = 0
		self.largest_width = 0

		self.font_images = []
		self.selected_font_images = []		
		for text in self.button_text_array:
			#make font surface
			new_font_image = self.font.render(text, False, button_border_and_font_color).convert()
			new_selected_font_image = self.font.render(text, False, selected_color_font_and_border).convert()
			
			self.font_images.append(new_font_image)
			self.selected_font_images.append(new_selected_font_image)			
			curr_height = new_font_image.get_height()
			curr_width = new_font_image.get_width()			
			if is_button_size_equalized:
				if curr_width > self.largest_width: self.largest_width = curr_width
				if curr_height > self.largest_height: self.largest_height = curr_height
		
		#instantiate buttons using font surfaces
		self.total_height = 0
		self.button_images = []
		self.selected_button_images = []
		size = (self.largest_width, self.largest_height)
		
		for index, font_image in enumerate(self.font_images):
			if not is_button_size_equalized: size = font_image.get_size()
			#make button surfaces, both unselected and selected colored
			new_button_image 			= makeSpeechBubble(	size[0], size[1], button_corner_radius, 
															False, True, 
															button_background_color, 
															button_border_and_font_color, 
															button_border_size, 
															button_alpha_colorkey_color)
			new_selected_button_image 	= makeSpeechBubble(	size[0], size[1], button_corner_radius, 
															False, True, 
															selected_color_background, 
															selected_color_font_and_border, 
															button_border_size, 
															button_alpha_colorkey_color)
			#draw font surfaces onto button surfaces
			blit_position = (font_image.get_rect().left + button_corner_radius, font_image.get_rect().top + button_corner_radius)			
			if is_button_size_equalized:
				blit_x_pos = font_image.get_rect().left + button_corner_radius + (self.largest_width/2 - font_image.get_width()/2)
				blit_y_pos = font_image.get_rect().top + button_corner_radius
				blit_position = (blit_x_pos, blit_y_pos)
			
			new_button_image.blit(font_image, blit_position)
			new_selected_button_image.blit(self.selected_font_images[index], blit_position)
			self.button_images.append([new_button_image, new_button_image.get_rect(), index])
			self.selected_button_images.append([new_selected_button_image, new_selected_button_image.get_rect(), index])
			self.total_height += new_button_image.get_rect().height
		#we now have a list of button+font surfaces, and their rects

	def activateMenu(self, menu_commands, direction_obj):
		"""display the menu, interupting other game functions, and running its own loop"""

		LEFT = direction_obj.left
		RIGHT = direction_obj.right 
		CENTER = direction_obj.center

		self.surface_copy = self.surface.copy()
		self.surface.blit(self.background, (0, 0))
		m_x_pos = m_y_pos = None
		stored_m_x_pos = stored_m_y_pos = None
		command = None
		while 1:
			#clock tick
			time_elapsed = CLOCK.tick(30)

			#handle events
			event_list = pygame.event.get()
			for event in event_list:
				if event.type == pygame.QUIT: sys.exit(0)		
				if hasattr(event, 'key'):
					down = event.type == KEYDOWN							
					if event.key == K_ESCAPE and not down: return

					if event.key == K_c and not down:
						pass
						#if self.button_stack_alignment == LEFT:
						#	self.button_stack_alignment = CENTER
						#elif self.button_stack_alignment == CENTER:
						#	self.button_stack_alignment = RIGHT
						#elif self.button_stack_alignment == RIGHT:
						#	self.button_stack_alignment = LEFT

				if event.type == MOUSEMOTION:
					m_x_pos, m_y_pos = event.pos
				if event.type == MOUSEBUTTONDOWN:
					stored_m_x_pos, stored_m_y_pos = event.pos
				if event.type == MOUSEBUTTONUP:
					m_x_pos, m_y_pos = event.pos
					command = self.mouseButtonUpHandler((m_x_pos, m_y_pos), (stored_m_x_pos, stored_m_y_pos))

			#Execute button command
			if command == menu_commands.QUIT: sys.exit(0)
			elif command == menu_commands.BACK_TO_GAME: return menu_commands.BACK_TO_GAME
			elif command == menu_commands.RESTART: return menu_commands.RESTART	

			#update visuals
			##Background:
			self.surface.blit(self.surface_copy, (0, 0))
			self.surface.blit(self.background, (0, 0))

			##Buttons:
			placement_position_x = 0
			placement_position_y = 0
			if self.button_stack_alignment == LEFT: placement_position_x = 0
			elif self.button_stack_alignment == RIGHT: placement_position_x = self.surface.get_width()-1
			elif self.button_stack_alignment == CENTER: placement_position_x = self.surface.get_width()/2			

			##Elements:
			y_offset = 0
			for elmnt in self.non_int_elmnt_sprite_group:
				if self.button_stack_alignment == CENTER: elmnt.rect.midtop = (placement_position_x, placement_position_y + y_offset)
				elif self.button_stack_alignment == RIGHT: elmnt.rect.topright = (placement_position_x, placement_position_y + y_offset)
				elif self.button_stack_alignment == LEFT: elmnt.rect.topleft = (placement_position_x, placement_position_y + y_offset)
				y_offset += elmnt.rect.height
			self.non_int_elmnt_sprite_group.draw(self.surface)			

			y_offset += 0	#(0 + (self.surface.get_height() - (self.total_height + len(self.button_images) * 5))/2)
			for button in self.button_images:
				if m_x_pos != None:
					if button[1].collidepoint(m_x_pos, m_y_pos):
						button = self.selected_button_images[button[2]]				
				if self.button_stack_alignment == LEFT: button[1].topleft = (placement_position_x, placement_position_y + y_offset)
				elif self.button_stack_alignment == RIGHT: button[1].topright = (placement_position_x, placement_position_y + y_offset)
				elif self.button_stack_alignment == CENTER: button[1].midtop = (placement_position_x, placement_position_y + y_offset)
				y_offset += (5 + button[1].height)
				self.surface.blit(button[0], button[1].topleft)

			#draw
			pygame.display.flip()

	def mouseButtonUpHandler(self, cur_pos, stored_pos):
		command = None
		for button in self.button_images:
			if button[1].collidepoint(cur_pos[0], cur_pos[1]) and button[1].collidepoint(stored_pos[0], stored_pos[1]):
				command = self.commands[button[2]]

		return command


	def resizeAllButtonWidths(self, new_width):
		"""
		remakes all buttons, repopulates self.largest_* variables, and self.button_images and self.selected_button_images, along with self.total_height
		will not attempt to equalize button images, but if equalization is set to True will re-set largest_width to provided size[0] value
		note: uses existing font images, as font images are not resized.
		"""
		self.total_height = 0
		self.button_images = []
		self.selected_button_images = []
		self.largest_width = new_width
		size = (self.largest_width, self.largest_height)
		for index, font_image in enumerate(self.font_images):
			if not self.is_button_size_equalized: size = font_image.get_size()
			#make button surfaces, both unselected and selected colored
			new_button_image 			= makeSpeechBubble(	size[0], size[1], self.button_corner_radius, 
															False, True, 
															self.button_background_color, 
															self.button_border_and_font_color, 
															self.button_border_size, 
															self.button_alpha_colorkey_color)
			new_selected_button_image 	= makeSpeechBubble(	size[0], size[1], self.button_corner_radius, 
															False, True, 
															self.selected_color_background, 
															self.selected_color_font_and_border, 
															self.button_border_size, 
															self.button_alpha_colorkey_color)
			#draw font surfaces onto button surfaces
			blit_position = (font_image.get_rect().left + self.button_corner_radius, font_image.get_rect().top + self.button_corner_radius)			
			if self.is_button_size_equalized:
				blit_x_pos = font_image.get_rect().left + self.button_corner_radius + (self.largest_width/2 - font_image.get_width()/2)
				blit_y_pos = font_image.get_rect().top + self.button_corner_radius
				blit_position = (blit_x_pos, blit_y_pos)
			
			new_button_image.blit(font_image, blit_position)
			new_selected_button_image.blit(self.selected_font_images[index], blit_position)
			self.button_images.append([new_button_image, new_button_image.get_rect(), index])
			self.selected_button_images.append([new_selected_button_image, new_selected_button_image.get_rect(), index])
			self.total_height += new_button_image.get_rect().height		

	def createNewButton(self, text):
		"""
		To be used to add a new button to the existing button menu, at the specified index.
		If self.is_button_size_equalized == True, addNewButton will use the self.largest_width to size the returned surfaces
		returns 2 button images (with font images blitted onto them), and 2 font images
		If size is larger than existing buttons and button size is set to be equalized, will attempt to re-add all existing buttons in order
		using the new size, first.
		"""

		#get font image
		new_font_image = self.font.render(text, False, self.button_border_and_font_color).convert()
		new_selected_font_image = self.font.render(text, False, self.selected_color_font_and_border).convert()
		#equalize widths if necessary
		new_width = new_font_image.get_width()
		if self.is_button_size_equalized:
			if new_width > self.largest_width:
				self.resizeAllButtonWidths(new_width)
				self.largest_width = new_width
			else: new_width = self.largest_width
		#create new button image
		size = (new_width, new_font_image.get_height())
		new_button_image 			= makeSpeechBubble(	size[0], size[1], self.button_corner_radius, 
															False, True, 
															self.button_background_color, 
															self.button_border_and_font_color, 
															self.button_border_size, 
															self.button_alpha_colorkey_color)
		new_selected_button_image 	= makeSpeechBubble(	size[0], size[1], self.button_corner_radius, 
															False, True, 
															self.selected_color_background, 
															self.selected_color_font_and_border, 
															self.button_border_size, 
															self.button_alpha_colorkey_color)
		#draw font surfaces onto button surfaces
		blit_position = (new_font_image.get_rect().left + self.button_corner_radius, new_font_image.get_rect().top + self.button_corner_radius)			
		if self.is_button_size_equalized:
			blit_x_pos = new_font_image.get_rect().left + self.button_corner_radius + (self.largest_width/2 - new_font_image.get_width()/2)
			blit_y_pos = new_font_image.get_rect().top + self.button_corner_radius
			blit_position = (blit_x_pos, blit_y_pos)
		
		new_button_image.blit(new_font_image, blit_position)
		new_selected_button_image.blit(new_selected_font_image, blit_position)

		return new_button_image, new_selected_button_image, new_font_image, new_selected_font_image

	def addNewButton(self, text, index, command):
		"""
		text will be passed to createNewButton
		resulting images will be inserted at index to self.button_images and self.selected_button_images
		insertion will 'bump up' the list order (ie: index 1 will shift current entry at 1 up to 2, etc.)
		if index == -1, images will be apended to end of respective lists 
		index entries larger than size of lists will also be appended to the end of the list			
		"""
		new_button_image, new_selected_button_image, new_font_image, new_selected_font_image = self.createNewButton(text)

		#index is either: less than -1: do nothing, -1 or >= size of list: append to end, 0-(size of list - 1): insertion
		height_to_add = 0
		if index == -1 or index >= len(self.button_images):
			#append		
			height_to_add = new_button_image.get_rect().height
			stored_index = len(self.button_images)
			self.button_images.append([new_button_image, new_button_image.get_rect(), stored_index])
			self.selected_button_images.append([new_selected_button_image, new_selected_button_image.get_rect(), stored_index])				
			self.font_images.append(new_font_image)
			self.selected_font_images.append(new_selected_font_image)
			self.button_text_array.append(text)
			self.commands.append(command)

		elif index >= 0 and index < len(self.button_images):
			#insert
			height_to_add = new_button_image.get_rect().height
			self.button_images = 	self.button_images[:index] + [
									[new_button_image, new_button_image.get_rect(), index]] + [
									[image, rect, old_index+1] for image, rect, old_index in self.button_images[index:]]

			self.selected_button_images = 	self.selected_button_images[:index] + [
											[new_selected_button_image, new_selected_button_image.get_rect(), index]] + [
											[image, rect, old_index+1] for image, rect, old_index in self.selected_button_images[index:]] 

			self.font_images = self.font_images[:index] + [new_font_image] + self.font_images[index:]
			self.selected_font_images = self.selected_font_images[:index] + [new_selected_font_image] + self.selected_font_images[index:]
			self.button_text_array = self.button_text_array[:index] + [text] + self.button_text_array[index:]
			self.commands = self.commands[:index] + [command] + self.commands[index:]
		self.total_height += height_to_add
	def removeButtonAtIndex(self, index):
		"""
		Entries must be removed from button_image lists, font_image lists, text list, commands list
		Also, buttons may be resized if equalization is set to true, dependent on remaining font_image widths
		Finally the total_height should be reduced by the height of the removed button image.
		If index == -1, or index is >= len(self.button_images), will remove last button in the list (the bottom button)
		If index < -1 nothing will happen
		If index is > -1 and < len(self.button_images) the indices of the remaining images will be decremented
		"""
		if len(self.button_images) == 0: return

		height_for_removal = 0
		if index == -1 or index >= len(self.button_images):
			#remove from end
			height_for_removal = self.button_images[-1][1].height
			self.button_images.pop()
			self.selected_button_images.pop()
			self.font_images.pop()
			self.selected_font_images.pop()
			self.button_text_array.pop()
			self.commands.pop()

		elif index > -1 and index < len(self.button_images):
			height_for_removal = self.button_images[index][1].height
			self.button_images = 	self.button_images[:index] + [
									[image, rect, old_index-1] for image, rect, old_index in self.button_images[index+1:]]

			self.selected_button_images = 	self.selected_button_images[:index] + [
											[image, rect, old_index-1] for image, rect, old_index in self.selected_button_images[index+1:]] 

			self.font_images = self.font_images[:index] + self.font_images[index+1:]
			self.selected_font_images = self.selected_font_images[:index] + self.selected_font_images[index+1:]
			self.button_text_array = self.button_text_array[:index] + self.button_text_array[index+1:]
			self.commands = self.commands[:index] + self.commands[index+1:]
		if self.is_button_size_equalized:
			find_largest_width = 0
			for font_image in self.font_images:
				if font_image.get_width() > find_largest_width:
					find_largest_width = font_image.get_width()
			if find_largest_width < self.largest_width:
				self.largest_width = find_largest_width
				self.resizeAllButtonWidths(find_largest_width)
		self.total_height -= height_for_removal

	def replaceButtonAtIndex(self, new_button_text, index_for_replacement, new_button_command):
		"""
		if index_for_replacement < -1, nothing will happen. 
		If index == -1 or index >= len(self.button_images), last button in the stack will be replaced
		Otherwise the button at index will be replaced
		"""
		self.removeButtonAtIndex(index_for_replacement)
		self.addNewButton(new_button_text, index_for_replacement, new_button_command)