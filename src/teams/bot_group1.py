# bot.turn              (0 if a/x, 1 if b/y)
# bot.other             (reference to other bot object in your team)
# bot.position          (coordinates of current bot)
# bot.legal_positions   (list of legal positions)
# bot.walls             (coordinates of all the walls)
# bot.graph             (representation of maze. useful for shortest path)
# bot.shape             (maze shape)
# bot.homezone          (coordinates of all positions in your homezone)
# bot.food              (coordinates of all the food pellets IN YOUR HOMEZONE!)
# bot.shaded_food       (food in homezone that is in a 1 block radius of one or both of your bots)
# bot.track             (track the pathe the bot has taken)
# bot.score             (score of your team)
# bot.round             (round youre in)
# bot.random            (pseudo nr generator)   -use->  bot.random.choice(bot.legal_positions)
# bot.error_count       (nr of errors)
# bot.say('text')       
# bot.kills             
# bot.deaths            
# bot.enemy             (reference to enemy bots. same properties)  [0]/[1] attributes such as team_name are shared
# bot.enemy[0].food     (food you want to eat)
# bot.enemy[].position  (position of one of the enemy bots | is exact if in 5 block radius)
# bot.enemy[0].is_noisy (is TRUE if enemy is > 5 blocks away)

# networkx.shortest_path(graph, position, target)   (list of moves from the shortest path to an object)
# example:  path = networkx.shortest_path(bot.graph, bot.position, target)[1:]


import networkx as nx

TEAM_NAME = "Attack Bot"

def initialize_atk_state():
    return{
        "enemy": None,
        "target": None,
        "path": None,
        "deaths": 0,
        "HELP": 0
    }

def initialize_def_state():
    return{
        "target": None,
        "enemy_target": None,
        "path": None,
        "enemy0": None,
        "enemy1": None,
        "p_path": None,
        "deaths": 0,
        "def_state": None       #0 if patroling, 1 if defending, 2  if chase
    }

def attack(bot, state):         #brain of the attacker
    enemy = bot.enemy
    target = state[1]["target"]
    path = state[1]["path"]
    deaths = state[1]["deaths"]

    print("-----------------------------ATTACK-------------------------------------------")

    if target == None or target not in enemy[0].food or path == None:
        target, path = shortest_food(bot.position, enemy[0].food, bot.graph)


    n_step = path.pop(0)

    if n_step not in bot.homezone:
        safe_positions = []
        for pos in bot.legal_positions:
            if pos not in (enemy[0].position, enemy[1].position):
                safe_positions.append(pos)

        if n_step not in safe_positions:
            state[1]["target"] = None
            state[1]["path"] = None

            n_step = bot.random.choice(safe_positions)

    state[1]["target"] = target
    state[1]["path"] = path

    print("-------------------------------------------------------------------------------")

    return n_step

def defense(bot, state):            #brain of the defender
    enemies = bot.enemy
    enemy0 = state[0]["enemy0"]
    enemy1 = state[0]["enemy1"]
    target = state[0]["target"]
    p_path = state[0]["p_path"]
    path = state[0]["path"]
    def_state = state[0]["def_state"]
    enemy_target = state[0]["enemy_target"]

    print("-----------------------------DEFENSE-------------------------------------------")

    
    #berechnet die Bedrohungsstufe der Gegner
    enemy0 = threat_lvl(bot.enemy[0], bot.is_blue, bot.homezone, bot.shape), enemies[0].position, bot.round
    enemy1 = threat_lvl(bot.enemy[1], bot.is_blue, bot.homezone, bot.shape), enemies[1].position, bot.round


    #wenn kein Ziel vorhanden ist
    if target == None:
        if enemy0[0] != 0 or enemy1[0] != 0:
            path, target, p_path, state[1]["Help"] = defending(enemies, enemy0, enemy1, bot)
            def_state = 1
        else:
            path, target, def_state = patrol(bot, bot.is_blue)
            def_state = 0
    elif def_state == 0:                #wenn verteidiger patrolliert
        if enemy0[0] != 0 or enemy1[0] != 0:        #check ob 
            path, target, p_path, state[1]["Help"] = defending(enemies, enemy0, enemy1, bot)
            def_state = 1
    
    if enemy0[0] == 1 or enemy1[0] == 1:          #wenn gegner evtl in homezone ist
        path, target, p_path, state[1]["Help"] = defending(enemies, enemy0, enemy1, bot)
    
    #wenn gegner von seinem Weg abweicht
    if enemy0[0] == 2:                      
        if enemies[0].position not in p_path:
            path, target, def_state = chase(enemies[0].position, bot.position, bot.graph)
            def_state = 2
            enemy_target = 0
    elif enemy1[0] == 2:
        if enemies[1].position not in p_path:
            path, target, def_state = chase(enemies[1].position, bot.position, bot.graph)
            def_state = 2
            enemy_target = 1

    #wenn der gegner gejagt wird, berechne den weg
    if def_state == 2:
        path, target, def_state = chase(enemies[enemy_target].position, bot.position, bot.graph)

    if path == None:
        path = nx.shortest_path(bot.graph, bot.position, target)

    if path[1] not in bot.homezone:
        path, target, def_state = patrol(bot, bot.is_blue)
        enemy_target = None

    n_step = path.pop(1)       #n_step = next step


    if n_step == target:
        target = None

    state[0]["target"] = target
    state[0]["path"] = path
    state[0]["def_state"] = def_state
    state[0]["enemy_target"] = enemy_target
    state[0]["p_path"] = p_path
    state[0]["enemy0"] = enemy0
    state[0]["enemy1"] = enemy1

    print("-------------------------------------------------------------------------------")

    return n_step
    
def chase(enemy_pos, bot_pos, graph):
    path = nx.shortest_path(graph, bot_pos, enemy_pos)
    return path, enemy_pos, 2


def defending(enemies, enemy0, enemy1, bot):
    food = bot.food
    help = 0
    p_path = None
    path = None

    if enemy0[0] == 2:
        T_food, p_path = shortest_food(enemy0[1], bot.food, bot.graph)            
        path = nx.shortest_path(bot.graph, bot.position, T_food)

        print("p_path: ", p_path)

        while len(p_path) + 1 != len(path):
            if len(p_path) + 1 > len(path):
                p_path.pop()
                food.remove(T_food)
                T_food, np_path = shortest_food(enemy0[1], food, bot.graph)   #np_path (next predicted path) is a Hilfsvariable to add to the predicted path
                p_path.extend(np_path)
                print("p_path: ", p_path)
                path = nx.shortest_path(bot.graph, bot.position, T_food)
            else:
                while len(p_path) + 1 != len(path):
                    if len(p_path) == len(path):
                        break
                    p_path.pop()
                    print("p_path: ", p_path)
                    print("length: ", len(p_path))

                    path = nx.shortest_path(bot.graph, bot.position, p_path[-1])
                    print("path: ", path)
                    print("length: ", len(path))
                    
                break


        if enemy1[0] == 2:
            help = 2

    elif enemy1[0] == 2:
        T_food, p_path = shortest_food(enemy1[1], bot.food, bot.graph)            
        path = nx.shortest_path(bot.graph, bot.position, T_food)

        while len(p_path) + 1 != len(path):
            if len(p_path) + 1 > len(path):
                p_path.pop()
                food.remove(T_food)
                T_food, np_path = shortest_food(enemy1[1], food, bot.graph)
                p_path.extend(np_path)
                print("p_path: ", p_path)
                path = nx.shortest_path(bot.graph, bot.position, T_food)
            else:
                print("before while loop:")
                print("p_path: ", p_path)
                print("length: ", len(p_path))
                print("path: ", path)
                print("length: ", len(path))
                print("-----------------------------")
                while len(p_path) + 1 != len(path):
                    if len(p_path) == len(path):
                        break
                    p_path.pop()

                    print("p_path: ", p_path)
                    print("length: ", len(p_path))

                    path = nx.shortest_path(bot.graph, bot.position, p_path[-1])
                    print("path: ", path)
                    print("length: ", len(path))
                    
                break

    elif enemy0[0] == 1:
        path = nx.shortest_path(bot.graph, bot.position, enemies[0].position)
        if enemy1[0] == 1:
            help = 1       

    elif enemy0[1] == 1:
        path = nx.shortest_path(bot.graph, bot.position, enemies[1].position)

    return path, path[-1], p_path, help


def patrol(bot, blue):      #patrols the homezone
    graph = bot.graph
    position = bot.position
    walls = bot.walls

    path = None

    if blue == 1:
        x = int(bot.shape[0] / 2) -4        #x = x-coordinate of the patrol positions
    else:
        x = int(bot.shape[0] / 2) +3
    
    patrol_position = [(x, int(bot.shape[1] / 2) -2), (x, int(bot.shape[1] / 2) + 2)]

    while patrol_position[0] in walls:
        patrol_position[0] = (patrol_position[0][0], patrol_position[0][1] - 1)

    while patrol_position[1] in walls:
        patrol_position[1] = (patrol_position[1][0], patrol_position[1][1] + 1)

    if position == patrol_position[0]:
        path = nx.shortest_path(graph, position, patrol_position[1])
    else:
        path = nx.shortest_path(graph, position, patrol_position[0])

    return path, path[-1], 0


# bot.is_blue --> 1 if blue, 0 if red
def threat_lvl(enemy, color, home, size):   #returns: threat lvl (0=no, 1=maybe, 2=YES!), the position of that enemy
    threat = None

    if not enemy.is_noisy:
        if enemy.position in home:
            threat = 2
        else:
            threat = 0
    elif enemy.is_noisy:
        maze_half = int(size[0] / 2)

        if color == 1:                      
            x = enemy.position[0] - 2

            if x <= maze_half:
                threat = 1
            else:
                threat = 0
        elif color == 0:
            x = enemy.position[1] + 2

            if x > maze_half:
                threat = 1
            else:
                threat = 0
    
    return threat

def shortest_food(pos, food, graph):                #gets the nearest food and the path to that pallet
    i = 100
    path = None                                    #path to the closest food pallet
    n_food = None                                  #next food (as in the pallet that turns out to be the closest)

    for nr in food:
        path_ex = nx.shortest_path(graph, pos, nr)  #place holder to see how long the path to each pallet is
        if len(path_ex) < i:
            i = len(path_ex)
            path = path_ex
            n_food = nr

    return n_food, path

def calc_path(graph, position, target):
    path = nx.shortest_path(graph, position, target)
    return path

def move(bot, state):
    turn = bot.turn
    n_step = None

    if state == {}:
        state[0] = initialize_def_state()
        state[1] = initialize_atk_state()

        #save what color our bots are:
        if bot.char == "a" or bot.char == "b":
            state[0]["color"] = 0                #blue
        elif bot.char == "x" or bot.char == "y":
            state[0]["color"] = 1                #red

    if state[turn]["deaths"] != bot.deaths:

        state[turn]["path"] = None
        state[turn]["target"] = None
        state[turn]["deaths"] = bot.deaths

    if turn == 0:
        n_step = defense(bot, state)
    elif turn == 1:
        n_step = attack(bot, state)

    return n_step
