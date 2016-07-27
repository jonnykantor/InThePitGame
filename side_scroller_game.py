import pygame, math, sys, os
from pygame import gfxdraw
from pygame.locals import *
from random import randint
from sys import argv

sys.dont_write_bytecode = True

from Globals import *
from Character_Object import *
from Scenery_Object import *
from Text_Object import *
from VerticalButtonsMenu import *
	
def event_LeftKeyPress():
	global X_LIMIT_TEST_POS
	background_left_limit_hit, X_LIMIT_TEST_POS = BACKGROUND_SURFACE_MANAGER.update(LEFT, BACKGROUND_SPEED, PLAYER)	

	every_character_rect_list = [x.rect for x in EVERY_CHARACTER_SPRITE_GROUP]					
	foreground_rect_list = [x.rect for x in FOREGROUND_SPRITE_GROUP]

	if not background_left_limit_hit and PLAYER.pos[0] == SCREEN_WIDTH/2:
		PLAYER_SPRITE_GROUP.update(LEFT, every_character_rect_list, every_character_rect_list, foreground_rect_list)	 
		FOREGROUND_SPRITE_GROUP.update(LEFT, FOREGROUND_SPEED)
		AI_CHARACTER_SPRITE_GROUP.update(PLAYER_LEFT_ONLY, every_character_rect_list, every_character_rect_list, foreground_rect_list)
	else:
		PLAYER_SPRITE_GROUP.update(PLAYER_LEFT_ONLY, every_character_rect_list, every_character_rect_list, foreground_rect_list)	
	
def event_RightKeyPress():
	global X_LIMIT_TEST_POS
	background_right_limit_hit, X_LIMIT_TEST_POS = BACKGROUND_SURFACE_MANAGER.update(RIGHT, BACKGROUND_SPEED, PLAYER)	

	every_character_rect_list = [x.rect for x in EVERY_CHARACTER_SPRITE_GROUP]					
	foreground_rect_list = [x.rect for x in FOREGROUND_SPRITE_GROUP]

	if not background_right_limit_hit and PLAYER.pos[0] == SCREEN_WIDTH/2:  
		PLAYER_SPRITE_GROUP.update(RIGHT, every_character_rect_list, every_character_rect_list, foreground_rect_list)	
		FOREGROUND_SPRITE_GROUP.update(RIGHT, FOREGROUND_SPEED)			
		AI_CHARACTER_SPRITE_GROUP.update(PLAYER_RIGHT_ONLY, every_character_rect_list, every_character_rect_list, foreground_rect_list)
	else:
		PLAYER_SPRITE_GROUP.update(PLAYER_RIGHT_ONLY, every_character_rect_list, every_character_rect_list, foreground_rect_list)	
	
def eventHandler(event_list):
	"""
	eventHandler takes a pygame.event.get() list and handles every event in the list	 
	"""
	global LEFT_KEY_DOWN
	global RIGHT_KEY_DOWN
	global CURR_FONT
	for event in event_list:		
		#KEYPRESS EVENTS
		if event.type == pygame.QUIT: sys.exit(0)			
		if hasattr(event, 'key'):
			
			every_character_rect_list = [x.rect for x in EVERY_CHARACTER_SPRITE_GROUP]					
			foreground_rect_list = [x.rect for x in FOREGROUND_SPRITE_GROUP]						
			
			down = event.type == KEYDOWN		
			if event.key == K_ESCAPE and not down: #sys.exit(0)
				MAIN_MENU_OBJ.activateMenu()
				RIGHT_KEY_DOWN = False
				LEFT_KEY_DOWN = False
			elif event.key == K_LEFT:
				if down: LEFT_KEY_DOWN = True						
				else: LEFT_KEY_DOWN = False
			elif event.key == K_RIGHT:
				if down: RIGHT_KEY_DOWN = True
				else: RIGHT_KEY_DOWN = False
			elif event.key == K_SPACE and down:
				PLAYER_SPRITE_GROUP.update(UP, every_character_rect_list, every_character_rect_list, foreground_rect_list)			
		
		if event.type == MOUSEMOTION: 
			m_x_pos, m_y_pos = event.pos
		elif event.type == MOUSEBUTTONUP:
			m_x_pos, m_y_pos = event.pos
			#TESTING TEXT - NOT PERMANENT, TO BE REMOVED						
			create_And_AddTextSpriteToGroup("123456789", 20, POINTS_FADING, "impact", GREEN, 40, (m_x_pos, m_y_pos), BLACK, WHITE, None, TEXT_SPRITE_GROUP_POINTS)
			#create_And_AddTextSpriteToGroup("I am a pie! You must eat me now, jerk!", 120, SPEECH_BUBBLE, "impact", BLACK, 40, (m_x_pos, m_y_pos), WHITE, LIGHT_BLUE, [False, True, 5], TEXT_SPRITE_GROUP_POINTS) 			 			
			
			#/TESTING
	
	if LEFT_KEY_DOWN and PLAYER.isCollidingLeft == False: 
		event_LeftKeyPress()
	if RIGHT_KEY_DOWN and PLAYER.isCollidingRight == False: 
		event_RightKeyPress()
				
def updateAllGroups(sprite_groups_list):
	"""All sprite groups in the list are given their basic per-frame update"""
	every_character_rect_list = [x.rect for x in EVERY_CHARACTER_SPRITE_GROUP]
	foreground_rect_list = [x.rect for x in FOREGROUND_SPRITE_GROUP]

	for group in sprite_groups_list:
		group.update(None, every_character_rect_list, every_character_rect_list, foreground_rect_list)
		
	spriteUpdateAndRemove_Text(TEXT_SPRITE_GROUP_POINTS)

def drawAllSprites(draw_list, surface):
	"""All objects in the draw_list have their draw method called"""
	for item in draw_list:
		item.draw(surface)
		
def debug_drawRects(rect_list):
	for rect in rect_list:
		pygame.draw_rect(SCREEN, BLUE, rect)
		
def AI_behavior_handler(AI_Character_list):
	global ai_rand_act
	global char_action	

	every_character_rect_list = [x.rect for x in EVERY_CHARACTER_SPRITE_GROUP]					
	foreground_rect_list = [x.rect for x in FOREGROUND_SPRITE_GROUP]

	for index, ai_character in enumerate(AI_Character_list):		
		isJumping = randint(0, 125)		
		if ai_rand_act[index] == 0:
			char_action[index] = randint(0, 2)			
			if char_action[index] == 2: ai_rand_act[index] = 15
			else: ai_rand_act[index] = randint(5, 10)
		else: ai_rand_act[index] -= 1
		if char_action[index] == 2:
			ai_character.update(None, every_character_rect_list, every_character_rect_list, foreground_rect_list)
			if isJumping == randint(0, 125): ai_character.update(UP, every_character_rect_list, every_character_rect_list, foreground_rect_list)
		else:			
			ai_character.update(char_action[index], every_character_rect_list, every_character_rect_list, foreground_rect_list)
			if isJumping == randint(0, 125): ai_character.update(UP, every_character_rect_list, every_character_rect_list, foreground_rect_list)	
			
def create_And_AddTextSpriteToGroup(text, duration, type, font, font_color, font_size, position, back_color, colorkey_color, argument_vector, sprite_group):
	text_sprite = textObject(SCREEN, text, duration, type, font, font_color, font_size, position, back_color, colorkey_color, argument_vector)	
	sprite_group.add(text_sprite)	

def spriteUpdateAndRemove_Text(text_sprite_group):
	for sprite in text_sprite_group.sprites():
		if sprite.duration == 0:
			text_sprite_group.remove(sprite)		
	text_sprite_group.update()
				
def loadImages(path, f_names):
	"""returns a list of pygame.Surface objects, loaded from images at 'path' having a name in the 'f_names' list"""
	ret_surfaces = []
	for f_name in f_names:		
		ret_surfaces.append( pygame.image.load(os.path.join(path, f_name)).convert_alpha() )
	return ret_surfaces

if __name__ == "__main__": #Globals
	pygame.init()
	##loading images for objects	
	foreground_surfaces 			= loadImages( ASSETS_PATH, FOREGROUND_ASSET_FNAMES )
	background_surfaces 			= loadImages( ASSETS_PATH, BACKGROUND_ASSET_FNAMES )
	player_object_surfaces 			= loadImages( ASSETS_PATH, PLAYER_ASSET_FNAMES )
	AI_character_object_surfaces 	= loadImages( ASSETS_PATH, AI_CHARACTER_ASSET_FNAMES )
	##

	##main menu instantiation
	MAIN_MENU_OBJ = VerticalButtonsMenu(SCREEN,
										["Play", "Quit"],
										[BACK_TO_GAME, QUIT],
										"impact",										
										50,
										background_surfaces[0],
										WHITE,
										BLACK,
										GREY,
										LIGHT_BLUE,
										5,
										15,
										CENTER,
										True,
										WHITE,
										DARK_GREY)
	##
	
	##instatiate sprite and sprite group objects
	TEXT_SPRITE_GROUP_POINTS = pygame.sprite.Group()
		#ALL BACKGROUND PANELS ASSUMED TO HAVE THE SAME WIDTH - THIS IS CRUCIAL - ALL MUST HAVE THE SAME WIDTH!

	if len(background_surfaces) > 0: pass

	BACKGROUND_SURFACE_MANAGER = BackgroundSurfacesManager(SCREEN, background_surfaces, [(-1600, 0), (-800, 0), (0, 0), (800, 0), (1600, 0)], False, X_SCROLL_LIMITS )		
	
	FOREGROUND_SPRITE_GROUP = pygame.sprite.Group()
	for index, forg_surf in enumerate(foreground_surfaces): FOREGROUND_SPRITE_GROUP.add(ForegroundSprite(SCREEN, forg_surf, FOREGROUND_ASSET_POSITIONS[index]))
	
	PLAYER = PlayerObject(SCREEN, player_object_surfaces, (SCREEN_WIDTH/2, FLOOR_HEIGHT))
	PLAYER_SPRITE_GROUP = pygame.sprite.Group()
	PLAYER_SPRITE_GROUP.add(PLAYER)
	
	AI_CHARACTER_SPRITE_GROUP = pygame.sprite.Group()
	for i in range(4): AI_CHARACTER_SPRITE_GROUP.add( AICharacterObject(SCREEN, AI_character_object_surfaces, (SCREEN_WIDTH/3 + randint(-50, 50), FLOOR_HEIGHT), DEFAULT_AI_TYPE, X_SCROLL_LIMITS)) 		
	EVERY_CHARACTER_SPRITE_GROUP = AI_CHARACTER_SPRITE_GROUP.copy()
	EVERY_CHARACTER_SPRITE_GROUP.add(PLAYER)
	##	
	
	##ai character rand action vars, temporary
	ai_rand_act = [0] * len(AI_CHARACTER_SPRITE_GROUP)	
	char_action = [2] * len(AI_CHARACTER_SPRITE_GROUP)
	
if __name__ == "__main__": #game loop
	
	MAIN_MENU_OBJ.activateMenu()	
	while 1:
		time_elapsed = CLOCK.tick(30)
		
		event_list = pygame.event.get()
		eventHandler(event_list)			
		
		AI_behavior_handler(AI_CHARACTER_SPRITE_GROUP)		
		updateAllGroups([AI_CHARACTER_SPRITE_GROUP, PLAYER_SPRITE_GROUP])				
		BACKGROUND_SURFACE_MANAGER.draw(SCREEN) #should be added to drawAllSprites once a sprite floor is added
		#temp floor
		pygame.draw.rect(SCREEN, GREY, ((0, FLOOR_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT-FLOOR_HEIGHT)) )				
		#/temp floor
		drawAllSprites([AI_CHARACTER_SPRITE_GROUP, PLAYER_SPRITE_GROUP, FOREGROUND_SPRITE_GROUP, TEXT_SPRITE_GROUP_POINTS], SCREEN)								
		#display new frame
		pygame.display.flip()