# https://www.codingame.com/ide/puzzle/the-grand-festival---ii
import sys
n = int(input())
r = int(input())
prize = [int(input()) for i in range(n)]

top_prize = [0 for i in range(n+1)]
res = [set() for _ in range(n+1)]
for i in range(1, n+1):
    if i<=r:
        top_prize[i] = top_prize[i-1] + prize[i-1]
        res[i] = {i}
        res[i].update(res[i-1])
    else:
        for j in range(i-r, i+1):
            if top_prize[i] < top_prize[j-1]+sum(prize[j:i]):
                top_prize[i] = top_prize[j-1]+sum(prize[j:i])
                res[i] = {x for x in range(j+1,i+1)}
                res[i].update(res[j-1])
            else:
                pass
print('>'.join([str(i) for i in res[n]]))