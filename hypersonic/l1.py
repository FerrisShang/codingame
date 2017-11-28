# https://www.codingame.com/ide/puzzle/hypersonic
import sys
import math
import random
from enum import Enum, IntEnum


def debug(msg):
    print(msg, file=sys.stderr)


class EntityType(IntEnum):
    Player = 0
    Bomb = 1


class Item(Enum):
    Empty = '.'
    Box = '0'


class Entity:
    def __init__(self, entity_str):
        self.type, self.owner, self.x, self.y, self.p1, self.p2 = list(map(int, entity_str.split()))


class G:
    def __init__(self, width, height, my_id):
        self.w = width
        self.h = height
        self.my_id = my_id
        self.map = None
        self.me = None
        self.enemies = None
        self.bombs = None

    def update_round(self, list_rows):
        self.map = [[[] for _ in range(self.w)] for _ in range(self.h)]
        self.me = None
        self.enemies = []
        self.bombs = []
        for r in range(len(list_rows)):
            row = list_rows[r]
            for i in range(self.w):
                self.map[r][i] = Item(row[i])

    def update_entity(self, entity):
        assert(isinstance(entity, Entity))
        if EntityType(entity.type) == EntityType.Player:
            if entity.owner == self.my_id:
                self.me = entity
            else:
                self.enemies.append(entity)
        if EntityType(entity.type) == EntityType.Bomb:
            self.bombs.append(entity)

    def in_range(self, x, y):
        return self.w > x >= 0 and self.h > y >= 0


def box_num(g, x, y, r=2):
    assert(isinstance(g, G))
    cnt = 0
    for _x in range(x - r, x + r):
        if g.in_range(_x, y) and g.map[y][_x]==Item.Box:
            cnt += 1
    for _y in range(y - r, y + r):
        if g.in_range(x, _y) and g.map[_y][x]==Item.Box:
            cnt += 1
    return cnt


def num_booms(g, id):
    assert(isinstance(g, G))
    cnt = 0
    for b in g.bombs:
        if b.owner == id:
            cnt += 1
    return cnt


def find_box(g, x, y, flag_map=None, res=None, r=2):
    assert(isinstance(g, G))
    if flag_map==None:
        flag_map = [[True for _ in range(g.w)] for _ in range(g.h)]
    if res==None:
        res = []
    if g.in_range(x, y) and flag_map[y][x]:
        flag_map[y][x] = False
        if g.map[y][x] == Item.Empty:
            num = box_num(g, x, y, r=r)
            if num > 0:
                res.append((num, [x, y]))
            for d in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                find_box(g, x+d[0], y+d[1], flag_map=flag_map, res=res)
    return res


def proc(g):
    assert(isinstance(g, G))
    boxes = find_box(g, g.me.x, g.me.y)
    _res = [-1, [0, 0]]
    for b in boxes:
        (n, x, y) = (b[0], b[1][0], b[1][1])
        _t = n / (abs(x)+abs(y)+1)
        if _t > _res[0]:
            _res = [_t, (x, y)]
    if (g.me.x, g.me.y) == (_res[1][0], _res[1][1]):
        return 'BOMB {} {}'.format(g.me.x, g.me.y)
    else:
        return 'MOVE {} {}'.format(_res[1][0], _res[1][1])


def run():
    width, height, my_id = list(map(int,input().split()))
    g = G(width, height, my_id)
    # game loop
    while True:
        rows = []
        for i in range(height):
            rows.append(input())
        g.update_round(rows)
        entities_num = int(input())
        for _ in range(entities_num):
            g.update_entity(Entity(input()))
        action = proc(g)
        print(action)

run()
