https://www.codingame.com/ide/puzzle/network-cabling
#include <bits/stdc++.h>
#define int long long
using namespace std;
#define P pair<int, int>
#define x first
#define y second
int N, L; P ps[1000000];
signed main()
{
	cin >> N;
	for(int i=0;i<N;i++){
		cin >> ps[i].x >> ps[i].y;
		//cerr << ps[i].x << ' ' << ps[i].y << '\n';
	}
	sort(ps, ps+N, [](P a,P b){return a.y<b.y;});
	int best_y = ps[N/2].y;
	auto minmax = minmax_element(ps, ps+N, [](P a,P b){return a.x<b.x;});
	L=minmax.y->x-minmax.x->x;
	cerr << L << ' '<< best_y << endl;
	for(int i=0;i<N;i++){
		L += abs(ps[i].y-best_y);
	}
	cout << L << endl;
}
