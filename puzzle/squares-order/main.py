# https://www.codingame.com/ide/puzzle/squares-order
'''
5 5
2
..111
22221
2.121
2..2.
2222.
'''
h, w, nb = (5, 5, 2)
num_map = [[0,0,1,1,1],[2,2,2,2,1],[2,0,1,2,1],[2,0,0,2,0],[2,2,2,2,0]]
h, w = [int(i) for i in input().split()]
nb = int(input())
_m = [input().strip().replace('.', '0') for _ in range(h)]
num_map = [[0 if ww == '.' else int(ww) for ww in hh] for hh in _m]

covered_map = [[False for _ in range(w)] for _ in range(h)]
result = []
output = []

def search(number):
    for i in range(h):
        for j in range(w):
            if num_map[i][j] == number:
                return j, i
def sq_list(base, size, op=False):
    res = set([(0, y) for y in range(size)] + [(size-1, y) for y in range(size)] +
              [(x, 0) for x in range(size)] + [(x, size-1) for x in range(size)])
    ret = set()
    for r in res:
        x = base[0]-r[0] if op else base[0]+r[0]
        y = base[1]-r[1] if op else base[1]+r[1]
        if 0 <= x < w and 0 <= y < h:
            ret.add((x, y))
        elif not op: return []
    return ret

def fit_square(num_map, covered_map, number):
    # return: n, x, y, size
    pos = search(number)
    if pos is not None:
        size_max = max([pos[0]+1, pos[1]+1, w - pos[0], h - pos[1]])
        for size in range(2, size_max+1):
            sql = [[pos, size, sq_list(pos, size)] for pos in sq_list(pos, size, True)]
            for sq in sql:
                p, s, sq_set = sq
                found = True
                for y in range(h):
                    for x in range(w):
                        if (x, y) in sq_set:
                            if num_map[y][x] != number and not covered_map[y][x]:
                                found = False
                                break
                        else:
                            if num_map[y][x] == number:
                                found = False
                                break
                    if not found: break
                if found: return number, p[0], p[1], s
    else:
        assert False
def update(covered_map, res):
    for x in range(res[1], res[1]+res[3]):
        covered_map[res[2]][x] = True
        covered_map[res[2]+res[3]-1][x] = True
    for y in range(res[2], res[2]+res[3]):
        covered_map[y][res[1]] = True
        covered_map[y][res[1]+res[3]-1] = True
def solve(num_map, covered_map, result):
    no_where = None
    for n in range(1, nb+1):
        if n in result: continue
        res = fit_square(num_map, covered_map, n)
        if res is not None:
            update(covered_map, res)
            result.append(res[0])
            output.append('%d %d' % (res[0], res[3]))
            return solve(num_map, covered_map, result)
    assert(no_where is None)
    return result

solve(num_map, covered_map, result)
for o in output[::-1]: print(o)