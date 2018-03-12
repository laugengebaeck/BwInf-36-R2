import networkx as nx
import heapq as hq


def dijkstra_st(G, source, target):
    G_succ = G._succ
    paths = {source: [source]}  # Pfad source->target
    dist = {}  # Distanzliste
    seen = {}  # schon besuchte Knoten
    queue = []  # Priorityqueue

    seen[source] = 0  # source hinzufügen
    hq.heappush(queue, (0, source))
    while queue:
        (d, v) = hq.heappop(queue)
        if v in dist:
            continue  # schon besucht
        dist[v] = d
        if v == target:  # gefunden
            break
        for u, e in G_succ[v].items():
            cost = G.edges[v, u]["weight"]
            vu_dist = dist[v] + cost  # Distanz berechnen
            if u not in dist and (u not in seen or vu_dist < seen[u]):  # Distanz und Pfad setzen, wenn notwendig
                seen[u] = vu_dist
                hq.heappush(queue, (vu_dist, u))
                paths[u] = paths[v] + [u]

    return dist[target], paths[target]


def shortest_path(matrix):
    size = len(matrix)
    graph = nx.DiGraph()
    graph.add_node("s")
    graph.add_node("t")
    for i in range(0, size):
        for k in range(0, size):
            graph.add_node(str(i) + "|" + str(k))

    for i in range(0, size):
        # Kanten von Quelle in erste Reihe
        graph.add_edge("s", "0|" + str(i), weight=0.0)
        # Kanten von letzter Reihe zu Senke
        graph.add_edge(str(size - 1) + "|" + str(i), "t", weight=0.0)
        # jeweils Kante zu Knoten direkt rechts und unten
        for k in range(0, size):
            if k + 1 < size:
                weight = abs(matrix[i][k + 1] - matrix[i][k])
                graph.add_edge(str(i) + "|" + str(k), str(i) + "|" + str(k + 1), weight=weight)
                graph.add_edge(str(i) + "|" + str(k + 1), str(i) + "|" + str(k), weight=weight)
            if i + 1 < size:
                weight = abs(matrix[i + 1][k] - matrix[i][k])
                graph.add_edge(str(i) + "|" + str(k), str(i + 1) + "|" + str(k), weight=weight)
                graph.add_edge(str(i + 1) + "|" + str(k), str(i) + "|" + str(k), weight=weight)

    dijkstr = dijkstra_st(graph, "s", "t")
    path = dijkstr[1]
    length = dijkstr[0]
    max_steigung = 0.0
    for i in range(0, len(path)-1):
        v1 = path[i]
        v2 = path[i+1]
        data = graph.get_edge_data(v1, v2)
        w = data["weight"]
        if w > max_steigung:
            max_steigung = w

    print("Zu überwindende Höhe: " + str(round(length,3)))
    print("Über den Pfad: " + str(path))
    print("Größte Einzelsteigung: " + str(round(max_steigung,3)))