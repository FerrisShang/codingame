/* https://www.codingame.com/ide/puzzle/a-childs-play */
#include <bits/stdc++.h>
using namespace std;

#define P pair<int,int>
#define POS pair<int, P>
#define F first
#define S second
char line[30][30];
int step[30][30][4];
int cx, cy, dir, w, h;
POS next(const POS &p)
{
    int x=p.S.F, y=p.S.S, d=p.F;
    if(d==0){ if(y<=0||line[y-1][x]=='#'){d++;} else { y--; }}
    if(d==1){ if(x>=w-1||line[y][x+1]=='#'){d++;} else { x++; }}
    if(d==2){ if(y>=h-1||line[y+1][x]=='#'){d++;} else { y++; }}
    if(d==3){ if(x<=0||line[y][x-1]=='#'){
        d=0; if(y>0&&line[y-1][x]!='#'){ y--; }
    } else { x--; }}

    if(d==0){ if(y<=0||line[y-1][x]=='#'){d++;}}
    else if(d==1){ if(x>=w-1||line[y][x+1]=='#'){d++;}}
    else if(d==2){ if(y>=h-1||line[y+1][x]=='#'){d++;}}
    else if(d==3){ if(x<=0||line[y][x-1]=='#'){d=0;}}

    return POS(d, P(x,y));
}
int main()
{
    cin >> w >> h; cin.ignore();
    long long n;
    cin >> n; cin.ignore();
    for (int i = 0; i < h; i++) {
        scanf("%s", line[i]);
    }
    for(int i=0;i<h;i++)for(int j=0;j<w;j++){
        for(int _=0;_<4;_++)step[i][j][_] = -1;
        if(line[i][j] == 'O'){
            step[i][j][0] = 0;
            cx = j, cy = i;
        }
    }
    long long cnt=0;
    while(++cnt && n--){
        auto np = next(POS(dir, P(cx, cy)));
        dir = np.F, cx = np.S.F, cy = np.S.S;
        if(step[cy][cx][dir] >= 0 && cnt < n){
            n = n % (cnt - step[cy][cx][dir]);
        }
    }
    printf("%d %d\n", cx, cy);
}
