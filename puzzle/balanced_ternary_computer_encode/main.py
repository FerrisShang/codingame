# https://www.codingame.com/ide/puzzle/balanced-ternary-computer-encode
n = int(input())
b = [0]+[3**i for i in range(11)]
bb = [sum(b[:i]) for i in range(1, len(b)+1)]
o = ''
for i in range(10, 0, -1):
    oo = None
    for j in range(-1, 2):
        if abs(n - j*b[i]) <= bb[i-1]:
            oo = 'T'if j < 0 else str(j)
            if oo != '0' or len(o) > 0: o += oo
            n -= j*b[i]
            break
print(o if len(o) else '0')