https://www.codingame.com/ide/puzzle/staircases
#include <bits/stdc++.h>
#define int long long
using namespace std;
int N;

int cal_0(int u, int d){
	if(d>u){
		int res = 1;
		//cerr << u << ' ' << d << endl;
		for(int i=u+1;d-i>i;i++){
			res += cal_0(i, d-i);
		}
		return res;
	}else{
		return 0;
	}
}

int cal_1(int n){
#define H 40
#define W 501
	int d[W][H] = {0};
	for(int i=1;i<W;i++){
		for(int j=1;j<H;j++){
			if(j==1){ d[i][j] = 1; }
			else if((1+j)*j/2>i){
				d[i][j] = 0;
				break;
			}else{
				d[i][j] = d[i-j][j] + d[i-j][j-1];
			}
		}
	}
	int res=0;
	for(int i=2;i<H;i++){ res += d[n][i]; }
	return res;
}

signed main()
{
	cin >> N;
	//cout << cal_0(0, N)-1 << endl;
	cout << cal_1(N) << endl;
}
