import pygame
from Globals import *

class textObject(pygame.sprite.Sprite):
	def __init__(	self, 					
					screen, 				#screen = main surface
					text, 					#text = string of text to be displayed
					duration, 				#duration = integer
					text_obj_type, 			#text_obj_type = see Globals.py for various types
					all_txt_obj_types,		#container of all text type index definitions
					font, 					#font = string indicating the name of a valid font for pygame.font.SysFont
					font_color, 			#font_color = see Globals.py for various colors
					font_size, 				#font_size = integer
					position, 				#position = (x, y) integer tuple
					back_color, 			#back_color = default None, otherwise used where necessary
					colorkey_color, 		#colorkey_color = used for alpha adjustments
					argument_vector			#argument_vector has been included for later use: should be a list of whatever extra arguments are needed for a specific type
				):
		"""		
		Intended to handle all textual elements more complex than simple pygame font surfaces
		"""

		pygame.sprite.Sprite.__init__(self)		
		self.text_obj_type = text_obj_type
		self.screen = screen
		self.font = pygame.font.SysFont(font, font_size)
		self.all_txt_obj_types = all_txt_obj_types

		self.argument_vector = argument_vector
			
		#This is the fading-points properties specification
		'''!!! POINTS_FADING argument vector layout: [isFading, isMoving, isTemporary]'''
		if self.text_obj_type == self.all_txt_obj_types.POINTS_FADING:
			self.font_image = self.font.render(text, False, back_color).convert()				
			self.rect = self.font_image.get_rect()
			size = (self.rect.right + 6, self.rect.bottom + 6)
			self.image = pygame.Surface(size, pygame.SRCALPHA).convert()		
			self.image.fill(colorkey_color) #for transparency, white will be the colorkey here
			
			self.image.blit(self.font_image, self.rect.topleft) 					#left-top corner
			self.image.blit(self.font_image, (self.rect.left+6, self.rect.top)) 	#right-top corner
			self.image.blit(self.font_image, (self.rect.left+3, self.rect.top)) 	#top middle
			self.image.blit(self.font_image, (self.rect.left, self.rect.top+6))		#left-bottom corner
			self.image.blit(self.font_image, (self.rect.left+6, self.rect.top+6))	#right-bottom corner
			self.image.blit(self.font_image, (self.rect.left+3, self.rect.top+6))	#bottom middle
			self.image.blit(self.font_image, (self.rect.left, self.rect.top+3))		#left middle
			self.image.blit(self.font_image, (self.rect.left+6, self.rect.top+3))		#right middle

			self.font_image = self.font.render(text, False, font_color).convert()
			self.image.blit(self.font_image, (self.rect.left+3, self.rect.top+3))
			self.image.set_colorkey(colorkey_color)

		#This is the speech bubble properties specification		
		'''!!! Speech Bubble argument vector layout [isLeftOriented, isButton, borderSize, max_line_length, isJustified] !!!'''
		if self.text_obj_type == self.all_txt_obj_types.SPEECH_BUBBLE:
			self.lines_array = wrap_text(text, argument_vector[3])
		
			#now create font surfaces from each line of wrapped text
			self.line_surfaces = []
			height = 0
			width = 0
			for text_line in self.lines_array:
				font_image = self.font.render(text_line, False, font_color).convert()
				size = font_image.get_size()
				self.line_surfaces.append([font_image, size])
				height += size[1]
				if size[0] > width: width = size[0]
				
			radius = height/(len(self.line_surfaces)+1)

			self.image = makeSpeechBubble(width, height, radius, self.argument_vector[0], self.argument_vector[1], back_color, font_color, self.argument_vector[2], colorkey_color)
			self.rect = self.image.get_rect()
			prev_surface_height = 0
			for index, line_surface in enumerate(self.line_surfaces):
				x_pos = self.rect.left				
				if argument_vector[4]: x_pos = self.rect.centerx - line_surface[1][0]/2 - radius
				self.image.blit(line_surface[0], (x_pos + radius, self.rect.top + radius + prev_surface_height))
				prev_surface_height += line_surface[1][1]
			self.image.set_colorkey(colorkey_color)
		
		self.rect = self.rect.move(position)		
		self.rect.center = position		
		self.font_color = font_color
		self.font_size = font_size
		self.back_color = back_color
		self.duration = duration		
		
	def update(self):
		
		#This is the fading-points behavior specification
		if self.text_obj_type == self.all_txt_obj_types.POINTS_FADING:			
			if self.argument_vector[0] == True: self.image.set_alpha(self.image.get_alpha()-10)
			if self.argument_vector[1] == True: self.rect.top = self.rect.top - 5
			if self.argument_vector[2] == True: self.duration -= 1

		if self.text_obj_type == self.all_txt_obj_types.SPEECH_BUBBLE:
			self.duration -= 1
			if self.duration < 10: self.image.set_alpha(self.image.get_alpha()-25)	

def wrap_text(text, length_limit):
	"""
	takes an input string and returns an array of lines of text with each line
	containing fewer characters (including white-space) than the length_limit
	"""
	text_split = text.split()
	lines_array = []
	line = ''
	total = 0
	for index, word in enumerate(text_split):
		word_len = len(word)
		if total + word_len < length_limit:
			total += word_len + 1
			if index == (len(text_split) - 1): line += word
			else: line += (word + ' ')
		else:			
			lines_array.append(line)
			line = word + ' '
			total = 0 + word_len + 1
	line_length = len(line)
	if line_length > 0:		
		lines_array.append(line) 
	return lines_array

def makeSpeechBubble(width, height, radius, isLeftOriented, isButton, background_color, border_color, border_size, colorkey_color):
	"""
	Takes the width/height/radius arguments and returns a surface with a speech bubble drawn to it
	default background color is white, border color is black, colorkey is light blue, border size is 5
	isLeftOriented determines the bubble-pointer (ie: if the speaker is to the left of the bubble, isLeftOriented = True)

	in short: 
	draws 8 cirlces (arcs were returning strange graphical glitches), first 4 of border color, latter 4 of background color
	then draws 5 rectangles (could be cut down to three easily enough) for the background of the bubble
	then draws lines for the border of the rectangles
	then draws a polygon for the speech triangle direction indicator (ie: who is talking)
	then draws lines for the borders of the polygon
	"""
	radius_adjustment_button_dependent = 3
	if isButton: radius_adjustment_button_dependent = 2
	size = (width+radius*2+border_size/2, height+radius*radius_adjustment_button_dependent+border_size/2)
	image = pygame.Surface(size, pygame.SRCALPHA).convert()
	image.fill(colorkey_color)	

	#corner circles, 4 for interior, 4 for border
	pygame.draw.circle(image, border_color, (radius, radius), radius, 0)
	pygame.draw.circle(image, background_color, (radius, radius), radius-border_size, 0)
	pygame.draw.circle(image, border_color, (radius+width, radius), radius, 0)
	pygame.draw.circle(image, background_color, (radius+width, radius), radius-border_size, 0)		
	pygame.draw.circle(image, border_color, (radius, radius+height), radius, 0)
	pygame.draw.circle(image, background_color, (radius, radius+height), radius-border_size, 0)		
	pygame.draw.circle(image, border_color, (radius+width, radius+height), radius, 0)
	pygame.draw.circle(image, background_color, (radius+width, radius+height), radius-border_size, 0)

	#interior rects
	pygame.draw.rect(image, background_color, ((radius, 0), (width, height + 2*radius)), 0)
	pygame.draw.rect(image, background_color, ((0, radius), (width + 2*radius, height)), 0)			

	#border lines for rects
	pygame.draw.line(image, border_color, (radius, border_size/2), (width+radius, border_size/2), border_size)
	pygame.draw.line(image, border_color, (width+(2*radius) - border_size/2, radius), (width+(2*radius) - border_size/2, radius+height), border_size)
	pygame.draw.line(image, border_color, (border_size/2, radius-1), (border_size/2, height+radius), border_size)
	pygame.draw.line(image, border_color, (radius-1, height+(2*radius) - border_size/2), (width+radius, height+(2*radius) - border_size/2), border_size)

	#speech bubble direction indicator if necessary
	if (isLeftOriented == True) and not (isButton):
		pygame.draw.polygon(image, background_color, [(radius, height + 2*radius - border_size),(radius, height + 3*radius),(2*radius, height + 2*radius - border_size)], 0)
		pygame.draw.line(image, border_color, (radius, height + 2*radius - border_size), (radius, height + 3*radius), border_size)
		pygame.draw.line(image, border_color, (radius, height + 3*radius), (2*radius, height + 2*radius - border_size/2), border_size)
	elif (isLeftOriented == False) and not (isButton): #therefore is right-oriented
		pygame.draw.polygon(image, background_color, [(width, height + 2*radius - border_size),(width + radius, height + 3*radius),(width + radius, height + 2*radius - border_size)], 0)
		pygame.draw.line(image, border_color, (width + radius, height + 2*radius - border_size), (width+ radius, height + 3*radius), border_size)
		pygame.draw.line(image, border_color, (width + radius, height + 3*radius), (width, height + 2*radius - border_size/2), border_size)
	image.set_colorkey(colorkey_color)

	return image	