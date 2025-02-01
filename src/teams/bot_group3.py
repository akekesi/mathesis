"""
Allgemeine Eindrücke
Struktur & Lesbarkeit:  Dein Code ist sauber strukturiert, gut kommentiert und verständlich.
                        Die Rollen von Angreifer- und Verteidiger-Bot sind klar definiert.
Modularität:            Die Funktionen sind sinnvoll aufgeteilt, was Wartung und Erweiterbarkeit erleichtert.
Effizienz:              Es gibt einige Optimierungsmöglichkeiten, insbesondere im Umgang mit safe_graph und der Suche nach Nahrung.



Positives
✅ Klare Struktur & Modularität
- Die Trennung zwischen attack und defend ist klar und in move() gut umgesetzt.
- Jede Funktion hat eine klar definierte Aufgabe.

✅ Fehlertoleranz & Fallbacks
- Falls ein direkter Weg nicht gefunden wird, gibt es immer ein alternatives Verhalten (z. B. try_random_move_in_safe_graph() oder zufällige Bewegung).

✅ Vermeidung von „Ping-Pong“-Bewegungen
- Der Code speichert vorherige Positionen und vermeidet es, direkt zum letzten Feld zurückzukehren. Dies verbessert die Effizienz der Bewegung.

✅ Dynamische Gefahrenbewertung
- create_safe_graph() entfernt feindliche Positionen aus dem Graphen, um sichere Pfade zu gewährleisten.



Verbesserungspotenzial & Optimierungsvorschläge
❌ safe_graph wird mehrfach unnötig neu berechnet
- create_safe_graph(bot) wird in mehreren Funktionen redundant aufgerufen, z. B. in try_random_move_in_safe_graph() und bfs_find_food().
🔹 Lösung: Berechne es einmal in move() und übergebe es als Argument.
    def move(bot, state):
        if not state:
            state.update(init_state(bot))

        safe_graph = create_safe_graph(bot)  # Nur einmal berechnen

❌ Redundante deque-Importe
- In bfs_find_food() wird from collections import deque erneut importiert, obwohl es oben bereits importiert wurde.
🔹 Lösung: Entferne den zweiten Import.

❌ Unbestimmter Rückgabewert von get_nearest_enemy_in_homezone()
- Aktuell gibst du das erste bot.enemy zurück und nicht unbeding das nächste.
🔹 Lösung: Direkt das kleinste Element per min() finden.
    def get_nearest_enemy_in_homezone(bot):
        return min(
            (enemy for enemy in bot.enemy if not enemy.is_noisy and enemy.position in bot.homezone),
            key=lambda e: abs(bot.position[0] - e.position[0]) + abs(bot.position[1] - e.position[1]),
            default=None
        )
        
❌ bfs_find_food() könnte effizienter sein
- sate ist nicht in Verwendung und könnte entfernt werden.
- Die Nahrungsliste all_food wird überprüft, bevor BFS überhaupt startet. Falls leer, könnte die Funktion sofort return None, None zurückgeben.
🔹 Lösung: Frühzeitiges return für bessere Lesbarkeit.
    def bfs_find_food(bot, state):
        safe_graph = create_safe_graph(bot)
        if bot.position not in safe_graph or not bot.enemy or not bot.enemy[0].food:
            return None, None  # Frühes Exit



Fazit
Gesamtbewertung: 9/10 ⭐⭐⭐⭐⭐⭐⭐⭐⭐☆
Dein Code ist insgesamt sehr solide, gut strukturiert und mit sinnvollen Sicherheitsmechanismen versehen.
Neben dem unbestimmten Rückgabewert von get_nearest_enemy_in_homezone() gibt es nur wenige Optimierungsmöglichkeiten.
Mit den vorgeschlagenen Änderungen könntest du die Effizienz und Lesbarkeit noch weiter verbessern! 🚀
"""

import networkx as nx
import random
from collections import deque

TEAM_NAME = 'SkibidiFortnite'

def init_state(bot):
    """
    Initialisiert den Zustand für beide Bots.
    Angepasste 'defender_region' liegt näher am Zentrum der Homezone.
    """
    if bot.is_blue:
        # Beispiel: Mitte der blauen Homezone
        attacker_region = [(7, 8), (8, 8), (9, 8), (10, 8), (11, 8)]
        # Verteidiger patrouilliert im mittleren Bereich der eigenen Hälfte
        defender_region = []
        for x in range(6, 11):    # x: 6..10
            for y in range(6, 10):  # y: 6..9
                defender_region.append((x, y))
    else:
        # Beispiel: Mitte der roten Homezone
        attacker_region = [(24, 8), (23, 8), (22, 8), (21, 8), (20, 8)]
        # Verteidiger patrouilliert im mittleren Bereich der eigenen Hälfte
        defender_region = []
        for x in range(21, 26):   # x: 21..25
            for y in range(6, 10):  # y: 6..9
                defender_region.append((x, y))

    return {
        0: {  # Angreifer
            "role": "attack",
            "target_region": attacker_region,
            "last_positions": [None, None]
        },
        1: {  # Verteidiger
            "role": "defend",
            "target_region": defender_region,
            "last_positions": [None, None]
        }
    }

def create_safe_graph(bot):
    safe_graph = bot.graph.copy()
    for enemy in bot.enemy:
        if not enemy.is_noisy:
            ex, ey = enemy.position
            for node in list(safe_graph.nodes()):
                if node == bot.position:
                    continue
                nx_, ny_ = node
                if abs(nx_ - ex) <= 1 and abs(ny_ - ey) <= 1:
                    if node in safe_graph:
                        safe_graph.remove_node(node)
    return safe_graph

def try_random_move_in_safe_graph(bot, safe_graph, state):
    if bot.position not in safe_graph:
        return None

    neighbors = list(safe_graph[bot.position])
    if not neighbors:
        return None

    bot_id = bot.turn
    last_positions = state[bot_id].get("last_positions", [None, None])

    # Vermeide letzte Positionen, um Ping-Pong zu reduzieren
    for lp in last_positions:
        if lp in neighbors and len(neighbors) > 1:
            neighbors.remove(lp)

    if not neighbors:
        return None

    next_move = random.choice(neighbors)

    # last_positions updaten
    last_positions.pop(0)
    last_positions.append(bot.position)
    state[bot_id]["last_positions"] = last_positions

    return next_move

def move_to_target(bot, target, state):
    safe_graph = create_safe_graph(bot) # TODO: safe_graph could be passed as argument
    if bot.position in safe_graph and target in safe_graph:
        try:
            path = nx.shortest_path(safe_graph, bot.position, target)
            if len(path) > 1:
                next_move = path[1]
                bot_id = bot.turn
                last_positions = state[bot_id]["last_positions"]
                last_positions.pop(0)
                last_positions.append(bot.position)
                state[bot_id]["last_positions"] = last_positions
                return next_move
        except nx.NetworkXNoPath:
            pass
    return try_random_move_in_safe_graph(bot, safe_graph, state)

def bfs_find_food(bot, state): # TODO: state is not used
    safe_graph = create_safe_graph(bot) # TODO: safe_graph could be passed as argument
    if bot.position not in safe_graph: # TODO: collect all early returns
        return (None, None)

    if not bot.enemy or not bot.enemy[0].food: # TODO: collect all early returns
        return (None, None)
    all_food = bot.enemy[0].food
    if not all_food: # TODO: collect all early returns
        return (None, None)

    from collections import deque # TODO: redundant import
    visited = set([bot.position])
    queue = deque([[bot.position]])

    while queue:
        path = queue.popleft()
        current = path[-1]
        if current in all_food:
            if len(path) > 1:
                next_step = path[1]
            else:
                next_step = current
            return (current, next_step)

        for neighbor in safe_graph[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)

    return (None, None)

def get_nearest_enemy_in_homezone(bot):
    in_home = [enemy for enemy in bot.enemy if (not enemy.is_noisy) and (enemy.position in bot.homezone)]
    if not in_home:
        return None
    return in_home[0] # TODO: return min(...)

def move(bot, state):
    if not state:
        state.update(init_state(bot))

    bot_id = bot.turn
    bot_state = state[bot_id]
    role = bot_state["role"]

    # -----------------------
    # ANGRIFFS-BOT
    # -----------------------
    if role == "attack":
        # Versuche Futter per BFS zu finden
        food_pos, next_step = bfs_find_food(bot, state)
        if food_pos and next_step:
            bot.say("Angriff: Futter ansteuern!")
            return next_step

        # Fallback: zufällige Bewegung im safe_graph
        fallback = try_random_move_in_safe_graph(bot, create_safe_graph(bot), state) # TODO: safe_graph could be passed as argument
        if fallback:
            bot.say("Angriff: Keine Nahrung? Bewege mich zufällig!")
            return fallback

        # Nichts möglich
        return bot.position

    # -----------------------
    # VERTEIDIGER-BOT
    # -----------------------
    elif role == "defend":
        # 1) Gegner in Homezone?
        home_enemy = get_nearest_enemy_in_homezone(bot)
        if home_enemy:
            next_step = move_to_target(bot, home_enemy.position, state)
            if next_step:
                bot.say("Verteidiger: Homezone sichern!")
                return next_step

        # 2) Falls kein Gegner in Homezone, patrouilliere in 'target_region'
        region = bot_state["target_region"]
        # Nur Felder nehmen, die wirklich frei sind
        valid_positions = [pos for pos in region if pos in bot.graph and pos not in bot.walls]
        if valid_positions:
            # Wähle das nächste Ziel in der Region, z.B. das nächste am Bot (Manhattan-Distanz)
            nearest_pos = min(valid_positions, key=lambda p: abs(bot.position[0] - p[0]) + abs(bot.position[1] - p[1]))
            next_step = move_to_target(bot, nearest_pos, state)
            if next_step:
                bot.say("Verteidiger: Patrouilliere im Zentrum!")
                return next_step

        # 3) Fallback: Zufallszug
        fallback = try_random_move_in_safe_graph(bot, create_safe_graph(bot), state) # TODO: safe_graph could be passed as argument 
        if fallback:
            bot.say("Verteidiger: Keine Ziele, laufe zufällig!")
            return fallback

        return bot.position

    return bot.position
