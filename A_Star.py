from random import randint
import A_star_min_heap as MH

##CELL STATES:
OBSTACLE = 1
START = PATH = 2
TARGET = UNREACHABLE = 3
EXPLORED = 4
TO_EXPLORE = 5
##/CELL STATES

##PathFinder object - one per navigation necessity
##mostly just stores positional data, but also indicates
##whether search should continue, and stores the path found 
class PathFinder(object):
	def __init__(self, game_grid_obj):
		self.position = None
		self.target = None
		self.open_list = []
		self.close_list = []		
		self.grid_obj = game_grid_obj
		self.finished = False
		self.found_path = []
		
	def update(self, position, target, open_list, close_list, finished, found_path):
		self.position = position
		self.target = target
		self.open_list = open_list
		self.close_list = close_list		
		self.finished = finished
		self.found_path = found_path
		
##GameGrid - should only be one per instance
##Stores info about obstacles, and currently explored cells
class GameGrid(object):
	def __init__(self, n, m, cell_size):
		"""creates a n by m size grid for tracking game objects"""
		self.width = n
		self.height = m
		self.size = n*m
		self.cell_size = cell_size
		self.grid_arr = [0]*self.size
		self.info_arr = [[None, None, None, None]]*self.size
		#entries in info_arr are: [h, g, f, parent]
		self.target = None
		self.start = None
		
	def randomizeGrid(self, chance_out_of_10, path_finder_obj):
		self.grid_arr = [0]*self.size
		self.info_arr = [[None, None, None, None]]*self.size
		for index in range(self.size):
			roll = randint(1, 10)
			if roll < chance_out_of_10: self.grid_arr[index] = OBSTACLE
		
		self.target = (randint(0, self.width-1), randint(0, self.height-1))
		self.grid_arr[(self.width * self.target[1]) + self.target[0]] = TARGET
		
		self.start = (randint(0, self.width-1), randint(0, self.height-1))
		while self.start == self.target:
			self.start = (randint(0, self.width-1), randint(0, self.height-1))
		self.grid_arr[(self.width * self.start[1]) + self.start[0]] = START
		man_dist = abs(self.target[0] - self.start[0]) + abs(self.target[1] - self.start[1])
		self.info_arr[(self.width * self.start[1]) + self.start[0]] = [man_dist, 0, man_dist, self.start]
		path_finder_obj.update(self.start, self.target, [], [self.start], False, [])
		
	def setGrid(self, path_finder_obj, obstacle_list, start_point, target_point):
		self.grid_arr = [0] * self.size
		self.info_arr = [[None, None, None, None]]*self.size
		
		for obstacle_info in obstacle_list:
			#obstacles are formatted: 
			#((x-coord for top left corner, y-coord for top left),(width, height))
			x, y = obstacle_info[0]
			w, h = obstacle_info[1]
			
			for step in range(w*h):
				pos = (x + step%w, y + step/w)
				self.grid_arr[(pos[1] * self.width) + pos[0]] = OBSTACLE
		
		self.target = target_point
		self.start = start_point
		self.grid_arr[(target_point[1] * self.width) + target_point[0]] = TARGET
		self.grid_arr[(start_point[1] * self.width) + start_point[0]] = START
		man_dist = abs(target_point[0] - start_point[0]) + abs(target_point[1] - start_point[1])
		self.info_arr[(self.width * start_point[1]) + start_point[0]] = [man_dist, 0, man_dist, start_point]
		path_finder_obj.update(start_point, target_point, [], [start_point], False, [])
		
	def copyGrid(self, grid_to_copy):
		self.width = grid_to_copy.width
		self.height = grid_to_copy.height
		self.size = grid_to_copy.size
		self.cell_size = grid_to_copy.cell_size
		self.grid_arr = grid_to_copy.grid_arr
		self.info_arr = grid_to_copy.info_arr		
		self.target = grid_to_copy.target
		self.start = grid_to_copy.start
		
	def resetGrid(self):
		self.grid_arr = [0]*self.size
		self.info_arr = [[None, None, None, None]]*self.size		
		self.target = None
		self.start = None

def A_star_step(pathfinder, grid):
	pos = pathfinder.position
	targ = pathfinder.target
	orig = grid.start	
	if pos == targ:		
		grid.grid_arr[(grid.width * targ[1]) + targ[0]] = PATH
		
		while pos != orig:
			pathfinder.found_path = [pos] + pathfinder.found_path
			grid.grid_arr[(grid.width * pos[1]) + pos[0]] = PATH
			pos = grid.info_arr[(grid.width * pos[1]) + pos[0]][3]			
		pathfinder.finished = True
	
	else:
		#target not yet found. Update surrounding nodes, 
		#set position to next cheapest node in open_list
		#move new position to close_list
		
		if pos[1] > 0:
		#north check
			node_pos = (pos[0], pos[1]-1)			
			if node_pos not in pathfinder.close_list and grid.grid_arr[(node_pos[1] * grid.width) + node_pos[0]] != 1:
				info_ind = (node_pos[1] * grid.width) + node_pos[0]		
				grid.info_arr[info_ind] = nodeInfoCheck(pos, node_pos, targ, grid.info_arr[(node_pos[1]*grid.width) + node_pos[0]], grid.info_arr[(pos[1]*grid.width) + pos[0]], pathfinder, grid)			
		if pos[0] > 0:
		#west check
			node_pos = (pos[0]-1, pos[1])
			if node_pos not in pathfinder.close_list and grid.grid_arr[(node_pos[1] * grid.width) + node_pos[0]] != 1:
				info_ind = (node_pos[1] * grid.width) + node_pos[0]		
				grid.info_arr[info_ind] = nodeInfoCheck(pos, node_pos, targ, grid.info_arr[(node_pos[1]*grid.width) + node_pos[0]], grid.info_arr[(pos[1]*grid.width) + pos[0]], pathfinder, grid)					
		if pos[0] < grid.width-1:
		#east check
			node_pos = (pos[0]+1, pos[1])
			if node_pos not in pathfinder.close_list and grid.grid_arr[(node_pos[1] * grid.width) + node_pos[0]] != 1:
				info_ind = (node_pos[1] * grid.width) + node_pos[0]
				grid.info_arr[info_ind] = nodeInfoCheck(pos, node_pos, targ, grid.info_arr[(node_pos[1]*grid.width) + node_pos[0]], grid.info_arr[(pos[1]*grid.width) + pos[0]], pathfinder, grid)					
		if pos[1] < grid.height-1:
		#south check
			node_pos = (pos[0], pos[1]+1)
			if node_pos not in pathfinder.close_list and grid.grid_arr[(node_pos[1] * grid.width) + node_pos[0]] != 1:
				info_ind = (node_pos[1] * grid.width) + node_pos[0]
				grid.info_arr[info_ind] = nodeInfoCheck(pos, node_pos, targ, grid.info_arr[(node_pos[1]*grid.width) + node_pos[0]], grid.info_arr[(pos[1]*grid.width) + pos[0]], pathfinder, grid)					
				
		##nodes updated, find cheapest node in pathfinder.open_list
		if len(pathfinder.open_list) > 0:
			next_node, pathfinder.open_list = MH.delete(pathfinder.open_list)
			pathfinder.position = next_node[1]
			pathfinder.close_list.append(pathfinder.position)
			grid.grid_arr[(pathfinder.position[1] * grid.width) + pathfinder.position[0]] = EXPLORED
		elif len(pathfinder.open_list) == 0 and pos != targ:
			print "NO AVAILABLE PATH"
			for node in pathfinder.close_list:
				grid.grid_arr[(node[1]*grid.width) + node[0]] = UNREACHABLE
			pathfinder.finished = True
	
def manDist(cur_pos, targ_pos):
	dist = abs(cur_pos[0] - targ_pos[0]) + abs(cur_pos[1] - targ_pos[1])
	return dist

def nodeInfoCheck(parent_pos, node_pos, targ_pos, info_list, parent_info_list, pathfinder, grid):	
	if info_list[3] == None:#no parent		
		new_info = [None] * 4
		new_info[3] = parent_pos
		new_info[0] = manDist(node_pos, targ_pos)
		new_info[1] = parent_info_list[1] + 1
		new_info[2] = new_info[0] + new_info[1]		
		info_list = new_info
		pathfinder.open_list = MH.insert(pathfinder.open_list, (info_list[2], node_pos))
		if grid.grid_arr[(node_pos[1] * grid.width) + node_pos[0]] != 3:
			grid.grid_arr[(node_pos[1] * grid.width) + node_pos[0]] = TO_EXPLORE
	elif parent_info_list[1] + 1 < info_list[1]: #change parent
		new_info = info_list
		new_info[3] = parent_pos
		new_info[1] = parent_info_list[1] + 1
		new_info[2] = new_info[0] + new_info[1]		
		info_list = new_info
	return info_list