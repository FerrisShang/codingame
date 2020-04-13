// https://www.codingame.com/ide/puzzle/the-lucky-number
#include <bits/stdc++.h>
#define int long long
using namespace std;
int L, R;
int cal(int n, int flag=0){ //flag:0x02->8,0x01->6
	if(n == 0 || flag==0x03) return 0;
	int h, w;
	for(h=n, w=0;h>=10;w++,h/=10);
	int total = 0;
	int tmp = flag?(powl(9,w)):(2*(powl(9,w)-powl(8,w)));
	cerr << ": " << n << ' ' << h << ' ' << w << ' ' << tmp << ' ' << flag << endl;
	if(n>=10){
		if(h > 8){ total = (h-2)*tmp + (flag?999:2)*powl(9,w); }
		else if(h > 6){ total = (h-1)*tmp + (flag==0x02?0:powl(9,w)); }
		else if(h > 0){ total = h*tmp; }
		if(h==6) flag|=0x01; else if(h==8) flag|=0x02;
		if(n>=10&&(n%(int)powl(10,w))==0){ total += ((flag)&&flag!=0x03); }
	}else{
		if(flag==0){ total += n>=8?2:n>=6?1:0; }
		else if(flag==0x01){ total += n>=8?n:n+1; }
		else if(flag==0x02){ total += n>=6?n:n+1; }
	}
	return total + cal(n%(int)powl(10,w), flag);
}

signed main()
{
	cin >> L >> R;
	//cerr << cal(L-1) << '\n' << cal(R) << endl;
	cout << cal(R) - cal(L-1) << endl;
}