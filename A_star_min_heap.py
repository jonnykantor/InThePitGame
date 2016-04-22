#from random import randint

##min-heap implementation for A*
#Note: when evaluating differences among tuples
#the insert/delete functions will only consider the first
#value of the tuple. So to evaluate distances in a
#2-dimensional space, the distance should be computed
#first and have the coordinate tuple appended to it as a
#new tuple, like so: (dist, (x-coord, y-coord))

def insert(heap, item):
	heap.append(item)
	item_pos = len(heap) - 1	
	not_done = True
	while not_done:
		if item_pos % 2 == 0: #k = (pos - 2)/2
			if heap[item_pos] < heap[(item_pos - 2)/2] and item_pos > 1:				
				swap(heap, item_pos, (item_pos-2)/2)				
				item_pos = (item_pos-2)/2
			else:
				not_done = False
		else: #k = (pos - 1)/2
			if heap[item_pos] < heap[(item_pos - 1)/2] and item_pos > 0:				
				swap(heap, item_pos, (item_pos-1)/2)								
				item_pos = (item_pos-1)/2
			else:
				not_done = False
	
	return heap

def swap(list, cur_pos, new_pos):
	tmp = list[cur_pos]
	list[cur_pos] = list[new_pos]
	list[new_pos] = tmp
				
def delete(heap):
	ret_item = heap[0]	
	heap[0] = heap[-1]
	heap = heap[:-1]	
	cur_pos = 0
	not_done = True
	heap_size = len(heap)	
	while not_done:				
		left = 2*cur_pos + 1
		right = 2*cur_pos + 2
		if heap_size > right:
			if heap[cur_pos] > heap[right] and heap[cur_pos] > heap[left]:
				#greater than both, swap with lesser value
				if heap[left] <= heap[right]:
					swap(heap, cur_pos, left)					
					cur_pos = left
				else:
					swap(heap, cur_pos, right)					
					cur_pos = right
			elif heap[cur_pos] > heap[right]:
				swap(heap, cur_pos, right)				
				cur_pos = right
			elif heap[cur_pos] > heap[left]:
				swap(heap, cur_pos, left)				
				cur_pos = left
			elif heap[cur_pos] <= heap[left] and heap[cur_pos] <= heap[right]:				
				not_done = False			
		elif heap_size > left:
			if heap[cur_pos] > heap[left]:				
				swap(heap, cur_pos, left)				
				cur_pos = left				
				not_done = False
			else: not_done = False
		else: not_done = False
	ret_list = heap
	return ret_item, ret_list
	
'''
heap = []
target = (10, 10)

def mandist(p1, p2):
	x1, y1 = p1
	x2, y2 = p2	
	return abs(x1 - x2) + abs(y1 - y2)

for _ in range(10):
	x = randint(0, 20)
	y = randint(0, 20)
	dist = mandist((x, y), target)	
	heap = insert(heap, (dist, (x, y)))
	print heap
print "###"
val, heap = delete(heap)
print val, heap
'''	
