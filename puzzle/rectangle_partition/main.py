# https://www.codingame.com/ide/puzzle/rectangle-partition
import sys

w, h, count_x, count_y = [int(i) for i in input().split()]
xl = [0] + [int(i) for i in input().split()] + [w]
yl = [0] + [int(i) for i in input().split()] + [h]

xs = [0 for _ in range(20001)]
ans = 0
for i in range(len(xl)-1):
    for j in range(i+1, len(xl)):
        xs[xl[j]-xl[i]] += 1
for i in range(len(yl)-1):
    for j in range(i+1, len(yl)):
        ans += xs[yl[j]-yl[i]]
print(ans)

