import pygame, sys
from pygame.locals import *
from Globals import *
from Text_Object import makeSpeechBubble

class VerticalButtonsMenu(object):
	def __init__(	self,
					surface, 						#surface that menu will be blitted to
					text_for_buttons,				#text list, each item is the content of one button
					commands_for_buttons,			#integer list, each item corresponds to a command in Globals
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
					title_text=None,
					title_text_size=100,
					title_text_font="impact",
					title_text_color=BLACK,
					is_title_text_above_buttons=True):		
		
		self.surface = surface
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
		self.title_text_image = None

		#set up background image
		
		if background_image == None:			
			self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA).convert()
			self.background.fill(self.background_color)
			self.background.set_alpha(200)
		else:
			self.background = background_image

		#instantiate font surfaces for the creation of buttons
		largest_height = 0
		largest_width = 0
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
				if curr_width > largest_width: largest_width = curr_width
				if curr_height > largest_height: largest_height = curr_height
		
		#instantiate buttons using font surfaces
		self.total_height = 0
		self.button_images = []
		self.selected_button_images = []
		size = (largest_width, largest_height)
		for index, font_image in enumerate(self.font_images):
			if not is_button_size_equalized: size = font_image.get_size()
			#make button surfaces, both unselected and selected colored
			new_button_image 			= makeSpeechBubble(	size[0], 
															size[1], 
															button_corner_radius, 
															False, 
															True, 
															button_background_color, 
															button_border_and_font_color, 
															button_border_size, 
															button_alpha_colorkey_color)
			new_selected_button_image 	= makeSpeechBubble(	size[0], 
															size[1], 
															button_corner_radius, 
															False, 
															True, 
															selected_color_background, 
															selected_color_font_and_border, 
															button_border_size, 
															button_alpha_colorkey_color)
			#draw font surfaces onto button surfaces
			blit_position = (font_image.get_rect().left + button_corner_radius, font_image.get_rect().top + button_corner_radius)			
			if is_button_size_equalized:
				blit_x_pos = font_image.get_rect().left + button_corner_radius + (largest_width/2 - font_image.get_width()/2)
				blit_y_pos = font_image.get_rect().top + button_corner_radius
				blit_position = (blit_x_pos, blit_y_pos)
			
			new_button_image.blit(font_image, blit_position)
			new_selected_button_image.blit(self.selected_font_images[index], blit_position)
			self.button_images.append([new_button_image, new_button_image.get_rect(), index])
			self.selected_button_images.append([new_selected_button_image, new_selected_button_image.get_rect(), index])
			self.total_height += new_button_image.get_rect().height
		#we now have a list of button+font surfaces, and their rects

	def activateMenu(self):
		"""display the menu, interupting other game functions, and running its own loop"""
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

				if event.type == MOUSEMOTION:
					m_x_pos, m_y_pos = event.pos
				if event.type == MOUSEBUTTONDOWN:
					stored_m_x_pos, stored_m_y_pos = event.pos
				if event.type == MOUSEBUTTONUP:
					m_x_pos, m_y_pos = event.pos
					command = self.mouseButtonUpHandler((m_x_pos, m_y_pos), (stored_m_x_pos, stored_m_y_pos))

			if command == QUIT: sys.exit(0)
			elif command == BACK_TO_GAME: break	

			#update visuals
			placement_position_x = 0
			placement_position_y = 0
			if self.button_stack_alignment == LEFT: placement_position_x = 0
			elif self.button_stack_alignment == RIGHT: placement_position_x = self.surface.get_width()-1
			elif self.button_stack_alignment == CENTER: placement_position_x = self.surface.get_width()/2			

			y_offset = 0 + (self.surface.get_height() - (self.total_height + len(self.button_images) * 5))/2
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

