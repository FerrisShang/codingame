import sys
wm = {
    'C':{'P', 'L'},
    'P':{'R', 'S'},
    'R':{'L', 'C'},
    'L':{'S', 'P'},
    'S':{'C', 'R'},

}
ll = [0 for _ in range(10000)]
n = int(input())
for i in range(n):
    numplayer, signplayer = input().split()
    ll[n+i] = (int(numplayer), signplayer)
def win(a, b):
    if b[1] in wm[a[1]]: return a
    if a[1] in wm[b[1]]: return b
    return a if a[0] < b[0] else b

for i in range(2*n-2, 1, -2):
    w = win(ll[i], ll[i+1])
    ll[i//2] = w
print(ll[1][0])

def dump_op(i=1, res = ''):
    if i >= n: return ''
    if ll[i*2][0] == ll[1][0]:
        res += dump_op(i*2, res)
        res += str(ll[i*2+1][0]) + ' '
    elif ll[i*2+1][0] == ll[1][0]:
        res += dump_op(i*2+1, res)
        res += str(ll[i*2][0]) + ' '
    return res

print(dump_op().strip())
