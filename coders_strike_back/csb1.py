# https://www.codingame.com/ide/puzzle/coders-strike-back
import sys
import math
import random
from enum import Enum, IntEnum


def debug(msg):
    print('DEBUG:'+msg, file=sys.stderr)


def dist(p1, p2):
    return math.sqrt(((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2))


def speed(v):
    return math.sqrt(v[0]**2+v[1]**2)


def optarget(me, tar):
    return [me[0] * 2 - tar[0], me[1] * 2 - tar[1]]


def direct(s, d):
    return [d[0]-s[0], d[1]-s[1]]


def dvan(s, d, sv):
    r = [d[0]-s[0], d[1]-s[1]]
    if speed(sv) < 0.1 or speed(r) < 0.1:
        return 180
    t = (r[0]*sv[0]+r[1]*sv[1]) / (math.sqrt(r[0]**2+r[1]**2)*math.sqrt(sv[0]**2+sv[1]**2))
    t = 1 if t > 1 else t
    t = -1 if t < -1 else t
    return math.acos(t)*180/3.14


class Id(IntEnum):
    ME = 0
    OP = 1


class Unit:
    def __init__(self, _id, x=0, y=0, nc_x=0, nc_y=0, nc_dist=0, nc_angle=0):
        assert(isinstance(_id, Id))
        self.owner = _id
        self.x = x
        self.y = y
        self.nc_x = nc_x
        self.nc_y = nc_y
        self.nc_dist = nc_dist
        self.nc_angle = nc_angle
        self.vx = None
        self.vy = None

    def update(self, x, y, nc_x=0, nc_y=0, nc_dist=0, nc_angle=0):
        if self.vx == None and self.vy == None:
            (self.vx, self.vy) = (0, 0)
        else:
            (self.vx, self.vy) = (x - self.x, y - self.y)
        self.x = x
        self.y = y
        self.nc_x = nc_x
        self.nc_y = nc_y
        self.nc_dist = nc_dist
        self.nc_angle = nc_angle


class G:
    def __init__(self):
        self.cps = []
        self.cps_clear = False
        self.cp_r = 600
        self.pod_r = 400
        self.ang_v = 18  # Angular velocity
        self.vr_rate = 0.85  # velocity reduce rate
        self.me = Unit(Id.ME)
        self.op = Unit(Id.OP)

    def update_myself(self, str_me, onp=[(-1, -1)]):
        x, y, nc_x, nc_y, nc_dist, nc_angle = list(map(int, str_me.split()))
        self.me.update(x, y, nc_x, nc_y, nc_dist, nc_angle)
        if not self.cps_clear and onp[0] != (self.me.nc_x, self.me.nc_y):
            onp[0] = (self.me.nc_x, self.me.nc_y)
            if not (self.me.nc_x, self.me.nc_y) in self.cps:
                self.cps.append((self.me.nc_x, self.me.nc_y))
            else:
                self.cps_clear = True

    def update_opponent(self, str_op):
        self.op.x, self.op.y = list(map(int, str_op.split()))

    def idx_cps(self, p):
        return self.cps.index(p)


def process(g):
    assert (isinstance(g, G))
    if g.me.nc_angle > 90 or g.me.nc_angle < -90:
        act_x = g.me.nc_x
        act_y = g.me.nc_y
        thrust = 0
    else:
        if g.cps_clear and g.me.nc_dist < 2500 and \
                dvan((g.me.x, g.me.y), (g.me.nc_x, g.me.nc_y), (g.me.vx, g.me.vy)) < 20 and \
                speed((g.me.vx, g.me.vy)) > 250:
            idx = g.idx_cps((g.me.nc_x, g.me.nc_y))
            (act_x, act_y) = g.cps[(idx+1) % len(g.cps)]
            thrust = 0
        else:
            act_x = g.me.nc_x
            act_y = g.me.nc_y
            if g.me.nc_dist > 2000:
                thrust = 100
            else:
                thrust = 40
    action_str = '{} {} {} v={}'.format(int(act_x), int(act_y), int(thrust), int(speed((g.me.vx, g.me.vy))))
    return action_str


# game loop
_g = G()
while True:
    _g.update_myself(input())
    _g.update_opponent(input())
    _action_str = process(_g)
    print(_action_str)
