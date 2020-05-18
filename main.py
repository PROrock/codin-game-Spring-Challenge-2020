import sys
import math

import time
import copy
import random

random.seed(0)

WALL = '#'
SPACE = ' '
EX_PELLET = '.'
ENEMY = 'E'

DIST_TO_ENEMY_ENGAGE = 4
beats={
    "ROCK": "SCISSORS",
    "SCISSORS": "PAPER",
    "PAPER": "ROCK"
}
is_beaten_by={
    "SCISSORS": "ROCK",
    "PAPER": "SCISSORS",
    "ROCK": "PAPER" 
}

map = []
# prev_round_pacs = {}
# my_pacs = {}

def debug_map():
    for row in map:
        print(row, file=sys.stderr, flush=True)

class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def l1dist(self, other_point):
        modulus_bs = lambda x, mod: min(x, mod-x)
        d = modulus_bs(abs(self.x-other_point.x), width) + modulus_bs(abs(self.y-other_point.y), height)
        # print(f"l1 dist: {self} and {other_point} is {d}", file=sys.stderr, flush=True)
        return d

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
        return Point((self.x + other_point.x)%width, (self.y+other_point.y)%height)

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
    def __init__(self, p, dist, p_value, path):
        self.p = p
        self.dist = dist
        self.p_value = p_value
        self.path = path

    def __str__(self):
        # todo path maybe?
        return f"N({self.p}, dist={self.dist}, p_val={self.p_value})"

    def __repr__(self):
        return self.__str__()

    def expand(self, visited):
        new_nodes = []
        possibilities = [Point(x,y) for x,y in zip([-1,1,0,0],[0,0,-1,1])]
        # random.shuffle(possibilities) # maybe worse than without shuffle?
        for poss in possibilities:
            new_p = self.p.add(poss)
            if(new_p not in visited):
                map_value = mapping(map, new_p)
                # print(f"new_point is {new_p}, map_val is: {map_value}", file=sys.stderr, flush=True)        
                if(map_value != WALL):
                    new_nodes.append(Node(new_p, self.dist+1, int(map_value)+1 if map_value in ['0', '9'] else -1, copy.copy(self.path)+[self.p]))

        # print(f"expanded from {self} are: {[str(node) for node in new_nodes]}", file=sys.stderr, flush=True)        
        return new_nodes

class Search:
    def __init__(self, start, goals):
        self.start = start
        self.goals = goals

    def search(self):
        s = 0
        for goal in self.goals:
            s+=sum([row.count(goal) for row in map])
        if s == 0:
            print(f"No goals {self.goals} on the map!", file=sys.stderr, flush=True)
            return None       

        front = [Node(self.start, 0, -1, [])]
        visited = set()
        
        while len(front) > 0:
            node = front.pop(0) ## take first element -> breadth-first
            # if(node.p not in visited):
            if True: ## todo
                if(mapping(map, node.p) in self.goals):
                    node.path.append(node.p)
                    print(f"Found goal: '{mapping(map, node.p)}'. Dist {node.dist}. Path is {node.path}", file=sys.stderr, flush=True)    
                    return node
                new_nodes = node.expand(visited)
                front.extend(new_nodes)
                visited.add(node.p)
                # print(f"visited is now: {[str(p) for p in visited]}", file=sys.stderr, flush=True)
            else:
                # print(f"l1 dist: {self} and {other_point} is {d}", file=sys.stderr, flush=True)
                pass
        print(f"Haven't found one of goals:{self.goals} for start: {self.start}", file=sys.stderr, flush=True)
        return None
        
class Goal:
    def __init__(self, command, comment):
        self.command = command
        self.comment = comment

    def to_print(self):
        return f"{self.command} {self.comment}"

    def __repr__(self):
        return f"G({self.to_print()})"

def argmax(list):
    list_val = lambda i: list[i]
    return max(range(len(list)), key=list_val)

def had_collision(id, prev_round_pacs, my_pacs):
    b=(id in prev_round_pacs and prev_round_pacs[id].p == my_pacs[id].p)
    # print(f"collision test id: {id} prev.p={'aaa'} curr.p={'bbb'} bool: {b}", file=sys.stderr, flush=True)
    return b
    
def move(id, p):
    return f"MOVE {id} {p.x} {p.y}"

def switch(id, type_id):
    return f"SWITCH {id} {type_id}"

def speed(id):
    return f"SPEED {id}"

def random_pellet():
    return Point(random.randrange(width), random.randrange(height))

def get_pac_move(pac, node):
    # print(f"node path {node.path}, speed {pac.speed_turns_left}", file=sys.stderr, flush=True)
    idx = 2 if pac.speed_turns_left > 0 and len(node.path) > 2 else 1
    for p in node.path[:idx+1]:
        map[p.y][p.x] = WALL # temp marking of future path of this pacman as walls so that other pacmans avoid this path 
    return node.path[idx]

def set_goal_with_close_enemy(pac, enemy, dist):
    type_id = is_beaten_by[enemy.type_id]
    max_dist = sum([speed>0 for speed in [pac.speed_turns_left, enemy.speed_turns_left]]) + 2
    print(f"conditions: dist={dist}, max_dist={max_dist}, pac={pac}, enemy={enemy}", file=sys.stderr, flush=True)
    
    if pac.ability_cooldown==0 and dist == (2 if enemy.speed_turns_left > 0 else 1):
        new_type = type_id if enemy.ability_cooldown>0 else is_beaten_by[is_beaten_by[pac.type_id]]
        return Goal(switch(pac.id, new_type), f"cool switching for {enemy}")

    if pac.type_id != type_id and pac.ability_cooldown==0 and dist <= max_dist:
        return Goal(switch(pac.id, type_id), f"switching for {enemy}")
    # todo : //4 because 2 is sometimes incorrect (3 can also be, if both are using speed)
    if (pac.type_id == type_id and enemy.ability_cooldown > (dist//2)) or (pac.ability_cooldown <= dist//2 and dist > max_dist):
        return Goal(move(pac.id, enemy.p), f"hunting {enemy}")
    if dist <= max_dist and (enemy.ability_cooldown <= (dist//2) or enemy.type_id == is_beaten_by[pac.type_id]):
        map[enemy.p.y][enemy.p.x] = ENEMY
        node = Search(pac.p, [ENEMY]).search()
        if node is not None:
            for p in node.path:
                map[p.y][p.x] = WALL
        
        # debug_map()

        node = Search(pac.p, [SPACE]).search()
        if node is not None:
            point = get_pac_move(pac, node)
            return Goal(move(pac.id, point), f"flee to {point}")
        else:
            print(f"cannot flee. ", file=sys.stderr, flush=True)

    return Goal(move(pac.id, random_pellet()), f"enemy close: {enemy} but dont know what to do")

def set_goal(pac,prev_round_pacs, my_pacs, goals):
    # hunting/fleeing from CLOSE enemy has priority
    if enemy_pacs:
        dist_map = {enemy.id: pac.p.l1dist(enemy.p) for enemy in enemy_pacs.values()}
        closest_enemy_id = min(dist_map.keys(), key=lambda key: dist_map[key])
        dist = dist_map[closest_enemy_id]
        # print(f"closest enemy to {pac} is enemy {enemy_pacs[closest_enemy_id]}, with dist {dist}", file=sys.stderr, flush=True)
    else:
        dist = 1000
    if dist < DIST_TO_ENEMY_ENGAGE:
        return set_goal_with_close_enemy(pac, enemy_pacs[closest_enemy_id], dist)

    # if had_collision(pac.id, prev_round_pacs, my_pacs):
    #     pellet = Point(random.randrange(width), random.randrange(height))
    #     return Goal(move(pac.id, pellet), f"coll -> random {pellet}")

    # todo must have next goal more distant than 1!
    if pac.ability_cooldown == 0:
        return Goal(speed(pac.id), f"speed!")


    node = Search(pac.p, ['9']).search()
    if node is not None and node.dist <= 12:
        point = get_pac_move(pac, node)
        return Goal(move(pac.id, point), f"vis. p. {point}")

    node = Search(pac.p, ['0', '9']).search()
    if node is not None and node.dist <= 7:
        point = get_pac_move(pac, node)
        return Goal(move(pac.id, point), f"vis. p. {point}")

    # prev_goal = goals[pac.id]
    # prev_cmd = prev_goal.command
    # if (prev_cmd.startswith("MOVE ")):
    #     x, y = prev_cmd.split(" ")[2:4]
    #     if (pac.p.x != int(x) or pac.p.y != int(y)):
    #         print(f"Prev goal not completed, continuing from pos {pac.p} to  x={x}, y={y} {prev_goal}", file=sys.stderr, flush=True)
    #         return prev_goal

    # go for closest unexplored space
    node = Search(pac.p, [' ']).search()
    if node is not None:
        point = get_pac_move(pac, node)
        return Goal(move(pac.id, point), f"explore {point}")
    else:
        point = Point(random.randrange(width), random.randrange(height))
        return Goal(move(pac.id, point), f"random {point}")

def generate_ex_pellets(pac):
    p = pac.p
    result = set([p])
    
    for grad in [Point(x, y) for x,y in zip([-1, 1, 0, 0], [0, 0, -1, 1])]:
        # print(f"p={p} grad={grad}", file=sys.stderr, flush=True)
        new_p = p

        while(True):
            new_p = new_p.add(grad)
            new_val = mapping(map, new_p)
            # print(f"new_p={new_p} new_val={new_val}", file=sys.stderr, flush=True)

            if (new_val == WALL):
                break
            if (new_val == SPACE):
                result.add(new_p)
    return result  

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
    my_score, opponent_score = [int(i) for i in input().split()]

    start_time = time.time()
    map = copy.deepcopy(orig_map)
    copy_time = time.time()
    print(f"copy time {copy_time-start_time}", file=sys.stderr, flush=True)


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

        # silver league BS
        if type_id == 'DEAD':
            continue
        pacman = Pac(pac_id, Point(x,y), mine, type_id, speed_turns_left, ability_cooldown)
        dictionary = my_pacs if mine else enemy_pacs
        dictionary[pac_id] = pacman
        print(f"pacman {pacman}", file=sys.stderr, flush=True)

    # print(f"prev dict {prev_round_pacs}", file=sys.stderr, flush=True)
    # print(f"my dict {my_pacs}", file=sys.stderr, flush=True)

    pacs_time = time.time()
    print(f"pacs time {pacs_time-copy_time}", file=sys.stderr, flush=True)


    visible_pellet_count = int(input())  # all pellets in sight
    # print(f"visible pellet count {visible_pellet_count}. Range {list(range(visible_pellet_count))}", file=sys.stderr, flush=True)

    for i in range(visible_pellet_count):
        # value: amount of points this pellet is worth
        x, y, value = [int(j) for j in input().split()]
        map[y][x] = str(value-1)

    pellet_time = time.time()
    print(f"pellet time1 {pellet_time-pacs_time}", file=sys.stderr, flush=True)


    # mark empty visible spaces as empty
    ex_pellets = set()
    for pac in my_pacs.values():
        ex_pellets.update(generate_ex_pellets(pac))
        # print(f"ex pellets now {ex_pellets}", file=sys.stderr, flush=True)
    

    for ex in ex_pellets:
        map[ex.y][ex.x] = EX_PELLET
        orig_map[ex.y][ex.x] = EX_PELLET


    # debug_map()

    # for id, pac in all_pacs.items():
        # print(f"{id}: {pac}", file=sys.stderr, flush=True)

    pellet_time = time.time()
    print(f"pellet time2 {pellet_time-pacs_time}", file=sys.stderr, flush=True)


    # todo detect dead pacs if you want nice code without warning
    # goals={}
    for pac in my_pacs.values():
        goals[pac.id] = set_goal(pac,prev_round_pacs, my_pacs, goals)


    # MOVE <pacId> <x> <y>
    # s=''.join([f"MOVE {id} {g.p.x} {g.p.y} {g.comment} | " for id, g in goals.items()])
    s=' | '.join([g.to_print() for g in goals.values()])
    print(s)
