# https://www.codingame.com/ide/puzzle/hypersonic
import sys
import math
import time
import random
import copy
from queue import PriorityQueue
from enum import Enum, IntEnum


def debug(msg):
    print('DEBUG: '+msg, file=sys.stderr)


class Time:
    min_t = 1e9
    max_t = 0
    sum_t = 0
    num = 0
    count = 0

    @staticmethod
    def set():
        Time.count = time.time()

    @staticmethod
    def get():
        _t = time.time() - Time.count
        Time.num += 1
        Time.sum_t += _t
        Time.min_t = min(_t, Time.min_t)
        Time.max_t = max(_t, Time.max_t)
        ave = Time.sum_t / Time.num
        debug('Time:{} ms, min:{} ms, max:{} ms, ave:{} ms'.format(
            int(_t*1000), int(Time.min_t*1000), int(Time.max_t*1000), int(ave*1000)))


def dist(x1, y1, x2, y2):
    return abs(x1-y1)+abs(x2-y2)


class EntityType(IntEnum):
    Walls = -2
    Boxes = -1
    Player = 0
    Bomb = 1
    Items = 2


class Entity:
    def __init__(self, t, o, x, y, p1, p2):
        self.type = t
        self.owner = o
        self.x = x
        self.y = y
        self.p1 = p1
        self.p2 = p2

    def __str__(self):
        return 'Entity: T:{},({},{}),P1:{},P2:{}'.format(self.type, self.x, self.y, self.p1, self.p2)


class C:
    dir_path_list = None

    def __init__(self):
        C.dir_path_list = [[[(x, 0) for x in range(1, r)],
                           [(x, 0) for x in range(-1, -r, -1)],
                           [(0, y) for y in range(1, r)],
                           [(0, y) for y in range(-1, -r, -1)]] for r in range(0, 15)]

    @staticmethod
    def get_dir_path_list(r):
        assert 3 <= r <= 13
        return C.dir_path_list[r]


class G:
    w = None
    h = None
    my_id = None

    def __init__(self):
        C()
        Time().set()
        width, height, my_id = list(map(int, input().split()))
        G.w = width
        G.h = height
        G.my_id = my_id
        self.path_map = None
        self.entities_map = None
        self.death_map = None
        self.me = None
        self.players = None
        self.bombs = None
        self.items = None
        self.boxes = None
        self.max_bomb_range = 3

    def update_round(self):
        self.path_map = [[True for _ in range(self.w)] for _ in range(self.h)]
        self.entities_map = [[None for _ in range(self.w)] for _ in range(self.h)]
        self.players = []
        self.bombs = []
        self.items = []
        self.boxes = []

        for h in range(G.h):
            rows = input()
            for w in range(G.w):
                if rows[w] != '.':
                    self.path_map[h][w] = False
                    if rows[w] == 'X':
                        item = Entity(EntityType.Walls.value, 0, w, h, 0, 0)
                    else:
                        item = Entity(EntityType.Boxes.value, 0, w, h, int(rows[w]), 0)
                        self.boxes.append(item)
                    self.entities_map[h][w] = item
        entities_num = int(input())
        for _ in range(entities_num):
            entity = Entity(*list(map(int, input().split())))
            self.entities_map[entity.y][entity.x] = entity
            if entity.type == EntityType.Player.value:
                if entity.owner == G.my_id:
                    self.me = entity
                self.players.append(entity)
            elif entity.type == EntityType.Bomb.value:
                self.path_map[entity.y][entity.x] = False
                self.bombs.append(entity)
            elif entity.type == EntityType.Items.value:
                self.items.append(entity)
        self.max_bomb_range = max([item.p2 for item in self.players])
        self.death_map = self.get_death_map()

    def get_death_map(self, extra_bombs=None, bombs_delay=0, e_map=(None,), bombs=(None,), d_map=(None,)):
        if d_map == (None,):
            d_map = [[[False for _ in range(G.w)] for _ in range(G.h)] for _ in range(8)]
            e_map = copy.deepcopy(self.entities_map)
            bombs = copy.deepcopy(self.bombs)
            for i in range(len(bombs)-1, -1, -1):
                if bombs[i].p1 - bombs_delay <= 0:
                    del(bombs[i])
                else:
                    bombs[i].p1 -= bombs_delay
            bombs += (extra_bombs if extra_bombs else [])
        # cal conn bombs
        num_bombs = len(bombs)
        if num_bombs == 0:
            return d_map
        least_boom = min(bombs, key=lambda _bomb: _bomb.p1).p1
        for i in range(num_bombs):
            for j in range(num_bombs):
                if i != j and (bombs[i].p1 == least_boom or bombs[j].p1 == least_boom):
                    if G.conn_boom(e_map, bombs[i], bombs[j]):
                        bombs[i].p1 = least_boom
                        bombs[j].p1 = least_boom
        # cal update death_map
        destroy_entities_list = []
        for i in range(num_bombs):
            if bombs[i].p1 == least_boom:
                d_map[bombs[i].p1-1][bombs[i].y][bombs[i].x] = True
                for p_bomb in C.get_dir_path_list(bombs[i].p2):
                    for p in p_bomb:
                        if not G.in_range(bombs[i].x+p[0], bombs[i].y+p[1]):
                            break
                        e = e_map[bombs[i].y+p[1]][bombs[i].x+p[0]]
                        d_map[bombs[i].p1-1][bombs[i].y+p[1]][bombs[i].x+p[0]] = True
                        if e and e.type != EntityType.Player.value and e.type != EntityType.Items.value:
                            destroy_entities_list.append((bombs[i].x+p[0], bombs[i].y+p[1]))
                            break
        # remove bombs
        for i in range(num_bombs-1, -1, -1):
            if bombs[i].p1 == least_boom:
                del(bombs[i])
        # remove destroyed entities
        for pos in destroy_entities_list:
            e_map[pos[1]][pos[0]] = None
        # iter d_map
        self.get_death_map(e_map=e_map, bombs=bombs, d_map=d_map)

        return d_map

    def create_bomb(self, x, y, r=None):
        return Entity(EntityType.Bomb.value, G.my_id, x, y, 8, r if r else self.me.p2)

    @staticmethod
    def conn_boom(e_map, b1, b2):
        m = max(b1.p2, b2.p2)
        if b1.x == b2.x and m > abs(b1.y - b2.y):
            for _y in range(b1.y+1, b2.y) if b2.y > b1.y else range(b2.y+1, b1.y):
                if G.in_range(b1.x, _y) and e_map[_y][b1.x] and e_map[_y][b1.x].type != EntityType.Player.value:
                    return False
            return True
        elif b1.y == b2.y and m > abs(b1.x - b2.x):
            for _x in range(b1.x+1, b2.x) if b2.x > b1.x else range(b2.x+1, b1.x):
                if G.in_range(_x, b1.y) and e_map[b1.y][_x] and e_map[b1.y][_x].type != EntityType.Player.value:
                    return False
            return True
        return False

    @staticmethod
    def in_range(x, y):
        return G.w > x >= 0 and G.h > y >= 0


def boom_num(g, x, y, r=3, entity_type=EntityType.Boxes.value):
    assert(isinstance(g, G))
    cnt = 0
    for p_bomb in C.get_dir_path_list(r):
        for p in p_bomb:
            (_x, _y) = (x+p[0], y+p[1])
            if g.in_range(_x, _y) and g.entities_map[_y][_x]:
                if entity_type == g.entities_map[_y][_x].type:
                    cnt += 1
                    break
                elif g.entities_map[_y][_x].type != EntityType.Player.value:
                    break
    return cnt


def wait_bomb(g):
    assert(isinstance(g, G))
    if g.me.p1 > 0:
        return 0
    _min = 8
    for b in g.bombs:
        if b.owner == G.my_id:
            _min = min(_min, b.p1)
    return _min


def find_box(g, x, y, r, init_pos=(None,), flag_map=(None,), res=(None,)):
    assert(isinstance(g, G))
    if flag_map == (None,):
        flag_map = [[True for _ in range(G.w)] for _ in range(G.h)]
        res = []
        init_pos = (x, y)
    if g.in_range(x, y) and flag_map[y][x]:
        flag_map[y][x] = False
        if g.path_map[y][x] or init_pos == (x, y):
            if g.path_map[y][x] or g.entities_map[y][x].type != EntityType.Bomb.value:
                num = boom_num(g, x, y, r, EntityType.Boxes.value)
                if num > 0:
                    res.append([num, x, y])
            for d in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                find_box(g, x+d[0], y+d[1], r, init_pos=init_pos, flag_map=flag_map, res=res)
    return res


def get_all_dist_pos(g, x, y, max_range=32, extra_block=None):
    assert(isinstance(g, G))
    flag_map = [[True for _ in range(G.w)] for _ in range(G.h)]
    flag_map[y][x] = False
    res = [(0, (x, y))]
    c_list = [(x, y), (x+1, y), (x-1, y), (x, y+1), (x, y-1)]
    t_path = copy.deepcopy(g.path_map)
    if extra_block:
        for b in extra_block:
            t_path[b[1]][b[0]] = False
    for _ in range(1, max_range):
        n_list = []
        for p in c_list:
            (x, y) = (p[0], p[1])
            if g.in_range(x, y) and flag_map[y][x] and t_path[y][x]:
                flag_map[y][x] = False
                res.append((_, (x, y)))
                for d in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    n_list.append((x+d[0], y+d[1]))
        c_list = n_list
        if len(c_list) == 0:
            return res
    return res


def get_all_step(g, x, y, extra_block=None):
    assert(isinstance(g, G))
    flag_map = [[True for _ in range(G.w)] for _ in range(G.h)]
    flag_map[y][x] = False
    res = [[(x, y)] for _ in range(8)]
    c_list = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
    t_path = copy.deepcopy(g.path_map)
    if extra_block:
        for b in extra_block:
            t_path[b[1]][b[0]] = False
    for step in range(1, 8):
        n_list = []
        for p in c_list:
            (x, y) = (p[0], p[1])
            if g.in_range(x, y) and flag_map[y][x] and t_path[y][x]:
                flag_map[y][x] = False
                for i in range(step, 8):
                    res[i].append((x, y))
                for d in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    n_list.append((x+d[0], y+d[1]))
        c_list = n_list
    return res


def get_path(me_pos, tar_pos, path_map):
    if me_pos == tar_pos:
        return [me_pos]
    frontier = PriorityQueue()
    frontier.put((0, me_pos))
    came_from = {me_pos: None}
    cost_so_far = {me_pos: 0}

    while not frontier.empty():
        current = frontier.get()[1]
        if current == tar_pos:
            break
        neighbors = [(current[0]+1, current[1]), (current[0], current[1]+1),
                     (current[0]-1, current[1]), (current[0], current[1]-1)]
        for n in neighbors:
            if not (G.in_range(n[0], n[1]) and path_map[n[1]][n[0]]):
                continue
            new_cost = cost_so_far[current] + 0.8
            if n not in cost_so_far or new_cost < cost_so_far[n]:
                cost_so_far[n] = new_cost
                priority = new_cost + abs(tar_pos[0] - n[0]) + abs(tar_pos[1] - n[1])
                frontier.put((priority, n))
                came_from[n] = current
    if tar_pos not in came_from:
        return []
    res = [tar_pos]
    _t = tar_pos
    while True:
        _t = came_from[_t]
        if _t == me_pos:
            break
        res.append(_t)
    return res[::-1]


def is_path_boom(g, path):
    assert(isinstance(g, G))
    idx_range = len(path)+1 if len(path) < 8 else 8
    for i in range(1, idx_range):
        (x, y) = (path[i-1][0], path[i-1][1])
        if g.death_map[i][y][x]:
            return True
    return False


def gen_bombs_players(g, exclude_id=None):
    assert(isinstance(g, G))
    if not exclude_id:
        exclude_id = []
    res = []
    for p in g.players:
        assert(isinstance(p, Entity))
        if p.owner not in exclude_id and p.p1 > 0:
            res.append(g.create_bomb(p.x, p.y, p.p2))
    return res


def is_dying(g, me_pos, extra_bombs=None, bombs_delay=0):
    assert(isinstance(g, G))
    t_path = copy.deepcopy(g.path_map)
    if extra_bombs:
        for b in extra_bombs:
            t_path[b.y][b.x] = False
    extra_block = []
    if extra_bombs:
        extra_block = [(b.x, b.y) for b in extra_bombs]
    all_pos = get_all_step(g, me_pos[0], me_pos[1], extra_block)
    death_map = g.get_death_map(extra_bombs, bombs_delay)
    p = all_pos[0][0]
    danger_flag = False
    for i in range(7, 0, -1):
        if death_map[i][p[1]][p[0]]:
            danger_flag = True
            break
    if danger_flag:
        ol_dict = set()
        for i in range(0, 8):
            if i == 0:
                ol_dict.add(me_pos)
                continue
            nl_dict = ol_dict
            ol_dict = set()
            for (_x, _y) in nl_dict:
                for d in [(0, 0), (-1, 0), (0, -1), (1, 0), (0, 1)]:
                    (x, y) = (_x+d[0], _y+d[1])
                    if g.in_range(x, y) and not death_map[i][y][x]:
                        if t_path[y][x] or (me_pos == (_x, _y) == (x, y)):
                            ol_dict.add((x, y))
        if len(ol_dict) == 0:
            return True
    return False


def item_pri(g, t_dist_pos):
    res = []
    for _d, (x, y) in t_dist_pos:
        is_item = g.entities_map[y][x].type == EntityType.Items.value if g.entities_map[y][x] else False
        if is_item:
            res.append([_d, (x, y)])
        else:
            b_delay = wait_bomb(g)
            b_num = boom_num(g, x, y, g.me.p2, EntityType.Boxes.value)
            if b_num > 0:
                res.append([b_delay + 4-b_num+_d, (x, y)])
    return res


def process(g):
    assert(isinstance(g, G))
    _tx, _ty = (-1, -1)
    target = None
    # terminate judgement
    if g.me.p1 > 0 and g.path_map[g.me.y][g.me.x] and boom_num(g, g.me.x, g.me.y, g.me.p2, EntityType.Player.value) > 0:
        if not is_dying(g, (g.me.x, g.me.y), gen_bombs_players(g), 0):
            debug('Hmmmm....')
            for p in g.players:
                if p.owner == G.my_id or (p.x != g.me.x and p.y != g.me.y) or dist(p.x, p.y, g.me.x, g.me.y) > g.me.p2:
                    continue
                if is_dying(g, (p.x, p.y), gen_bombs_players(g, exclude_id=[p.owner]), 0):
                    debug('Yooooo !!!')
                    target = (g.me.x, g.me.y)
    # find box
    if not target and g.me.p1 > 0:
        box_pos = find_box(g, g.me.x, g.me.y, g.me.p2)
        extra_weight = 1 if g.me.p1 == 1 else 1
        box_pos.sort(key=lambda n: (extra_weight+len(get_path((g.me.x, g.me.y), (n[1], n[2]), g.path_map))) / n[0])
        for p in box_pos:
            ref_pos = (p[1], p[2])
            _path = get_path((g.me.x, g.me.y), ref_pos, g.path_map)
            _bombs = gen_bombs_players(g, exclude_id=[G.my_id])+[g.create_bomb(ref_pos[0], ref_pos[1])]
            if is_path_boom(g, _path) or is_dying(g, ref_pos, _bombs, len(_path)):
                continue
            target = (p[1], p[2])
            _tx, _ty = (_path[0][0], _path[0][1])
            debug('TargetBox:({}, {}), pri:{}'.format(p[1], p[2], p[0]))
            break
    # item on path of target
    for d in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
        (x, y) = (g.me.x+d[0], g.me.y+d[1])
        if G.in_range(x, y) and g.entities_map[y][x] and g.entities_map[y][x].type == EntityType.Items.value:
            _path = [(x, y)]
            bombs = gen_bombs_players(g, exclude_id=[] if target == (g.me.x, g.me.y) else [G.my_id])
            if is_path_boom(g, _path) or is_dying(g, (x, y), bombs, len(_path)):
                continue
            _tx, _ty = (_path[0][0], _path[0][1])
            debug('Item on path:({}, {})'.format(x, y))
            break
    # no target & no item on path
    if target == (g.me.x, g.me.y) or (_tx, _ty) == (-1, -1):
        all_dist_pos = get_all_dist_pos(g, g.me.x, g.me.y)
        all_pos_pri = item_pri(g, all_dist_pos)
        all_pos_pri.sort(key=lambda item: item[0])
        for pri, _pos in all_pos_pri:
            _path = get_path((g.me.x, g.me.y), (_pos[0], _pos[1]), g.path_map)
            bombs = gen_bombs_players(g, exclude_id=[] if target == (g.me.x, g.me.y) else [G.my_id])
            if is_path_boom(g, _path) or is_dying(g, _pos, bombs, len(_path)):
                continue
            _tx, _ty = (_path[0][0], _path[0][1])
            debug('seek item:({}, {})'.format(_tx, _ty))
            break
    # need random walk
    if target == (g.me.x, g.me.y) or (_tx, _ty) == (-1, -1):
        all_dist_pos = get_all_dist_pos(g, g.me.x, g.me.y)
        for _, (x, y) in all_dist_pos:
            if g.path_map[y][x] or (x, y) == (g.me.x, g.me.y):
                _path = get_path((g.me.x, g.me.y), (x, y), g.path_map)
                bombs = gen_bombs_players(g, exclude_id=[] if target == (g.me.x, g.me.y) else [G.my_id])
                if is_path_boom(g, _path) or is_dying(g, (x, y), bombs, len(_path)):
                    continue
                _tx, _ty = (_path[0][0], _path[0][1])
                debug('Random walk:({}, {})'.format(_tx, _ty))
                break
    if (_tx, _ty) == (-1, -1):
        debug('No where to go !!')
    debug('C:({},{}) T:({},{})'.format(g.me.x, g.me.y, target[0] if target else -1, target[1] if target else -1))
    if target == (g.me.x, g.me.y):
        _act = 'BOMB'
    else:
        _act = 'MOVE'
    if (_tx, _ty) == (-1, -1):
        return '{} {} {} ???'.format(_act, _tx, _ty)
    else:
        return '{} {} {}'.format(_act, _tx, _ty)


def run():
    random.seed(0)
    g = G()
    # game loop
    while True:
        g.update_round()
        debug('----------------')
        Time().set()
        action = process(g)
        print(action)
        Time.get()

if __name__ == '__main__':
    run()
