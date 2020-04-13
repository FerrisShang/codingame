# https://www.codingame.com/ide/puzzle/the-river-ii-

N = 100000
res = [[0, -1] for i in range(N)]
for i in range(1, N):
    last = i
    if res[i][1] < 0:
        res[i][1] = i
    while last < N:
        res[last][0] += 1
        nn = last + sum([int(last) for last in str(last)])
        if nn < N and res[nn][1] < 0:
            res[nn][1] = last
            last = nn
        else: break
print('YES' if res[int(input())][0] > 1 else 'NO')
