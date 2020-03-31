# https://www.codingame.com/ide/puzzle/minesweeper
from copy import deepcopy
h, w, nb = (2, 3, 1)
m = [[1,1,1],[-1,-1,-1]]
result = []

h, w = [int(i) for i in input().split()]
nb = int(input())
_m = [input().strip().replace('.', '0') for _ in range(h)]
m = [[-1 if ww == '?' else int(ww) for ww in hh] for hh in _m]

def sum_spec_num(x, y, num, find_all=False):
    ret = []
    if find_all: x1, x2, y1, y2 = (0, w, 0, h)
    else: x1, x2, y1, y2 = (x-1, x+2, y-1, y+2)
    for i in range(y1, y2):
        for j in range(x1, x2):
            if i == y and j == x and not find_all: continue
            if 0 <= i < h and 0 <= j < w and m[i][j] == num:
                ret.append((j, i))
    return ret

# -1: unkonown, -2: not mine, -3: mine
def check():
    if len(result) > nb: return False
    for i in range(h):
        for j in range(w):
            if m[i][j] >= 0 and len(sum_spec_num(j, i, -3)) > m[i][j]: return False
    return True


def find():
    changed = True
    while changed:
        changed = False
        for i in range(h):
            for j in range(w):
                unknown_list = sum_spec_num(j, i, -1)
                mine_list = sum_spec_num(j, i, -3)
                if len(unknown_list) + len(mine_list) == m[i][j] > 0:
                    for u in unknown_list:
                        m[u[1]][u[0]] = -3
                        result.append(u)
                        changed = True
                        break
                if m[i][j] - len(mine_list) == 0:
                    for u in unknown_list:
                        m[u[1]][u[0]] = -2
                all_unknown_list = sum_spec_num(j, i, -1, True)
                if len(all_unknown_list) + len(result) == nb:
                    for u in all_unknown_list:
                        m[u[1]][u[0]] = -3
                        result.append(u)
                        changed = True
                        break
                if changed: break
            if changed: break

def solve(mm, result):
    find()
    if not check():
        return False
    else:
        if len(result) == nb: return deepcopy(result)
        else:
            all_unknown_list = sum_spec_num(0, 0, -1, True)
            for a in all_unknown_list:
                m_bk = deepcopy(mm)
                res_bk = deepcopy(result)
                mm[a[1]][a[0]] = -2
                res = solve(mm, result)
                mm.clear()
                mm.extend(m_bk)
                result.clear()
                result.extend(res_bk)
                if res: return deepcopy(res)
            return False

res = solve(m, result)
res.sort()
for r in res:
    print('%d %d' % (r[0], r[1]))