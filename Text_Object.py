import pygame
from Globals import *

class textObject(pygame.sprite.Sprite):
	def __init__(self, screen, text, duration, text_obj_type, font, font_color, font_size, position, back_color=None, colorkey_color=WHITE):
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