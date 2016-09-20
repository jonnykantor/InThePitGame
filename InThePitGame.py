import pygame, math, sys, os
from pygame.locals import *
from random import randint
from sys import argv

sys.dont_write_bytecode = True

from Globals import *
from Character_Object import *
from Scenery_Object import *
from Text_Object import *
from VerticalButtonsMenu import *
from GameStatsTracker import *

def event_DirectionKeyPress(direction, player_obj, all_background_surface_managers, sprite_groups_list, direction_obj, dimensions_and_limits_obj, movement_measures_obj):
	
	left = direction_obj.left
	right = direction_obj.right

	for bsm in all_background_surface_managers:
		background_limit_hit, dimensions_and_limits_obj.x_limit_test_pos = bsm.update(direction, movement_measures_obj.background_speed, player_obj, direction_obj, dimensions_and_limits_obj)	

	player_direction = None
	if direction == left: player_direction = direction_obj.player_left_only
	elif direction == right: player_direction = direction_obj.player_right_only

	every_character_rect_list 	= [x.rect for x in sprite_groups_list[0]]					
	foreground_rect_list 		= [x.rect for x in sprite_groups_list[1]]
	
	if not background_limit_hit and player_obj.pos[0] == dimensions_and_limits_obj.screen_width/2:
		sprite_groups_list[2].update(direction, movement_measures_obj.background_speed, every_character_rect_list, every_character_rect_list, foreground_rect_list, direction_obj, dimensions_and_limits_obj)	 
		sprite_groups_list[1].update(direction, movement_measures_obj.foreground_speed, direction_obj)
		sprite_groups_list[3].update(player_direction, movement_measures_obj.background_speed, every_character_rect_list, every_character_rect_list, foreground_rect_list, direction_obj, dimensions_and_limits_obj)
	else:
		sprite_groups_list[2].update(player_direction, movement_measures_obj.background_speed, every_character_rect_list, every_character_rect_list, foreground_rect_list, direction_obj, dimensions_and_limits_obj)		
	
def eventHandler(	event_list, menu_obj, menu_commands, sprite_groups_list, player_obj, game_stats_obj, all_background_surface_managers, direction_obj, colors_obj, dimensions_and_limits_obj, movement_measures_obj, txt_types_obj):
	"""
	eventHandler takes a pygame.event.get() list and handles every event in the list	 
	
	sprite_groups_list content and ordering:
		EVERY_CHARACTER_SPRITE_GROUP
		FOREGROUND_SPRITE_GROUP
		PLAYER_SPRITE_GROUP
		AI_CHARACTER_SPRITE_GROUP
		TEXT_SPRITE_GROUP_POINTS
	"""
	left = direction_obj.left
	right = direction_obj.right
	down = direction_obj.down
	up = direction_obj.up

	for event in event_list:		

		#KEYPRESS EVENTS
		if event.type == pygame.QUIT: sys.exit(0)			
		if hasattr(event, 'key'):
			
			every_character_rect_list = [x.rect for x in sprite_groups_list[0]]					
			foreground_rect_list = [x.rect for x in sprite_groups_list[1]]						
			
			down = event.type == KEYDOWN		
			if event.key == K_ESCAPE and not down:
				game_stats_obj.current_game_state = game_stats_obj.STATE_PAUSED
				command_return = menu_obj.activateMenu(menu_commands, direction_obj)
				if command_return == menu_commands.RESTART:
					return menu_commands.RESTART
				game_stats_obj.current_game_state = game_stats_obj.STATE_PLAYING
				direction_obj.direction_key_states[left] = False
				direction_obj.direction_key_states[right] = False

			elif event.key == K_LEFT:
				if down: direction_obj.direction_key_states[left] = True						
				else: direction_obj.direction_key_states[left] = False

			elif event.key == K_RIGHT:
				if down: direction_obj.direction_key_states[right] = True						
				else: direction_obj.direction_key_states[right] = False

			elif event.key == K_SPACE and down:
				sprite_groups_list[2].update(up, movement_measures_obj.background_speed, every_character_rect_list, every_character_rect_list, foreground_rect_list, direction_obj, dimensions_and_limits_obj)

			elif event.key == K_f and down:
				#update for aggression animation
				if player_obj.isCollidingRight and player_obj.facing_direction == right:
					#rect that has been collided with is stored in CharacterObject super class
						
					for npc_object in sprite_groups_list[3]: #this is super inefficient
						if npc_object.rect == player_obj.collisionObjectRight:
							
							npc_object.update(direction_obj.nudge_right, movement_measures_obj.nudge_amount, [], [], [], direction_obj, dimensions_and_limits_obj)
							
							create_And_AddTextSpriteToGroup(	dimensions_and_limits_obj.screen, "50", 30, txt_types_obj.POINTS_FADING, 
																txt_types_obj, "impact", colors_obj.GOLD, 50, npc_object.rect.midtop, 
																colors_obj.WHITE, colors_obj.LIGHT_BLUE, [True, True, True], sprite_groups_list[4][0])
							
							updateGameStats(game_stats_obj, 5, 5, 50)
				elif player_obj.isCollidingLeft and player_obj.facing_direction == left:
					
					for npc_object in sprite_groups_list[3]: #also super inefficient
						if npc_object.rect == player_obj.collisionObjectLeft:
							
							npc_object.update(direction_obj.nudge_left, movement_measures_obj.nudge_amount, [], [], [], direction_obj, dimensions_and_limits_obj)
							
							create_And_AddTextSpriteToGroup(	dimensions_and_limits_obj.screen, "50", 30, txt_types_obj.POINTS_FADING, 
																txt_types_obj, "impact", colors_obj.GOLD, 50, npc_object.rect.midtop, 
																colors_obj.WHITE, colors_obj.LIGHT_BLUE, [True, True, True], sprite_groups_list[4][0])
							
							updateGameStats(game_stats_obj, 5, 5, 50)
		
		#mouse events not used here currently
		#if event.type == MOUSEMOTION: 
		#	m_x_pos, m_y_pos = event.pos
		#elif event.type == MOUSEBUTTONUP:
		#	m_x_pos, m_y_pos = event.pos
	
	if direction_obj.direction_key_states[left]: #left key down
		event_DirectionKeyPress(left, player_obj, all_background_surface_managers, sprite_groups_list, direction_obj, dimensions_and_limits_obj, movement_measures_obj)
	if direction_obj.direction_key_states[right]: #right key down
		event_DirectionKeyPress(right, player_obj, all_background_surface_managers, sprite_groups_list, direction_obj, dimensions_and_limits_obj, movement_measures_obj)
				
def updateAllGroups(sprite_groups_list, collision_groups_list, text_sprite_groups, direction_obj, dimensions_and_limits_obj, speed):
	"""All sprite groups in the list are given their basic per-frame update"""
	every_character_rect_list = [x.rect for x in collision_groups_list[0]]
	foreground_rect_list = [x.rect for x in collision_groups_list[1]]

	for group in sprite_groups_list:
		group.update(None, speed, every_character_rect_list, every_character_rect_list, foreground_rect_list, direction_obj, dimensions_and_limits_obj)
		
	for text_group in text_sprite_groups:
		spriteUpdateAndRemove_Text(text_group)

def drawAllSprites(draw_list, surface):
	"""All objects in the draw_list have their draw method called"""
	for item in draw_list:
		item.draw(surface)

def updateGameStats(game_stats_object, beer_adjustment, security_adjustment, points_adjustment):
	
	game_stats_object.update(beer_adjustment, security_adjustment, points_adjustment)

def drawGameStats(game_stats_object):
	
	game_stats_object.draw()
		
def debug_drawRects(rect_list, colors_obj, dimensions_and_limits_obj):
	for rect in rect_list:
		pygame.draw.rect(dimensions_and_limits_obj.screen, colors_obj.BLUE, rect)

def AI_characters_update(AI_Character_list, dimensions_and_limits_obj, directions_obj, sprite_groups_list, movement_measures_obj):
	"""
	determines, for each object in the AI_Character_list, what their current action is (either continuing an existing one,
	choosing a new one, or interrupting the current action based on some interraction with another object)
	"""

	every_character_rect_list = [x.rect for x in sprite_groups_list[0]]
	foreground_rect_list = [x.rect for x in sprite_groups_list[1]]

	for index, ai_char in enumerate(AI_Character_list):
		if ai_char.action_counter <= 0 or ai_char.current_action == None:
			#choose new action
			ai_char.decideAction(every_character_rect_list, False, dimensions_and_limits_obj.screen_width/2, directions_obj)
		
		else:
			#continue with current action
			action = ai_char.current_action
			if action[0] == ai_char.ATTACK_TARGET:
				#check if colliding with target
				#if not, check target x-location and move towards it
				#if so, attack target (nudge)
				if (ai_char.facing_direction == directions_obj.right 
					and ai_char.right_side_collision_rect.colliderect(action[2])):
					#nudge target, choose new action
					for char_object in sprite_groups_list[0]:
						if char_object.rect == action[2]:
							char_object.update(directions_obj.nudge_right, 50, [], [], [], directions_obj, dimensions_and_limits_obj)
					ai_char.decideAction(every_character_rect_list, True, dimensions_and_limits_obj.screen_width/2, directions_obj)
				elif (ai_char.facing_direction == directions_obj.left 
					and ai_char.left_side_collision_rect.colliderect(action[2])):
					#nudge target, choose new action
					for char_object in sprite_groups_list[0]:
						if char_object.rect == action[2]:
							char_object.update(directions_obj.nudge_left, 50, [], [], [], directions_obj, dimensions_and_limits_obj)
					ai_char.decideAction(every_character_rect_list, True, dimensions_and_limits_obj.screen_width/2, directions_obj)
				else:
					#no collision yet, update with a move in the direction of the target
					speed = movement_measures_obj.background_speed
					if action[2].centerx <= ai_char.rect.centerx:
						if ai_char.rect.centerx - action[2].centerx < speed: speed = ai_char.rect.centerx - action[2].centerx
						ai_char.update(	directions_obj.left, speed, every_character_rect_list, every_character_rect_list,
										foreground_rect_list, directions_obj, dimensions_and_limits_obj)
					elif action[2].centerx > ai_char.rect.centerx:						
						if action[2].centerx - ai_char.rect.centerx < speed: speed = action[2].centerx - ai_char.rect.centerx
						ai_char.update(	directions_obj.right, speed, every_character_rect_list, every_character_rect_list,
										foreground_rect_list, directions_obj, dimensions_and_limits_obj)
			
			
			elif action[0] == ai_char.MOVE_FREELY:
				ai_char.update(	action[1], movement_measures_obj.background_speed, every_character_rect_list, every_character_rect_list,
										foreground_rect_list, directions_obj, dimensions_and_limits_obj)	
	
def create_And_AddTextSpriteToGroup(surface, text, duration, type, all_types, font, font_color, font_size, position, back_color, colorkey_color, argument_vector, sprite_group):
	text_sprite = textObject(	surface, text, duration, type, all_types, font, font_color, font_size, 
								position, back_color, colorkey_color, argument_vector)	
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

def gameSetup(dimensions_and_limits_obj, DrawPos, menu_commands, colors_obj, directions_obj, movement_measures_obj, txt_types_obj, all_surfaces):
	
	##all_surfaces:
	## 0	[foreground_surfaces, 				
	## 1	background_surfaces_far, 
	## 2	background_surfaces_near, 
	## 3	player_object_surfaces, 
	## 4	AI_character_object_surfaces, 
	## 5	drummer_all_surfaces_subdivided]
	
	##main menu instantiation

	mm_extra_text =	[	
						
						["*IN*THE*PIT*", 1, txt_types_obj.SPEECH_BUBBLE, txt_types_obj, "impact", colors_obj.BLACK, 100, (0, 0), 
						colors_obj.TEST_COL, colors_obj.LIGHT_BLUE, [False, True, 15, 30, True]],

						["MAIN MENU", 1, txt_types_obj.POINTS_FADING, txt_types_obj, "impact", colors_obj.RED, 80, (0, 0), 
						colors_obj.BLACK, colors_obj.LIGHT_BLUE, [True, True, True]]	

						#,
						#["This is a test of the button text bubble object that I created some time ago to see what would happen if I were to set the border-size to 0, with a transparent background, using lots of text with a wider character size limit", 
						#1, txt_types_obj.SPEECH_BUBBLE, txt_types_obj, "impact", colors_obj.RED, 30, (0, 0), 
						#colors_obj.LIGHT_BLUE, colors_obj.LIGHT_BLUE, [False, True, 0, 80, True]],
						
	]
	
	main_menu_obj = VerticalButtonsMenu(	dimensions_and_limits_obj.screen, ["Play", "Quit"], [menu_commands.BACK_TO_GAME, 
											menu_commands.QUIT],	"impact", 50, None,	colors_obj.WHITE, 
											colors_obj.BLACK,	colors_obj.GREY, colors_obj.LIGHT_BLUE, 5, 15, directions_obj.center, 
											True, colors_obj.WHITE, colors_obj.DARK_GREY, mm_extra_text)
	
	##instatiate sprite and sprite group objects
	text_sprite_group_points = pygame.sprite.Group()
	drummer_sprite_group = pygame.sprite.OrderedUpdates()
	foreground_sprite_group = pygame.sprite.Group()
	player_sprite_group = pygame.sprite.Group()
	ai_character_sprite_group = pygame.sprite.Group()

	for i in range(10): ai_character_sprite_group.add( 	AICharacterObject(dimensions_and_limits_obj.screen, all_surfaces[4], 
														(dimensions_and_limits_obj.screen_width/3 + randint(-50, 50), DrawPos.character_y_pos), 
														dimensions_and_limits_obj.x_scroll_limits, dimensions_and_limits_obj)	) 		

	every_character_sprite_group = ai_character_sprite_group.copy()

	#for index, forg_surf in enumerate(all_surfaces[0]): 
	#	foreground_sprite_group.add(ForegroundSprite(dimensions_and_limits_obj.screen, forg_surf, DrawPos.foreground_asset_positions[index]))
	
	player_obj = PlayerObject(	dimensions_and_limits_obj.screen, all_surfaces[3], 
								(dimensions_and_limits_obj.screen_width/2, DrawPos.character_y_pos), 
								None, dimensions_and_limits_obj)
	player_sprite_group.add(player_obj)	
	every_character_sprite_group.add(player_obj)

	sprite_groups_list = [	every_character_sprite_group,
							foreground_sprite_group,
							player_sprite_group,
							ai_character_sprite_group,
							[text_sprite_group_points]]

	#surface and scene managers
	background_surface_manager_far = BackgroundSurfacesManager(	dimensions_and_limits_obj.screen, all_surfaces[1], 
																DrawPos.background_asset_positions_far,	False, dimensions_and_limits_obj.x_scroll_limits, 
																dimensions_and_limits_obj.screen_width )
	background_surface_manager_near = BackgroundSurfacesManager(dimensions_and_limits_obj.screen, all_surfaces[2], 
																DrawPos.background_asset_positions_near, False, dimensions_and_limits_obj.x_scroll_limits, 
																dimensions_and_limits_obj.screen_width )		
	
	drummer_animation_start_delays 	= [0, 0, 0, 0, 5, 5]	#each entry corresponds to the drummer_*_surfaces entries above, same order
	drummer_inter_frame_delays 		= [0, 0, 0, 1, 0, 0] 	#same correspondence

	for index, drummer_surfaces_list in enumerate(all_surfaces[5]):
		drummer_sprite_group.add(AnimatedScenerySprite(	dimensions_and_limits_obj.screen,						#surface for sprite superclass
														drummer_surfaces_list, 					#subdivided list of animation sequences
														DrawPos.drum_kit_position,				#upper-left corner of rect draw position
														(0, 0), 								#(sequence, frame) starting numbers
														drummer_inter_frame_delays[index], 		#inter-frame delay amount
														drummer_animation_start_delays[index])) #animation start delay
								

	drummer_anim_scene_manager = (
		AnimatedSceneryAnimationManager(	
			drummer_sprite_group, 																#sprite group
			[x for x in drummer_sprite_group], 													#list of sprites for direct updating
			[[(0, 49), (50, 79), (80, 99)], [(0, 79), (80, 99)], [(0, 99)], None, None, None], 	#list_animation_occurence_rates
			[(0, 2, 4), (1, 1, 5), (2, 0, 3)],												 	#list_active_reactive_animation_tuples
			[2, 2, 0])) 																		#list_active_reactive_animation_offsets
	
	##GameStatsTracker instantiation	
	game_stats_obj = GameStatsTracker(	50, 0, 0, 999, 
									[dimensions_and_limits_obj.screen, "0", 1, txt_types_obj.POINTS_FADING, txt_types_obj, "impact", colors_obj.GREEN, 
									60, (dimensions_and_limits_obj.screen_width-50, dimensions_and_limits_obj.screen_height-25), colors_obj.LIGHT_BLUE, 
									colors_obj.WHITE, [False, False, False]], colors_obj.LIGHT_BLUE, colors_obj.GOLD, colors_obj.RED)

	game_stats_obj.current_game_state = game_stats_obj.STATE_PAUSED
	
	cmd = mainGameLoop([	main_menu_obj,
							sprite_groups_list,
							player_obj,
							game_stats_obj,
							background_surface_manager_far,
							background_surface_manager_near,
							directions_obj,
							colors_obj,
							dimensions_and_limits_obj,
							movement_measures_obj,
							txt_types_obj,
							menu_commands,
							drummer_anim_scene_manager
						])

	if cmd == menu_commands.RESTART: return cmd

def initialGameSetup():
	pygame.init()

	#definition class insantiations
	directions_obj = Directions(0, 1, 2, 3, [False, False, False, False], 4, 5, 6, 7, 8)
	menu_commands = MenuButtonCommands(0, 1, 2, 3, 4)
	colors_obj = ColorDefs()
	dimensions_and_limits_obj = DimensionsAndLimits(800, 600, 5, 5)
	movement_measures_obj = MovementMeasures(20, 18, 50)
	DrawPos = DrawPositions(450, (310, 198), [(0, 0)], [(310, 198), (0, 0), (0, 0)], [(0, 0), (310, 198)])
	txt_types_obj = TextObjectTypes()
	AA = ArtAssets('art_assets')

	#loading images for objects	
	foreground_surfaces 			= loadImages( AA.path, AA.foreground_asset_fnames )
	background_surfaces_far			= loadImages( AA.path, AA.background_asset_fnames_far )
	background_surfaces_near		= loadImages( AA.path, AA.background_asset_fnames_near )
	player_object_surfaces 			= loadImages( AA.path, AA.player_asset_fnames )
	AI_character_object_surfaces 	= loadImages( AA.path, AA.ai_character_asset_fnames )
	
	#load images for drummer sprite
	drummer_left_arm_surfaces 		= loadImages( AA.path + AA.drummer_path, AA.drummer_asset_fnames[0] + AA.drummer_asset_fnames[1] + AA.drummer_asset_fnames[2] )
	drummer_right_arm_surfaces 		= loadImages( AA.path + AA.drummer_path, AA.drummer_asset_fnames[3] + AA.drummer_asset_fnames[4] )
	drummer_high_hat_surfaces 		= loadImages( AA.path + AA.drummer_path, AA.drummer_asset_fnames[5] )
	drummer_high_hat_foot_surfaces 	= loadImages( AA.path + AA.drummer_path, AA.drummer_asset_fnames[6] )
	drummer_left_cymbal_surfaces 	= loadImages( AA.path + AA.drummer_path, AA.drummer_asset_fnames[7] )
	drummer_right_cymbal_surfaces 	= loadImages( AA.path + AA.drummer_path, AA.drummer_asset_fnames[8] )
	drummer_all_surfaces_subdivided = [	[drummer_left_arm_surfaces[0:1], drummer_left_arm_surfaces[1:3], drummer_left_arm_surfaces[3:]], 
										[drummer_right_arm_surfaces[0:2], drummer_right_arm_surfaces[2:]],
										[drummer_high_hat_foot_surfaces], 
										[drummer_high_hat_surfaces], 
										[drummer_left_cymbal_surfaces], 
										[drummer_right_cymbal_surfaces]
									  ]

	while(1):
		cmd = gameSetup(dimensions_and_limits_obj, DrawPos, menu_commands, colors_obj, directions_obj, movement_measures_obj, txt_types_obj, 
					[foreground_surfaces, 
					background_surfaces_far, 
					background_surfaces_near, 
					player_object_surfaces, 
					AI_character_object_surfaces, 
					drummer_all_surfaces_subdivided])
		if cmd == menu_commands.RESTART: 
			dimensions_and_limits_obj.screen.fill(colors_obj.BLACK)

def mainGameLoop(game_loop_args):
	"""
	game loop args contains all input arguments for the main game loop: 
		##game_loop_args:
			#
			# 0: main_menu_obj
			# 1: sprite_groups_list: [0: every_char, 1: foreground, 2: player, 3: ai, 4: [text_groups]]
			# 2: player_obj
			# 3: game_stats_obj
			# 4: background_surface_manager_far
			# 5: background_surface_manager_near
			# 6: directions_obj
			# 7: colors_obj
			# 8: dimensions_and_limits_obj
			# 9: movement_measures_obj
			#10: txt_types_obj
			#11: menu_commands
			#12: drummer_anim_scene_manager
			#13: rect_to_object_lookup_dict
	"""
	main_menu_obj 						= game_loop_args[0] 
	sprite_groups_list 					= game_loop_args[1]
	player_obj 							= game_loop_args[2]
	game_stats_obj 						= game_loop_args[3]
	background_surface_manager_far 		= game_loop_args[4]
	background_surface_manager_near 	= game_loop_args[5]
	directions_obj 						= game_loop_args[6]
	colors_obj 							= game_loop_args[7]
	dimensions_and_limits_obj 			= game_loop_args[8]
	movement_measures_obj 				= game_loop_args[9]
	txt_types_obj 						= game_loop_args[10]
	menu_commands 						= game_loop_args[11]
	drummer_anim_scene_manager			= game_loop_args[12]

	##ai character rand action vars, temporary
	ai_rand_act = [0] * len(sprite_groups_list[3])	
	char_action = [2] * len(sprite_groups_list[3])

	main_menu_obj.activateMenu(menu_commands, directions_obj)
	game_stats_obj.current_game_state = game_stats_obj.STATE_PLAYING
	main_menu_obj.addNewButton("Restart", -1, menu_commands.RESTART)
	main_menu_obj.replaceButtonAtIndex("Back To Game", 0, menu_commands.BACK_TO_GAME )

	other_tick = False	
	command_return = None
	while 1:
		#try:
		time_elapsed = CLOCK.tick(30)
		other_tick = not other_tick

		event_list = pygame.event.get()			

		command_return = eventHandler(	event_list, main_menu_obj, menu_commands, sprite_groups_list, player_obj, game_stats_obj, 
										[background_surface_manager_far, background_surface_manager_near], directions_obj, 
										colors_obj, dimensions_and_limits_obj, movement_measures_obj, txt_types_obj)			
		
		if command_return == menu_commands.RESTART:	return command_return

		AI_characters_update(	sprite_groups_list[3], dimensions_and_limits_obj, directions_obj, sprite_groups_list, movement_measures_obj)

		#AI_behavior_handler(	sprite_groups_list[3], dimensions_and_limits_obj, sprite_groups_list[0], sprite_groups_list[1], 
		#						ai_rand_act, char_action, movement_measures_obj, directions_obj)
		
		updateAllGroups(	[sprite_groups_list[3], sprite_groups_list[2]], [sprite_groups_list[0], sprite_groups_list[1]], 
							sprite_groups_list[4], directions_obj, dimensions_and_limits_obj, movement_measures_obj.background_speed)				
		
		if other_tick: drummer_anim_scene_manager.update(movement_measures_obj.background_speed, directions_obj)			
		
		drawAllSprites(	[background_surface_manager_far, drummer_anim_scene_manager, background_surface_manager_near, 
						sprite_groups_list[0], sprite_groups_list[1], sprite_groups_list[4][0]], 
						dimensions_and_limits_obj.screen)								
		
		updateGameStats(game_stats_obj, 1, 0, 0)
		drawGameStats(game_stats_obj)
		if game_stats_obj.current_game_state == game_stats_obj.STATE_GAMEOVER:
			main_menu_obj.clearMenu()
			main_menu_obj.addNewButton("Restart", -1, menu_commands.RESTART)
			main_menu_obj.addNewButton("Quit", -1, menu_commands.QUIT)
			command_return = main_menu_obj.activateMenu(menu_commands, directions_obj)
			if command_return == menu_commands.RESTART: return menu_commands.RESTART

		pygame.display.flip()

#		except Exception:
			#pass
#			print sys.exc_info()

if __name__ == "__main__":
	initialGameSetup()