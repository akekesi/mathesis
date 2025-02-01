import networkx

TEAM_NAME = 'Code4mation'

def init_attack_state():
    return {
            "attack_target": None,
            "attack_path": None,
        }

def move(bot, state):
    """
    # for better overwiev in the console when debugging
    print()
    print(f"Round {bot.round}", "turn", bot.turn)
    """

    # The state dictionary is initially empty
    if state == {}:
        # Initialize the state dictionary.
        # Each bot needs its own state dictionary to keep track of the
        # food targets.
        state[0] = init_attack_state()
        state[1] = init_attack_state()
        # further information is stored under state[2]
        state[2] = {
        # gaps (on the blue side) of the border
        "border_gaps": [],

        # quadrants of the map
        "blue_upper" : [],
        "blue_lower" : [],
        "red_upper" : [],
        "red_lower" : [],

        # exact positions of the enemies
        "ex_en_0" : None,
        "ex_en_1" : None,

        # the intruder we have targeted
        # either None, 0, 1
        "intruder" : None,
        }
    
    # gaps in the border are appended to the list state[2]["border_gaps"]
    if bot.is_blue:
        for coordinate in bot.graph:
            if coordinate[0] == 15:
                state[2]["border_gaps"].append(coordinate)
    else:
         for coordinate in bot.graph:
            if coordinate[0] == 16:
                state[2]["border_gaps"].append(coordinate)
    
    # Seperating the map into everlapping quadrants (i.e. an enemy can be in two quadrants at the same time)
    for coordinate in bot.graph:
        if coordinate[0] <= 15:
            if coordinate[1] <= 10:
                state[2]["blue_upper"].append(coordinate)
            if coordinate[1] >= 5:
               state[2]["blue_lower"].append(coordinate)
        else:
            if coordinate[1] <= 10:
                state[2]["red_upper"].append(coordinate)
            if coordinate[1] >= 5:
               state[2]["red_lower"].append(coordinate)

    # If we know the exact location of an enemy, we save it in a list. In addition, we save the current round.
    if not bot.enemy[0].is_noisy:
        state[2]["ex_en_0"] = [bot.enemy[0].position, bot.round]
    # If we have saved the enemy's position earlier, we check if it is still up to date.
    if state[2]["ex_en_0"] is not None:
        if (bot.round - state[2]["ex_en_0"][1]) > 2:
            state[2]["ex_en_0"] = None
    # The same for the other enemy
    if not bot.enemy[1].is_noisy:
        state[2]["ex_en_1"] = [bot.enemy[1].position, bot.round]
    if state[2]["ex_en_1"] is not None:
        if (bot.round - state[2]["ex_en_1"][1]) > 3:
            state[2]["ex_en_1"] = None

    def ex_en_pos(targeted):
        """
        targeted must be 0 or 1.
        This function returns the most exact available position of an enemy.
        """
        if targeted not in [0, 1]:
            raise ValueError("targeted must be 0 or 1")
        
        # If we know the exact position of the enemy, we return it.
        if not bot.enemy[targeted].is_noisy:
            enemy_coordinates = bot.enemy[targeted].position
        # Otherwise: If we have saved the enemy's position earlier, we use it.
        elif state[2][f"ex_en_{targeted}"] is not None:
            enemy_coordinates = state[2][f"ex_en_{targeted}"][0]
        # Otherwise: We use the noisy position.
        else:
            enemy_coordinates = bot.enemy[targeted].position

        return enemy_coordinates

    def attacking():
        # We create a list of paths to every enemy food pellet and sort it by length.
        food_paths = []
        for pellet in bot.enemy[0].food:
            food_paths.append(networkx.shortest_path(bot.graph, bot.position, pellet))
        food_paths.sort(key=len)

        # For each coordinate of the shortest path to the closest enemy food pellet, we check if the bot is closer to it than the enemy.
        for i in range(2):
            for coordinate in food_paths[0]:
                bot_food_path = networkx.shortest_path(bot.graph, bot.position, coordinate)
                enemy_food_path = networkx.shortest_path(bot.graph, ex_en_pos(i), coordinate)
                if len(bot_food_path) < len(enemy_food_path):
                    safe_path = True
                else:
                    safe_path = False
                    break
            if not safe_path: break
        
        if safe_path:
            # If the path is safe, we attack the enemy food pellet.
            state[bot.turn]["attack_target"] = food_paths[0][-1]
        else:
            # If the path is unsafe, we go to the default positions: the highest and the lowest gap in the border.
            state[0]["attack_target"] = state[2]["border_gaps"][0]
            state[1]["attack_target"] = state[2]["border_gaps"][-1]

    # If intruder is not in homezone anymore:
    if state[2]["intruder"] is not None:
        if ex_en_pos(state[2]["intruder"]) not in bot.homezone:
            state[2]["intruder"] = None

    # If we do not know the intruder yet:
    if state[2]["intruder"] is None:
        # checking if an enemy is in our homezone
        if ex_en_pos(1) in bot.homezone:
            state[2]["intruder"] = 1
        elif ex_en_pos(0) in bot.homezone:
            state[2]["intruder"] = 0

    # attacking and positioning the supporter
    if state[2]["intruder"] is not None:
        if bot.is_blue:
            if ex_en_pos(state[2]["intruder"]) in state[2]["blue_upper"] and ex_en_pos(state[2]["intruder"]) in state[2]["blue_lower"]:
                # If the intruder is in the middle of the map (i.e. in both quadrants), we attack it with both bots.
                state[0]["attack_target"] = ex_en_pos(state[2]["intruder"])
                state[1]["attack_target"] = ex_en_pos(state[2]["intruder"])
            elif ex_en_pos(state[2]["intruder"]) in state[2]["blue_upper"]:
                # If the intruder is in the upper quadrant, bot 0 attacks it and bot 1 comes closer.
                #pos_supporter()
                #state[1]["attack_target"] = state[2]["border_gaps"][-3]
                attacking()
                state[0]["attack_target"] = ex_en_pos(state[2]["intruder"])
            elif ex_en_pos(state[2]["intruder"]) in state[2]["blue_lower"]:
                # If the intruder is in the lower quadrant, bot 1 attacks it and bot 0 comes closer.
                #pos_supporter()
                #state[0]["attack_target"] = state[2]["border_gaps"][2]
                attacking()
                state[1]["attack_target"] = ex_en_pos(state[2]["intruder"])
        else:
            if ex_en_pos(state[2]["intruder"]) in state[2]["red_upper"] and ex_en_pos(state[2]["intruder"]) in state[2]["red_lower"]:
                # If the intruder is in the middle of the map (i.e. in both quadrants), we attack it with both bots.
                state[0]["attack_target"] = ex_en_pos(state[2]["intruder"])
                state[1]["attack_target"] = ex_en_pos(state[2]["intruder"])
            elif ex_en_pos(state[2]["intruder"]) in state[2]["red_upper"]:
                attacking()
                state[0]["attack_target"] = ex_en_pos(state[2]["intruder"])
            elif ex_en_pos(state[2]["intruder"]) in state[2]["red_lower"]:
                attacking()
                state[1]["attack_target"] = ex_en_pos(state[2]["intruder"])

    elif state[2]["intruder"] is None:
        attacking()

    # If an enemy is in our homezone and it is right next to us, we attack it.
    if ex_en_pos(0) in bot.homezone or ex_en_pos(1) in bot.homezone:
        if len(networkx.shortest_path(bot.graph, bot.position, bot.enemy[0].position)) <= 1:
            state[bot.turn]["attack_target"] = bot.enemy[0].position
        elif len(networkx.shortest_path(bot.graph, bot.enemy[1].position)) <= 1:
            state[bot.turn]["attack_target"] = bot.enemy[1].position

    # If the bot is already at its target, it does not move.
    if bot.position == state[bot.turn]["attack_target"]:
        next_pos = bot.position
    else:
        next_pos = networkx.shortest_path(bot.graph, bot.position, state[bot.turn]["attack_target"])[1]

    # Speech: The bot says what it is doing.
    if state[2]["intruder"] is not None:
        bot.say(f"Intruder: {state[2]['intruder']}")
    else:
        bot.say(f"Target: {state[bot.turn]['attack_target']}")

    # If next_pos is in the enemy's homezone
    counter = 0
    if next_pos not in bot.homezone:
        # While next_pos is next to an enemy (i.e. it could kill us in the next round), we choose a random position.
        while next_pos == bot.position or len(networkx.shortest_path(bot.graph, next_pos, ex_en_pos(0))) <= 2 or len(networkx.shortest_path(bot.graph, next_pos, ex_en_pos(1))) <= 2:
            counter += 1
            next_pos = bot.random.choice(bot.legal_positions) 
            bot.say("RANDOM")
            if counter >= 10000: break # Ensures that the bot does not get stuck in an infinite loop and prevents a timeout.

    return next_pos