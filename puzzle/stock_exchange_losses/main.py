https://www.codingame.com/ide/puzzle/stock-exchange-losses
n = int(input())
v = [int(i) for i in input().split()]
m = v[:]
n = v[:]
for i in range(1, len(v)-1):
    m[i] = max(m[i-1], v[i])
for i in range(len(v)-2, -1, -1):
    n[i] = min(n[i+1], v[i])
print(min(0, min([a-b for a,b in zip(n, m)])))