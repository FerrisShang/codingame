# https://www.codingame.com/ide/puzzle/tron-battle
import sys
import math
import time
import random
import copy
from queue import PriorityQueue
from enum import Enum, IntEnum


def debug(msg):
    print('DEBUG: '+str(msg), file=sys.stderr)


class Time:
    _round_time = 100
    _min_t = 1e9
    _max_t = 0
    _sum_t = 0
    _num = 0
    _count = 0

    @staticmethod
    def set():
        Time._count = time.time()

    @staticmethod
    def get():
        _t = time.time() - Time._count
        Time._num += 1
        Time._sum_t += _t
        Time._min_t = min(_t, Time._min_t)
        Time._max_t = max(_t, Time._max_t)
        ave = Time._sum_t / Time._num
        debug('Time:{} ms, min:{} ms, max:{} ms, ave:{} ms'.format(
            int(_t*1000), int(Time._min_t*1000), int(Time._max_t*1000), int(ave*1000)))

    @staticmethod
    def left():
        return _round_time - int((time.time() - Time._count)*1000)


class C:
    dir = [(1, 0), (0, -1), (-1, 0), (0, 1)]
    dir_str = ['RIGHT', 'UP', 'LEFT', 'DOWN', ]


class P:
    def __init__(self):
        self.l = []
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None


class G:
    w = 30
    h = 20
    my_id = None

    def __init__(self):
        self.round = 0
        self.me = None
        self.player = [P() for _ in range(4)]
        self.map = [[False for _ in range(self.w)] for _ in range(self.h)]
        # init @ first time
        n, G.my_id = list(map(int, input().split()))
        for i in range(n):
            self.player[i].x0, self.player[i].y0, self.player[i].x1, self.player[i].y1 = \
                [int(j) for j in input().split()]
            self.map[self.player[i].y0][self.player[i].x0] = True
            self.map[self.player[i].y1][self.player[i].x1] = True
            self.player[i].l.append((self.player[i].y0, self.player[i].x0))
            self.player[i].l.append((self.player[i].y1, self.player[i].x1))
            if i == G.my_id:
                self.me = self.player[i]
        Time.set()

    @staticmethod
    def in_range(x, y):
        return G.w > x >= 0 and G.h > y >= 0

    def update_round(self):
        n, G.my_id = list(map(int, input().split()))
        for i in range(n):
            self.player[i].x0, self.player[i].y0, self.player[i].x1, self.player[i].y1 = \
                [int(j) for j in input().split()]
            if self.player[i].x1 >= 0:
                self.map[self.player[i].y1][self.player[i].x1] = True
                self.player[i].l.append((self.player[i].y1, self.player[i].x1))
            else:
                while len(self.player[i].l) > 0:
                    self.map[self.player[i].l[1]][self.player[i].l[0]] = False
                    del(self.player[i][0])
            if i == G.my_id:
                self.me = self.player[i]
        Time.set()


def live_num(g, x, y, flag_map=(None,)):
    assert(isinstance(g, G))
    if flag_map == (None,):
        flag_map = copy.deepcopy(g.map)
    res = 0
    if g.in_range(x, y) and not flag_map[y][x]:
        flag_map[y][x] = True
        res += 1
        for d in C.dir:
            res += live_num(g, x+d[0], y+d[1], flag_map)
    return res


def process(g):
    assert(isinstance(g, G))
    max_d, max_n = ('LEFT', 0)
    for d, d_str in zip(C.dir, C.dir_str):
        _t = live_num(g, g.me.x1+d[0], g.me.y1+d[1])
        if _t > max_n:
            max_n = _t
            max_d = d_str
        elif _t == max_n and random.randint(0, 1) > 0:
            max_n = _t
            max_d = d_str
    act = max_d
    return act


def run():
    random.seed(0)
    g = G()
    # game loop
    while True:
        debug('-------------({}, {}) {}'.format(
            g.me.x1, g.me.y1,
            [g.map[y][x] for x in range(G.w) for y in range(G.h)].count(True)))
        action = process(g)
        print(action)
        Time.get()
        g.update_round()

if __name__ == '__main__':
    run()
