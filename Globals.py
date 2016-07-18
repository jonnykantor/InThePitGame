import pygame, os

"""GLOBALS"""

##directions for movement
LEFT = 0
RIGHT = 1
DOWN = 2
UP = 3
#next two are to avoid animation of non-player objects 
#when they are only moving relative to player object movement
PLAYER_LEFT_ONLY = 4 
PLAYER_RIGHT_ONLY = 5
##/directions for movement

##colors
GREY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (125, 125, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
##/colors

##
#NOTE: THESE FONTS DO NOT WORK:
#anything ending in 'bold' (FONT_LIST[CURR_FONT][-4:] == "bold")	
#anything ending in 'italic' (FONT_LIST[CURR_FONT][-6:] == "italic")
#cambria
#yugothic
FONT_LIST = pygame.font.get_fonts()
CURR_FONT = 0
FONT_LIMIT = len(FONT_LIST)
##

##TextObj types
POINTS_FADING = 0
SPEECH_BUBBLE = 1
##

##speeds
BACKGROUND_SPEED = 10
FOREGROUND_SPEED = 8
##/speeds

##collision rect widths - these are for character/player object extended collision rectangles
LEFT_RECT_WIDTH = 5
RIGHT_RECT_WIDTH = 5
##

##universal scenery heights
#remember that (0, 0) in pygame is the top-left corner; y > 0 is below this point
FLOOR_HEIGHT = 400
##

##image array layout keys	
#LEFT
LEFT_0 	= 0
LEFT_1 	= 1
LEFT_2 	= 2
LEFT_3 	= 3
#RIGHT
RIGHT_0 = 4
RIGHT_1 = 5
RIGHT_2 = 6
RIGHT_3 = 7
#IDLE
IDLE_0 	= 8
IDLE_1 	= 9
IDLE_2 	= 10
IDLE_3 	= 11
#UP
UP_0 	= 12
UP_1 	= 13
UP_2 	= 14
UP_3 	= 15
#DOWN
DOWN_0 	= 16
DOWN_1 	= 17
DOWN_2 	= 18
DOWN_3 	= 19
##

##AI states
DEFAULT_AI_TYPE = 0 #debugging ai type
##

##Screen attributes
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
SCREEN_RECT = SCREEN.get_rect()
##

##Bools for determining whether a key is held down
LEFT_KEY_DOWN = False
RIGHT_KEY_DOWN = False
##

##art assets and asset arrays
#These should probably all be moved to a separate text file and processed programmatically 
#to avoid unncessary bulk in the code as asset amounts rise

ASSETS_PATH = r'art_assets/'

PLAYER_ASSET_FNAMES = [
'death_sprite_left_1.png',
'death_sprite_left_2.png',
'death_sprite_left_3.png',
'death_sprite_left_4.png',
'death_sprite_right_1.png',
'death_sprite_right_2.png',
'death_sprite_right_3.png',
'death_sprite_right_4.png'
]

AI_CHARACTER_ASSET_FNAMES = [
'red_death_sprite_left_1.png',
'red_death_sprite_left_2.png',
'red_death_sprite_left_3.png',
'red_death_sprite_left_4.png',
'red_death_sprite_right_1.png',
'red_death_sprite_right_2.png',
'red_death_sprite_right_3.png',
'red_death_sprite_right_4.png'
]

FOREGROUND_ASSET_FNAMES = ['vending.png'] * 15
''', 
'vending.png', 
'vending.png', 
'vending.png',
'vending.png', 
'vending.png', 
'vending.png', 
'vending.png',
'vending.png', 
'vending.png', 
'vending.png', 
'vending.png',
'vending.png', 
'vending.png', 
'vending.png', 
'vending.png']
'''
#positions indicate top-left corner of rectangle
FOREGROUND_ASSET_POSITIONS = [
(650, 400),
(100, 200),
(500, 300),
(0, 600),
(600, 0),
(400, 400),
(800, 400),
(800, 600),
(300, 500),
(0, 200),
(-500, 300),
(-1000, 600),
(1600, 0),
(1400, 400),
(-800, 400),
(1800, 600)]

BACKGROUND_ASSET_FNAMES = [
'b1.jpg',
'b2.jpg',
'b3.jpg',
'b4.jpg',
'b5.jpg']	
##

## Screen side limits
#note that this limit is when the background screen will stop scrolling
#the player character will still be at the screen mid-point, and AI
#characters move independent of background coords
X_SCROLL_LIMIT_LEFT = -SCREEN_WIDTH/2
X_SCROLL_LIMIT_RIGHT = SCREEN_WIDTH + SCREEN_WIDTH/2
X_SCROLL_LIMITS = (X_SCROLL_LIMIT_LEFT, X_SCROLL_LIMIT_RIGHT)
X_PLAYER_MOVE_LIMIT = (0, SCREEN_WIDTH)
AT_LIMIT_LEFT = 1 #left-side of background limit has been reached
AT_LIMIT_RIGHT = 2 #right-side of background limit has been reached
X_LIMIT_TEST_POS = SCREEN_WIDTH/2
##