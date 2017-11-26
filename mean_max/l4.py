import time
import random
import sys
import math
from enum import IntEnum

THROTTLE = 300
RADIUS = 6000
MAP_R = round(RADIUS/150)


def debug(msg):
    print('DEBUG:'+msg, file=sys.stderr)

def map_dump2str(m):
    for y in range(20):
        line = ''
        for x in range(20):
            s = sum([len(m[10*y+a][10*x+b]) for a in range(10) for b in range(10)])
            line += '  ' if s == 0 else '{:02d}'.format(s)
        debug(' > '+line+'|')
    debug(' ------------------- ')


def dist(p1, p2):
    return math.sqrt(((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2))


def speed(v):
    return math.sqrt(v[0]**2+v[1]**2)


def optarget(me, tar):
    return [me[0] * 2 - tar[0], me[1] * 2 - tar[1]]


def direct(s, d):
    return [d[0]-s[0], d[1]-s[1]]


def dvan(s, d, sv):
    if speed(sv) < 2:
        return 3.14
    r = [d[0]-s[0], d[1]-s[1]]
    return math.acos((r[0]*sv[0]+r[1]*sv[1])/math.sqrt(r[0]**2+r[1]**2)/math.sqrt(sv[0]**2+sv[1]**2))


def dis_brake(vs, mass, fr):
    if vs <= 0:
        return 0
    max_a = 300 / mass
    length = 0
    while vs > 0:
        vs = vs - max_a if max_a < vs else 0
        length += vs
        vs *= (1-fr)
    return length


def acc_to_dest(vs, dis, mass, fr, f=0.0, fmin=-300.0, fmax=300.0):
    if dis < 33:
        return -vs * mass
    res = None
    if fmax - fmin < 1:
        return f
    tvs = vs + f/mass
    tdis = dis - tvs
    tvs *= (1-fr)
    if tdis < 0 or tdis < dis_brake(tvs, mass, fr):  # Can NOT brake in time
        res = acc_to_dest(vs, dis, mass, fr, (f+fmin)/2, fmin=fmin, fmax=f)
    else:
        if tdis > dis_brake(tvs, mass, fr):  # f is ok, but maybe not best
            res = f
        if res != None:  # find best result
            t = acc_to_dest(vs, dis, mass, fr, (f+fmax)/2, fmin=f, fmax=fmax)
            if t:
                res = t
        else:  # no result can be use, reduce f then find again
            t = acc_to_dest(vs, dis, mass, fr, (f+fmin)/2, fmin=fmin, fmax=f)
            if res == None:
                res = t
    return res


def ppath(s, d, vs, mass, fr):
    _dist = dist(s, d)
    _m = _dist/(speed(vs)+1)
    if _dist > 2000:
        _m = _m if _m < 2 else 2
    else:
        _m = _m if _m < 0.1 else 0.1

    (tx, ty) = (d[0] - vs[0]*_m, d[1] - vs[1]*_m)
    f = acc_to_dest(speed(vs), _dist, mass, fr)
    if f != None:
        if f < 0:
            (tx, ty) = (s[0]-vs[0], s[1]-vs[1])
            throttle = -f
        else:
            throttle = f
    else:
        throttle = 0

    throttle = throttle if throttle < 300 else 300
    # print('--------- {} {} {}'.format(int(tx), int(ty), int(throttle)))
    return tx, ty, throttle


class UnitType(IntEnum):
    Reaper = 0
    Destroyer = 1
    Doof = 2
    T = 3
    W = 4
    Tar = 5
    O = 6


class Unit:
    def __init__(self, str_line):
        unit_id, unit_type, player, mass, radius, x, y, vx, vy, extra, extra_2 = str_line.split()
        self.unit_id = int(unit_id)
        self.unit_type = int(unit_type)
        self.player = int(player)
        self.mass = float(mass)
        self.radius = int(radius)
        self.x = int(x)
        self.y = int(y)
        self.vx = int(vx)
        self.vy = int(vy)
        self.tx = int(0)
        self.ty = int(0)
        self.extra = int(extra)
        self.extra_2 = int(extra_2)
        self.friction = [0.2, 0.3, 0.25, 0.4, 0, 0, 0][self.unit_type]


class MUnit:
    def __init__(self, time, u):
        self.time = time
        self.ID = u.unit_id
        self.unit_type = u.unit_type
        self.player = u.player
        self.extra = u.extra
        self.extra_2 = u.extra_2


class CMap:
    def __init__(self):
        self.map = [[[] for _ in range(int(MAP_R*2+1))] for _ in range(int(MAP_R*2+1))]

    @staticmethod
    def a2m(point):
        (x, y) = (round(point[0] / MAP_R * RADIUS - RADIUS), round(point[1] / MAP_R * RADIUS - RADIUS))
        x = RADIUS * 2 if x > RADIUS*2-1 else x
        x = 0 if x < 0 else x
        y = RADIUS * 2 if y > RADIUS*2-1 else y
        y = 0 if y < 0 else y
        return [x, y]

    @staticmethod
    def m2a(point):
        (x, y) = (round(point[0] / RADIUS * MAP_R + MAP_R), round(point[1] / RADIUS * MAP_R + MAP_R))
        x = MAP_R * 2 if x > MAP_R*2-1 else x
        x = 0 if x < 0 else x
        y = MAP_R * 2 if y > MAP_R*2-1 else y
        y = 0 if y < 0 else y
        return [x, y]


    def add_item(self, u):
        interval = 0.25
        t = 0
        (x, y) = (u.x, u.y)
        (vx, vy) = (u.vx, u.vy)
        for _ in range(0, int(1.0/interval)):
            x += vx * interval
            y += vy * interval
            t += interval
            for idx in [[1,0],[0,1],[-1,0],[0,-1],[0,0]]:
            # for idx in [[1,0],[1.4,1.4],[0,1],[-1.4,1.4],[-1,0],[-1.4,-1.4],[0,-1],[1.4,-1.4]]:
                (tx, ty) = CMap.m2a((x+idx[0]*u.radius, y+idx[1]*u.radius))
                self.map[ty][tx].append(MUnit(t, u))

    def clean_map(self):
        self.map = [[[] for _ in range(int(MAP_R*2+1))] for _ in range(int(MAP_R*2+1))]


class G(CMap):
    def __init__(self):
        CMap.__init__(self)
        self.scores = None
        self.rages = None
        self.reapers = None
        self.destroyers = None
        self.doofs = None
        self.list_tanker = None
        self.list_player = None
        self.list_wreck = None
        self.TEST = 0

    def round_init(self, scores, rages, unit_list):
        CMap.clean_map(self)
        self.scores = scores
        self.rages = rages
        self.reapers = []
        self.destroyers = []
        self.doofs = []
        self.list_tanker = []
        self.list_player = []
        self.list_wreck = []

        for _ in range(len(unit_list)):
            u = unit_list[_]
            g.add_item(u)
            # if u.player == 0:
            #     debug('ID({}) {} {} ({},{}) ({},{}) {}\n'.format(u.unit_id, u.player, UnitType(u.unit_type),
            #                                                      u.x, u.y, u.vx, u.vy, u.extra))
            if u.unit_type == 0:  # Reaper
                g.reapers.append(u)
                g.reapers.sort(key=lambda x:x.player)
            if u.unit_type == 1:  # Destroyer
                g.destroyers.append(u)
                g.reapers.sort(key=lambda x:x.player)
            if u.unit_type == 2:  # Doof
                g.doofs.append(u)
                g.reapers.sort(key=lambda x:x.player)
            if UnitType(u.unit_type) == UnitType.W:  # W
                g.list_wreck.append(u)
            if UnitType(u.unit_type) == UnitType.T:  # T
                g.list_tanker.append(u)


def v_dirc(v):
    l = speed(v)
    x = v[0] / (l+.1)
    y = v[1] / (l+.1)
    return [round(x), round(y)]


def doof_direc(g):
    target = g.reapers[1] if g.scores[1] > g.scores[2] else g.reapers[2]
    m = g.map
    doof = g.doofs[0]
    _dist = dist([g.reapers[0].x, g.reapers[0].y], [g.doofs[0].x,g.doofs[0].y])
    _ang = (-0.03*_dist+210)*3.14/180 if _dist>1000 else 30*3.14/180 # 30~180 -> 6000~1000
    if  _dist < 2000 and dvan([g.reapers[0].x, g.reapers[0].y], [g.doofs[0].x,g.doofs[0].y],
            direct([g.reapers[0].x, g.reapers[0].y], [g.reapers[0].tx, g.reapers[0].ty])) < _ang:
        _dir = get_outdirect([g.reapers[0].x, g.reapers[0].y], [g.doofs[0].x,g.doofs[0].y],step=1000)
        return "{} {} {} H".format(int(doof.x+_dir[0]), int(doof.y+_dir[1]), int(300))
    elif dist([g.doofs[0].x,g.doofs[0].y], [target.x,target.y]) < 6500:
        tx,ty,th = ppath((g.doofs[0].x, g.doofs[0].y), (target.x, target.y), (g.doofs[0].vx, g.doofs[0].vy),
              g.doofs[0].mass, g.doofs[0].friction)
        return "{} {} {} T:{}".format(int(tx), int(ty), int(th), target.player)
    else:
        dirc_weight = [random.randint(100, 200) for _ in range(8)]
        dirc = [[1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1]]
        ap = CMap.m2a([doof.x, doof.y])
        for i in range(len(dirc)):
            if 0<=ap[1]+15*dirc[i][1]<=MAP_R*2 and 0<=ap[0]+15*dirc[i][0]<=MAP_R*2:
                l = m[ap[1]+15*dirc[i][1]][ap[0]+15*dirc[i][0]]
            else:
                l = m[ap[1]+2*dirc[i][1]][ap[0]+2*dirc[i][0]]
            for m_item in l:  # judge object
                if m_item.unit_type == 0 and m_item.player != 0:  # other player
                    dirc_weight[i] += 1000
                elif m_item.unit_type == 0 and m_item.player == 0:  # my reaper
                    dirc_weight[i] -= 5000
                else:
                    if 0 < m_item.unit_type < 4:  # other object which can be collision
                        dirc_weight[i] -= 200
            if 0<=ap[1]+15*dirc[i][1]<=MAP_R*2 and 0<=ap[0]+15*dirc[i][0]<=MAP_R*2:
                _d = dist(CMap.a2m([ap[0] + 15*dirc[i][0], ap[1] + 15*dirc[i][1]]), (0, 0))
            else:
                _d = dist(CMap.a2m([ap[0] + 2*dirc[i][0], ap[1] + 2*dirc[i][1]]), (0, 0))
            if _d > RADIUS-800:  # judge boundary
                dirc_weight[i] -= 5000
            if dirc[i] == v_dirc([doof.vx, doof.vy]):  # judge v direction
                dirc_weight[i] += 1000
        i = dirc_weight.index(max(dirc_weight))
        return "{} {} {} R".format(int(doof.x+dirc[i][0]), int(doof.y+dirc[i][1]), int(300))


def get_interpolation(s, d, step=600):
    if abs(s[0]-d[0])<step or abs(s[1]-d[1])<step:
        return []
    _n = round(abs(s[0] - d[0]) / step if abs(s[0] - d[0]) > abs(s[1] - d[1]) else abs(s[1] - d[1]) / step)
    xl = (d[0] - s[0]) / _n
    yl = (d[1] - s[1]) / _n
    return list(zip([int(s[0] + xl * _) for _ in range(1, n)], [int(s[1] + yl * _) for _ in range(1, n)]))


def get_outdirect(s, d, step=1200):
    tp = [d[0]-s[0], d[1]-s[0]]
    _l = dist((0,0),tp)
    return [step*tp[0]/(_l+0.01), step*tp[1]/(_l+0.01)]


def tanker_boom(g, u):
    res = 0
    for d in g.destroyers:
        if dist((d.x,d.y), (u.x,u.y)) < d.radius+u.radius+speed((d.vx,d.vy))*1.5 and \
                        dvan((u.x,u.y), (d.x,d.y),(d.vx,d.vy)) < (30/180*3.14):
            return 0.95
        else:
            if dist((d.x,d.y), (u.x,u.y)) < 3500 and u.extra > 0:
                _ = (3500 - dist((d.x,d.y), (u.x,u.y))) / 3500 * 0.1
                if _ > res:
                    res = _
    return res


def get_reaper_target(g):
    _min_dis = pri_dist = 100
    _reaper_target = None
    for w in g.list_wreck:
        pri_dist = dist((g.reapers[0].x, g.reapers[0].y), (w.x, w.y))/100
        pri_dist -= w.extra * 5
        ipoint = get_interpolation((g.reapers[0].x, g.reapers[0].y), (w.x, w.y))
        if len(ipoint)> 2:
            for p in ipoint[1:-2]:
                np = CMap.m2a(p)
                if len(g.map[np[1]][np[0]]) != 0:
                    pri_dist += 5 * 600 / dist(np, (g.reapers[0].x, g.reapers[0].y))
        for tw in g.list_wreck:
            if w.unit_id != tw.unit_id:
                tdist = int(dist((w.x,w.y),(tw.x,tw.y))/400)
                tdist = 5 if tdist > 5 else tdist
                pri_dist -= 5 * [3, 1, 0.5, 0.3, 0.1, 0][tdist]
        if pri_dist < _min_dis:
            _min_dis = pri_dist
            _reaper_target = w
    for t in g.list_tanker:
        for d in g.destroyers:
            _dist = dist((t.x,t.y),(d.x,d.y))
            _ang = (-0.01*_dist+60)*3.14/180 if _dist>1000 else 60*3.14/180 # 10~50 -> 5000~1000
            if _dist < 2000 and dvan((d.x,d.y), (t.x,t.y), (d.vx,d.vy)) < _ang:
                pri_dist = dist((g.reapers[0].x, g.reapers[0].y), (t.x, t.y))/150
                pri_dist -= t.extra * 2
                ipoint = get_interpolation((g.reapers[0].x, g.reapers[0].y), (t.x, t.y))
                if len(ipoint)> 2:
                    for p in ipoint[1:-2]:
                        np = CMap.m2a(p)
                        if len(g.map[np[1]][np[0]]) != 0:
                            pri_dist += 6
                if pri_dist < _min_dis:
                    _min_dis = pri_dist
                    _reaper_target = t
    return _reaper_target, int(pri_dist)


def proc(g, scores, rages, unit_list):
    debug_str = 'score:{},{},{} - '.format(scores[0],scores[1],scores[2])
    g.round_init(scores, rages, unit_list)
    # Reaper
    _reaper_target, debug_num = get_reaper_target(g)
    if _reaper_target:
        debug_str += 'Reaper target:{},{}(id={})'.format(_reaper_target.unit_id, UnitType(_reaper_target.unit_type).name, len(g.list_wreck))
        _reaper_tx = _reaper_target.x
        _reaper_ty = _reaper_target.y
    else:
        debug_str += 'Reaper target:-,-'
        (_reaper_tx, _reaper_ty) = (0, 0)
    (g.reapers[0].tx, g.reapers[0].ty) = (_reaper_tx, _reaper_ty)
    r_destx, r_desty, r_throttle = ppath((g.reapers[0].x, g.reapers[0].y), (g.reapers[0].tx, g.reapers[0].ty),
                                         (g.reapers[0].vx, g.reapers[0].vy), g.reapers[0].mass, g.reapers[0].friction)
    # Destroyer Tanker
    _min_dis_tank = 1e10
    _destroyer_target = None
    _dist = dist([g.reapers[0].x, g.reapers[0].y], [g.destroyers[0].x,g.destroyers[0].y])
    _ang = (-0.03*_dist+210)*3.14/180 if _dist>1000 else 30*3.14/180 # 30~180 -> 6000~1000
    if  _dist < 2200 and dvan([g.reapers[0].x, g.reapers[0].y], [g.destroyers[0].x,g.destroyers[0].y],
                              direct([g.reapers[0].x, g.reapers[0].y], [g.reapers[0].tx, g.reapers[0].ty])) < _ang:
        _dir = get_outdirect([g.reapers[0].x, g.reapers[0].y], [g.destroyers[0].x,g.destroyers[0].y],step=1000)
        de_destx = g.destroyers[0].x+_dir[0]
        de_desty = g.destroyers[0].y+_dir[1]
        de_throttle = 300
        action_destroyer = "{} {} {} H".format(int(de_destx), int(de_desty), int(de_throttle))
    else:
        for ta in g.list_tanker:
            _dist = dist((ta.x, ta.y), (g.reapers[0].x, g.reapers[0].y))
            if _dist < _min_dis_tank and dist((0, 0), (ta.x, ta.y)) < 5000:
                _min_dis_tank = _dist
                _destroyer_target = ta
        if _destroyer_target:
            de_destx, de_desty, de_throttle = ppath((g.destroyers[0].x, g.destroyers[0].y),
                                                    (_destroyer_target.x, _destroyer_target.y),
                                                    (g.destroyers[0].vx, g.destroyers[0].vy),
                                                    g.destroyers[0].mass, g.destroyers[0].friction)
        else:
            (de_destx, de_desty, de_throttle) = (0, 0, 50)
        action_destroyer = "{} {} {} T:{}".format(int(de_destx), int(de_desty), int(de_throttle),
                                                  _destroyer_target.unit_id if _destroyer_target else None)
    # Destroyer Skill
    target = g.reapers[1] if g.scores[1] > g.scores[2] else g.reapers[2]
    if g.rages[0] > 60:
        for w in g.list_wreck:
            if dvan((target.x,target.y), (w.x,w.y), (target.vx, target.vy)) < 3.14/4:  # right direction
                for di in range(700, 2000, 100):
                    (bx, by) = [target.x + target.vx/(abs(target.vx)+0.1)*di,
                                target.y + target.vy/(abs(target.vy)+0.1)*di]
                    if dist([bx, by], [g.reapers[0].x, g.reapers[0].y]) > 3000 and \
                            1500 > dist((bx, by), (g.destroyers[0].x, g.destroyers[0].y)):
                        action_destroyer = "SKILL {} {} D={}({},{})".format(int(bx), int(by),
                                        int(dist((bx, by), (g.destroyers[0].x, g.destroyers[0].y))), int(bx/100), int(by/100))
                        break
            if dist((target.x,target.y), (w.x,w.y)) < w.radius + 100:
                for p in [(random.randint(-1000, 1000), random.randint(-1000, 1000)) for _ in range(10)]:
                    if dist([p[0], p[1]], [g.reapers[0].x, g.reapers[0].y]) > 3000 and \
                            1500 > dist((p[0], p[1]), (g.destroyers[0].x, g.destroyers[0].y)):
                        action_destroyer = "SKILL {} {} D={}({},{})".format(int(p[0]), int(p[1]),
                                        int(dist((p[0], p[1]), (g.destroyers[0].x, g.destroyers[0].y))), int(p[0]), int(p[1]))
                        break
    if g.rages[0] > 250 and not "SKILL" in action_destroyer:
        v = speed([target.vx, target.vy])
        for di in range(100, 2000, 200):
            (bx, by) = [target.x + target.vx/(abs(target.vx)+0.1)*di,target.y + target.vy/(abs(target.vy)+0.1)*di]
            if dist((bx, by), [g.reapers[0].x, g.reapers[0].y]) > 2000 > \
                    dist((bx, by), (g.destroyers[0].x, g.destroyers[0].y)):
                action_destroyer = "SKILL {} {} D={}({},{})".format(int(bx), int(by),
                                    int(dist((bx, by), (g.destroyers[0].x, g.destroyers[0].y))), int(bx), int(by))
                break
    # Doof
    action_doof = doof_direc(g)

    # map_dump2str(g.map)
    print("{} {} {} {}|{}|{},{}".format(int(r_destx), int(r_desty), int(r_throttle),
                               UnitType(_reaper_target.unit_type).name if _reaper_target else 'N',
                                       _reaper_target.unit_id if _reaper_target else 'N',
                                        int(r_destx/100), int(r_desty/100)))
    print(action_destroyer)
    print(action_doof)
    return debug_str
# game loop
g = G()
tout = 0
while True:
    _scores = []
    for _ in range(3):
        _scores.append(int(input()))
    _rages = []
    for __ in range(3):
        _rages.append(int(input()))
    _unit_list = []
    st = int(round(time.time() * 1000))
    n = int(input())
    for i in range(n):
        _unit_list.append(Unit(input()))
    debug_str = proc(g, _scores, _rages, _unit_list)
    en = int(round(time.time() * 1000))
    if en -st >= 50:
        tout += 1
    if len(debug_str) > 0:
        debug(debug_str)
    debug('delay:{}ms, timeout count: {}'.format(en - st, tout))
