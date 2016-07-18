import pygame
from Globals import *

class textObject(pygame.sprite.Sprite):
	def __init__(self, screen, text, duration, text_obj_type, font, font_color, font_size, position, back_color=None, colorkey_color=WHITE, argument_vector=None):
		"""
		screen = main surface
		text = string of text to be displayed
		duration = integer
		text_obj_type = see Globals.py for various types
		font = string indicating the name of a valid font for pygame.font.SysFont
		font_color = see Globals.py for various colors
		font_size = integer
		position = (x, y) integer tuple
		back_color = default None, otherwise used where necessary
		colorkey_color = used for alpha adjustments
		argument_vector has been included for later use: should be a list of whatever extra arguments are needed for a specific type 
		"""

		pygame.sprite.Sprite.__init__(self)		
		self.text_obj_type = text_obj_type
		self.screen = screen
		self.font = pygame.font.SysFont(font, font_size)
			
		#This is the fading-points properties specification
		if self.text_obj_type == POINTS_FADING:
			self.font_image = self.font.render(text, False, back_color).convert()				
			self.rect = self.font_image.get_rect()
			size = (self.rect.right + 6, self.rect.bottom + 6)
			self.image = pygame.Surface(size, pygame.SRCALPHA).convert()		
			self.image.fill(colorkey_color) #for transparency, white will be the colorkey here
			self.image.blit(self.font_image, self.rect.topleft)
			self.image.blit(self.font_image, (self.rect.left+6, self.rect.top))
			self.image.blit(self.font_image, (self.rect.left, self.rect.top+6))
			self.image.blit(self.font_image, (self.rect.left+6, self.rect.top+6))
			self.font_image = self.font.render(text, False, font_color).convert()
			self.image.blit(self.font_image, (self.rect.left+3, self.rect.top+3))
			self.image.set_colorkey(colorkey_color)

		if self.text_obj_type == SPEECH_BUBBLE:
			self.text_array = text.split()
			self.lines_array = []
			line = ''
			total = 0
			for index, word in enumerate(self.text_array):
				if total + len(word) < 20:
					total+= len(word) + 1
					if index == (len(self.text_array) - 1): line += word
					else: line += (word + ' ')
				else:
					self.lines_array.append(line)
					line = word + ' '
					total = 0
			if len(line) > 0:
				self.lines_array.append(line)

			#now have a list of lines, comprised of words such that the total 
			#line length is at most 20 characters including whitespace
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

			self.image = makeSpeechBubble(width, height, radius, False)
			self.rect = self.image.get_rect()
			prev_surface_height = 0
			for index, text_surface_atribs in enumerate(self.line_surfaces):
				self.image.blit(text_surface_atribs[0], (self.rect.left + radius, self.rect.top + radius + prev_surface_height))
				prev_surface_height += text_surface_atribs[1][1]
			self.image.set_colorkey(colorkey_color)
			



		self.rect = self.rect.move(position)		
		self.rect.center = position		
		self.font_color = font_color
		self.font_size = font_size
		self.back_color = back_color
		self.duration = duration
		
		
		
	def update(self):
		
		#This is the fading-points behavior specification
		if self.text_obj_type == POINTS_FADING:			
			self.image.set_alpha(self.image.get_alpha()-10)
			self.rect.top = self.rect.top - 5
			self.duration -= 1

		if self.text_obj_type == SPEECH_BUBBLE:
			self.duration -= 1
			if self.duration < 10: self.image.set_alpha(self.image.get_alpha()-25)	

def makeSpeechBubble(width, height, radius, isLeftOriented, background_color=WHITE, border_color=BLACK, border_size=5, colorkey_color=LIGHT_BLUE):
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
	size = (width+radius*2+border_size/2, height+radius*3+border_size/2)
	image = pygame.Surface(size, pygame.SRCALPHA).convert()
	image.fill(colorkey_color)	
	pygame.draw.circle(image, border_color, (radius, radius), radius, 0)
	pygame.draw.circle(image, background_color, (radius, radius), radius-border_size, 0)
	pygame.draw.circle(image, border_color, (radius+width, radius), radius, 0)
	pygame.draw.circle(image, background_color, (radius+width, radius), radius-border_size, 0)		
	pygame.draw.circle(image, border_color, (radius, radius+height), radius, 0)
	pygame.draw.circle(image, background_color, (radius, radius+height), radius-border_size, 0)		
	pygame.draw.circle(image, border_color, (radius+width, radius+height), radius, 0)
	pygame.draw.circle(image, background_color, (radius+width, radius+height), radius-border_size, 0)
	pygame.draw.rect(image, background_color, ((radius, radius), (width, height)), 0)
	pygame.draw.rect(image, background_color, ((0, radius), (radius, height)), 0)
	pygame.draw.rect(image, background_color, ((radius, 0), (width, radius)), 0)
	pygame.draw.rect(image, background_color, ((width+radius, radius), (radius, height)), 0)
	pygame.draw.rect(image, background_color, ((radius, height+radius), (width, radius)), 0)		
	pygame.draw.line(image, border_color, (radius, border_size/2), (width+radius, border_size/2), border_size)
	pygame.draw.line(image, border_color, (width+(2*radius) - border_size/2, radius), (width+(2*radius) - border_size/2, radius+height), border_size)
	pygame.draw.line(image, border_color, (border_size/2, radius-1), (border_size/2, height+radius), border_size)
	pygame.draw.line(image, border_color, (radius-1, height+(2*radius) - border_size/2), (width+radius, height+(2*radius) - border_size/2), border_size)
	if isLeftOriented:
			pygame.draw.polygon(image, background_color, [(radius, height + 2*radius - border_size),(radius, height + 3*radius),(2*radius, height + 2*radius - border_size)], 0)
			pygame.draw.line(image, border_color, (radius, height + 2*radius - border_size), (radius, height + 3*radius), border_size)
			pygame.draw.line(image, border_color, (radius, height + 3*radius), (2*radius, height + 2*radius - border_size/2), border_size)
	else:
		pygame.draw.polygon(image, background_color, [(width, height + 2*radius - border_size),(width + radius, height + 3*radius),(width + radius, height + 2*radius - border_size)], 0)
		pygame.draw.line(image, border_color, (width + radius, height + 2*radius - border_size), (width+ radius, height + 3*radius), border_size)
		pygame.draw.line(image, border_color, (width + radius, height + 3*radius), (width, height + 2*radius - border_size/2), border_size)
	image.set_colorkey(LIGHT_BLUE)

	return image	