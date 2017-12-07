import turtle
import math
from csb3 import *


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


def path_test(target, tt1=180, tt2=90, tt3=20, tt4=250):
    ss = Sim(target=target)
    (x, y, vx, vy, a) = (target[-1][0], target[-1][1], 0, 0,
                         math.atan2(target[0][1]-target[-1][1], target[0][0]-target[-1][0]))
    for i in range(len(target)):
        while True:
            nc_p = (target[i][0], target[i][1])
            nnc_p = (target[(i+1) % len(target)][0], target[(i+1) % len(target)][1])
            _dist_tar = M.dist((x, y), nc_p)
            _vp_ang = M.ang_p2v([x, y], nc_p, [vx, vy])
            _ap_ang = M.ang_a2p(a, [x, y], nc_p)
            if U.glide_dist(math.cos(_vp_ang)*M.speed([vx, vy]), tt4) < _dist_tar:
                if abs(_ap_ang) < math.radians(45):
                    thrust = tt1
                    if abs(_ap_ang) < math.radians(20):
                        act_target = M.point_lpa([x, y],
                                                 M.op_ang_av(a, M.vec([x, y], nc_p)))
                    else:
                        act_target = nc_p
                elif abs(_ap_ang) < math.radians(60):
                    thrust = tt2
                    act_target = nc_p
                elif abs(_ap_ang) < math.radians(90):
                    thrust = tt3
                    act_target = nc_p
                else:
                    thrust = 0
                    act_target = nc_p
            else:
                act_target = nnc_p
                thrust = 0
            x, y, vx, vy, a = ss.update(act_target[0], act_target[1], thrust, np=nc_p, nnp=nnc_p)
            if M.dist((x, y), target[i]) < Sim.cp_r or ss.step > 1000:
                break

    print('------------------------- {}'.format(ss.step))
    return ss.get_path_list()


if __name__ == '__main__':
    # _target = [(4096, 7407), (13475, 2359), (12944, 7202), (5620, 2550)] * 5
    # _target = [(6532, 7848), (7469, 1372), (12723, 7077), (4054, 4657), (13051, 1902)] * 5
    _target = [(3339, 7225), (14567, 7708), (10547, 5084), (13121, 2310), (4548, 2182), (7342, 4917)] * 5
    _path_lists = [
        path_test(_target),
    ]
    _d = Draw()
    _d.init_cp(_target)
    _d.perform(_path_lists, step_for_all=False)