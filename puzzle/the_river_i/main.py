# https://www.codingame.com/ide/puzzle/the-river-i-
import sys
r_1 = int(input())
r_2 = int(input())
def nn(n):
    return n + sum([int(n) for n in str(n)])

while(r_1 != r_2):
    if r_1 < r_2:
        r_1 = nn(r_1)
    else:
        r_2 = nn(r_2)
print(r_1)