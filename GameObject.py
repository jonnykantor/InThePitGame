from random import randint

class GameObject(pygame.sprite.Sprite):
	def __init__(self, position):
		pygame.sprite.Sprite.__init__(self)
		self.id = randint(0, 5000)
		self.position = position
		self.direction = 0	

class Person(GameObject):
	MOVE_UNIT = 5
	def __init__(self, position):
		GameObject.__init__(self, position)

class Customer(Person):
	def __init__(self, image, position):
		Person.__init__(self, position)
		self.src_image = pygame.image.load(image)

	def update(self, change):
		#update position and such here
		self.image = pygame.transform.rotate(self.src_image, self.direction)
		self.rect = self.image.get_rect()
		self.rect.center = self.position

class Player(Person):
	def __init__(self, image, position):
		Person.__init__(self, position)
		self.src_image = pygame.image.load(image)
		#base player attributes should be instantiated
		self.player_energy = 1
		self.player_mood = 1
		self.player_money = 500
		self.player_costs = {'rent': 0, 'food': 50, 'entertainment': 30}

	def update(self, change):
		#update position and such here
		self.image = pygame.transform.rotate(self.src_image, self.direction)
		self.rect = self.image.get_rect()
		self.rect.center = self.position

class AIServer(Person):
	def __init__(self, image, position):
		Person.__init__(self, position)	
		self.src_image = pygame.image.load(image)	

	def update(self, change):
		#update position and such here
		self.image = pygame.transform.rotate(self.src_image, self.direction)
		self.rect = self.image.get_rect()
		self.rect.center = self.position

class Restaurant(GameObject):
	def __init__(self, image, position):
		GameObject.__init__(self, (0, 0))
		self.src_image = pygame.image.load(image)
		self.restaurant_type = 'diner'

	def update(self, change):
		#update position and such here
		self.image = pygame.transform.rotate(self.src_image, self.direction)
		self.rect = self.image.get_rect()
		self.rect.center = self.position

class Table(GameObject):

	table_UseStates = ['empty', 'occupied']
	table_EnviroStates = ['clean', 'meal_in_progress', 'to_be_cleared', 'dirty']

	def __init__(self, image, position, enviro_state, use_state):
		self.src_image = pygame.image.load(image)
		self.table_use_state = use_state
		self.table_enviro_state = enviro_state
		self.table_num_seats = 4
		self.table_seats = [None] * table_num_seats

	def setToOccupied():
		pass

	def update(self, change):
		#update position and such here
		self.image = pygame.transform.rotate(self.src_image, self.direction)
		self.rect = self.image.get_rect()
		self.rect.center = self.position


