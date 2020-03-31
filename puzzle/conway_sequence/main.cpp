https://www.codingame.com/ide/puzzle/conway-sequence
#include <bits/stdc++.h>
using namespace std;
int R, L;
vector<int> res[30];
signed main()
{
	cin >> R >> L;
	res[1].push_back(R);
	for(int line=2;line<=L;line++){
		for(int idx=1,c=res[line-1][0],len=1;idx<=res[line-1].size();idx++){
			if(idx==res[line-1].size() || res[line-1][idx]!=c){
				res[line].push_back(len);
				res[line].push_back(c);
				if(idx==res[line-1].size()){ break; }
				c = res[line-1][idx];
				len = 1;
			}else{
				len++;
			}
		}
	}
	printf("%d", res[L][0]);
	for(int i=1;i<res[L].size();i++)
		printf(" %d", res[L][i]);
	cout << endl;
}