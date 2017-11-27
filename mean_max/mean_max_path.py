import random
import math


def dist(p1, p2):
    return math.sqrt(((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2))


def speed(v):
    return math.sqrt(v[0]**2+v[1]**2)


def dis_break(vs, mass, fr, max_f=300):
    vs = abs(vs)
    if vs <= 0.1:
        return 0
    max_a = max_f / mass
    length = 0
    while vs > 0:
        vs = vs - max_a if max_a < vs else 0
        length += vs
        vs *= (1-fr)
    return length


def acc_to_dest(vs, dis, mass, fr, f=0, fmin=-300, fmax=300):
    if fmax - fmin < 1:
        return f
    tvs = vs + f/mass
    tdis = dis - tvs
    tvs *= (1-fr)
    if tdis > dis_break(tvs, mass, fr):
        res = acc_to_dest(vs, dis, mass, fr, (f+fmax)/2, fmin=f, fmax=fmax)
    else:
        res = acc_to_dest(vs, dis, mass, fr, (f+fmin)/2, fmin=fmin, fmax=f)
    return res


def dvan(s, d, sv):
    r = [d[0]-s[0], d[1]-s[1]]
    if speed(sv) < 0.1 or speed(r) < 0.1:
        return 3.14
    t = (r[0]*sv[0]+r[1]*sv[1]) / (math.sqrt(r[0]**2+r[1]**2)*math.sqrt(sv[0]**2+sv[1]**2))
    t = 1 if t > 1 else t
    t = -1 if t < -1 else t
    return math.acos(t)


def ppath(s, d, vs, mass, fr):
    _dist = dist(s, d)
    _dist = 0.1 if _dist < 0.1 else _dist
    vsd = speed(vs)*math.cos(dvan(s, d, vs))
    f = acc_to_dest(vsd, _dist, mass, fr)
    if f != None and abs(f) > 0.01:
        _v = f / mass + vsd  # end of v
        _v = [_v*(d[0]-s[0])/_dist, _v*(d[1]-s[1])/_dist]
        _tv = (_v[0]-vs[0], _v[1]-vs[1])
        (tx, ty) = (s[0]+_tv[0], s[1]+_tv[1])
        throttle = speed(_tv) * mass
    else:
        (tx, ty, throttle) = (0, 0, 0)
    throttle = throttle if throttle < 300 else 300
    # print('--------- {} {} {}'.format(int(tx), int(ty), int(throttle)))
    return tx, ty, throttle


def run(vs, d, mass=0.5, fr=0.2, s=(0, 0)):
    rec = 0
    _ = 0
    for _ in range(20):
        # print("s=({},{}),d=({},{}),vs=({},{}) | {}=({},{})".format(int(s[0]), int(s[1]), int(d[0]), int(d[1]), int(vs[0]), int(vs[1]), int(dist(s,d)), int(s[0]-d[0]), int(s[1]-d[1])))
        if rec == int(dist(s,d)):
            break
        else:
            rec = int(dist(s,d))
        x, y, f = ppath(s, d, vs, mass, fr)
        (vx, vy) = (x-s[0], y-s[1])
        if speed((vx, vy)) > 0:
            a = (f/speed((vx, vy))*vx/mass, f/speed((vx, vy))*vy/mass)
        else:
            a = (f/mass, 0)
        vs = (vs[0]+a[0], vs[1]+a[1])
        s = (s[0]+vs[0], s[1]+vs[1])
        vs = (vs[0]*(1-fr), vs[1]*(1-fr))
    return _


def main():
    mean = 0
    for _ in range(5000):
        vs = (random.randint(-1000, 1000), random.randint(-1000, 1000))
        d = (4000, 4000 + random.randint(-1000, 1000))
        mean += run(vs, d)
    print(mean/5000)
main()