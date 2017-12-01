# https://www.codingame.com/ide/puzzle/coders-strike-back
import sys
import math
import time


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


M1 = 0
M2 = 1
O1 = 2
O2 = 3


class Unit:
    def __init__(self, g):
        assert(isinstance(g, G))
        self.g = g
        self.boost = True
        self.shield = 0
        self.lap = 0
        self.p = (0, 0)
        self.v = (0, 0)
        self.ang = 0
        self.nc_id = 0
        self.onp = (None, None)
        self.act = None
        self.debug_msg = None

    def update(self, x, y, vx=0, vy=0, ang=0, nc_id=0):
        self.p = (x, y)
        self.v = (vx, vy)
        self.ang = ang
        self.nc_id = nc_id

        self.shield = self.shield - 1 if self.shield > 0 else 0
        check_points = self.g.cps
        if self.onp != check_points[nc_id]:
            self.onp = check_points[nc_id]
            if self.nc_id == 0:
                self.lap += 1


class G:
    H = 9000
    W = 16000
    BOOST = 650
    cp_r = 600
    pod_r = 400
    ang_v = 18  # Angular velocity
    vr_rate = 0.85  # velocity reduce rate

    def __init__(self):
        self.pods = []
        for _ in range(4):
            self.pods.append(Unit(self))
        self.cps = []
        self.lap_num = int(input())
        self.cps_num = int(input())
        for _ in range(self.cps_num):
            (_x, _y) = list(map(int, input().split()))
            self.cps.append((_x, G.m2m(_y)))
        debug('Laps:{}'.format(self.lap_num))
        debug('CheckPoint:{}'.format(self.cps))

    def update_pods(self, pod_idx, str_me):
        x, y, vx, vy, ang, nc_id = list(map(int, str_me.split()))
        self.pods[pod_idx].update(x, G.m2m(y), vx,  G.m2m(vy), G.m2m(ang), nc_id)

    def action(self, act_1, act_2, debug1_msg=None, debug2_msg=None):
        x1, y1, t1 = (int(act_1[0]), int(G.m2m(act_1[1])), int(act_1[2]) if isinstance(act_1[2], int) else act_1[2])
        x2, y2, t2 = (int(act_2[0]), int(G.m2m(act_2[1])), int(act_2[2]) if isinstance(act_2[2], int) else act_2[2])
        for act, idx in zip([act_1, act_2], [0, 1]):
            if isinstance(act[2], str) and act[2] == 'BOOST':
                self.pods[idx].boost = False
            elif isinstance(act[2], str) and act[2] == 'SHIELD':
                self.pods[idx].shield = 3
        if isinstance(debug1_msg, str) and len(debug1_msg) > 0:
            print('{} {} {} {}'.format(x1, y1, t1, debug1_msg))
        else:
            print('{} {} {}'.format(x1, y1, t1))
        if isinstance(debug2_msg, str) and len(debug2_msg) > 0:
            print('{} {} {} {}'.format(x2, y2, t2, debug2_msg))
        else:
            print('{} {} {}'.format(x2, y2, t2))

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

    for pid in range(2):
        me = g.pods[pid]
        nc_p = g.cps[me.nc_id]
        nnc_p = g.cps[(me.nc_id+1)%g.cps_num]
        act_target = (None, None)
        if dist(me.p, nc_p) < 4000:
            thrust = int(dist(nc_p, nnc_p) / 10)
            thrust = 100 if thrust > 100 else 30 if thrust < 30 else thrust
            s = Sim(x=me.p[0], y=me.p[1], ang=me.ang, vx=me.v[0], vy=me.v[1])
            for _ in range(20):
                tx, ty, ta, tvx, tvy = s.update(nnc_p[0], nnc_p[1], thrust)
                if dist(nc_p, (tx, ty)) < G.cp_r - 20:
                    act_target = nnc_p
                    break
            if act_target == (None, None):  # ##
                thrust = 100
                act_target = nc_p
        else:
            act_target = nc_p
            if dist(nc_p, me.p) > 5000 and dvan(me.p, nc_p, me.v) < 30:
                thrust = 'BOOST' if me.boost else 100
            else:
                thrust = 100
        me.act = (act_target[0], act_target[1], thrust)
        me.debug_msg = '{}-{}'.format(me.lap, me.nc_id)
    return g.pods[M1].act, g.pods[M1].debug_msg, g.pods[M2].act, g.pods[M2].debug_msg


if __name__ == '__main__':
    # game loop
    _g = G()
    while True:
        for _ in range(4):
            _g.update_pods(_, input())
        _st = int(round(time.time() * 1000))
        _act_1, _msg1, _act_2, _msg2 = process(_g)
        _g.action(_act_1, _act_2, _msg1, _msg2)
        _en = int(round(time.time() * 1000))
        debug('delay:{}ms'.format(_en - _st))
