# https://www.codingame.com/ide/puzzle/coders-strike-back
import sys
import math
import time
from enum import IntEnum


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


def vvan(v1, v2):
    if speed(v2) < 0.1 or speed(v1) < 0.1:
        return 180
    t = (v1[0]*v2[0]+v1[1]*v2[1]) / (math.sqrt(v1[0]**2+v1[1]**2)*math.sqrt(v2[0]**2+v2[1]**2))
    t = 1 if t > 1 else t
    t = -1 if t < -1 else t
    return math.acos(t) * 180 / math.pi


def abs_ang(a):
    return a - 360 if a > 180 else a + 360 if a < -180 else a


def d_ang_abs(s, d, re_ang):
    _res = int(math.atan2((d[1] - s[1]), (d[0] - s[0])) * 180 / math.pi)
    return abs_ang(_res - re_ang)


class Id(IntEnum):
    ME = 0
    OP = 1


class Unit:
    def __init__(self, g, _id, x=0, y=0, nc_x=0, nc_y=0, nc_dist=0, nc_angle=0):
        assert(isinstance(_id, Id))
        assert(isinstance(g, G))
        self.g = g
        self.owner = _id
        self.boost = True
        self.lap = 0
        self.p = (x, y)
        self.ang = 0
        self.nc = (nc_x, nc_y)
        self.nnc = (None, None)
        self.nc_dist = nc_dist
        self.nc_angle = nc_angle
        self.onp = (-1, -1)
        self.v = (None, None)
        self.path = []

    def update(self, x, y, nc_x=0, nc_y=0, nc_dist=0, nc_angle=0):
        if self.v == (None, None):
            self.v = (0, 0)
        else:
            self.v = (int((x - self.p[0]) * G.vr_rate), int((y - self.p[1]) * G.vr_rate))
        self.p = (x, y)
        if self.owner != Id.ME:
            return
        self.nc = (nc_x, nc_y)
        self.nc_dist = nc_dist
        self.nc_angle = nc_angle
        self.ang = d_ang_abs(self.p, self.nc, self.nc_angle)
        self.path.append((x, y))
        check_points = self.g.cps
        if self.onp != (nc_x, nc_y):
            self.onp = (nc_x, nc_y)
            if self.onp == check_points[0]:
                self.lap += 1
        if self.g.cps_clear:
            _idx = self.g.idx_cps(self.nc)
            self.nnc = self.g.cps[(_idx + 1) % len(self.g.cps)]
        else:
            self.nnc = (int(G.W/2), int(-G.H/2))


class G:
    H = 9000
    W = 16000
    BOOST = 650
    cp_r = 600
    pod_r = 400
    ang_v = 18  # Angular velocity
    vr_rate = 0.85  # velocity reduce rate

    def __init__(self):
        self.cps = []
        self.cps_clear = False
        self.me = Unit(self, Id.ME)
        self.op = Unit(self, Id.OP)

    def update_myself(self, str_me):
        x, y, nc_x, nc_y, nc_dist, nc_angle = list(map(int, str_me.split()))
        nc_y = G.m2m(nc_y)
        if not self.cps_clear:
            if not (nc_x, nc_y) in self.cps:
                self.cps.append((nc_x, nc_y))
            elif (nc_x, nc_y) == self.cps[0] and len(self.cps) > 1:
                debug('CheckPoint:{}'.format(self.cps))
                self.cps_clear = True
        self.me.update(x, G.m2m(y), nc_x, nc_y, nc_dist, G.m2m(nc_angle))

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


class Sim:
    ang_v = 18  # Angular velocity
    vr_rate = 0.85  # velocity reduce rate
    cp_r = 600

    def __init__(self, target=None, x=None, y=None, ang=None, vx=0, vy=0):
        self.x = target[-1][0] if x==None else x
        self.y = target[-1][1] if y==None else y
        self.ang = d_ang_abs(target[-1], target[0], 0) if ang==None else ang
        self.vx = vx
        self.vy = vy
        self.step = 0
        self.path_list = []

    def update(self, x, y, t):
        des_ang = int(math.atan2(y-self.y, x-self.x)*180/math.pi)
        if abs(abs_ang(des_ang - self.ang)) <= self.ang_v:
            self.ang = des_ang
        else:
            self.ang += self.ang_v \
                if abs(abs_ang(des_ang-(self.ang+self.ang_v))) < abs(abs_ang(des_ang-(self.ang-self.ang_v))) \
                else -self.ang_v
        self.vy += round(math.sin(self.ang*math.pi/180)*t)
        self.vx += round(math.cos(self.ang*math.pi/180)*t)
        self.x += self.vx
        self.y += self.vy
        self.vx = int(self.vx * self.vr_rate)
        self.vy = int(self.vy * self.vr_rate)
        self.path_list.append((int(self.x), int(self.y), int(self.ang), int(self.vx), int(self.vy)))
        self.step += 1
        # print('{},{},{} | {},{}'.format(int(self.x), int(self.y), int(self.ang), int(self.vx), int(self.vy)))
        return int(self.x), int(self.y), int(self.ang), int(self.vx), int(self.vy)

    def get_path_list(self):
        return self.path_list


def process(g):
    assert (isinstance(g, G))
    (act_x, act_y) = (None, None)
    if g.me.nc_dist < 3500:
        thrust = int(dist(g.me.nc, g.me.nnc) /10)
        thrust = 100 if thrust > 100 else 30 if thrust < 30 else thrust
        s = Sim(x=g.me.p[0], y=g.me.p[1], ang=g.me.ang, vx=g.me.v[0], vy=g.me.v[1])
        for _ in range(20):
            tx, ty, ta, tvx, tvy = s.update(g.me.nnc[0], g.me.nnc[1], thrust)
            if dist(g.me.nc, (tx, ty)) < g.cp_r - 20:
                (act_x, act_y) = (g.me.nnc[0], g.me.nnc[1])
                break
        if (act_x, act_y) == (None, None):
            thrust = 100
            (act_x, act_y) = (g.me.nc[0], g.me.nc[1])
    else:
        (act_x, act_y) = g.me.nc
        if g.me.nc_dist > 7000 and g.me.v != (0, 0) and False:
            thrust = 'BOOST' if g.me.boost else 100
        else:
            thrust = 100
    debug('({},{},{}|{})({},{}) - ({},{},{})'.format(g.me.p[0], g.me.p[1], g.me.ang, g.me.nc_angle, g.me.v[0], g.me.v[1], act_x, act_y, thrust))
    # debug('({},{}),({},{})'.format(g.me.nc[0], g.me.nc[1], g.me.nnc[0], g.me.nnc[1]))
    debug_msg = '{}-{}'.format(g.me.lap, g.idx_cps(g.me.nc))
    return act_x, act_y, thrust, debug_msg


if __name__ == '__main__':
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
