import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.collections import PatchCollection
from matplotlib.patches import Circle
import random
from csb3 import *


def test1(target):
    s = Sim(target=target)
    (x, y, a, vx, vy) = (target[-1][0], target[-1][1], 0, 0, 0)
    cp_num = len(target)
    for i in range(cp_num):
        while True:
            if M.dist((x, y), target[i]) > 400:
                thrust = 100
                tp = (target[i][0], target[i][1])
            else:
                thrust = 20
                if i == cp_num - 1:
                    tp = (target[i][0], target[i][1])
                else:
                    tp = (target[i+1][0], target[i+1][1])
            x, y, vx, vy, a = s.update(tp[0], tp[1], thrust, np=(target[i][0], target[i][1]),
                                       nnp=(target[(i+1) % len(target)][0], target[(i+1) % len(target)][1]))
            if M.dist((x, y), target[i]) < Sim.cp_r or s.step > 4000:
                break

    print('_ {} _'.format(s.step))
    return s.get_path_list()


def test2(target):
    s = Sim(target=target)
    (x, y, a, vx, vy) = (target[-1][0], target[-1][1],
                         math.atan2(target[0][1]-target[-1][1], target[0][0]-target[-1][0]),
                         0, 0)
    cp_num = len(target)
    for i in range(cp_num):
        nc_p = target[i]
        nnc_p = target[0] if i == cp_num - 1 else target[i+1]
        while True:
            act_target = None
            thrust = None
            # v v v v v v v v v v v v v v v v v v v v v v v v v v v v v v v v v

            angs = [-math.pi / 10, -math.pi / 20, 0, math.pi / 20, math.pi / 10]
            dist_tar = M.dist((x, y), target[i])
            nc_v_ad = M.ang_v2p((vx, vy), (x, y), nc_p)
            nnc_v_ad = M.ang_v2p((vx, vy), (x, y), nnc_p)
            v_abs = M.speed((vx, vy))
            e_value = -1e9
            for ta in angs:
                nc_h_ad = M.ang_a2p(a+ta, (x, y), nc_p)
                nnc_h_ad = M.ang_a2p(a+ta, (x, y), nnc_p)

                ps = [
                    v_abs * math.cos(nc_v_ad),
                    v_abs * math.cos(nc_h_ad),
                    v_abs * math.cos(nnc_v_ad),
                    v_abs * math.cos(nnc_h_ad),
                ]
                if dist_tar > 2000:
                    hr = [.9, 0.6, .02, .01]
                    tr = [.2, .4, .01, .01]
                else:
                    hr = [0, 2, .1, .1]
                    tr = [.1, .5, .01, .01]
                value = sum([ps[i] * hr[i] for i in range(len(ps))])
                if value > e_value:
                    e_value = value
                    e_ang = a + ta
                    act_target = M.point_la_a((x, y), a, ta)
                    thrust = 40 + sum([ps[i] * tr[i] for i in range(len(ps))])
                    thrust = min(200, max(0, thrust))
            # print('{:5d} {:5d} {:5d}'.format(round(v_abs), round(thrust), round(math.degrees(e_ang))))

            # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            x, y, vx, vy, a = s.update(act_target[0], act_target[1], thrust)
            if M.dist((x, y), target[i]) < Sim.cp_r or s.step > 4096:
                break

    print('^ {} ^'.format(s.step))
    return s.get_path_list()


class Draw:
    class Anim:
        def __init__(self, cb, line_num, pods=None, interval=10, x_lim=16000, y_lim=12000):
            fig, ax = plt.subplots()
            if pods is not None:
                ax.add_collection(
                    PatchCollection([Circle(pod, 600) for pod in pods], alpha=0.5)
                )
            ud = self.UpdateDist(ax, cb, line_num, x_lim, y_lim)
            _ = FuncAnimation(fig, ud, interval=interval)
            plt.show()

        class UpdateDist(object):
            def __init__(self, _ax, _cb, line_num, x_lim, y_lim):
                color = ['k', 'b', 'r', 'g']
                self.lines = [_ax.plot([], [], color[_])[0] for _ in range(line_num)]
                self.ax = _ax
                self.cb = _cb
                # Set up plot parameters
                self.ax.set_xlim(0, x_lim)
                self.ax.set_ylim(0, y_lim)

            def init(self):
                for line in self.lines:
                    line.set_data([], [])
                return self.lines,

            def __call__(self, i):
                if i == 0:
                    return self.init()
                for idx, line in enumerate(self.lines):
                    line.set_data(self.cb(idx, i))
                return self.lines,

    def __init__(self, pods, path_list):
        self.pods = pods
        self.path_list = path_list
        self.Anim(self.callback, len(path_list), pods)

    def callback(self, idx, i):
        n = min(i, len(self.path_list[idx]))
        return [x[0] for x in self.path_list[idx][:n]], [y[1] for y in self.path_list[idx][:n]]


if __name__ == '__main__':
    random.seed(20)
    _targets = [
        [(random.randint(1000, 15000), random.randint(1000, 8000)) for _ in range(random.randint(2, 8))]*5
        for _ in range(2)
    ]
    print(len(_targets[0]))
    # for t in _targets: Draw(t, [test1(t), test2(t)])
    for t in _targets: test1(t), test2(t)

