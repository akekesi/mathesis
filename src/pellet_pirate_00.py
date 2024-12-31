# deadlock:
# --seed 3027016763252906255


import copy
import networkx as nx


TEAM_NAME = 'Pellet Pirates'
BOT_1 = ["a", "x"]
BOT_2 = ["b", "y"]
DISTANCE = 3

def init_state(state: dict) -> None:
    state["bot_1"] = {
        "position": [],
    }
    state["bot_2"] = {
        "position": [],
    }


def get_shortest_path(graph: nx.Graph, source: tuple[int, int], targets: list[tuple[int, int]]) -> list[tuple[int, int]]:
    length = float("inf")
    shortest_path = []
    for target in targets:
        try:
            # node reachable
            shortest_path_ = nx.shortest_path(G=graph, source=source, target=target)
            length_ = len(shortest_path_)
        except:
            # node not reachable
            continue
        if  length_ < length:
            length = length_
            shortest_path = shortest_path_
    return shortest_path


def get_surrounding_coords(point: tuple[int, int], distance: int) -> list[tuple[int, int]]:
    x, y = point
    surrounding_coords = [
        (x + dx, y + dy)
        for dx in range(-distance, distance + 1)
        for dy in range(-distance, distance + 1)
        if abs(dx) + abs(dy) <= distance
    ]
    return surrounding_coords


def is_deadlock(state: dict, position_next: tuple[int, int]) -> bool:
    n = 0
    for position in state["bot_1"]["position"][-5:]:
        if position == position_next:
            n += 1
        if n > 1:
            return True
    return False


def move(bot, state):
    if state == {}:
        init_state(state)

    graph = bot.graph.copy()
    enemies = bot.enemy

    # attacker
    if bot.char in BOT_1:
        # optional: after death maybe try to catch attacker
        # shortest path to the nearest pellet
        foods = copy.deepcopy(bot.enemy[0].food)
        enemies_noisy = [enemy for enemy in enemies if not enemy.is_noisy]
        nodes_delete = []
        for enemy in enemies_noisy:
            nodes_delete += get_surrounding_coords(point=enemy.position, distance=DISTANCE)
        for node_delete in nodes_delete:
            if node_delete in enemies[0].homezone and node_delete != bot.position:
                if node_delete in graph:
                    graph.remove_node(node_delete)
                if node_delete in foods:
                    foods.remove(node_delete)
        shortes_path = get_shortest_path(graph=graph, source=bot.position, targets=foods)
        if shortes_path:
            position_next = shortes_path[1]
        else:
            position_next = bot.random.choice(bot.legal_positions)
        if is_deadlock(state=state, position_next=position_next):
            print("deadlock")
            # ???
        state["bot_1"]["position"].append(position_next)

    # defender
    if bot.char in BOT_2:
        # optional: if nothing to do try to collect pellet
        lenght = float("inf")
        enemies_attacker = [enemy for enemy in enemies if enemy.position in bot.homezone]
        for enemy in enemies_attacker:
            # shortest path to the nearest attacker enemy
            shortes_path_ = nx.shortest_path(G=graph, source=bot.position, target=enemy.position)
            lenght_ = len(shortes_path_)
            if lenght_ < lenght:
                lenght = lenght_
                shortes_path = shortes_path_

        if not enemies_attacker:
            for enemy in enemies:
                # shortest path to the nearest target of enemy
                shortes_path_ = get_shortest_path(graph=graph, source=enemy.position, targets=bot.food)
                shortes_path_ = nx.shortest_path(G=graph, source=bot.position, target=shortes_path_[-1])
                lenght_ = len(shortes_path_)
                if lenght_ < lenght:
                    lenght = lenght_
                    shortes_path = shortes_path_

        if len(shortes_path) < 2:
            position_next = shortes_path[0]
        else:
            position_next = shortes_path[1]
        if position_next not in bot.homezone:
            position_next = shortes_path[0]
        state["bot_2"]["position"].append(position_next)

    return position_next
