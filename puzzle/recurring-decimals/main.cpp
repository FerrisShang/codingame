// https://www.codingame.com/ide/puzzle/recurring-decimals
#include <bits/stdc++.h>
#define int long long
#define PII pair<int,int>
using namespace std;
int N, o, num=1, z;
map<PII, int> rec;
vector<char> res;
signed main()
{
	cin >> N;
	if(N==1) cerr<<1<<endl;
	else{
		while(1){num *= 10; if(num<N){ res.push_back(0);z++;} else break; }
		for(int idx=z;;idx++){
			o=num; int mult = num/N;
			num = num - mult * N;
			res.push_back(mult);
			if(!num || rec.count(PII(o, num))){ break; }
			rec[PII(o,num)] = idx;
			//printf("%d %d %d idx=%d\n", o,num, mult, idx);
			num *= 10;
		}
		int idx = rec[PII(o,num)];
		//printf("%d %d idx=%d\n\n", o, num, idx);
		if(!num){ cout << "0."; for(int i=0;i<res.size();i++) printf("%c", '0'+res[i]); }
		else{
			int tail_z = 0;
			for(auto it=res.rbegin()+1;it!=res.rend();it++){ if(*it==0) tail_z++; else break; }
			//int offset = 0; //min(tail_z, z);
			int offset = min(tail_z, z);
			int idx = rec[PII(o,num)];
			cout << "0.";
			for(int i=0;i<res.size()-offset-1;i++){
				if(i==idx-offset){ putchar('('); }
				printf("%c", '0'+res[i]);
			}
			putchar(')');
		}
		printf("\n");
	}
}