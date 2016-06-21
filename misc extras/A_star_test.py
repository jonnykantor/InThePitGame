import pygame, math, sys
from pygame.locals import *
from random import randint
from sys import argv
import A_star_min_heap as MH
import A_Star as AS

##Colors
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 100, 0)
ORANGE = (255, 164, 0)
RED = (255, 0, 0)
LIGHT_BLUE = (150, 180, 200)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
##/Colors

pygame.init()

class MainScreenMenu():
	def __init__(self, screen, items, width, height, extra_items=None, fill=BLACK):
		self.screen = screen
		self.screen_width = width
		self.screen_height = height
		self.fill = fill
		self.clock = pygame.time.Clock()
		self.items = items
		self.extra_items = extra_items
		self.labels = []		
		self.extra_labels = []
		#aesthetics
		
		self.font = pygame.font.SysFont("Arial", 30)
		self.font_color = ORANGE
		
		
		for i, item in enumerate(self.items):
			label = self.font.render(item, 1, self.font_color)
			width = label.get_rect().width
			height = label.get_rect().height
			posx = (self.screen_width/2) - (width/2)
			stack_height = len(items) * height
			posy = (self.screen_height/2) - (stack_height/2) + (i * height)
			button_rect = Rect(posx, posy, width, height)
			self.labels.append([item, label, (width, height), (posx, posy), button_rect])
		
		self.font = pygame.font.SysFont("Arial", 15)		
		
		
		for i, item in enumerate(self.extra_items):
			OFFSET = 10
			label = self.font.render(item, 1, WHITE, DARK_GREEN)
			width = label.get_rect().width
			height = label.get_rect().height
			posx = 0 + OFFSET
			if i == 0: posy = 0 + OFFSET
			else: posy = (self.extra_labels[i-1][2][1]*i) + OFFSET
			self.extra_labels.append([item, label, (width, height), (posx, posy)])
		
		self.font = pygame.font.SysFont("Arial", 30)
		self.font_color = ORANGE
		
	def execute_loop(self):
		
		isButtonDown = False
		rect_clickedOn = None
				
		isRunning = True		
		while isRunning:
			self.clock.tick(30)
			
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					isRunning = False
					sys.exit(0)
				if hasattr( event, 'key'):
					down = event.type == KEYDOWN		
					if event.key == K_ESCAPE: 
						isRunning = False
						sys.exit(0)
				
				if event.type == MOUSEMOTION: 
					m_x_pos, m_y_pos = event.pos
					for label_container in self.labels:						
						if label_container[4].collidepoint(m_x_pos, m_y_pos):							
							label_container[1] = self.font.render(label_container[0], 1, self.font_color, WHITE)							
						else: 							
							label_container[1] = self.font.render(label_container[0], 1, self.font_color) 						
				if event.type == MOUSEBUTTONDOWN:
					left_button, mid_button, right_button = pygame.mouse.get_pressed()
					if left_button: 
						isButtonDown = True
						m_x_pos, m_y_pos = event.pos						
						for label_container in self.labels:						
							if label_container[4].collidepoint(m_x_pos, m_y_pos):
								rect_clickedOn = label_container[4]								
								
					elif not left_button: isButtonDown = False
				
				if event.type == MOUSEBUTTONUP:
					if isButtonDown:
						left_button, mid_button, right_button = pygame.mouse.get_pressed()
						if not left_button:						
							isButtonDown = False						
							m_x_pos, m_y_pos = event.pos						
							for label_container in self.labels:						
								if label_container[4].collidepoint(m_x_pos, m_y_pos):
									if rect_clickedOn == label_container[4]:
										if label_container[0] == self.items[1]:
											isRunning = False
											sys.exit(0)
										if label_container[0] == self.items[0]:
											isRunning = False
					
					
					
					
			self.screen.fill(self.fill)
			for name, label, (width, height), (posx, posy), button_rect in self.labels:
				self.screen.blit(label, (posx, posy))
			for name, label, (width, height), (posx, posy) in self.extra_labels:
				self.screen.blit(label, (posx, posy))
			
			pygame.display.flip()
			

def drawBoard(inp_grid):
	#color squares
	for i in range(inp_grid.size):
		if inp_grid.grid_arr[i] == 1: pygame.draw.rect(screen, ORANGE, pygame.Rect((i%inp_grid.width)*inp_grid.cell_size, (i/inp_grid.width)*inp_grid.cell_size, inp_grid.cell_size, inp_grid.cell_size))
		elif inp_grid.grid_arr[i] == 2: pygame.draw.rect(screen, GREEN, pygame.Rect((i%inp_grid.width)*inp_grid.cell_size, (i/inp_grid.width)*inp_grid.cell_size, inp_grid.cell_size, inp_grid.cell_size))
		elif inp_grid.grid_arr[i] == 3: pygame.draw.rect(screen, RED, pygame.Rect((i%inp_grid.width)*inp_grid.cell_size, (i/inp_grid.width)*inp_grid.cell_size, inp_grid.cell_size, inp_grid.cell_size))
		elif inp_grid.grid_arr[i] == 4: pygame.draw.rect(screen, DARK_GREEN, pygame.Rect((i%inp_grid.width)*inp_grid.cell_size, (i/inp_grid.width)*inp_grid.cell_size, inp_grid.cell_size, inp_grid.cell_size))
		elif inp_grid.grid_arr[i] == 5: pygame.draw.rect(screen, LIGHT_BLUE, pygame.Rect((i%inp_grid.width)*inp_grid.cell_size, (i/inp_grid.width)*inp_grid.cell_size, inp_grid.cell_size, inp_grid.cell_size))
	#/color squares
	
	#draw gridlines
	for i in range(0, SCREEN_WIDTH, inp_grid.cell_size): pygame.draw.line(screen, WHITE, (i, 0), (i, SCREEN_HEIGHT), 2)
	for i in range(0, SCREEN_HEIGHT, inp_grid.cell_size): pygame.draw.line(screen, WHITE, (0, i), (SCREEN_WIDTH, i), 2)
	#/draw gridlines
			
if __name__ == "__main__":

	if len(argv) < 3:
		print "USAGE: A_star_test.py <width> <height> <cell-side size>"
		print "cells are square. For best results, make width and height multiples of the cell side size"
		exit()

	SCREEN_WIDTH = int(argv[1])
	SCREEN_HEIGHT = int(argv[2])
	CELL_SIZE = int(argv[3])

	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	screen_rect = screen.get_rect()
	clock = pygame.time.Clock()

	GRID = AS.GameGrid(SCREEN_WIDTH/CELL_SIZE, SCREEN_HEIGHT/CELL_SIZE, CELL_SIZE)

	PATHER = AS.PathFinder(GRID)

	#GRID.randomizeGrid(4, PATHER)
	#GRID.setGrid(PATHER, [((2, 5),(5, 2)) , ((1, 8),(2, 2)), ((5, 1),(3, 3))], (0, 0), (SCREEN_WIDTH/CELL_SIZE -1, SCREEN_HEIGHT/CELL_SIZE -1))
	
	#Main Menu Screen
	MM_TEXTUAL_ITEMS = ('Controls:', 
						'R: reset', 
						'N: repopulate grid', 
						'SPACE: find full solution', 
						'Right-Click: step through solution',
						'ESC: Back to Menu')
	MAIN_MENU_ITEMS = ('Start', 'Quit')
	MAIN_MENU = MainScreenMenu(screen, MAIN_MENU_ITEMS, SCREEN_WIDTH, SCREEN_HEIGHT, MM_TEXTUAL_ITEMS)
	MAIN_MENU.execute_loop()
	MAIN_MENU_ITEMS = ('Resume', 'Quit')
	MAIN_MENU = MainScreenMenu(screen, MAIN_MENU_ITEMS, SCREEN_WIDTH, SCREEN_HEIGHT, MM_TEXTUAL_ITEMS)
	#Main Menu Screen End
	
	print PATHER
	print GRID
	
	while 1:
		time_elapsed = clock.tick(30)
		screen.fill((0,0,0))	
		event_list = pygame.event.get()
		for event in event_list:
			#KEYPRESS EVENTS
			if event.type == pygame.QUIT: sys.exit(0)			
			if hasattr(event, 'key'):				
				down = event.type == KEYDOWN		
				if event.key == K_ESCAPE and not down: MAIN_MENU.execute_loop()					
				elif event.key == K_n and not down: #new layout
					GRID.randomizeGrid(4, PATHER)				
				elif event.key == K_SPACE and not down: #A* step					
					while not PATHER.finished: 
						AS.A_star_step(PATHER, GRID)				
				elif event.key == K_r and not down: #reset grid
					GRID.resetGrid(PATHER)				
			#MOUSEPRESS EVENTS
			if event.type == MOUSEMOTION: 
				m_x_pos, m_y_pos = event.pos
			elif event.type == MOUSEBUTTONUP:
				AS.A_star_step(PATHER, GRID)
			elif event.type == MOUSEBUTTONDOWN:	pass			
		
		
		
		drawBoard(GRID)
		
		#display new frame
		pygame.display.flip()