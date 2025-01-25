# TODO: avoid suicide where randomchoice is used!
# TODO: defender's shortest path to the enemy instead of waiting in the middle point (even if enemy is not in the homezone)
# TODO: defender's shortest path between enemy and pellet
# TODO-?: Which distance_*() function should be used?
# TODO-?: Is path always longer than 1? (if the pellet is moved to the bot's position)


import networkx


TEAM_NAME = "group2 pelita bot 00"
SAFE_DISTANCE_ENEMYZONE = 3  # minimum distance to opponents in enemyzone
SAFE_DISTANCE_HOMEZONE = 2   # minimum distance to opponents in homezone # TODO: test with 2 or 1
DEADLOCK_LAST_STEPS = 6
DEADLOCK_REPETITION = 3


def distance_theo(pos1, pos2):
    """Returns the Manhattan distance between two positions."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def distance_real(graph, pos1, pos2):
    """Returns the lenght of shortest path between two positions."""
    return len(networkx.shortest_path(G=graph, source=pos1, target=pos2))


def move(bot, state):
    enemies = bot.enemy
    enemies_pos = [enemy.position for enemy in enemies]
    enemies_pos_homezone = [enemy_pos for enemy_pos in enemies_pos if enemy_pos in bot.homezone]

    bot_in_homezone = bot.position in bot.homezone

    # strategy of the 1. bot (bot-a or bor-x)
    if bot.char in ["a", "x"]:
        next_pos_1 = None

        # bot is in homezone and there is enemy in homezone
        # try to catch the enemy in homezone, if the distance is less than SAFE_DISTANCE_HOMEZONE
        if bot_in_homezone and enemies_pos_homezone:
            closest_enemy = min(enemies_pos_homezone, key=lambda pos: distance_theo(pos1=bot.position, pos2=pos))

            if distance_theo(pos1=bot.position, pos2=closest_enemy) <= SAFE_DISTANCE_HOMEZONE:
                path_to_enemy = networkx.shortest_path(G=bot.graph, source=bot.position, target=closest_enemy)
                next_pos_1 = path_to_enemy[1] if len(path_to_enemy) > 1 else bot.position # TODO-?: Is if-else necessary?

        # bot is in enemyzone or there is no catchable enemy in homezone
        if not next_pos_1:
            # define safe positions
            legal_positions = [pos for pos in bot.legal_positions if pos != bot.position]
            bot.random.shuffle(legal_positions)
            if not legal_positions:
                legal_positions = [bot.position]
            safe_positions = [
                pos for pos in legal_positions
                if all(distance_theo(pos1=pos, pos2=enemies_pos[i]) >= SAFE_DISTANCE_ENEMYZONE for i in range(2))
            ]

            # try to catch the closest, safe pellet
            if safe_positions:
                path_length = float("inf")
                for pellet in bot.enemy[0].food:
                    path_to_pellet = networkx.shortest_path(G=bot.graph, source=bot.position, target=pellet)
                    if len(path_to_pellet) < path_length and path_to_pellet[1] in safe_positions: # TODO-?: Is path always longer than 1? (if the pellet is moved to the bot's position)
                        next_pos_1 = path_to_pellet[1]
                        path_length = len(path_to_pellet)
                
                # no path to pellet in safe_positions
                if not next_pos_1:
                    next_pos_1 = bot.random.choice(safe_positions)
            
            # no safe position in enemyzone
            else:
                # redefine safe positions
                max_dist = float("-inf")
                legal_positions_random = list(bot.legal_positions)
                bot.random.shuffle(legal_positions_random)
                for pos in legal_positions_random:
                    min_dist_to_enemy = min([distance_theo(pos1=pos, pos2=enemy_pos) for enemy_pos in enemies_pos])
                    if min_dist_to_enemy >= max_dist and pos not in enemies_pos:
                        max_dist = min_dist_to_enemy
                        safe_positions.append(pos)

                # try to catch the closest, least dangerous pellet
                path_length = float("inf")
                for pellet in bot.enemy[0].food:
                    path_to_pellet = networkx.shortest_path(G=bot.graph, source=bot.position, target=pellet)
                    if len(path_to_pellet) < path_length and path_to_pellet[1] in safe_positions: # TODO-?: Is path always longer than 1? (if the pellet is moved to the bot's position)
                        next_pos_1 = path_to_pellet[1]
                        path_length = len(path_to_pellet)

        next_pos = next_pos_1 if next_pos_1 else bot.position

        # deadlock
        if len(bot.track) > DEADLOCK_LAST_STEPS:
            if len([pos for pos in bot.track[-DEADLOCK_LAST_STEPS:] if pos == next_pos]) >= DEADLOCK_REPETITION:
                safe_positions = [pos for pos in bot.legal_positions if pos in bot.homezone and pos not in enemies_pos]
                next_pos = bot.random.choice(safe_positions) if safe_positions else next_pos
                # TODO-DEADLOCK:  pelita group2_pelita_bot_00.py demo06_switching_bots.py --seed 3245525151750523456

    # strategy of the 2. bot (bot-b or bor-y)
    elif bot.char in ["b", "y"]:
        next_pos_2 = None

        # define graph of homezone
        graph_homezone = bot.graph.copy()
        for pos in bot.graph: 
            if pos not in bot.homezone:
                graph_homezone.remove_node(pos)

        # bot is in homezone and there is enemy in homezone
        if bot_in_homezone and enemies_pos_homezone:
            closest_enemy = min(enemies_pos_homezone, key=lambda pos: distance_theo(pos1=bot.position, pos2=pos))
            path_to_enemy = networkx.shortest_path(G=graph_homezone, source=bot.position, target=closest_enemy)
            next_pos_2 = path_to_enemy[1] if len(path_to_enemy) > 1 else bot.position# TODO-?: Is path always longer than 1?

        # middle position of homezone
        column_middle = [pos for pos in bot.graph if pos[0] == 15] 
        zu_mitte = networkx.shortest_path(graph_homezone, bot.position, column_middle[len(column_middle) // 2])
        next_pos_2_to_middle = zu_mitte[1] if len(zu_mitte) > 1 else bot.position

        next_pos = next_pos_2 if next_pos_2 else next_pos_2_to_middle

    return next_pos
