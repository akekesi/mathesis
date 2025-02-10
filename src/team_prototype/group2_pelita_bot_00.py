import networkx


TEAM_NAME = "group2 pelita bot 00"
SAFE_DISTANCE_ENEMYZONE = 3  # minimum distance to opponents in enemyzone
SAFE_DISTANCE_HOMEZONE = 2   # minimum distance to opponents in homezone # TODO: test with 2 or 1
DEADLOCK_LAST_STEPS = 6      # number of last steps to check for deadlock
DEADLOCK_REPETITION = 3      # number of repetitions to detect deadlock


def distance_theo(pos1, pos2):
    """Returns the Manhattan distance between two positions."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def distance_real(graph, pos1, pos2):
    """Returns the lenght of shortest path between two positions."""
    return len(networkx.shortest_path(G=graph, source=pos1, target=pos2))


def move(bot, state):
    # define enemies and their positions
    enemies = bot.enemy
    enemies_pos = [enemy.position for enemy in enemies]
    enemies_pos_homezone = [enemy_pos for enemy_pos in enemies_pos if enemy_pos in bot.homezone]

    # define graph of homezone
    graph_homezone = bot.graph.copy()
    for pos in bot.graph: 
        if pos not in bot.homezone:
            graph_homezone.remove_node(pos)

    # middle position of border in homezone
    column_middle = [pos for pos in graph_homezone if pos[0] in [15, 16]]

    # strategy of the 1. bot (bot-a or bot-x)
    if bot.char in ["a", "x"]:
        next_pos_1 = None

        # bot is in homezone and there is enemy in homezone
        # try to catch the enemy in homezone, if the distance is less than SAFE_DISTANCE_HOMEZONE
        if bot.position in bot.homezone and enemies_pos_homezone:
            closest_enemy = min(enemies_pos_homezone, key=lambda pos: distance_real(graph=bot.graph, pos1=bot.position, pos2=pos))

            # distance to closest enemy is less than SAFE_DISTANCE_HOMEZONE
            if distance_real(graph=bot.graph, pos1=bot.position, pos2=closest_enemy) <= SAFE_DISTANCE_HOMEZONE:
                path_to_enemy = networkx.shortest_path(G=bot.graph, source=bot.position, target=closest_enemy)
                next_pos_1 = path_to_enemy[1] if len(path_to_enemy) > 1 else bot.position

            # do not follow enemy if it is in its own homezone
            if next_pos_1 not in bot.homezone:
                next_pos_1 = None

        # bot is in enemyzone or there is no catchable enemy in homezone
        if not next_pos_1:
            # define safe positions
            legal_positions = [pos for pos in bot.legal_positions if pos != bot.position]
            bot.random.shuffle(legal_positions)
            if not legal_positions:
                legal_positions = [bot.position]
            safe_positions = [
                pos for pos in legal_positions
                if all(distance_real(graph=bot.graph, pos1=pos, pos2=enemies_pos[i]) >= SAFE_DISTANCE_ENEMYZONE for i in range(2))
            ]

            # try to catch the closest, safe pellet
            if safe_positions:
                path_length = float("inf")
                for pellet in bot.enemy[0].food:
                    path_to_pellet = networkx.shortest_path(G=bot.graph, source=bot.position, target=pellet)
                    if len(path_to_pellet) < path_length and path_to_pellet[1] in safe_positions:
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
                    min_dist_to_enemy = min([distance_real(graph=bot.graph, pos1=pos, pos2=enemy_pos) for enemy_pos in enemies_pos])
                    if min_dist_to_enemy >= max_dist and pos not in enemies_pos:
                        max_dist = min_dist_to_enemy
                        safe_positions.append(pos)

                # try to catch the closest, least dangerous pellet
                path_length = float("inf")
                for pellet in bot.enemy[0].food:
                    path_to_pellet = networkx.shortest_path(G=bot.graph, source=bot.position, target=pellet)
                    if len(path_to_pellet) < path_length and path_to_pellet[1] in safe_positions:
                        next_pos_1 = path_to_pellet[1]
                        path_length = len(path_to_pellet)
                    else:
                        safe_positions = [pos for pos in safe_positions if pos != bot.position]
                        if safe_positions:
                            next_pos_1 = bot.random.choice(safe_positions)
    
        next_pos = next_pos_1 if next_pos_1 else bot.position

        # deadlock
        if len(bot.track) > DEADLOCK_LAST_STEPS:
            if len([pos for pos in bot.track[-DEADLOCK_LAST_STEPS:] if pos == next_pos]) >= DEADLOCK_REPETITION:
                safe_positions = [pos for pos in bot.legal_positions if pos in bot.homezone and pos not in enemies_pos]
                next_pos = bot.random.choice(safe_positions) if safe_positions else next_pos

    # strategy of the 2. bot (bot-b or bot-y)
    elif bot.char in ["b", "y"]:
        next_pos_2 = None

        # Huston we have a problem (no winning situation in the last rounds)
        # OK:  pelita src/team_prototype/group2_pelita_bot_00.py src/teams/bot_group0.py --seed 5594238220701511451
        # OK:  pelita src/team_prototype/group2_pelita_bot_00.py src/teams/bot_group0.py --seed 935242389108134692
        # OK:  pelita src/team_prototype/group2_pelita_bot_00.py src/teams/bot_group0.py --seed 4510689608527088892
        # NOK: pelita src/team_prototype/group2_pelita_bot_00.py src/teams/bot_group0.py --seed 1014449433168419070     (unlucky random relocation)
        # NOK: pelita src/team_prototype/group2_pelita_bot_00.py src/teams/bot_group0.py --seed 8832177988451015326     (no shortest path to pellet)
        # NOK: pelita src/team_prototype/group2_pelita_bot_00.py src/teams/bot_group0.py --seed 1566749212818251437     (no shortest path to pellet)
        score_diff = bot.score - bot.enemy[0].score
        if score_diff < 1 and 25 < bot.enemy[0].score:
            length_max = float("inf")
            for pellet in bot.food:
                shortest_path_bot = networkx.shortest_path(G=graph_homezone, source=bot.position, target=pellet)
                shortest_path_enemy = min([networkx.shortest_path(G=bot.graph, source=enemy_pos, target=pellet) for enemy_pos in enemies_pos], key=len)
                if len(shortest_path_bot) < length_max and len(shortest_path_bot) <= len(shortest_path_enemy):
                    next_pos_2 = shortest_path_bot[1] if len(shortest_path_bot) > 1 else shortest_path_bot[0]
                    length_max = len(shortest_path_bot)
                    if not length_max:
                        break

        # defender switches to attacker
        if not enemies_pos_homezone and not next_pos_2 and bot.enemy[0].score < bot.score:
        # pelita src/team_prototype/group2_pelita_bot_00.py src/teams/bot_group4.py --seed 6949900630900720448
            length_min_to_home = float("inf")
            for pos in column_middle:
                shortest_path_bot = networkx.shortest_path(G=bot.graph, source=bot.position, target=pos)
                if len(shortest_path_bot) < length_min_to_home:
                    length_min_to_home = len(shortest_path_bot)
            length_max = float("inf")
            for pellet in bot.enemy[0].food:
                shortest_path_bot = networkx.shortest_path(G=bot.graph, source=bot.position, target=pellet)
                shortest_path_enemy = min([networkx.shortest_path(G=bot.graph, source=enemy_pos, target=bot.position) for enemy_pos in enemies_pos], key=len)
                if len(shortest_path_bot) < length_max and len(shortest_path_bot) + length_min_to_home < len(shortest_path_enemy):
                    next_pos_2 = shortest_path_bot[1] if len(shortest_path_bot) > 1 else shortest_path_bot[0]
                    length_max = len(shortest_path_bot)
            if next_pos_2:
                return next_pos_2

        # bot in enemyzone goes home
        if bot.position in bot.enemy[0].homezone:
            length_min_to_home = float("inf")
            for pos in column_middle:
                shortest_path_bot = networkx.shortest_path(G=bot.graph, source=bot.position, target=pos)
                if len(shortest_path_bot) < length_min_to_home:
                    next_pos_2 = shortest_path_bot[1] if len(shortest_path_bot) > 1 else shortest_path_bot[0]
                    length_min_to_home = len(shortest_path_bot)
            return next_pos_2

        # bot is in homezone
        if bot.position in bot.homezone and not next_pos_2:
            # there is enemy in homezone
            if enemies_pos_homezone:
                closest_enemy = min(enemies_pos_homezone, key=lambda pos: distance_real(graph=graph_homezone, pos1=bot.position, pos2=pos))
                path_to_enemy = networkx.shortest_path(G=graph_homezone, source=bot.position, target=closest_enemy)
                next_pos_2 = path_to_enemy[1] if len(path_to_enemy) > 1 else bot.position
            # there is no enemy in homezone
            else:
                closest_enemy = min(enemies_pos, key=lambda pos: distance_real(graph=bot.graph, pos1=bot.position, pos2=pos))
                path_to_enemy = networkx.shortest_path(G=bot.graph, source=bot.position, target=closest_enemy)
                next_pos_2 = path_to_enemy[1] if len(path_to_enemy) > 1 else bot.position


        # do not follow enemy if it is in its own homezone
        if next_pos_2 not in bot.homezone:
            zu_mitte = networkx.shortest_path(graph_homezone, bot.position, column_middle[len(column_middle) // 2])
            next_pos_2 = zu_mitte[1] if len(zu_mitte) > 1 else bot.position

        next_pos = next_pos_2

    return next_pos
