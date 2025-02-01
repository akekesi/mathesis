# very funny game

# Replay this game with --seed 4107593880482396555
# Using layout 'normal_361'
# ᗧ blue team: 'can can'
# ᗧ red team: 'Clever Bot'

import networkx

TEAM_NAME = 'Cant touch this'

# *** INFORMATIONAL FUNCTIONS ***

# These function will provide information based on ???

def initialize_state():
    """

    """
    return {
            "attack_target": None,
            "attack_path": None,
            "enemy_1_pos": [],
            "enemy_2_pos": [],
        }

def get_adjacent_info(bot, x, y, ignore_path = 1, path = []):
	""" 
    This function returns a dictionary containing information about the surrounding walls of a coordinate. 
	
    dict entries => 'num_of_walls', 'adjacent_walls'
    
	'adjacent_walls' is a dictionary with four directions as "keys". each direction has a "bool" varibale and a "tuple of integers"
    	the "bool" value represents if there is a wall in the according direction (up, down, right or left).
    	the tuple is the coordinate (up, down, right or left)
    
    'num_of_walls' is the number of walls that surround the x and y parameter
    
    PARAMETERS:
    'ignore_path' and 'path' are used to count a list of coordinates as walls
	"""
	adjacent_walls = {'up': (bool, (int, int)), 'down': (bool, (int, int)), 'right': (bool, (int, int)), 'left': (bool, (int, int))}
	adjacent_info = {'num_of_walls': int, 'adjacent_walls': dict}
	
	if (ignore_path == 1):
		is_up_wall = (x, y-1) in bot.walls
		is_down_wall = (x, y+1) in bot.walls
		is_right_wall = (x+1, y) in bot.walls
		is_left_wall = (x-1, y) in bot.walls
	else:
		is_up_wall = (x, y-1) in bot.walls or (x, y-1) in path
		is_down_wall = (x, y+1) in bot.walls or (x, y+1) in path
		is_right_wall = (x+1, y) in bot.walls or (x+1, y) in path
		is_left_wall = (x-1, y) in bot.walls or (x-1, y) in path
	adjacent_walls['up'] = (is_up_wall, (x, y-1))
	adjacent_walls['down'] = (is_down_wall, (x, y+1))
	adjacent_walls['right'] = (is_right_wall, (x+1, y))
	adjacent_walls['left'] = (is_left_wall, (x-1, y))

	adjacent_info["adjacent_walls"] = adjacent_walls
	adjacent_info["num_of_walls"] = sum([is_up_wall, is_down_wall, is_left_wall, is_right_wall])

	# print("pos:", x, y, "sum:", sum([is_up_wall, is_down_wall, is_left_wall, is_right_wall]))
	return adjacent_info

def get_deadends(bot):
	""" 'get_deadends' scan the enemy side and compare each coordinate 
    to find out where a dead end is located
    
    Parameter
    -------
    bot : Bot
		the 'bot' parameter is used 
    
    Return
    -------
    deadends : array of tuples
		each tuple represents the END of a dead end

	"""
	deadends = []
    # the 'width' and 'hight' variables are used to determin the size of the maze
	width = None
	height = bot.shape[1]

	# using the bot variable 'start' is set to the left most X coordinate of the enemy side
    # 'width' is set to the right most X coordinate of the enemy side
	if not (bot.is_blue):
		start = 1
		width = (bot.shape[0] / 2) - 1
	else:
		start = (bot.shape[0] / 2)
		width = (bot.shape[0]) - 1

	# this 2 dimensional loop will check each coordinate (note) of our maze
	for x in range(int(start), int(width)):
		for y in range(1, height):

			# define what the condition for the current coordinate if it is a wall
			is_wall = (x, y) in bot.walls

			# check if the current position is NOT a wall
			if (not is_wall):
				adjacent_info = get_adjacent_info(bot, x, y, 1)
				# use the 'get_adjacent_info' function to find out
				# how many walls the current coordinate is surrounded by
				if (adjacent_info['num_of_walls'] == 3):
					deadends.append((x, y))
	
	return deadends

def get_next_deadend_position(bot, path = [], position = (0, 0)):
	""" 'get_next_deadend_position' starting from a deadend, this function will find out
    where it should move.
    
    Parameters
    -------
    bot : Bot
		the bot object
    
	path : array of tuples
		current path, positions of the deadends

	position : tuple
		the previous position
    """

	x = position[0]
	y = position[1]

	adjacent_info = get_adjacent_info(bot, x, y, 0, path)

	for direction, wall_info in adjacent_info['adjacent_walls'].items():
		# check each surrounding position, if the position is not a wall,
		# it will be saved in next_position.
		# (this works because this function is only used when there are 3 walls)
		if wall_info[0] == False:
			next_position = wall_info[1]

	return next_position

def get_food_in_deadends(bot):
    """ 'get_food_in_deadends' starting from a deadend, move through the dead end,
    save each food pellet and return a array.
    
    Parameters
    -------
    bot : Bot
		the bot object
          
    Returns
    -------
    food_in_deadends : array of tuples
        this array will contain each food if it's located in a dead end
    """

    food_in_deadends = []

    deadends = get_deadends(bot)
	
    for deadend in deadends:
        enemy_food = bot.enemy[0].food
        position = deadend
        path = []

        while (get_adjacent_info(bot, position[0], position[1], 0, path)['num_of_walls'] > 2):
            if position in enemy_food:
                food_in_deadends.append(position)

            path.append(position)
            position = get_next_deadend_position(bot, path, position)

    return food_in_deadends

# --- x ---

def legal_moves_from(pos):
        '''
        legal_moves_from returns all positions around our bot(including walls, it doesn't matter for this use case)
        
        Parameter:
            pos: Tuple
                The position we want all legal moves from
                
        Returns:
            list of legal moves: list
        '''
        legal_moves = []
        legal_moves.append(pos)
        legal_moves.append((pos[0] + 1, pos[1]))  # Move one step in the positive x direction
        legal_moves.append((pos[0] - 1, pos[1]))  # Move one step in the negative x direction
        legal_moves.append((pos[0], pos[1] + 1))  # Move one step in the positive y direction
        legal_moves.append((pos[0], pos[1] - 1))  # Move one step in the negative y direction
        return legal_moves
        
def is_camped(last_3_moves1, last_3_moves2, food):
    '''
    is_camped finds all food pellets that are camped by the enemy.
    Camped pellets are defined as pellets that have been in the enemies shadow for the last 3 rounds.
    
    Parameters:
        last_3_moves1: list
            the last three moves of bot 1
        last_3_moves2: list
            the last three moves of bot 2
        food: list
            list of food pellets
            
    Returns:
        camped food pellets:list
    '''
    is_camped = []
    
    for num in food:
        if num in legal_moves_from(last_3_moves1[0]) and num in legal_moves_from(last_3_moves1[1]) and num in legal_moves_from(last_3_moves1[2]):
            is_camped.append(num)        
        if num in legal_moves_from(last_3_moves2[0]) and num in legal_moves_from(last_3_moves2[1]) and num in legal_moves_from(last_3_moves2[2]):
            is_camped.append(num)
    return is_camped

def get_target(G,bot_pos,enemy_food):
    '''
    get_target finds the closest food to our bot and sets it as our target
    
    Parameters:
        G: the nx.Graph 
        bot_pos: Tuple 
            the position of our bot
        enemy_food: list
            the list of targets 
    
    Returns: Tuple
        The closest food-pellet to our bot.
    '''
    x=1000
    target = None

    #find closest food to define a target
    for num in enemy_food:
                        
        shortest_path1 = networkx.shortest_path(G,bot_pos,num)
        length = len(shortest_path1)

        if length < x:
            x = length
            target = num

    return target

def get_different_target(G,bot_pos,enemy_food,unwanted_target):
    """
    Does the same thing as the above function with one key difference.

    unwanted_target = list of targets that we will diregard when choosing our target.
    """
    x=1000
    target = None

    #find closest food to define a target
    for num in enemy_food:
        if num in unwanted_target:
            continue

        shortest_path1 = networkx.shortest_path(G,bot_pos,num)
        length = len(shortest_path1)

        if length < x:
            x = length
            target = num

    return target     
                
def get_food_in_top_half(food):
    """ get_food_in_top_half will return a list of pellets that stops after the y coordinate 7

    Parameter
    ---------
    food : list of tuples
        The list of all pellets
    
    Returns
    ---------
    food_in_top_half : array of tuples
        The list of pellets with a Y coordinate that is lower than 7
    """

    food_in_top_half = []

    for pellet in food:
        if pellet[1] < 7:
            continue
        food_in_top_half.append(pellet)

    return food_in_top_half
    
def get_food_in_bottom_half(food):
    """ get_food_in_bottom_half will return a list of pellets that 
    only includes pellets with a Y coordinate higher than 8

    Parameter
    ---------
    food : list of tuples
        The list of all pellets
    
    Returns
    ---------
    food_in_top_half : array of tuples
        The list of pellets with a Y coordinate that is higher than 8
    """

    food_in_bottom_half = []

    for pellet in food:
        if pellet[1] > 8:
            continue
        food_in_bottom_half.append(pellet)

    return food_in_bottom_half

#DEADLOCK FUNCTIONS//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    
def distance(pos1, pos2):
    """ 'distance' get the distance between two coordinates 
    """
    return (abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]))

def is_bot_deadlocked(bot):
    """ 'is_bot_deadlocked' find out if the current bot is deadlocked (is being trapped by the enemy)

    Returns
    -------
    True or False : boolean
        TRUE > falls die variablen 'b_enemy_close' und 'b_distance_past' 

    """
    enemy = bot.enemy

    # Check if an enemy is near
    if not (enemy[0].is_noisy):
        closest_enemy = enemy[0]
    elif not (enemy[1].is_noisy):
        closest_enemy = enemy[1]
    else:
        closest_enemy = None

    if closest_enemy:
        b_enemy_close = (distance(bot.position, closest_enemy.position) <= 3)

        # past moves
        distance_of_past = list(set(bot.track[-6:]))
        b_distance_past = (len(distance_of_past) <= 2)

        # **DEBUG**
        # print("bot", bot.turn, 
        #         "\nenemy", closest_enemy.turn, 
        #         "\nb_enemy", b_enemy_close, 
        #         "\npast", distance_of_past, 
        #         "\nb_past", b_distance_past,
        #         "\n\n")
        if (b_enemy_close and b_distance_past):
            #breakpoint()
            return True
    else:
        return False
        
def copy_graph(bot):
    '''
    Creates a new nx.graph without the legal positions of our enemy,
    thereby forcing our bot to find a path around our enemies.
    
    Parameters
        bot: Bot
        the bot object
    Returns:
        A new graph: nx.Graph
    '''
    graph_copy = bot.graph.copy()
    # Identify bad nodes (enemy legal positions) as a set
    bad_nodes = set(bot.enemy[0].legal_positions) | set(bot.enemy[1].legal_positions)
    if bot.position in bad_nodes:
        bad_nodes.remove(bot.position)
    # remove bad eggs 
    graph_copy.remove_nodes_from(bad_nodes)
    #make sure our bot position is still in it
    
        
    return graph_copy

#START //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def move(bot, state):
    if state == {}:
        # Initialize the state dictionary.
        # Each bot needs its own state dictionary to keep track of food target
        state[0] = initialize_state()
        state[1] = initialize_state()
        
    # shorten the variable from "bot.enemy" to "enemy"
    enemy = bot.enemy

    # create two lists of the avaible food
    targets_bot_0 = get_food_in_top_half(enemy[0].food)
    targets_bot_1 = get_food_in_bottom_half(enemy[0].food)
    
    #Get values from state
    target = state[bot.turn]["attack_target"]
    path = state[bot.turn]["attack_path"]
    
    #Enemy positions stored in state
    state[bot.turn]["enemy_1_pos"].append(enemy[0].position)
    state[bot.turn]["enemy_2_pos"].append(enemy[1].position)
    enemy_1_pos = state[bot.turn]["enemy_1_pos"]
    enemy_2_pos = state[bot.turn]["enemy_2_pos"]
    
    #Get the last 3 moves of each bot
    if bot.round > 2:
        last_3_moves1 = enemy_1_pos[-3:]
        last_3_moves2 = enemy_2_pos[-3:]
    
    #If there is no target we find one here    
    if (target is None) or (target not in enemy[0].food):
        
        #find closest food to define a target
        if bot.turn == 0 and len(targets_bot_0) > 0:
            target = get_target(bot.graph, bot.position,targets_bot_0)
            path = networkx.shortest_path(bot.graph, bot.position, target)[1:]
        if bot.turn == 1 and len(targets_bot_1) > 0:
            target = get_target(bot.graph, bot.position,targets_bot_1)
            path = networkx.shortest_path(bot.graph, bot.position, target)[1:]
        
        #find the shortest path and save it in the state
        
        state[bot.turn]["attack_path"] = path
        state[bot.turn]["attack_target"] = target    
          
    # If we are deadlocked find a new path
    if is_bot_deadlocked(bot) and target:
        print('im deadlocked!')
        bot.say('im deadlocked!')
        
        new_graph = copy_graph(bot)
        
        if target not in new_graph.nodes:
            print('shit')
            bot.say('shit')
            new_graph = bot.graph

        try:
            path = networkx.shortest_path(new_graph, bot.position, target)
            if len(path)>0:
                
                path.pop(0)    
            state[bot.turn]["attack_path"] = path
        except networkx.NetworkXNoPath:
            pass 
        #Deadlock tester seeds
        #--seed 2622592952459897599
        #--seed 6428248470586952279        
        
    #Before we proceed we should check if our target is camped
    if bot.round > 2:
        camped = is_camped(last_3_moves1, last_3_moves2, enemy[0].food)        
                        
        #get new target if it is camped
        if target in camped:
            bot.say('dirty camper!')
            target = get_different_target(bot.graph, bot.position, enemy[0].food, camped)
            if target:
                path = networkx.shortest_path(bot.graph, bot.position, target)[1:]

    # implementation: avoid the dead ends if a bot is nearby            *****
    if not (enemy[0].is_noisy):
        closest_enemy = enemy[0]
    elif not (enemy[1].is_noisy):
        closest_enemy = enemy[1]
    else:
        closest_enemy = None

    if closest_enemy:
        distance_to_enemy = distance(bot.position, closest_enemy.position)
        if distance_to_enemy <= 2 and target in get_food_in_deadends(bot) and len(enemy[0].food) > 1:
            target = get_different_target(bot.graph, bot.position, enemy[0].food, target)
            path = networkx.shortest_path(bot.graph, bot.position, target)[1:]

    if (target is None) or (target not in enemy[0].food):
        bot.say('failsafe')
        target = get_target(bot.graph, bot.position, enemy[0].food)
        path = networkx.shortest_path(bot.graph, bot.position, target)[1:]
    # get the next position along the shortest path to reach our target
    
    next_pos = path.pop(0)
    
    # if we are not in our homezone we should check if it is safe to proceed
    
    if next_pos not in bot.homezone:
        # get a list of safe positions
        safe_positions = []
        
        for pos in bot.legal_positions:
            if pos not in enemy[0].legal_positions and pos not in enemy[1].legal_positions:
                safe_positions.append(pos)                
        
        # we are running into our imminent demise
        if next_pos not in safe_positions:
            # abort!
            # overwrite our target
            # We will choose a new target in the next round
            state[bot.turn]["attack_target"] = None
            state[bot.turn]["attack_path"] = None           
            bot.say('oh boi')
            

            # Choose one safe position at random(if there is one)  
            if safe_positions: 
                next_pos = bot.random.choice(safe_positions)
            
              
    return next_pos