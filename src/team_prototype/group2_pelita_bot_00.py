import networkx

TEAM_NAME = 'Prototype' 
# Hilfsfunktion: Manhattan-Distanz(berechnet den Pfad zwischen zwei Punkten) 
def distance(graph, pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    #return len(networkx.shortest_path(G=graph, source=pos1, target=pos2))
# Main Funktion Bot 
def move(bot, state):
    enemy = bot.enemy #sagt, dass enemy gleich bot.emnemy
    enemy_pos = [enemy[0].position, enemy[1].position]  # Positionen der Gegner
    enemy_pos_homezone = [enemy_.position for enemy_ in enemy if enemy_.position in bot.homezone]  # Positionen der Gegner in homezone

    graph = bot.graph 

    # Mindestabstand zu Gegnern
    SAFE_DISTANCE = 3

    # Prüfe, ob der Bot in der Homezone ist
    in_homezone = bot.position in bot.homezone

    # Strategie für Charaktere "a" und "x"
    if bot.char in ["a", "x"]:
        nex_1 = None #Nächste Position ist vorerst nichts

        if in_homezone and enemy_pos_homezone:
            # Versuche, den Gegner in der Homezone zu verfolgen
            closest_enemy = min(enemy_pos_homezone, key=lambda pos: distance(graph, bot.position, pos)) #lambda ist fiunktion die nur innerhalb dere if funktion darüber gilt 27 bis 29
            if distance(graph, bot.position, closest_enemy) <= SAFE_DISTANCE:
                # Bewege dich auf den nächsten Gegner zu
                sp_to_enemy = networkx.shortest_path(bot.graph, bot.position, closest_enemy) 
                nex_1 = sp_to_enemy[1] if len(sp_to_enemy) > 1 else bot.position # bestimmung Position vom Bot1 
        
        if not nex_1:  # Standardstrategie, falls kein Gegner verfolgt werden kann
            legal_positions_2 = [pos for pos in bot.legal_positions if pos != bot.position]
            if not legal_positions_2:
                legal_positions_2 = [bot.position]
            
            way_1 = 150 #geht durch welcher der kürzeste weg zum foodpallet ist
            safe_positions = [
                pos for pos in legal_positions_2
                if all(distance(graph, pos, enemy_pos[i]) >= SAFE_DISTANCE for i in range(2))
            ]

            
            if safe_positions: #Prüft auf sichere position
                for pellet in bot.enemy[0].food: #Navigation zu den Pellets
                    sp_1 = networkx.shortest_path(bot.graph, bot.position, pellet) #prüft in welchem sicheren positionsbereich ein foodpallet ist?
                    if len(sp_1) < way_1 and sp_1[1] in safe_positions:
                        nex_1 = sp_1[1]
                        way_1 = len(sp_1)
                if not nex_1:
                    #-nex_1 = bot.random.choice(safe_positions)
                    
                    nex_1 = bot.random.choice(safe_positions)
            else:   #wenn es keine Sichere Position gibt
                max_dist = -1 #bestimmt vielleicht wie weit der bot vom anderem Gengner weg geht, sonst weiß ich leideer nicht
                for pos in bot.legal_positions:
                    min_dist_to_enemy = min(distance(graph, pos, enemy_pos[0]), distance(graph, pos, enemy_pos[1]))
                    if min_dist_to_enemy > max_dist:
                        max_dist = min_dist_to_enemy
                        nex_1 = pos
                        #geht von dem anderen bot weg (aber nicht weit genug)

        next_pos = nex_1 if nex_1 else bot.position #auswahl der nächsten Position 

        # code to loop-detection
        loop_detected = False 
        move_history = bot.track # was der Bot gelaufen ist 
        for i in range(1, len(move_history) // 2 + 1): #wenn er das dritte mal im loop hängt geht er einen anderen weg
            if move_history[-i:] == move_history[-2*i:-i]: #
                loop_detected = True  # wenn bot in einem Loop fest hängt und nur hin und her läuft, macht der das dadurch nicht mehr
        #last_positions.pop(0) 
        #remove the last element of the list 
        if loop_detected:
            safe_loop = [pos for pos in bot.legal_positions if pos in bot.homezone] 
            next_pos = bot.random.choice(safe_loop) if safe_loop else bot.random.choice(legal_positions_2)
        # Standard: Falls keine Bedingung erfüllt ist, bleibt die Position unverändert
    
    # Strategie für Charaktere "b" und "y"
    elif bot.char in ["b", "y"]:
        nex_2 = None
        graph_homezone = bot.graph.copy()
        for pos in bot.graph: 
            if pos not in bot.homezone:
                graph_homezone.remove_node(pos)
                #=> nächstes mal wieder prüfen!!!!!!!
                # --seed 1423702797381110628
        if in_homezone and enemy_pos_homezone: 
            # Versuche, den Gegner in der Homezone zu verfolgen
            closest_enemy = min(enemy_pos_homezone, key=lambda pos: distance(graph, bot.position, pos))
            # Bewege dich auf den nächsten Gegner zu
            sp_to_enemy = networkx.shortest_path(graph_homezone, bot.position, closest_enemy)
            nex_2 = sp_to_enemy[1] if len(sp_to_enemy) > 1 else bot.position

        #bestimmt die mittlere Position (da wo der Bot ist)
        mitte = [pos for pos in graph if pos[0] == 15] 
        mitte_len = len(mitte)
        zu_mitte = networkx.shortest_path(graph_homezone, bot.position, mitte[mitte_len // 2]) 
        nex_2_zu_mitte = zu_mitte[1] if len(zu_mitte) > 1 else bot.position
        next_pos = nex_2 if nex_2 else nex_2_zu_mitte
        #Die mittlere Position wird verwendet, um den Bot auf diese zentrale Position entlang der Linie 
        # 𝑥 = 15 x=15 zu navigieren, falls keine andere Zielposition (nex_2) definiert ist.
    
    return next_pos #gibt die nächste Position zurück
    
    # bot.graph.copy 