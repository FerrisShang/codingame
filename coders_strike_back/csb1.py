# https://www.codingame.com/ide/puzzle/coders-strike-back
import sys
import math
import random
import time
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
    return math.acos(t) * 180 / math.pi


def d_ang_abs(s, d, re_ang):
    _res = int(math.atan2((d[1] - s[1]), (d[0] - s[0])) * 180 / math.pi)
    if _res - re_ang > 180:
        return _res - re_ang - 360
    elif _res - re_ang < -180:
        return _res - re_ang + 360
    else:
        return _res - re_ang


class Id(IntEnum):
    ME = 0
    OP = 1


class Unit:
    def __init__(self, _id, x=0, y=0, nc_x=0, nc_y=0, nc_dist=0, nc_angle=0):
        assert(isinstance(_id, Id))
        self.owner = _id
        self.boost = True
        self.lap = 1
        self.x = x
        self.y = y
        self.nc_x = nc_x
        self.nc_y = nc_y
        self.nc_dist = nc_dist
        self.nc_angle = nc_angle
        self.vx = None
        self.vy = None
        self.path = []

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
        self.path.append((x, y))


class G:
    def __init__(self):
        self.H = 9000
        self.W = 16000
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
        self.me.update(x, G.m2m(y), nc_x, G.m2m(nc_y), nc_dist, G.m2m(nc_angle))
        if not self.cps_clear and onp[0] != (self.me.nc_x, self.me.nc_y):
            onp[0] = (self.me.nc_x, self.me.nc_y)
            if not (self.me.nc_x, self.me.nc_y) in self.cps:
                self.cps.append((self.me.nc_x, self.me.nc_y))
            else:
                self.cps_clear = True

    def update_opponent(self, str_op):
        x, y = list(map(int, str_op.split()))
        self.op.update(x, G.m2m(y))

    def idx_cps(self, p):
        return self.cps.index(p)

    def action(self, x, y, t, debug_msg=None):
        (x, y, t) = (int(x), int(G.m2m(y)), int(t) if isinstance(t, int) else t)
        if t == 'BOOST':
            self.me.boost = False
        if isinstance(debug_msg, str) and len(debug_msg) > 0:
            print('{} {} {} {}'.format(x, y, t, debug_msg))
        else:
            print('{} {} {}'.format(x, y, t))

    @staticmethod
    def m2m(y):
        return -y


def process(g):
    debug_msg = ''
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
                thrust = 'BOOST' if g.me.boost else 100
            else:
                thrust = 40
    debug_msg = '{}'.format(d_ang_abs((g.me.x, g.me.y), (g.me.nc_x, g.me.nc_y), g.me.nc_angle))
    return act_x, act_y, thrust, debug_msg


# game loop
_g = G()
while True:
    _g.update_myself(input())
    _g.update_opponent(input())
    st = int(round(time.time() * 1000))
    _x, _y, _t, _msg = process(_g)
    _g.action(_x, _y, _t, _msg)
    en = int(round(time.time() * 1000))
    debug('delay:{}ms'.format(en - st))
