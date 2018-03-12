import networkx as nx

# Breitensuche
def breadth_first_search(adj, firstlevel):
    seen = {}                  # Dictionary mit Entfernung vom Start
    level = 0                  # aktuelle Ebene
    nextlevel = firstlevel     # Knoten auf der nächsten Ebene

    while nextlevel:
        thislevel = nextlevel  # neue Ebene
        nextlevel = {}         # Dictionary für nächste Ebene
        for v in thislevel:
            if v not in seen:
                seen[v] = level  # Entfernung für Knoten setzen
                nextlevel.update(adj[v])  # Nachbarn für nächste Ebene hinzufügen
                yield (v, level)
        level += 1
    del seen

# Residualnetzwerk erstellen
def build_residual_network(G):
    # neues Netzwerk mit gleichen Knoten
    R = nx.DiGraph()
    R.add_nodes_from(G)

    inf = float('inf')

    # Kanten-Liste holen
    edge_list = [(u, v, attr) for u, v, attr in G.edges(data=True)]

    for u, v, attr in edge_list:
        r = min(attr.get('capacity', inf), inf)
        if not R.has_edge(u, v):
            # Hinkante hat entsprechende Kapazität
            R.add_edge(u, v, capacity=r)
            # Rückkante mit Kapazität null
            R.add_edge(v, u, capacity=0)
        else:
            # Kapazität für Rückkante doch definiert
            # wird entsprechend gesetzt
            R[u][v]['capacity'] = r

    # Fluss auf allen Kanten null
    for u in R:
        for e in R[u].values():
            e['flow'] = 0

    return R


# Edmonds-Karp-Algorithmus
def edmonds_karp(G, s, t):
    R = build_residual_network(G)
    R_pred = R.pred
    R_succ = R.succ

    # Fluss entlang eines Pfades augmentieren
    def augment(path):
        flow = float('inf')
        # minimale Residualkapazität entlang des Pfades bestimmen
        it = iter(path)
        u = next(it)
        for v in it:
            attr = R_succ[u][v]
            flow = min(flow, attr['capacity'] - attr['flow'])
            u = v
        # augmentieren
        it = iter(path)
        u = next(it)
        for v in it:
            # Fluss auf Hinkante erhöhen
            R_succ[u][v]['flow'] += flow
            # Fluss auf Rückkante verringern
            R_succ[v][u]['flow'] -= flow
            u = v
        return flow

    # bidirektionale Breitensuche nach augmentierendem Pfad
    def bidirectional_bfs():
        pred = {s: None}
        q_s = [s]
        succ = {t: None}
        q_t = [t]
        while True:
            q = []
            # von s aus suchen
            if len(q_s) <= len(q_t):
                for u in q_s:
                    for v, attr in R_succ[u].items():
                        # nur wenn nächster Knoten noch nicht im Pfad
                        # ... und entsprechende Kante noch nicht gesättigt
                        if v not in pred and attr['flow'] < attr['capacity']:
                            pred[v] = u
                            # Pfade treffen sich
                            if v in succ:
                                return v, pred, succ
                            q.append(v)
                # kein augmentierender Pfad mehr vorhanden
                if not q:
                    return None, None, None
                q_s = q
            # von t aus suchen -> gleiches Prinzip
            else:
                for u in q_t:
                    for v, attr in R_pred[u].items():
                        if v not in succ and attr['flow'] < attr['capacity']:
                            succ[v] = u
                            if v in pred:
                                return v, pred, succ
                            q.append(v)
                if not q:
                    return None, None, None
                q_t = q

    # maximalen Fluss bestimmen
    flow_value = 0
    while flow_value < float('inf'):
        v, pred, succ = bidirectional_bfs()
        # kein augmentierender Pfad mehr vorhanden -> max. Fluss
        if pred is None:
            break
        path = [v]
        # Pfad von s bis zum Treffpunkt
        u = v
        while u != s:
            u = pred[u]
            path.append(u)
        path.reverse()
        # weiterer Pfad bis zu t
        u = v
        while u != t:
            u = succ[u]
            path.append(u)
        # Fluss augmentieren
        flow_value += augment(path)

    R.graph['flow_value'] = flow_value
    return R

# minimaler Schnitt
def minimum_cut(flowgraph, s, t):

    R = edmonds_karp(flowgraph, s, t)
    # gesättigte Kanten aus Residualnetzwerk entfernen
    cutset = [(u, v, d) for u, v, d in R.edges(data=True)
              if d['flow'] == d['capacity']]
    R.remove_edges_from(cutset)

    # per Breitensuche von s aus ...
    # ... werden von s erreichbare Knoten gesammelt
    nextlevel = {s: 1}
    non_reachable = set(dict(dict(breadth_first_search(R.adj, nextlevel))))
    # nicht erreichbar sind alle anderen Knoten
    # => in 2 Partitionen geteilt
    partition = (set(flowgraph) - non_reachable, non_reachable)

    return R.graph['flow_value'], partition
