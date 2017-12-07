# https://www.codingame.com/ide/puzzle/coders-strike-back
import sys
import math
import time
import random


class C:
    # pod ID
    ALL_POD_NUM = 4
    MY_POD_NUM = 2
    M1 = 0
    M2 = 1
    O1 = 2
    O2 = 3
    # pod action
    POD_TARGET_X = 0
    POD_TARGET_Y = 1
    POD_THRUST = 2
    # Env param
    H = 9000
    W = 16000
    BASE_X = 0
    BASE_Y = -H
    MAX_THRUST = 200
    BOOST = 650
    R_CHECK_POINT = 600
    R_POD = 400
    V_ANG = math.pi/10  # Angular velocity
    VR_RATE = 0.85  # velocity reduce rate
    SHIELD_DELAY = 3
    # pod mode
    MODE_NORMAL = 0
    MODE_BLOCKING = 1
    MODE_END = 2
    # const math param
    RATE_MTV = 1 / 0.85 - 1


class M:  # math function
    @staticmethod
    def dist(p1, p2):
        return math.sqrt(((p1[0] - p2[0]) ** 2) + ((p1[1] - p2[1]) ** 2))

    @staticmethod
    def dist_low(p1, p2):
        _x = abs(p2[0] - p1[0])
        _y = abs(p2[1] - p1[1])
        _d = min(_x, _y)
        r = _d * 1.41421356
        r += (_x - _d) + (_y - _d)
        return r

    @staticmethod
    def speed(v):
        return math.sqrt(v[0] ** 2 + v[1] ** 2)

    @staticmethod
    def vec(p1, p2):
        return [p2[0]-p1[0], p2[1]-p1[1]]

    @staticmethod
    def regular_ang(ang):
        ang = math.fmod(ang, (math.pi+math.pi))
        return ang - (math.pi+math.pi) if ang > math.pi else ang + (math.pi+math.pi) if ang < -math.pi else ang

    @staticmethod
    def op_point(pt_s, pt_ref):
        return [pt_ref[0] * 2 - pt_s[0], pt_ref[1] * 2 - pt_s[1]]

    @staticmethod
    def op_ang_vv(vec_s, vec_ref):
        return M.regular_ang(math.atan2(vec_ref[1], vec_ref[0]) * 2 - math.atan2(vec_s[1], vec_s[0]))

    @staticmethod
    def op_ang_av(ang_s, vec_ref):
        _ang = math.atan2(vec_ref[1], vec_ref[0])
        return M.regular_ang(_ang * 2 - ang_s)

    @staticmethod
    def points2vec(pt_s, pt_d):
        return [pt_d[0] - pt_s[0], pt_d[1] - pt_s[1]]

    @staticmethod
    def ang_v2v(vec_s, vec_d):
        return M.regular_ang(math.atan2(vec_d[1], vec_d[0]) - math.atan2(vec_s[1], vec_s[0]))

    @staticmethod
    def ang_p2v(pt_s, pt_d, vec):
        return M.regular_ang(M.ang_v2v(M.points2vec(pt_s, pt_d), vec))

    @staticmethod
    def ang_v2p(vec, pt_s, pt_d):
        return M.regular_ang(M.ang_v2v(vec, M.points2vec(pt_s, pt_d)))

    @staticmethod
    def ang_a2p(ang, pt_s, pt_d):
        return M.regular_ang(math.atan2(pt_d[1] - pt_s[1], pt_d[0] - pt_s[0]) - ang)

    @staticmethod
    def ang_turn(s, d1, d2):
        return M.regular_ang(M.ang_v2v(M.points2vec(s, d1), M.points2vec(d1, d2)))

    @staticmethod
    def point_v_a(vec, ang):
        _ang = math.atan2(vec[1], vec[0])+ang
        return [C.R_POD*math.cos(_ang), C.R_POD*math.sin(_ang)]

    @staticmethod
    def point_lp_a(pt_l, pt_d, ang):
        _ang = M.regular_ang(math.atan2(pt_d[1] - pt_l[1], pt_d[0] - pt_l[0]) + ang)
        return [pt_l[0]+C.R_POD*math.cos(_ang), pt_l[1]+C.R_POD*math.sin(_ang)]

    @staticmethod
    def point_lpa(pt_l, ang):
        return [pt_l[0] + C.R_POD * math.cos(ang), pt_l[1] + C.R_POD * math.sin(ang)]

    @staticmethod
    def point_la_a(pt_l, local_ang, ang):
        _ang = M.regular_ang(local_ang + ang)
        return [pt_l[0]+C.R_POD*math.cos(_ang), pt_l[1]+C.R_POD*math.sin(_ang)]

    @staticmethod
    def vmap_sd_v(s, d, v):
        _ang = M.ang_p2v(s, d, v)
        return math.cos(_ang) * v


class U:  # utils
    @staticmethod
    def debug(msg):
        print('DEBUG:'+msg, file=sys.stderr)

    @staticmethod
    def op_lead():
        return G.pods[C.O1] if G.pods[C.O1].lap*C.W - M.dist(G.pods[C.O1].p, G.cps[G.pods[C.O1].nc_id]) > \
                             G.pods[C.O2].lap*C.W - M.dist(G.pods[C.O2].p, G.cps[G.pods[C.O2].nc_id]) else G.pods[C.O2]

    @staticmethod
    def glide_dist(v0, v_last=0):
        length = 0
        while v0 > v_last:
            length += v0
            v0 = v0 * 17 / 20
        return length

    @staticmethod
    def coll_point(p_out, p_in, o):  # dist(p_out, o)>2*r & dist(p_in, o)<r
        _mid = ((p_out[0]+p_in[0])/2, (p_out[1]+p_in[1])/2)
        tmp_dist = M.dist(_mid, o)
        if abs(tmp_dist - G.pod_r*2) < 5:
            return [round(_mid[0]), round(_mid[1])]
        elif abs(p_out[0] - p_in[0]) + abs(p_out[0] - p_in[0]) < 1:
            return None
        if tmp_dist - G.pod_r*2 < 0:
            return G.coll_point(_mid, p_in, o)
        else:
            return G.coll_point(p_out, _mid, o)

    class Time:
        def __init__(self):
            self.count = time.time()

        def get_s(self):
            return time.time() - self.count

class P:  # pod define
    def __init__(self, g, _id):
        assert(isinstance(g, G))
        self.id = _id
        self.g = g
        self.boost = True
        self.shield = 0
        self.lap = 0
        self.p = (0, 0)
        self.v = (0, 0)
        self.ang = 0
        self.nc_id = 0
        self.onc_id = 0
        self.mode = C.MODE_NORMAL
        self.act = None
        self.debug_msg = None

    def update(self, x, y, vx=0, vy=0, ang=0, nc_id=0):
        self.p = (x, y)
        self.v = (vx, vy)
        self.ang = ang
        self.nc_id = nc_id
        # lap
        self.shield = self.shield - 1 if self.shield > 0 else 0
        if self.onc_id != self.nc_id:
            self.onc_id = self.nc_id
            if self.nc_id == 0:
                self.lap += 1

    def lap_count(self):
        return self.lap * G.cps_num + self.nc_id


class G:  # match define
    round = 0
    pods = []
    cps = []
    lap_num = 0
    cps_num = 0

    def __init__(self):
        for _id in range(C.ALL_POD_NUM):
            G.pods.append(P(self, _id))
        G.lap_num = int(input())
        G.cps_num = int(input())
        for _ in range(G.cps_num):
            (_x, _y) = list(map(int, input().split()))
            G.cps.append((_x, G.m2m(_y)))
        U.debug('Laps:{}'.format(G.lap_num))
        U.debug('CheckPoint:{}'.format(G.cps))

    @staticmethod
    def update_pods(pod_id, str_pod):
        x, y, vx, vy, ang, nc_id = list(map(int, str_pod.split()))
        G.pods[pod_id].update(x, G.m2m(y), vx,  G.m2m(vy), math.radians(G.m2m(
            ang - 360 if ang > 180 else ang + 360 if ang < -180 else ang)), nc_id)

    @staticmethod
    def action(pods):
        assert(len(pods) == C.MY_POD_NUM and isinstance(pods[C.M1], P) and isinstance(pods[C.M2], P))
        G.round += 1
        _act = [G.target_regular(pods[i], enabled=False) for i in range(C.MY_POD_NUM)]
        for i in range(C.MY_POD_NUM):
            _thrust = int(_act[i][C.POD_THRUST]) if isinstance(_act[i][C.POD_THRUST], int) else _act[i][C.POD_THRUST]
            if isinstance(_thrust, str):
                if _thrust == 'BOOST':
                    G.pods[idx].boost = False
                elif _thrust == 'SHIELD':
                    G.pods[idx].shield = SHIELD_DELAY

            if isinstance(pods[i].debug_msg, str) and len(pods[i].debug_msg) > 0:
                print('{} {} {} {}'.format(
                    int(_act[i][C.POD_TARGET_X]), int(_act[i][C.POD_TARGET_Y]), _thrust, pods[i].debug_msg))
            else:
                print('{} {} {}'.format(int(_act[i][C.POD_TARGET_X]), int(_act[i][C.POD_TARGET_Y]), _thrust))

    @staticmethod
    def target_regular(pod, enabled=True):
        assert(isinstance(pod, P))
        action = pod.act
        local_p = pod.p
        _d = M.dist((action[0], action[1]), local_p)
        if _d > C.R_POD and enabled:
            _r = C.R_POD / _d
            _act0 = local_p[0] + (action[0] - local_p[0]) * _r
            _act1 = local_p[1] + (action[1] - local_p[1]) * _r
        else:
            _act0 = action[0]
            _act1 = action[1]
        return int(_act0), int(G.m2m(_act1)), action[2]

    @staticmethod
    def m2m(y):
        return -y


class Sim:
    ang_v = C.V_ANG  # Angular velocity
    vr_rate = C.VR_RATE  # velocity reduce rate
    cp_r = C.R_CHECK_POINT
    max_thrust = C.MAX_THRUST

    def __init__(self, x=(None,), y=(None,), vx=0, vy=0, ang=(None,), target=None, step=0):
        self.x = target[-1][0] if x == (None,) else x
        self.y = target[-1][1] if y == (None,) else y
        self.ang = ang
        self.vx = vx
        self.vy = vy
        self.step = step
        self.path_list = []

    def update(self, x, y, t, np=(0, 0), nnp=(0, 0)):
        # Rotation: the pod rotates to face the target point, with a maximum of 18 degrees (except for the 1rst round).
        if self.ang == (None,):
            self.ang = math.atan2(y-self.y, x-self.x)
        else:
            des_ang = math.atan2(y-self.y, x-self.x)
            if abs(M.regular_ang(des_ang - self.ang)) <= Sim.ang_v:
                self.ang = des_ang
            else:
                if abs(M.regular_ang(des_ang - (self.ang + Sim.ang_v))) < abs(
                        M.regular_ang(des_ang - (self.ang - Sim.ang_v))):
                    self.ang += Sim.ang_v
                else:
                    self.ang -= Sim.ang_v
        # Acceleration: the pod's facing vector is multiplied by the given thrust value.
        # The result is added to the current speed vector.
        self.vx += math.cos(self.ang)*t
        self.vy += math.sin(self.ang)*t
        # Movement: The speed vector is added to the position of the pod.
        # The position's values are rounded to the nearest integer.
        self.x = round(self.x + self.vx)
        self.y = round(self.y + self.vy)
        # Friction: the current speed vector of each pod is multiplied by 0.85
        # The speed's values are truncated.
        self.vx = int(self.vx * Sim.vr_rate)
        self.vy = int(self.vy * Sim.vr_rate)
        self.path_list.append((int(self.x), int(self.y), int(self.vx), int(self.vy), self.ang, np, nnp))
        self.step += 1
        self.ang = math.radians(int(math.degrees(self.ang)))
        # print('{}  ({},{}),({},{}),{}'.format(self.step, self.x, self.y, self.vx, self.vy, self.ang))
        return int(self.x), int(self.y), int(self.vx), int(self.vy), self.ang

    def get_path_list(self):
        return self.path_list


def process(g):
    assert(isinstance(g, G))
    for i in range(C.MY_POD_NUM):
        g.pods[i].act = None
        g.pods[i].debug_msg = None
        g.pods[i].act = [C.BASE_X+C.W/2, C.BASE_Y+C.H/2, C.MAX_THRUST]
        g.pods[i].debug_msg = 'POD-{}'.format(i)
    return [g.pods[C.M1], g.pods[C.M2]]


if __name__ == '__main__':
    # game loop
    _g = G()
    flag = True
    while True:
        for _ in range(C.ALL_POD_NUM):
            _g.update_pods(_, input())
        _time = U.Time()
        _g.action(process(_g))
        _t = _time.get_s()
        U.debug('delay:{}s'.format(_t))
