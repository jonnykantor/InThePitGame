import pygame, os

"""GLOBALS"""

##directions for movement, also used for alignment
LEFT = 0
RIGHT = 1
DOWN = 2
UP = 3
CENTER = 4
PLAYER_LEFT_ONLY = 4 
PLAYER_RIGHT_ONLY = 5
NUDGE_LEFT = 6
NUDGE_RIGHT = 7
##/directions for movement

##Menu button commands:
BACK_TO_GAME = 0
QUIT = 1
CONTROLS = 2
OPTIONS = 3
##

##colors
GREY = (128, 128, 128)
DARK_GREY = (50, 50, 50)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (125, 125, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
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
NUDGE_AMMOUNT = 15
##/speeds

##collision rect widths - these are for character/player object extended collision rectangles
LEFT_RECT_WIDTH = 5
RIGHT_RECT_WIDTH = 5
##

##universal scenery heights
#remember that (0, 0) in pygame is the top-left corner; y > 0 is below this point
FLOOR_HEIGHT = 500
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

##Screen attributes and clock
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
SCREEN_RECT = SCREEN.get_rect()
CLOCK = pygame.time.Clock()
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

FOREGROUND_ASSET_FNAMES = [
'Foreground_Crowd_Shadows_1.png'
]
#positions indicate top-left corner of rectangle
FOREGROUND_ASSET_POSITIONS = [
(0, 0)
]

DRUM_KIT_POSITION = (311, 200)

BACKGROUND_ASSET_POSITIONS = [
(0, 0),
DRUM_KIT_POSITION,
DRUM_KIT_POSITION,
(0, 0),
(0, 0),
]

BACKGROUND_ASSET_FNAMES = [

'Stage_Background_Far_1.png',
'DRUMMER/Drummer_Immobile_Area.png',
'Drum_Kit_Plus_Stands.png',
'Stage_Background_Near_1.png',
'Background_Crowd_Outlines.png'
]	

##Drummer is actually 5 animated images: left arm, right arm, foot, high-hat, left-cymbal, right-cymbal
DRUMMER_ASSET_FNAMES = [
	['DRUMMER_LEFT_Arm_Floor_Tom_Hit.png'],
	
	['DRUMMER_LEFT_Arm_Neutral_1.png',
	'DRUMMER_LEFT_Arm_Neutral_2.png'],
	
	['DRUMMER_LEFT_Hand_Up_1.png',
	'DRUMMER_LEFT_Hand_Up_2.png',
	'DRUMMER_LEFT_Hand_Up_3.png',
	'DRUMMER_LEFT_Hand_Up_4.png',
	'DRUMMER_LEFT_Hand_Up_5.png'],

	['DRUMMER_RIGHT_Arm_Neutral_1.png',
	'DRUMMER_RIGHT_Arm_Neutral_2.png'],

	['DRUMMER_RIGHT_Hand_Up_1.png',
	'DRUMMER_RIGHT_Hand_Up_2.png',
	'DRUMMER_RIGHT_Hand_Up_3.png',
	'DRUMMER_RIGHT_Hand_Up_4.png',
	'DRUMMER_RIGHT_Hand_Up_5.png'],

	['DRUMMER_High_Hat_UP.png',
	'DRUMMER_High_Hat_DOWN.png'],

	['DRUMMER_High_Hat_FOOT_UP.png',
	'DRUMMER_High_Hat_FOOT_DOWN.png'],

	['DRUMMER_Cymbal_LEFT_STILL.png',
	'DRUMMER_Cymbal_LEFT_HIT_1.png',
	'DRUMMER_Cymbal_LEFT_HIT_2.png',
	'DRUMMER_Cymbal_LEFT_HIT_1.png',
	'DRUMMER_Cymbal_LEFT_STILL.png',
	'DRUMMER_Cymbal_LEFT_HIT_REVERSE_1.png',
	'DRUMMER_Cymbal_LEFT_HIT_REVERSE_2.png',
	'DRUMMER_Cymbal_LEFT_HIT_REVERSE_1.png',
	'DRUMMER_Cymbal_LEFT_STILL.png'],

	['DRUMMER_Cymbal_RIGHT_STILL.png',
	'DRUMMER_Cymbal_RIGHT_HIT_1.png',
	'DRUMMER_Cymbal_RIGHT_HIT_2.png',
	'DRUMMER_Cymbal_RIGHT_HIT_1.png',
	'DRUMMER_Cymbal_RIGHT_STILL.png',
	'DRUMMER_Cymbal_RIGHT_HIT_REVERSE_1.png',
	'DRUMMER_Cymbal_RIGHT_HIT_REVERSE_2.png',
	'DRUMMER_Cymbal_RIGHT_HIT_REVERSE_1.png',
	'DRUMMER_Cymbal_RIGHT_STILL.png']
]
##



## Screen side limits
#note that this limit is when the background screen will stop scrolling
#the player character will still be at the screen mid-point, and AI
#characters move independent of background coords
X_SCROLL_LIMIT_LEFT = SCREEN_WIDTH/2
X_SCROLL_LIMIT_RIGHT = SCREEN_WIDTH/2
X_SCROLL_LIMITS = (X_SCROLL_LIMIT_LEFT, X_SCROLL_LIMIT_RIGHT)
X_PLAYER_MOVE_LIMIT = (0, SCREEN_WIDTH)
AT_LIMIT_LEFT = 1 #left-side of background limit has been reached
AT_LIMIT_RIGHT = 2 #right-side of background limit has been reached
X_LIMIT_TEST_POS = SCREEN_WIDTH/2
##