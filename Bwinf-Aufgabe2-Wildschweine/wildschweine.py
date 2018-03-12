import networkx as nx
import os.path
import sys
import boarflow
import copy
import datetime
import dijkstra

epsilon = 10e-4

def TimestampMillisec64():
    return int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)

# Einlesen der Eingabedatei
def read(filename):
    with open(filename, "r") as file:
        content = file.read().splitlines()
        size_read = int(content[0])
        content.pop(0)
        content = [x.strip("\n") for x in content]
        for line in range(0, len(content)):
            content[line] = content[line].split(" ")
            for z in range(0, len(content)):
                content[line][z] = float(content[line][z])
        return size_read, content

# Funktion zur Auswahl des Feldes, von dem in Sonderfall (s.u.) Erde genommen wird
def auswahl(size, u, bisher_ob, bisher_unt):
    moeglich_liste = []
    # direkt oben, unten, links, rechts vom Feld
    if (int(u[1])-1) >= 0:
        links = u[0] + "|" + str(int(u[1])-1)
        moeglich_liste.append(links)
    if (int(u[1])+1) < size:
        rechts = u[0] + "|" + str(int(u[1])+1)
        moeglich_liste.append(rechts)
    if (int(u[0])+1) < size:
        unten = str(int(u[0])+1) + "|" + u[1]
        moeglich_liste.append(unten)
    if (int(u[0])-1) >= 0:
        oben = str(int(u[0])-1) + "|" + u[1]
        moeglich_liste.append(oben)
    for moeglich in moeglich_liste:
        # Feld bisher nicht in Höhe verändert?
        if moeglich in bisher_ob or moeglich in bisher_unt:
            moeglich_liste.remove(moeglich)
    return moeglich_liste[len(moeglich_liste)-1]


filename = input("Bitte Namen der Eingabedatei eingeben: ")
if not os.path.isfile(filename):
    sys.exit(0)

vt = read(filename)
size = vt[0]
vertex_matrix = vt[1]

impossible_height = 1
height_inp = input("Falls gewünscht, unüberwindbare Steigung angeben (Enter=Default/1):")
if height_inp != "":
    impossible_height = int(height_inp)
# "Sicherheitskopie" der Matrix
old_vertex_matrix = copy.deepcopy(vertex_matrix)
time_start = TimestampMillisec64()

graph = nx.DiGraph()
# Quelle und Senke
graph.add_node("s")
graph.add_node("t")

# Knoten für jedes Feld der Matrix
# Benennung der Knoten: ReiheInMatrix|SpalteInMatrix
for i in range(0, size):
    for k in range(0, size):
        graph.add_node(str(i)+"|"+str(k))

for i in range(0, size):
    # Kanten von Quelle in erste Reihe
    graph.add_edge("s", "0|"+str(i))
    # Kanten von letzter Reihe zu Senke
    graph.add_edge(str(size-1)+"|"+str(i), "t")
    # jeweils Kante zu Knoten direkt rechts und unten, ...
    for k in range(0, size):
        if k+1 < size:
            capacity = impossible_height - abs(vertex_matrix[i][k+1] - vertex_matrix[i][k])
            # ... aber nur wenn nötige Höhenänderung größer als 10^-4
            if capacity > epsilon:
                graph.add_edge(str(i)+"|"+str(k), str(i)+"|"+str(k+1), capacity=capacity)
                graph.add_edge(str(i) + "|" + str(k+1), str(i) + "|" + str(k), capacity=capacity)
        if i+1 < size:
            capacity = impossible_height - abs(vertex_matrix[i+1][k] - vertex_matrix[i][k])
            if capacity > epsilon:
                graph.add_edge(str(i) + "|" + str(k), str(i+1) + "|" + str(k), capacity=capacity)
                graph.add_edge(str(i+1) + "|" + str(k), str(i) + "|" + str(k), capacity=capacity)

# Berechnen des minimalen Schnitts
mincut = boarflow.minimum_cut(graph, "s", "t")
cutedges = []

# wenn Mincut Wert von 0 hat, existiert kein Weg von s nach t
if mincut[0] == 0:
    print("Bereits unpassierbar!")
    sys.exit(0)

# Finden der Mincut-Kanten mithilfe der beiden Partitionen des Graphen
for (u, v) in graph.edges:
    if u in mincut[1][0] and v in mincut[1][1]:
        cutedges.append([u, v])

# Zählvariable für verschobene Erde => Kosten
verschobene_erde = 0.0

bisher_obere_knoten = []
bisher_untere_knoten = []

# für jede Mincut-Kante
for edge in cutedges:
    u = edge[0].split("|")
    v = edge[1].split("|")
    if vertex_matrix[int(u[0])][int(u[1])] <= vertex_matrix[int(v[0])][int(v[1])]:
        # benötigte Höhenänderung
        delta = impossible_height - (vertex_matrix[int(v[0])][int(v[1])] - vertex_matrix[int(u[0])][int(u[1])])
        # Hälfte davon wird von tieferem auf höheres Feld gebracht
        delta = delta / 2
        if delta < 0:
            continue
        verschobene_erde += delta
        vertex_matrix[int(u[0])][int(u[1])] -= delta
        vertex_matrix[int(v[0])][int(v[1])] += delta
        bisher_obere_knoten.append(edge[1])
        bisher_untere_knoten.append(edge[0])
    elif vertex_matrix[int(u[0])][int(u[1])] > vertex_matrix[int(v[0])][int(v[1])]:
        # gleiches Prinzip
        delta = impossible_height - (vertex_matrix[int(u[0])][int(u[1])] - vertex_matrix[int(v[0])][int(v[1])])
        delta = delta / 2
        if delta < 0:
            continue
        verschobene_erde += delta
        vertex_matrix[int(u[0])][int(u[1])] += delta
        vertex_matrix[int(v[0])][int(v[1])] -= delta
        bisher_obere_knoten.append(edge[0])
        bisher_untere_knoten.append(edge[1])

# Behandlung des Sonderfalls (treppenartiger Mincut) => siehe Doku
for edge in cutedges:
    u = edge[0].split("|")
    v = edge[1].split("|")
    do_tausch = False
    if vertex_matrix[int(u[0])][int(u[1])] <= vertex_matrix[int(v[0])][int(v[1])]:
        # hier tieferes Feld war schon mal höheres Feld -> Änderung nötig
        if edge[0] in bisher_obere_knoten:
            index = bisher_obere_knoten.index(edge[0])
            unterer_knoten = bisher_untere_knoten[index]
            do_tausch = True
    elif vertex_matrix[int(u[0])][int(u[1])] > vertex_matrix[int(v[0])][int(v[1])]:
        if edge[1] in bisher_obere_knoten:
            index = bisher_obere_knoten.index(edge[1])
            unterer_knoten = bisher_untere_knoten[index]
            do_tausch = True
    # Änderung durchführen
    if do_tausch:
        # Sortieren der drei Felder nach ursprünglicher Höhe
        list_knoten = [edge[0], edge[1], unterer_knoten]
        list_knoten = sorted(list_knoten, key=lambda knoten: old_vertex_matrix[int(knoten.split("|")[0])][int(knoten.split("|")[1])])
        knoten_unten = list_knoten[0].split("|")
        knoten_mitte = list_knoten[1].split("|")
        knoten_oben = list_knoten[2].split("|")
        # Wiederherstellen der ursprünglichen Höhe
        vertex_matrix[int(knoten_unten[0])][int(knoten_unten[1])] = old_vertex_matrix[int(knoten_unten[0])][int(knoten_unten[1])]
        vertex_matrix[int(knoten_mitte[0])][int(knoten_mitte[1])] = old_vertex_matrix[int(knoten_mitte[0])][int(knoten_mitte[1])]
        vertex_matrix[int(knoten_oben[0])][int(knoten_oben[1])] = old_vertex_matrix[int(knoten_oben[0])][int(knoten_oben[1])]
        # Verschiebung zwischen tiefstem und mittlerem Feld normal durchführen
        delta = impossible_height - (vertex_matrix[int(knoten_mitte[0])][int(knoten_mitte[1])] - vertex_matrix[int(knoten_unten[0])][int(knoten_unten[1])])
        delta = delta / 2
        vertex_matrix[int(knoten_unten[0])][int(knoten_unten[1])] -= delta
        vertex_matrix[int(knoten_mitte[0])][int(knoten_mitte[1])] += delta
        # für höchstes Feld wird noch benötigte Höhenänderung ...
        # ... mithilfe eines anderen Nachbarfelds erreicht
        knoten_to_take_from = auswahl(size, knoten_oben, bisher_obere_knoten, bisher_untere_knoten).split("|")
        delta1 = impossible_height - (vertex_matrix[int(knoten_oben[0])][int(knoten_oben[1])] - vertex_matrix[int(knoten_mitte[0])][int(knoten_mitte[1])])
        delta2 = delta1 / 2
        verschobene_erde -= delta2
        verschobene_erde += delta1
        vertex_matrix[int(knoten_oben[0])][int(knoten_oben[1])] += delta1
        vertex_matrix[int(knoten_to_take_from[0])][int(knoten_to_take_from[1])] -= delta1

time_end = TimestampMillisec64()

# Ausgabe und Formatierung wie in Eingabedatei
outstring = ""
outstring += str(size) + "\n"
for i in range(0, size):
    for k in range(0, size):
        vertex_matrix[i][k] = round(vertex_matrix[i][k], 3)
        outstring += ("{0:.3f}".format(vertex_matrix[i][k]))+" "
    outstring += "\n"

# Konsolenausgabe
print(outstring)
print("{0:.2f}".format(round(round(verschobene_erde, 3) * 100, 2)) + " Euro werden benötigt.")
print("Laufzeit des Programms:", time_end-time_start, "Millisekunden")

# Dateiausgabe
fp = open(filename.split(".")[0] + "-lsg.txt", "w")
fp.write(outstring)
fp.close()

print()
print("Erweiterung für Eingabematrix: ")
dijkstra.shortest_path(old_vertex_matrix)
print("Erweiterung für Ausgabematrix: ")
dijkstra.shortest_path(vertex_matrix)
