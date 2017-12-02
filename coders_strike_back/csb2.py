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


def op_ang(tdirect, ref_direct):
    return (math.atan2(ref_direct[1], ref_direct[1]) * 2 - math.atan2(tdirect[1], tdirect[1])*2)*180/math.pi


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


def turn_an(s, d1, d2):
    _res = (math.atan2((d2[1] - d1[1]), (d2[0] - d1[0]))-math.atan2((d1[1] - s[1]), (d1[0] - s[0]))) * 180 / math.pi
    return abs_ang(_res)


def vvan(v1, v2):
    _res = (math.atan2(v1[1], v1[0])-math.atan2(v2[1], v2[0])) * 180 / math.pi
    return abs_ang(_res)


def adan(ang, s, d):
    _res = (ang*math.pi/180 - math.atan2(d[1]-s[1], d[0]-s[0])) * 180 / math.pi
    return abs_ang(_res)


def abs_ang(a):
    return a - 360 if a > 180 else a + 360 if a < -180 else a


def d_ang_abs(s, d, re_ang):
    _res = int(math.atan2((d[1] - s[1]), (d[0] - s[0])) * 180 / math.pi)
    return abs_ang(_res - re_ang)


M1 = 0
M2 = 1
O1 = 2
O2 = 3
MODE_NORMAL = 0
MODE_ASSIST = 1
MODE_END = 2


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
        self.mode = MODE_NORMAL
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

    def dest_real_ang(self, d, ang):
        _l = G.pod_r
        _ang = math.atan2(d[1]-self.p[1], d[0]-self.p[0])
        _ang += ang * math.pi / 180
        (_x, _y) = (self.p[0]+_l*math.cos(_ang), self.p[1]+_l*math.sin(_ang))
        return _x, _y


class G:
    H = 9000
    W = 16000
    BOOST = 650
    cp_r = 600
    pod_r = 400
    ang_v = 18  # Angular velocity
    vr_rate = 0.85  # velocity reduce rate

    def __init__(self):
        self.round = 0
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
        self.round += 1
        x1, y1, t1 = G.target_regular(act_1, self.pods[M1].p)
        x2, y2, t2 = G.target_regular(act_2, self.pods[M2].p)
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

    def op_lead(self):
        return self.pods[O1] if self.pods[O1].lap*self.cps_num+self.pods[O1].nc_id > \
                                self.pods[O2].lap*self.cps_num+self.pods[O2].nc_id else self.pods[O2]

    @staticmethod
    def target_regular(action, local_p):
        _d = dist((action[0], action[1]), local_p)
        if _d > 400:
            _r = 400 / _d
            _act0 = local_p[0] + (action[0] - local_p[0]) * _r
            _act1 = local_p[1] + (action[1] - local_p[1]) * _r
        else:
            _act0 = action[0]
            _act1 = action[1]
        return int(_act0), int(G.m2m(_act1)), int(action[2]) if isinstance(action[2], int) else action[2]

    @staticmethod
    def coll_point(p_out, p_in, o):  # dist(p_out, o)>2*r & dist(p_in, o)<r
        _mid = ((p_out[0]+p_in[0])/2, (p_out[1]+p_in[1])/2)
        tmp_dist = dist(_mid, o)
        if abs(tmp_dist - G.pod_r*2) < 5:
            return [round(_mid[0]), round(_mid[1])]
        elif abs(p_out[0] - p_in[0]) + abs(p_out[0] - p_in[0]) < 1:
            return None
        if tmp_dist - G.pod_r*2 < 0:
            return G.coll_point(_mid, p_in, o)
        else:
            return G.coll_point(p_out, _mid, o)

    def is_coll(self, me, op):
        _s_me = Sim(x=me.p[0], y=me.p[1], ang=me.ang, vx=me.v[0], vy=me.v[1])
        thrust = G.BOOST if me.act[2] == 'BOOST' else 0 if me.shield > 0 or me.act[2] == 'SHIELD' else me.act[2]
        (mx, my, mang, mvx, mvy) = _s_me.update(me.act[0], me.act[1], thrust)
        _s_op = Sim(x=op.p[0], y=op.p[1], ang=op.ang, vx=op.v[0], vy=op.v[1])
        (opx, opy, opang, opvx, opvy) = _s_op.update(self.cps[op.nc_id][0], self.cps[op.nc_id][1], 100)
        if dist((mx, my), (opx, opy)) <= G.pod_r * 2:
            return abs(speed((mvx, mvy))*math.cos(dvan(me.p, op.p, (mvx, mvy))) +
                       speed((opvx, opvy))*math.cos(dvan(op.p, me.p, (opvx, opvy))))
        else:
            return -1

    @staticmethod
    def m2m(y):
        return -y


class Sim:
    ang_v = 18  # Angular velocity
    vr_rate = 0.85  # velocity reduce rate
    cp_r = 600

    def __init__(self, target=None, x=(None,), y=(None,), ang=(None,), vx=0, vy=0):
        self.x = target[-1][0] if x == (None,) else x
        self.y = target[-1][1] if y == (None,) else y
        self.ang = d_ang_abs(target[-1], target[0], 0) if ang == (None,) else ang
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


def proc_end(g, me):
    assert (isinstance(g, G))
    assert(isinstance(me, Unit))
    assert(me.mode == MODE_END)
    nc_p = g.cps[me.nc_id]
    _re_ang = adan(me.ang, me.p, nc_p)
    if abs(_re_ang) < 30:
        me.act = (nc_p[0],  nc_p[1], 'BOOST' if me.boost else 100)
    elif abs(_re_ang) < 90:
        _x, _y = me.dest_real_ang(nc_p, -_re_ang)
        me.act = (_x, _y, 100)
    else:
        me.act = (nc_p[0],  nc_p[1], 0)
    (_shield_re_v1, _shield_re_v2) = (g.is_coll(me, g.pods[O1]), g.is_coll(me, g.pods[O2]))
    if _shield_re_v1 > 500 or _shield_re_v2 > 500:
        me.act = (me.act[0],  me.act[1], 'SHIELD')


def proc_normal(g, me):
    assert (isinstance(g, G))
    assert(isinstance(me, Unit))
    assert(me.mode == MODE_NORMAL)
    nc_p = g.cps[me.nc_id]
    nnc_p = g.cps[(me.nc_id+1) % g.cps_num]
    _dist_tar = dist(me.p, nc_p)
    act_target = (None, None)
    thrust = 100
    if _dist_tar < 5000:
        for thrust in range(100, 90, -1):
            s = Sim(x=me.p[0], y=me.p[1], ang=me.ang, vx=me.v[0], vy=me.v[1])
            for _ in range(20):
                tx, ty, ta, tvx, tvy = s.update(nnc_p[0], nnc_p[1], thrust)
                if dist(nc_p, (tx, ty)) < G.cp_r - 3:
                    act_target = nnc_p
                    break
            if act_target != (None, None):
                break
    if act_target == (None, None):
        if _dist_tar > 3000:
            _ang = turn_an(me.p, nc_p, nnc_p)
            me.debug_msg = 'R'+str(int(_ang)) if _ang < 0 else 'L' + str(int(_ang))
            _ang = - _ang / 9
            _dist = dist(me.p, nc_p)
            _atar = d_ang_abs(me.p, nc_p, 0)
            _ares = abs_ang(_atar + _ang) * math.pi / 180
            act_target = (me.p[0] + _dist*math.cos(_ares), me.p[1] + _dist*math.sin(_ares))
        else:
            act_target = nc_p
        if dvan(me.p, act_target, me.v) > 120:
            thrust = 70
    if dist(act_target, me.p) > 5000 and dvan(me.p, act_target, me.v) < 30:
        thrust = 'BOOST' if me.boost else 100
    me.act = (act_target[0], act_target[1], thrust)
    (_shield_re_v1, _shield_re_v2) = (g.is_coll(me, g.pods[O1]), g.is_coll(me, g.pods[O2]))
    if _shield_re_v1 > 300 or _shield_re_v2 > 300:
        me.act = (me.act[0],  me.act[1], 'SHIELD')
        debug('SHIELD')
        me.debug_msg = 'SHIELD - {} {}'.\
            format(me.shield, int(_shield_re_v1) if _shield_re_v1 > 200 else int(_shield_re_v2))
    if me.shield > 0 and 'SHIELD' not in me.debug_msg:
        me.debug_msg = 'SHIELD - {}'.format(me.shield)


def process(g):
    assert (isinstance(g, G))
    for i in range(2):
        me = g.pods[i]
        if me.lap == g.lap_num and me.nc_id == 0:  # last check point
            me.mode = MODE_END
            proc_end(g, me)
        else:
            me.mode = MODE_NORMAL
            proc_normal(g, me)
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
