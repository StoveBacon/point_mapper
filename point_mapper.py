from collections import namedtuple
import csv
import math


Circle = namedtuple('Circle', ['x', 'y', 'r'])

# Data management
PointData = namedtuple('PointData', ['id', 'distances'])
DistanceData = namedtuple('DistanceData', ['origin', 'distance'])

# Data format:
# point id | measured point id 1 | measured point distance 1 | ... (more measurements)
def load_data(path):
    with open(path) as file:
        data = []
        rows = csv.reader(file)
        for row in rows:
            point_id = int(row[0])
            dist_data = []
            # Starting at 1 because the id is at 0
            for i in range(1, len(row), 2):
                if row[i] == '':
                    break
                origin = int(row[i])
                distance = float(row[i+1])
                dist_data.append(DistanceData(origin, distance))
            data.append(PointData(point_id, dist_data))

        return data

def write_csv(points):
    with open('points.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        for id, pos in points.items():
            writer.writerow([id, *pos])

# OpenSCAD doesn't support csv. Instead, a library of the data can be written and imported
def write_scad(points):
    with open('points.scad', 'w', newline='') as file:
        # Assigning the declaration string so it can be used for indentation later
        dec_string = 'points = ['
        file.write(dec_string + '\n')
        for id, pos in points.items():
            # Subtract 1 so it starts at the same position
            file.write(' ' * (len(dec_string)-1))
            file.write('[{0}, [{1},{2}]],\n'.format(id, *pos))
        file.write('];\n')

def write_tris_scad(tris):
    with open('tris.scad', 'w', newline='') as file:
        # Assigning the declaration string so it can be used for indentation later
        dec_string = 'tris = ['
        file.write(dec_string + '\n')
        for id, cons in tris.items():
            # Subtract 1 so it starts at the same position
            file.write(' ' * (len(dec_string)-1))
            file.write('[{0}, {1}],\n'.format(id, cons))
        file.write('];\n')


# Takes DistanceData and looks up point locations to make Circle(s) for use in equations
def convert_to_circle(points, distance_data):
    return [Circle(*points[p], d) for (p,d) in distance_data]

# Find the solutions for the intersections of two circles
def circle_intersect(circle1, circle2):
    # Check to make sure the circles actually intersect and aren't tangent
    circle_center_distance = math.dist((circle1.x,circle1.y), (circle2.x,circle2.y))
    if (circle_center_distance >= circle1.r + circle2.r or
        circle_center_distance + circle1.r < circle2.r or
        circle_center_distance + circle2.r < circle1.r):
        raise RuntimeError("Circles {} and {} do not intersect".format(circle1, circle2))

    precision = 10e-7
    delta = math.pi/10
    theta = 0.0
    last_distance = circle1.r * 2
    lowest = last_distance
    x1 = 0.0
    y1 = 0.0

    while lowest > precision:
        x1 = math.cos(theta)*circle1.r + circle1.x
        y1 = math.sin(theta)*circle1.r + circle1.y
        distance = abs(math.dist((x1,y1), (circle2.x,circle2.y)) - circle2.r)
        if distance > last_distance:
            delta *= -0.5
        theta += delta
        last_distance = distance
        if distance < lowest:
            lowest = distance

    # Compute the other point
    offset_angle = math.atan2((circle2.y-circle1.y), (circle2.x-circle1.x))
    theta += 2*(offset_angle-theta)
    x2 = math.cos(theta)*circle1.r + circle1.x
    y2 = math.sin(theta)*circle1.r + circle1.y

    return [(x1, y1), (x2, y2)]

# Manually solve first 3 points, making arbitrary decisions for ambiguous positons
# Arbitary decisions resolves any future ambiguity for later points
def solve_initial(data):
    points = {}
    
    # Manually fix the first point to 0
    points[data[0].id] = (0, 0)

    # Manually fix the second point to be directly above the first point
    point2_dist = data[1].distances[0].distance
    points[data[1].id] = (0, point2_dist)
    
    # Manually fix the third point to the first intersection found by the first two points
    intersects = convert_to_circle(points, data[2].distances)
    position = circle_intersect(intersects[0], intersects[1])[0]
    points[data[2].id] = position

    return points

def solve():
    data = load_data('data.csv')
    points = solve_initial(data)

    # We've already checked the first 3 points
    for point in data[3:]:
        circles = convert_to_circle(points, point.distances)
        intersects = circle_intersect(circles[0], circles[1])
        dists = [math.dist((circles[2].x, circles[2].y), p) for p in intersects]
        norm = [abs(dist-circles[2].r) for dist in dists]
        point_pos = intersects[0] if norm[0] < norm[1] else intersects[1]
        points[point.id] = point_pos

    return points

# Creates tringles between every point
def triangles(points):
    seen = {}
    for id, pos in points.items():
        dists = [(i, math.dist(pos, p)) for i, p in points.items() if i != id]
        unseen = [(i, p) for i, p in dists if seen.get(i) is None or id not in seen.get(i)]
        close = sorted(unseen, key=lambda p: p[1])[:2]
        seen[id] = [i[0] for i in close]
    return seen

locs = solve()
print("\n".join(map("Point: {0}, Position: {1}".format, locs, locs.values())))

#write_csv(locs)
# write_scad(locs)
# tris = triangles(locs)
# write_tris_scad(tris)
