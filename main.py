import sys
import math

import time
import copy
import random

random.seed(0)

WALL = '#'
SPACE = ' '
map = []

class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"P({self.x},{self.y})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, othr):
        return (isinstance(othr, type(self))
                and (self.x, self.y) ==
                    (othr.x, othr.y))
    def __hash__(self):
        return hash((self.x, self.y))

    def add(self, other_point):
        return Point(self.x + other_point.x, self.y+other_point.y)

class Pac:
    def __init__(self, id, p, mine, type_id, speed_turns_left, ability_cooldown):
        self.id = id
        self.p = p
        self.mine = mine
        self.type_id = type_id
        self.speed_turns_left = speed_turns_left
        self.ability_cooldown = ability_cooldown

    def __repr__(self):
        return f"Pac({self.id}, {self.p}, mine={self.mine}, type={self.type_id}, speed_t_left={self.speed_turns_left}, ab_coold={self.ability_cooldown})"


def mapping(map, point):
    if(point.x < 0 or point.x >= width or point.y < 0 or point.y >= height):
        return WALL
    return map[point.y][point.x]

class Node:
    def __init__(self, p, dist, p_value):
        self.p = p
        self.dist = dist
        self.p_value = p_value

    def __str__(self):
        return f"N({self.p}, dist={self.dist}, p_val={self.p_value})"

    def __repr__(self):
        return self.__str__()

    def expand(self, visited):
        new_nodes = []
        possibilities = [Point(x,y) for x,y in zip([-1,1,0,0],[0,0,-1,1])]
        for poss in possibilities:
            new_p = self.p.add(poss)
            if(new_p not in visited):
                map_value = mapping(map, new_p)
                # print(f"new_point is {new_p}, map_val is: {map_value}", file=sys.stderr)        
                if(map_value != WALL):
                    new_nodes.append(Node(new_p, self.dist+1, int(map_value)+1 if map_value!=SPACE else -1))

        # print(f"expanded from {self} are: {[str(node) for node in new_nodes]}", file=sys.stderr)        
        return new_nodes

class Search:
    def __init__(self, start):
        self.start = start
        # self.map = map

    def search(self):
        front = [Node(self.start, 0, -1)]
        visited = set()
        
        while len(front) > 0:
            node = front.pop(0) ## take first element -> breadth-first
            # if(node.p not in visited):
            if True: ## todo
                if(mapping(map, node.p) in ['0', '9']):
                    return node.p
                new_nodes = node.expand(visited)
                front.extend(new_nodes)
                visited.add(node.p)
                # print(f"visited is now: {[str(p) for p in visited]}", file=sys.stderr)
            else:
                # print(f"l1 dist: {self} and {other_point} is {d}", file=sys.stderr)
                pass
        print(f"Haven't found pellet for start: {self.start}", file=sys.stderr)
        return None
        
class Goal:
    def __init__(self, p, comment):
        self.p = p
        self.comment = comment

    def __repr__(self):
        return f"G({self.p},{self.comment})"


def had_collision(id, prev_round_pacs, my_pacs):
    return (id in prev_round_pacs and prev_round_pacs[id].p == my_pacs[id].p)

# Grab the pellets as fast as you can!

# width: size of the grid
# height: top left corner is (x=0, y=0)
width, height = [int(i) for i in input().split()]
orig_map = []
for i in range(height):
    row = input()  # one line of the grid: space " " is floor, pound "#" is wall
    orig_map.append(list(row))


my_pacs = {}
goals = {}

# game loop
while True:
    
    start_time = time.time()
    map = copy.deepcopy(orig_map)
    copy_time = time.time()
    print(f"copy time {copy_time-start_time}", file=sys.stderr)


    my_score, opponent_score = [int(i) for i in input().split()]

    prev_round_pacs = my_pacs
    my_pacs = {}
    enemy_pacs = {}
    visible_pac_count = int(input())  # all your pacs and enemy pacs in sight
    for i in range(visible_pac_count):
        # pac_id: pac number (unique within a team)
        # mine: true if this pac is yours
        # x: position in the grid
        # y: position in the grid
        # type_id: unused in wood leagues
        # speed_turns_left: unused in wood leagues
        # ability_cooldown: unused in wood leagues
        pac_id, mine, x, y, type_id, speed_turns_left, ability_cooldown = input().split()
        pac_id = int(pac_id)
        mine = mine != "0"
        x = int(x)
        y = int(y)
        speed_turns_left = int(speed_turns_left)
        ability_cooldown = int(ability_cooldown)

        pacman = Pac(pac_id, Point(x,y),mine, type_id, speed_turns_left, ability_cooldown)
        dictionary = my_pacs if mine else enemy_pacs
        dictionary[pac_id] = pacman
        # print(f"pacman {pacman}", file=sys.stderr)


    pacs_time = time.time()
    print(f"pacs time {pacs_time-copy_time}", file=sys.stderr)


    visible_pellet_count = int(input())  # all pellets in sight
    for i in range(visible_pellet_count):
        # value: amount of points this pellet is worth
        x, y, value = [int(j) for j in input().split()]
        map[y][x] = str(value-1)

    # for row in map:
        # print(row, file=sys.stderr)

    # for id, pac in all_pacs.items():
        # print(f"{id}: {pac}", file=sys.stderr)


    # todo detect dead pacs if you want nice code without warning
    goals={}
    for pac in my_pacs.values():
        pellet = Search(pac.p).search()
        # closest_pellet_d[pac.id] = pellet
        if pellet is not None and not had_collision(id,prev_round_pacs, my_pacs):
            goals[pac.id] = Goal(pellet, f"vis. p. {pellet}")
        elif had_collision(id,prev_round_pacs, my_pacs):
            pellet = Point(random.randrange(width), random.randrange(height))
            goals[pac.id] = Goal(pellet, f"coll -> random {pellet}")
        else:
            pellet = Point(random.randrange(width), random.randrange(height))
            goals[pac.id] = Goal(pellet, f"random {pellet}")


    pellet_time = time.time()
    print(f"pellet time {pellet_time-pacs_time}", file=sys.stderr)

    # MOVE <pacId> <x> <y>
    s=''.join([f"MOVE {id} {g.p.x} {g.p.y} {g.comment} | " for id, g in goals.items()])
    print(s)
