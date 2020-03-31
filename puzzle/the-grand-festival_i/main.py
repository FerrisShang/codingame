# https://www.codingame.com/ide/puzzle/the-grand-festival---i
import sys
n = int(input())
r = int(input())
prize = [int(input()) for i in range(n)]

res = [0 for i in range(n+1)]
for i in range(1, n+1):
    if i<=r:
        res[i] = res[i-1] + prize[i-1]
    else:
        for j in range(i-r, i):
            res[i] = max(res[i], res[j-1]+sum(prize[j:i]))
print(res[n])
