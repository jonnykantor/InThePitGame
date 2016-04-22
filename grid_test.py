import pygame, math, sys
from pygame.locals import *
from random import randint
from sys import argv
import A_star_min_heap as MH
import A_Star as AS

##Colors
GREEN = (0, 255, 0)
DARK_GREEN = (0, 100, 0)
ORANGE = (255, 164, 0)
RED = (255, 0, 0)
LIGHT_BLUE = (150, 180, 200)
WHITE = (255, 255, 255)
##/Colors

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
	for i in range(0, SCREEN_WIDTH, inp_grid.cell_size): pygame.draw.line(screen, (255, 255, 255), (i, 0), (i, SCREEN_HEIGHT), 2)
	for i in range(0, SCREEN_HEIGHT, inp_grid.cell_size): pygame.draw.line(screen, (255, 255, 255), (0, i), (SCREEN_WIDTH, i), 2)
	#/draw gridlines	
				
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



	
while 1:
	time_elapsed = clock.tick(30)
	screen.fill((0,0,0))	
	event_list = pygame.event.get()
	for event in event_list:		
		if hasattr(event, 'key'):		
			down = event.type == KEYDOWN		
			if event.key == K_ESCAPE: sys.exit(0)
			elif event.key == K_n and not down: #new layout
				GRID.randomizeGrid(4, PATHER)
			elif event.key == K_SPACE and not down: #A* step
				while not PATHER.finished: 
					AS.A_star_step(PATHER, GRID)				
			elif event.key == K_r and not down: #reset grid
				GRID.resetGrid()				
							
		if event.type == MOUSEMOTION: 
			m_x_pos, m_y_pos = event.pos
		elif event.type == MOUSEBUTTONUP: pass
		elif event.type == MOUSEBUTTONDOWN:	pass			
	
	
	
	drawBoard(GRID)
	
	#display new frame
	pygame.display.flip()