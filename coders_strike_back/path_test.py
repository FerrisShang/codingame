import turtle
import math
from csb1 import *


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
    def perform(path_lists):
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
                    pass

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
            x, y, a, vx, vy = s.update(tp[0], tp[1], thrust)
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


if __name__ == '__main__':
    _target = [(4096, 7407), (13475, 2359), (12944, 7202), (5620, 2550)]
    # _target = [(6532, 7848), (7469, 1372), (12723, 7077), (4054, 4657), (13051, 1902)] *2
    # _target = [(3339, 7225), (14567, 7708), (10547, 5084), (13121, 2310), (4548, 2182), (7342, 4917)] * 2
    _path_lists = []
    _path_lists.append(test1(_target))
    _path_lists.append(test2(_target))
    _d = Draw()
    _d.init_cp(_target)
    _d.perform(_path_lists)
