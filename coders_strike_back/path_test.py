import turtle
import math
from csb2 import *


class Draw:
    def __init__(self):
        turtle.screensize(16000, 16000)
        turtle.setworldcoordinates(0, 0, 20000, 16000)
        turtle.begin_fill()
        turtle.bgcolor('#2b2b2b')
        self.start_point = None
        self.start_ang = None
        self.points = []

    def reset_pos(self):
        turtle.speed(0)
        turtle.up()
        turtle.setposition(self.start_point)
        turtle.down()
        turtle.seth(self.start_ang)

    def init_cp(self, cp_list):
        turtle.ht()
        self.start_point = cp_list[-1]
        self.start_ang = math.atan2(cp_list[0][1]-cp_list[-1][1], cp_list[0][0]-cp_list[-1][0])*180/math.pi
        turtle.speed(0)
        for l in cp_list:
            turtle.up()
            turtle.setposition(l[0], l[1] - 600)
            turtle.seth(0)
            turtle.down()
            turtle.circle(600)
        turtle.up()
        turtle.setposition(self.start_point)
        turtle.seth(self.start_ang)
        turtle.st()

    def add_point(self, point, v=1800, ang=0):
        turtle.down()
        turtle.speed([0, 1, 2, 3, 4, 5, 6, 7, 8, 9][int(v/200)+1])
        turtle.seth(ang)
        turtle.setposition(point)
        self.points.append(point)

    @staticmethod
    def perform(path_lists, step_for_all=True):
        max_len = max([len(_) for _ in path_lists])
        turtle.hideturtle()
        turtle.speed(0)
        for step in range(max_len-1):
            for i in range(len(path_lists)):
                turtle.color(["#003300", "#330033"][i])
                try:
                    turtle.up()
                    turtle.setposition(path_lists[i][step][0], path_lists[i][step][1])
                    turtle.down()
                    turtle.setposition(path_lists[i][step+1][0], path_lists[i][step+1][1])
                except:
                    if not step_for_all:
                        return

    def __del__(self):
        time.sleep(1)
        turtle.end_fill()


def test1(target):
    s = Sim(target)
    (x, y, a, vx, vy) = (target[-1][0], target[-1][1], 0, 0, 0)
    cp_num = len(target)
    for i in range(cp_num):
        while True:
            if dist((x, y), target[i]) > 2500:
                thrust = 100
                tp = (target[i][0], target[i][1])
            else:
                thrust = 20
                if i == cp_num - 1:
                    tp = (target[i][0], target[i][1])
                else:
                    tp = (target[i+1][0], target[i+1][1])
            x, y, a, vx, vy = s.update(tp[0], tp[1], thrust, np=(target[i][0], target[i][1]),
                                       nnp=(target[(i+1) % len(target)][0], target[(i+1) % len(target)][1]))
            if dist((x, y), target[i]) < Sim.cp_r or s.step > 1000:
                break

    print('------------------------- {}'.format(s.step))
    return s.get_path_list()


def test2(target):
    s = Sim(target)
    (x, y, a, vx, vy) = (target[-1][0], target[-1][1], 0, 0, 0)
    cp_num = len(target)
    for i in range(cp_num):
        while True:
            if dist((x, y), target[i]) > 2500:
                thrust = 100
                tp = (target[i][0], target[i][1])
            else:
                thrust = 40
                if i == cp_num - 1:
                    tp = (target[i][0], target[i][1])
                else:
                    tp = (target[i+1][0], target[i+1][1])
            x, y, a, vx, vy = s.update(tp[0], tp[1], thrust)
            if dist((x, y), target[i]) < Sim.cp_r or s.step > 1000:
                break

    print('------------------------- {}'.format(s.step))
    return s.get_path_list()


def test2_5(target):
    ss = Sim(target)
    (x, y, a, vx, vy) = (target[-1][0], target[-1][1], 0, 0, 0)
    cp_num = len(target)
    for i in range(cp_num):
        while True:
            nc_p = (target[i][0], target[i][1])
            nnc_p = (target[(i+1) % len(target)][0], target[(i+1) % len(target)][1])
            _dist_tar = dist((x, y), nc_p)
            act_target = (None, None)
            thrust = 100

            if _dist_tar < 5000:
                for thrust in range(100, 90, -1):
                    s = Sim(x=x, y=y, ang=a, vx=vx, vy=vy)
                    for _ in range(20):
                        tx, ty, ta, tvx, tvy = s.update(nnc_p[0], nnc_p[1], thrust)
                        if dist(nc_p, (tx, ty)) < G.cp_r - 3:
                            act_target = nnc_p
                            break
                    if act_target != (None, None):
                        break
            if act_target == (None, None):
                if _dist_tar > 3000:
                    _ang = turn_an((x, y), nc_p, nnc_p)
                    _ang = - _ang / 9
                    _dist = dist((x, y), nc_p)
                    _atar = d_ang_abs((x, y), nc_p, 0)
                    _ares = math.radians(abs_ang(_atar + _ang))
                    act_target = (x + _dist * math.cos(_ares), y + _dist * math.sin(_ares))
                else:
                    act_target = nc_p
                if dvan((x, y), act_target, (vx, vy)) > 120:
                    thrust = 70
            x, y, a, vx, vy = ss.update(act_target[0], act_target[1], thrust, np=nc_p, nnp=nnc_p)
            if dist((x, y), target[i]) < Sim.cp_r or ss.step > 1000:
                break

    print('------------------------- {}'.format(ss.step))
    return ss.get_path_list()


def blocking_op(me, op):
    np = op[5]
    nnp = op[6]
    ov = (op[2], op[3])
    oa = op[4]
    op = (op[0], op[1])
    mp = (me[0], me[1])
    mv = (me[2], me[3])
    ma = me[4]

    if dvan(op, np, ov) < 40:
        _s = speed(ov)
        _s = _s if _s > 100 else 100
        _d_mo = dist(mp, op)
        if _d_mo > 3000 or dvan(mp, op, ov) > 50:
            (_x, _y) = ((op[0] + ov[0]*_d_mo/300), (op[1] + ov[1]*_d_mo/300))
        else:
            (_x, _y) = ((op[0] + ov[0]*_d_mo/600), (op[1] + ov[1]*_d_mo/600))
    else:
        (_x, _y) = (np[0], np[1])
    return _x, _y, 100


def test3(target, op_path):
    s_me = Sim(x=0, y=0, ang=0)
    (x, y, a, vx, vy) = (0, 0, 0, 0, 0)
    while True:
        op = op_path[s_me.step]
        _x, _y, _t = blocking_op((x, y, a, vx, vy), op)
        x, y, a, vx, vy = s_me.update(_x, _y, _t)
        if s_me.step >= len(op_path):
            break
        if dist((x, y), (op[0], op[1])) < Sim.cp_r or s_me.step > 1000 or s_me.step >= len(op_path):
            pass
    return s_me.get_path_list()


if __name__ == '__main__':
    # _target = [(4096, 7407), (13475, 2359), (12944, 7202), (5620, 2550)]
    # _target = [(6532, 7848), (7469, 1372), (12723, 7077), (4054, 4657), (13051, 1902)] *2
    _target = [(3339, 7225), (14567, 7708), (10547, 5084), (13121, 2310), (4548, 2182), (7342, 4917)] * 2
    _path_lists = []
    # _path_lists.append(test1(_target))
    # _path_lists.append(test2(_target))
    _path_lists.append(test2_5(_target))
    _path_lists.append(test3(_target, _path_lists[0]))
    _d = Draw()
    _d.init_cp(_target)
    _d.perform(_path_lists, step_for_all=False)
