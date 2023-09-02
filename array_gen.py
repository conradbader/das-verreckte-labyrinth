import random
import math
import inspect
from itertools import combinations
import numpy as np  # pip install numpy
from collections import deque

def generate_valid_regions(width, height, num_regions, seed):
    while True:
        regions, region_map = generate_regions(width, height, num_regions, seed)

        # Überprüfe die Bedingungen
        if (check_outer_contact(region_map, 1, width, height) and
                check_outer_contact(region_map, num_regions, width, height) and
                check_adjacency(region_map, num_regions) and
                check_min_distance(region_map) and
                check_distance_to_border(region_map)):
            return regions, region_map, seed
        seed += 1


def check_outer_contact(region_map, region_id, width, height):
    # Überprüfe den äußeren Rand auf Kontakt mit der gegebenen Region
    for x in range(width):
        if region_map[0][x] == region_id or region_map[height - 1][x] == region_id:
            return True
    for y in range(height):
        if region_map[y][0] == region_id or region_map[y][width - 1] == region_id:
            return True
    return False


def check_adjacency(region_map, num_regions):
    # Überprüfe, ob jede Region außer der letzten an die nächsthöhere Region angrenzt
    for region_id in range(1, num_regions):
        found_adjacency = False
        for y in range(len(region_map)):
            for x in range(len(region_map[0])):
                if region_map[y][x] == region_id:
                    # Überprüfe die Nachbarn des Pixels
                    for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < len(region_map) and 0 <= nx < len(region_map[0]) and region_map[ny][
                            nx] == region_id + 1:
                            found_adjacency = True
                            break
            if found_adjacency:
                break
        if not found_adjacency:
            return False
    return True


def check_min_distance(region_map):
    min_distance = 13
    junction_points = find_junction_points(region_map)

    # Überprüfe den Abstand zwischen den Knotenpunkten
    for point1, point2 in combinations(junction_points, 2):
        distance = calculate_distance(point1, point2)
        if distance < min_distance:
            return False
    return True


def check_distance_to_border(region_map):
    min_distance = 10
    height, width = len(region_map), len(region_map[0])
    junction_points = find_junction_points(region_map)

    for y, x in junction_points:
        # Abstand zu den vier Rändern
        top_distance = y
        bottom_distance = height - y - 1
        left_distance = x
        right_distance = width - x - 1

        if (top_distance < min_distance or
                bottom_distance < min_distance or
                left_distance < min_distance or
                right_distance < min_distance):
            return False
    return True


def find_junction_points(region_map):
    # Identifiziere zunächst alle Knotenpunkte
    raw_junction_points = {}
    for y in range(1, len(region_map) - 1):
        for x in range(1, len(region_map[0]) - 1):
            unique_regions = set()
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    unique_regions.add(region_map[y + dy][x + dx])
            if len(unique_regions) >= 3:
                raw_junction_points[(x, y)] = region_map[y][x]

    # Gruppiere die Rohknotenpunkte, die denselben Knotenpunkt repräsentieren
    visited = set()
    junction_points = []
    for x, y in raw_junction_points.keys():
        if (x, y) in visited:
            continue
        group = []
        queue = [(x, y)]
        while queue:
            cx, cy = queue.pop()
            if (cx, cy) in visited or (cx, cy) not in raw_junction_points:
                continue
            visited.add((cx, cy))
            group.append((cx, cy))
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                queue.append((nx, ny))
        # Wähle den Pixel, mit der niedrigsten Regions-ID aus der Gruppe
        min_region_id_pixel = min(group, key=lambda p: raw_junction_points[p])
        junction_points.append(min_region_id_pixel)
    return junction_points


def generate_regions(width, height, num_regions, seed):
    regions = {}
    region_map = [[0] * width for _ in range(height)]

    # Generiere Startpunkt für jeden Bereich
    start_points = generate_start_points(width, height, num_regions, seed)

    # Weise jedem Punkt im Viereck den Bereich entsprechend dem nächstgelegenen Startpunkt zu
    for y in range(height):
        for x in range(width):
            min_distance = float('inf')
            region_id = None

            # Finde den nächsten Startpunkt
            for i in range(min(num_regions, len(start_points))):
                distance = calculate_distance((x, y), start_points[i])
                if distance < min_distance:
                    min_distance = distance
                    region_id = i

            regions[(x, y)] = region_id + 1
            region_map[y][x] = region_id + 1

    region_map = reorder_regions(region_map, num_regions, start_region_id=1)
    return regions, region_map


def reorder_regions(region_map, num_regions, start_region_id):
    # Erstelle eine Verbindungsstruktur (Adjazenzliste)
    connections = {i: set() for i in range(1, num_regions + 1)}
    for y in range(1, len(region_map) - 1):
        for x in range(1, len(region_map[0]) - 1):
            current_region = region_map[y][x]
            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ny, nx = y + dy, x + dx
                adjacent_region = region_map[ny][nx]
                if adjacent_region != current_region:
                    connections[current_region].add(adjacent_region)
                    connections[adjacent_region].add(current_region)

    # Rekursive Funktion, um Pfade zu erkunden
    def explore_path(path, visited):
        current_region = path[-1]
        if len(path) == num_regions:
            return path
        for neighbor in connections[current_region]:
            if neighbor not in visited:
                new_path = path + [neighbor]
                new_visited = visited | {neighbor}
                result = explore_path(new_path, new_visited)
                if result:
                    return result
        return None

    # Finde einen gültigen Pfad
    valid_path = explore_path([start_region_id], {start_region_id})
    if valid_path is None:
        return region_map

    # Erstelle eine Zuordnung von alten zu neuen Regionen-IDs
    region_id_mapping = {old_id: new_id for new_id, old_id in enumerate(valid_path, start=1)}

    # Aktualisiere die Regionen-IDs in der Regionenkarte
    for y in range(len(region_map)):
        for x in range(len(region_map[0])):
            old_region_id = region_map[y][x]
            new_region_id = region_id_mapping.get(old_region_id, old_region_id)
            region_map[y][x] = new_region_id
    return region_map


def generate_start_points(width, height, num_regions, seed):
    random.seed(seed)
    start_points = []

    # Berechne die Anzahl der Zeilen und Spalten im Gitter
    num_rows = int(np.ceil(num_regions ** 0.5))
    num_cols = int(np.ceil(num_regions / num_rows))

    # Berechne die Breite und Höhe jedes Teilbereichs
    region_width = width // num_cols
    region_height = height // num_rows

    # Generiere die Startpunkte für jeden Teilbereich
    for row in range(num_rows):
        for col in range(num_cols):
            if len(start_points) >= num_regions:
                break

            x = random.randint(col * region_width, (col + 1) * region_width - 1)
            y = random.randint(row * region_height, (row + 1) * region_height - 1)
            start_points.append((x, y))
    return start_points


def calculate_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


def extract_region_grid(labeled_map, region_id, points):
    start_point = get_point_for_region(points, region_id, point_type='start')
    end_point = get_point_for_region(points, region_id, point_type='end')

    # Verschieben Sie den Startpunkt, wenn er in einem Knotenpunkt liegt
    start_point = move_start_point_within_junction(labeled_map, region_id, start_point)

    region_grid = []
    height, width = len(labeled_map), len(labeled_map[0])

    for y in range(height):
        region_row = []
        for x in range(width):
            cell_value = labeled_map[y][x]

            if (y, x) == start_point:
                region_row.append(2)  # Startpunkt
            elif (y, x) == end_point:
                region_row.append(5)  # Endpunkt
            elif cell_value == f'__{region_id}':
                region_row.append(1)  # Region
            elif is_junction_point(y, x, labeled_map, region_id):
                region_row.append(1)  # Knotenpunkt
            else:
                region_row.append(0)  # Sonst

        region_grid.append(region_row)
    return region_grid


def move_start_point_within_junction(labeled_map, region_id, start_point):
    if region_id == 1:
        return start_point
    height, width = len(labeled_map), len(labeled_map[0])

    for y in range(height):
        for x in range(width):
            if labeled_map[y][x].startswith('T') and labeled_map[y][x].endswith(str(region_id-1)):
                return y, x

    return None  # Rückgabe von None, falls kein Startpunkt gefunden wurde


def is_junction_point(y, x, labeled_map, region_id):
    # Überprüfen Sie, ob der Punkt zu einem Knotenpunkt gehört
    if not labeled_map[y][x].startswith('KP'):
        return False

    # Überprüfen Sie, ob der Punkt an die aktuelle Region angrenzt
    for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        ny, nx = y + dy, x + dx
        if labeled_map[ny][nx] == f'__{region_id}':
            return True


def prepare_array(region_map, num_regions):
    height, width = len(region_map), len(region_map[0])
    labeled_map = [[''] * width for _ in range(height)]
    # Identifiziere die Knotenpunkte
    junction_points = find_junction_points(region_map)

    # Durchlaufen Sie jeden Bereich und füllen Sie die verbleibenden Zellen mit der Regions-ID
    for region_id in range(1, num_regions + 1):
        for y in range(height):
            for x in range(width):
                # Überprüfen, ob die Zelle an eine Zelle aus einer anderen Region grenzt
                if region_map[y][x] == region_id:
                    for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < height and 0 <= nx < width and region_map[ny][nx] != region_id:
                            labeled_map[y][x] = f'WW{region_id}'
                            break

                    # Wenn die Zelle nicht bereits als Grenze markiert ist, fügen Sie die Regions-ID hinzu
                    if not labeled_map[y][x]:
                        labeled_map[y][x] = f'__{region_id}'
    labeled_map = prepare_knots(labeled_map, region_map, num_regions, height, width, junction_points)
    return labeled_map


def prepare_knots(labeled_map, region_map, num_regions, height, width, junction_points):
    # Iterate through each junction point and mark it and its surroundings
    for knot_id, (x, y) in enumerate(junction_points, start=1):
        radius = 5

        # Identify the outer border of the node (KP1) in a circle shape
        outer_border = set()
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                ny, nx = y + dy, x + dx
                if 0 <= ny < height and 0 <= nx < width and abs(math.sqrt(dy ** 2 + dx ** 2) - radius) <= 1:
                    outer_border.add((ny, nx))

        # Identify the inner border of the node (KW1) in a circle shape
        inner_border = set()
        inner_radius = radius - 1
        for dy in range(-inner_radius, inner_radius + 1):
            for dx in range(-inner_radius, inner_radius + 1):
                ny, nx = y + dy, x + dx
                if 0 <= ny < height and 0 <= nx < width and abs(math.sqrt(dy ** 2 + dx ** 2) - inner_radius) <= 0.5:
                    inner_border.add((ny, nx))

        # Assign the borders, but do not overwrite WW{*} cells or the doors
        for ny, nx in outer_border:
            if not labeled_map[ny][nx].startswith(('T', 'WW')):
                labeled_map[ny][nx] = f'KP{knot_id}'
        for ny, nx in inner_border:
            if not labeled_map[ny][nx].startswith(('T')):
                labeled_map[ny][nx] = f'KW{knot_id}'

        # Mark the remaining cells as node
        for dy in range(-inner_radius + 1, inner_radius):
            for dx in range(-inner_radius + 1, inner_radius):
                ny, nx = y + dy, x + dx
                if 0 <= ny < height and 0 <= nx < width and math.sqrt(dy ** 2 + dx ** 2) < inner_radius and not \
                labeled_map[ny][nx].startswith(('KP', 'KW', 'T')):
                    labeled_map[ny][nx] = f'K_{knot_id}'

        # logic to set a door and set direction within each region
        for region_id in range(1, num_regions + 1):
            door_set_for_region = False  # Flag to check if a door has been set for the current region

            for door_y, door_x in inner_border:
                if door_set_for_region:  # If a door is already set for the region, skip the loop
                    break

                if labeled_map[door_y][door_x] == f'KW{knot_id}' and region_map[door_y][door_x] == region_id:
                    # Set the door orientation based on the KP cell direction
                    for dy, dx, direction in [(-1, 0, 'U'), (1, 0, 'D'), (0, -1, 'L'), (0, 1, 'R')]:
                        ny, nx = door_y + dy, door_x + dx
                        opposite_ny, opposite_nx = door_y - dy, door_x - dx
                        if 0 <= ny < height and 0 <= nx < width and labeled_map[ny][nx] == f'KP{knot_id}' and \
                                labeled_map[opposite_ny][opposite_nx].startswith('K_'):
                            if (region_id == 1):
                                labeled_map[door_y][door_x] = f't{direction}1'  # Setze ein Feld für das Sound Item.
                            else:
                                labeled_map[door_y][door_x] = f'T{direction}{region_id - 1}'
                            door_set_for_region = True  # Set the flag to true
                            break

    return labeled_map


def get_adjacent_regions(y, x, region_map):
    unique_regions = set()
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            unique_regions.add(region_map[y + dy][x + dx])

    return unique_regions - {0}  # Ignorieren Sie die Zellen, die nicht zu einer Region gehören


def punkt_an_kante_gen(width, height, region_map, region_id):
    punkt = None

    def is_valid_point(y, x):
        # Überprüfe den Abstand von mindestens vier Feldern zur nächsten Region
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                ny, nx = y + dy, x + dx
                if 0 <= ny < height and 0 <= nx < width and region_map[ny][nx] != 0 and region_map[ny][nx] != region_id:
                    return False
        return True

    # Definieren Sie die Kanten
    top_edge = [(0, x) for x in range(3, width - 3) if region_map[0][x] == region_id and all(
        region_map[y][x] == region_id for y in range(1, 4)) and is_valid_point(0, x)]
    right_edge = [(y, width - 1) for y in range(3, height - 3) if region_map[y][width - 1] == region_id and all(
        region_map[y][x] == region_id for x in range(width - 4, width - 1)) and is_valid_point(y, width - 1)]
    bottom_edge = [(height - 1, x) for x in range(3, width - 3) if region_map[height - 1][x] == region_id and all(
        region_map[y][x] == region_id for y in range(height - 4, height - 1)) and is_valid_point(height - 1, x)]
    left_edge = [(y, 0) for y in range(3, height - 3) if region_map[y][0] == region_id and all(
        region_map[y][x] == region_id for x in range(1, 4)) and is_valid_point(y, 0)]

    # Überprüfen Sie, ob eine der Kanten Punkte hat, und setzen Sie den Startpunkt
    for edge in [top_edge, right_edge, bottom_edge, left_edge]:
        if edge:
            y, x = edge[random.randint(0, len(edge) - 1)]  # Wählen Sie einen zufälligen Punkt entlang der Kante
            punkt = (y, x)
            break
    return punkt


def calculate_start_and_end_points(region_map, seed, num_regions):
    height, width = len(region_map), len(region_map[0])
    # Identifiziere die Knotenpunkte
    junction_points = find_junction_points(region_map)
    random.seed(seed)

    points = []
    for region_id in range(1, num_regions + 1):
        start_point = None
        end_point = None
        # Generiert den Startpunkt für Region 1
        if region_id == 1:
            start_point = punkt_an_kante_gen(width, height, region_map, region_id)
        else:
            # Restliche Startpunkte holen
            start_point = points[-1]['end']  # Setzen Sie den Startpunkt auf den Endpunkt der vorherigen Region

        if region_id == num_regions:
            end_point = punkt_an_kante_gen(width, height, region_map, region_id)
            # Letzten End Punkt selber erstellen
        else:
            potential_end_points = []
            for y, x in junction_points:
                adjacent_regions = get_adjacent_regions(x, y, region_map)
                if region_id in adjacent_regions and (region_id + 1) in adjacent_regions:
                    # Dieser Punkt ist ein gültiger Endpunkt für die aktuelle Region
                    potential_end_points.append((x, y))

            if potential_end_points:
                end_point = random.choice(potential_end_points)  # Wählen Sie einen zufälligen Punkt aus den möglichen Endpunkten
            else:
                return None

        points.append({'start': start_point, 'end': end_point})

    return points


def get_point_for_region(points, region_id, point_type):
    """
    Retrieve the start or end point for a specific region.

    :param points: List of dictionaries containing start and end points for regions
    :param region_id: The region ID to retrieve the point for
    :param point_type: 'start' or 'end' to specify which point to retrieve
    :return: Coordinates of the point for the given region, or None if not found
    """
    if point_type not in ['start', 'end']:
        raise ValueError("point_type must be 'start' or 'end'")

    if 1 <= region_id <= len(points):
        return points[region_id - 1].get(point_type)

    return None


def generate_maze_with_backtracking(region_grid, seed):
    # Initialisieren Sie die Gittergröße
    height, width = len(region_grid), len(region_grid[0])

    # Initialisieren Sie den Zufallszahlengenerator mit dem gegebenen Seed
    random.seed(seed)

    # Markieren Sie alle Punkte als unbesucht
    visited = [[False] * width for _ in range(height)]

    # Finden Sie den Startpunkt (die Zelle mit dem Wert 2)
    y_start, x_start = next((y, x) for y in range(height) for x in range(width) if region_grid[y][x] == 2)
    visited[y_start][x_start] = True

    # Rekursive Backtracking-Funktion
    def recursive_backtracking(y, x):
        # Mischen Sie die Richtungen, um eine zufällige Reihenfolge zu erhalten
        directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        random.shuffle(directions)

        # Durchlaufen Sie die Nachbarn in zufälliger Reihenfolge
        for dy, dx in directions:
            ny, nx = y + dy, x + dx
            wall_y, wall_x = y + dy // 2, x + dx // 2

            # Überprüfen Sie, ob der Nachbar innerhalb der Grenzen und unbesucht ist
            # und ob der Nachbarpunkt ein gültiger Pfadpunkt ist (keine Wand)
            if 0 <= ny < height and 0 <= nx < width and not visited[ny][nx] and region_grid[ny][nx] == 1:
                # Entfernen Sie die Wand zwischen dem aktuellen Punkt und dem Nachbarn
                region_grid[wall_y][wall_x] = 4  # Pfad
                region_grid[ny][nx] = 4  # Pfad

                # Markieren Sie den Nachbarn als besucht
                visited[ny][nx] = True

                # Rekursiver Aufruf für den Nachbarn
                recursive_backtracking(ny, nx)

    # Starten Sie den rekursiven Backtracking-Algorithmus am Startpunkt
    recursive_backtracking(y_start, x_start)
    return region_grid

def generate_maze_with_prim(region_grid, seed):
    height, width = len(region_grid), len(region_grid[0])
    random.seed(seed)

    # Markieren Sie alle Punkte als unbesucht
    visited = [[False] * width for _ in range(height)]

    # Finden Sie den Startpunkt (die Zelle mit dem Wert 2)
    y_start, x_start = next((y, x) for y in range(height) for x in range(width) if region_grid[y][x] == 2)

    # Verwenden Sie eine Liste, um die Grenzzellen zu speichern
    frontier = [(y_start, x_start)]
    visited[y_start][x_start] = True

    while frontier:
        y, x = random.choice(frontier)
        frontier.remove((y, x))
        region_grid[y][x] = 4  # Pfad

        # Fügen Sie Nachbarn zur Grenzliste hinzu
        for dy, dx in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            ny, nx = y + dy, x + dx
            if 0 <= ny < height and 0 <= nx < width and not visited[ny][nx] and region_grid[ny][nx] == 1:
                frontier.append((ny, nx))
                visited[ny][nx] = True
                wall_y, wall_x = y + dy // 2, x + dx // 2
                region_grid[wall_y][wall_x] = 4  # Pfad

    return region_grid


def find(parent, node):
    if parent[node] != node:
        parent[node] = find(parent, parent[node])
    return parent[node]

def union(parent, rank, x, y):
    xroot = find(parent, x)
    yroot = find(parent, y)

    if rank[xroot] < rank[yroot]:
        parent[xroot] = yroot
    elif rank[xroot] > rank[yroot]:
        parent[yroot] = xroot
    else:
        parent[yroot] = xroot
        rank[xroot] += 1

def generate_maze_with_kruskal(region_grid, seed):
    height, width = len(region_grid), len(region_grid[0])
    random.seed(seed)

    # Union-Find-Struktur
    parent = [i for i in range(height * width)]
    rank = [0] * (height * width)

    # Kantenliste (Wände)
    edges = []
    for y in range(0, height, 2):
        for x in range(0, width, 2):
            if region_grid[y][x] == 1:
                for dy, dx in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < height and 0 <= nx < width and region_grid[ny][nx] == 1:
                        edges.append((y, x, ny, nx))

    random.shuffle(edges)

    # Kruskal's Algorithmus
    for y1, x1, y2, x2 in edges:
        set1 = find(parent, y1 * width + x1)
        set2 = find(parent, y2 * width + x2)

        if set1 != set2:
            region_grid[y1][x1] = region_grid[y2][x2] = 4  # Pfad
            wall_y, wall_x = (y1 + y2) // 2, (x1 + x2) // 2
            region_grid[wall_y][wall_x] = 4  # Pfad

            union(parent, rank, set1, set2)

    return region_grid


def remove_walls_random(region_grid, seed, häufigkeit):
    random.seed(seed)

    # Finde alle Wände im Labyrinth
    walls = [(i, j) for i in range(len(region_grid)) for j in range(len(region_grid[0])) if region_grid[i][j] == 1]

    # Bestimme, wie viele Wände entfernt werden sollen
    num_walls_to_remove = int(len(walls) * häufigkeit)

    # Wähle zufällig Wände aus und ersetze sie durch Pfade
    for _ in range(num_walls_to_remove):
        i, j = random.choice(walls)
        region_grid[i][j] = 4
        walls.remove((i, j))

    return region_grid


def remove_walls_shortcut(region_grid, seed, häufigkeit):
    random.seed(seed)

    # Finde alle Wände im Labyrinth, die zwei gegenüberliegende Pfade haben
    walls = [(i, j) for i in range(1, len(region_grid) - 1) for j in range(1, len(region_grid[0]) - 1)
             if region_grid[i][j] == 1 and (
                 (region_grid[i-1][j] == 4 and region_grid[i+1][j] == 4) or
                 (region_grid[i][j-1] == 4 and region_grid[i][j+1] == 4))]

    # Bestimme, wie viele Wände entfernt werden sollen
    num_walls_to_remove = int(len(walls) * häufigkeit)

    # Wähle zufällig Wände aus und ersetze sie durch Pfade
    for _ in range(num_walls_to_remove):
        i, j = random.choice(walls)
        region_grid[i][j] = 4
        walls.remove((i, j))

    return region_grid


def remove_walls_edges(region_grid):
    new_region_grid = [row.copy() for row in region_grid]

    # Überprüfe jede Zelle im Labyrinth (außer die Randzellen)
    for i in range(1, len(region_grid) - 1):
        for j in range(1, len(region_grid[0]) - 1):
            # Wenn die aktuelle Zelle eine Wand ist
            if region_grid[i][j] == 1:
                # Zähle, wie viele der Nachbarzellen Pfade sind
                path_count = sum([
                    region_grid[i - 1][j] == 4,  # Oben
                    region_grid[i + 1][j] == 4,  # Unten
                    region_grid[i][j - 1] == 4,  # Links
                    region_grid[i][j + 1] == 4  # Rechts
                ])

                # Entferne die Wand, wenn mindestens drei Nachbarn Pfade sind
                if path_count >= 3:
                    new_region_grid[i][j] = 4

    return new_region_grid



def update_array_with_region_grid(map, region_grid, region_id, num_regions):
    height, width = len(region_grid), len(region_grid[0])
    for y in range(height):
        for x in range(width):
            cell_value = region_grid[y][x]
            if map[y][x] == f'__{region_id}':
                if cell_value == 4:  # Pfad
                    map[y][x] = f'P_{region_id}'
                elif cell_value == 1:  # Wand
                    map[y][x] = f'W_{region_id}'
                elif cell_value == 2:  # Start
                    map[y][x] = 's' + map[y][x][1:]

    return map


def clean_up(map, points, seed, num_regions, region_map):
    # Globalen Start Punkt setzen
    start_punkt = get_point_for_region(points, 1, point_type='start')
    x = start_punkt[1]
    y = start_punkt[0]
    radius = 1
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            ny, nx = y + dy, x + dx
            if 0 <= ny < len(map) and 0 <= nx < len(map[0]):
                map[ny][nx] = f's_1'
    map[y][x] = 'S_1'

    # Globalen End Punkt setzen
    end_punkt = get_point_for_region(points, num_regions, point_type='end')
    x = end_punkt[1]
    y = end_punkt[0]

    radius = 1
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            ny, nx = y + dy, x + dx
            if 0 <= ny < len(map) and 0 <= nx < len(map[0]):
                map[ny][nx] = f'e_{num_regions}'
    map[y][x] = f'E_{num_regions}'

    map = schlüssel_plazieren(map, num_regions, seed)
    map = fix_knot_path(map, region_map)
    map = wand_um_alles(map)
    map = dealer_platzieren(map, region_map, seed)
    return map


def fix_knot_path(map, region_map):
    rows, cols = len(map), len(map[0])
    transformed_map = [[None for _ in range(cols)] for _ in range(rows)]

    for i in range(rows):
        for j in range(cols):
            if "KP" in map[i][j]:
                transformed_map[i][j] = f"P_{region_map[i][j]}"
            else:
                transformed_map[i][j] = map[i][j]

    return transformed_map



def wand_um_alles(map):
    # Höhe und Breite der ursprünglichen Karte ermitteln
    height, width = len(map), len(map[0])

    # Neue Karte mit zusätzlichem Rand erstellen
    new_map = [['WWW'] * (width + 2) for _ in range(height + 2)]

    # Die ursprüngliche Karte in die neue Karte kopieren, wobei ein Rand von 1 Zelle freigelassen wird
    for y in range(height):
        for x in range(width):
            new_map[y + 1][x + 1] = map[y][x]

    return new_map


def dealer_platzieren(map, region_map, seed):
    junction_points = find_junction_points(region_map)
    random.seed(seed)

    for knot_id, (x, y) in enumerate(junction_points, start=1):
        # Identify the region by using the region_map
        region_id = region_map[y][x]
        # Generate random coordinates within the 3x3 block
        dx = random.randint(0, 1)
        dy = random.randint(0, 1)
        # Update the map position to "D_*" at the random location within the block
        map[y + dy + 1][x + dx + 1] = f'D_{region_id}'

    return map

def schlüssel_plazieren(map, num_regions, seed):
    height, width = len(map), len(map[0])
    random.seed(seed)

    for region_id in range(1, num_regions):
        positions = [(y, x) for y in range(1, height - 1) for x in range(1, width - 1) if map[y][x] == f'P_{region_id}']
        if positions:
            y, x = random.choice(positions)
            map[y][x] = f'KY{region_id + 1}'

    return map


def test_maze(map, num_regions):
    map = maze_vereinfachen(map, num_regions)
    #print("maze_vereinfachen: ")
    #print_map(map)
    height, width = len(map), len(map[0])

    # Finde den Startpunkt
    start_y, start_x = next((y, x) for y in range(height) for x in range(width) if map[y][x] == 2)

    # Erstelle eine Matrix, um die besuchten Punkte zu verfolgen
    visited = [[False] * width for _ in range(height)]

    # Erstelle eine Matrix für den Pfad
    path = [[0] * width for _ in range(height)]

    # Erstelle eine Warteschlange für die BFS
    queue = deque([(start_y, start_x)])

    # Beginne die BFS
    while queue:
        y, x = queue.popleft()

        # Überprüfe, ob der aktuelle Punkt das Ende ist
        if map[y][x] == 3:
            path[y][x] = 1  # Markiere das Ende im Pfad
            return path

        # Markiere den aktuellen Punkt im Pfad
        path[y][x] = 1

        # Gehe durch alle möglichen Richtungen (oben, unten, links, rechts)
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ny, nx = y + dy, x + dx

            # Überprüfe, ob der neue Punkt innerhalb der Grenzen und unbesucht ist und ob er ein Pfad ist
            if 0 <= ny < height and 0 <= nx < width and not visited[ny][nx] and map[ny][nx] != 1:
                visited[ny][nx] = True  # Markiere den neuen Punkt als besucht
                queue.append((ny, nx))  # Füge den neuen Punkt zur Warteschlange hinzu

    return None  # Gibt None zurück, wenn kein Pfad gefunden wurde


def maze_vereinfachen(map, num_regions):
    height, width = len(map), len(map[0])

    # Neue Karte erstellen
    simplified_map = [[0 for _ in range(width)] for _ in range(height)]

    for y in range(height):
        for x in range(width):
            cell_value = map[y][x]
            # Wenn die Zelle der Startpunkt ist
            if cell_value == "S_1":
                simplified_map[y][x] = 2
            # Wenn die Zelle der Endpunkt ist
            elif cell_value == f"E_{num_regions}":
                simplified_map[y][x] = 3
            # Wenn die Zelle ein Pfad ist
            elif cell_value.startswith(("P_", "K_", "s_", "e_")):
                simplified_map[y][x] = 0
            # Wenn die Zelle eine Wand ist
            else:
                simplified_map[y][x] = 1

    return simplified_map


def print_map(map_array):
    for row in map_array:
        print(" ".join(str(cell) for cell in row))


def print_junction_points(region_map):
    junction_points = find_junction_points(region_map)
    print("junction_points: " + str(junction_points))


def return_map(width, height, num_regions, seed):
    while True:
        #print(f" --------- SEED: {seed} ----------")


        regions, region_map, seed = generate_valid_regions(width - 2, height - 2, num_regions, seed)
        #print("prepare_array: Start")
        #print_map(region_map)
        map = prepare_array(region_map, num_regions)
        #print("prepare_array: Finish")
        #print_map(map)
        points = calculate_start_and_end_points(region_map, seed, num_regions)
        if points is not None:
            # Teilt num_regions so ein, dass maze_kategorie_leicht die meisten mazes enthält.
            maze_kategorie_teil = int(round((num_regions / 3), 0))
            maze_kategorie_rest = num_regions - 2 * maze_kategorie_teil
            if maze_kategorie_rest >= maze_kategorie_teil:
                maze_kategorie_mittel = maze_kategorie_rest
                maze_kategorie_leicht = maze_kategorie_teil
                maze_kategorie_Schwer = maze_kategorie_teil
            else:
                maze_kategorie_mittel = maze_kategorie_teil
                maze_kategorie_leicht = maze_kategorie_teil
                maze_kategorie_Schwer = maze_kategorie_rest

            # Listen der Algorithmen für die Kategorie "leicht", "mittel" und "schwer"
            leicht_algorithmen = [generate_maze_with_prim]
            mittel_algorithmen = [generate_maze_with_kruskal]
            schwer_algorithmen = [generate_maze_with_backtracking]


            for region_id in range(1, num_regions + 1):
                random_häufigkeit = round((num_regions - region_id) / (100 * (1 / 3)), 2)
                shortuct_häufigkeit = random_häufigkeit/3
                random.seed(seed)
                region_grid = extract_region_grid(map, region_id, points)
                #print("extract_region_grid: Start")
                #print_map(region_grid)
                if not maze_kategorie_leicht == 0:
                    # Wählen Sie einen Algorithmus zufällig aus der Liste aus
                    chosen_algorithm = random.choice(leicht_algorithmen)
                    # Entfernen Sie den ausgewählten Algorithmus aus der Liste
                    leicht_algorithmen.remove(chosen_algorithm)
                    # Führen Sie den ausgewählten Algorithmus aus
                    region_grid = chosen_algorithm(region_grid, seed)
                    if region_id == 1:
                        region_grid = remove_walls_edges(region_grid)
                        random_häufigkeit = 0
                        shortuct_häufigkeit = 0
                    maze_kategorie_leicht -= 1
                    # Wenn alle Algorithmen verwendet wurden, setzen Sie die Liste zurück
                    if not leicht_algorithmen:
                        leicht_algorithmen = [generate_maze_with_prim]
                elif not maze_kategorie_mittel == 0:
                    # Wählen Sie einen Algorithmus zufällig aus der Liste aus
                    chosen_algorithm = random.choice(mittel_algorithmen)
                    # Entfernen Sie den ausgewählten Algorithmus aus der Liste
                    mittel_algorithmen.remove(chosen_algorithm)
                    # Führen Sie den ausgewählten Algorithmus aus
                    region_grid = chosen_algorithm(region_grid, seed)
                    maze_kategorie_mittel -= 1
                    # Wenn alle Algorithmen verwendet wurden, setzen Sie die Liste zurück
                    if not mittel_algorithmen:
                        mittel_algorithmen = [generate_maze_with_kruskal]
                elif not maze_kategorie_Schwer == 0:
                    # Wählen Sie einen Algorithmus zufällig aus der Liste aus
                    chosen_algorithm = random.choice(schwer_algorithmen)
                    # Entfernen Sie den ausgewählten Algorithmus aus der Liste
                    schwer_algorithmen.remove(chosen_algorithm)
                    # Führen Sie den ausgewählten Algorithmus aus
                    region_grid = chosen_algorithm(region_grid, seed)
                    maze_kategorie_Schwer -= 1
                    # Wenn alle Algorithmen verwendet wurden, setzen Sie die Liste zurück
                    if not schwer_algorithmen:
                        schwer_algorithmen = [generate_maze_with_backtracking]
                #print("extract_region_grid: Finish")
                #print_map(region_grid)
                region_grid = remove_walls_random(region_grid, seed, random_häufigkeit)
                region_grid = remove_walls_shortcut(region_grid, seed, shortuct_häufigkeit)
                map = update_array_with_region_grid(map, region_grid, region_id, num_regions)
                #print("update_array_with_region_grid: Finish")
                #print_map(map)

            map = clean_up(map, points, seed, num_regions, region_map)

            '''
            if test_maze(map, num_regions):
                lösung = test_maze(map, num_regions)
                print("Lösung: ")
                print_map(lösung)
                print("FINAL: ")
                print_map(map)
            '''
            #print("Final Map:")
            #print_map(map)
            return map
        seed += 42


if  __name__ == '__main__':
    # Beispielaufruf
    width = 50
    height = 50
    num_regions = 6
    seed = random.randint(1, 1000000)

    map = return_map(width, height, num_regions, seed)
    print("Final Map:")
    print_map(map)

