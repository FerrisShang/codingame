# https://www.codingame.com/ide/puzzle/the-labyrinth
from queue import PriorityQueue


def get_path(me_pos, tar_pos, path_map):
    if me_pos == tar_pos:
        return [me_pos]
    frontier = PriorityQueue()
    frontier.put((0, me_pos))
    came_from = {me_pos: None}
    cost_so_far = {me_pos: 0}

    while not frontier.empty():
        current = frontier.get()[1]
        if current == tar_pos:
            break
        neighbors = [(current[0]+1, current[1]), (current[0], current[1]+1),
                     (current[0]-1, current[1]), (current[0], current[1]-1)]
        for n in neighbors:
            if not (0 <= n[0] < len(path_map[0]) and 0 <= n[1] < len(path_map) and path_map[n[1]][n[0]] != '#'):
                continue
            if path_map[n[1]][n[0]] == '?':
                new_cost = cost_so_far[current] + 10
            else:
                new_cost = cost_so_far[current] + 1
            if n not in cost_so_far or new_cost < cost_so_far[n]:
                cost_so_far[n] = new_cost
                priority = new_cost + abs(tar_pos[0] - n[0]) + abs(tar_pos[1] - n[1])
                frontier.put((priority, n))
                came_from[n] = current
    if tar_pos not in came_from:
        return []
    res = [tar_pos]
    _t = tar_pos
    while True:
        _t = came_from[_t]
        if _t == me_pos:
            break
        res.append(_t)
    return res[::-1]


def get_tar_pos(path_map, target):
    for i in range(len(path_map)):
        for j in range(len(path_map[0])):
            if path_map[i][j] == target:
                return j, i
    return None


def find_target(path_map, cur_pos):
    tm = []
    for s in path_map:
        tm.append([_ for _ in s])
    n_pos = [(cur_pos[0]-1, cur_pos[1]), (cur_pos[0], cur_pos[1]+1),
                 (cur_pos[0]+1, cur_pos[1]), (cur_pos[0], cur_pos[1]-1)]
    while True:
        t_pos = []
        for n in n_pos:
            if 0 <= n[0] < len(path_map[0]) and 0 <= n[1] < len(path_map) and tm[n[1]][n[0]] != '#':
                if tm[n[1]][n[0]] == '?':
                    return n[0], n[1]
                tm[n[1]][n[0]] = '#'
                t_pos.append((n[0]-1, n[1]))
                t_pos.append((n[0], n[1]+1))
                t_pos.append((n[0]+1, n[1]))
                t_pos.append((n[0], n[1]-1))
        n_pos = t_pos
    return 0, 0


def dirc(me_pos, next_pos):
    # print("({},{}) | {}".format(me_pos[0], me_pos[1], next_pos), file=sys.stderr)
    if next_pos[0][0] > me_pos[0]:
        return 'RIGHT'
    elif next_pos[0][0] < me_pos[0]:
        return 'LEFT'
    elif next_pos[0][1] > me_pos[1]:
        return 'DOWN'
    else:
        return 'UP'

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

# r: number of rows.
# c: number of columns.
# a: number of rounds between the time the alarm countdown is activated and the time the alarm goes off.
r, c, a = [int(i) for i in input().split()]
path_map = [None for __ in range(r)]
# print('{}'.format(a), file=sys.stderr)
start_pos = None
flag = False
# game loop
while True:
    # kr: row where Kirk is located.
    # kc: column where Kirk is located.
    kr, kc = [int(i) for i in input().split()]
    if not start_pos:
        start_pos = (kc, kr)
    me_pos = (kc, kr)
    for i in range(r):
        row = input()  # C of the characters in '#.TC?' (i.e. one line of the ASCII maze).
        path_map[i] = row
    # for _ in path_map:
    #     print(_, file=sys.stderr)
    target = 'T' if flag else 'C'
    tar_pos = get_tar_pos(path_map, target)
    if tar_pos:
        if len(get_path(start_pos, tar_pos, path_map)) <= a:
            pass
        else:
            tar_pos = find_target(path_map, me_pos)
    else:
        tar_pos = find_target(path_map, me_pos)
    # print('{}'.format(tar_pos), file=sys.stderr)
    p = get_path(me_pos, tar_pos, path_map)
    if (p[0][0], p[0][1]) == tar_pos:
        flag = True
    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)

    # Kirk's next move (UP DOWN LEFT or RIGHT).
    print(dirc(me_pos, p))
