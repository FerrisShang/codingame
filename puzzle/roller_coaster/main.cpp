/* https://www.codingame.com/ide/puzzle/roller-coaster */
#include <bits/stdc++.h>
#define int long long
using namespace std;
int L,C,N;
#define PII pair<int, int> //Group index, number of people
int team[1002];
int mark[1002];
int queue_cost[1002];
int gp, q_i;

signed main()
{
	cin >> L >> C >> N;
	for(int i=0;i<N;i++){ cin >> team[i]; mark[i] = -1; }
	int sum_n=accumulate(team,team+N,0);
	if(sum_n <= L){ cout << C*sum_n << endl; exit(0); }
	while(mark[gp]<0){
		mark[gp] = q_i;
		int l=L;
		while(l>=team[gp]){ l -= team[gp]; gp = (gp+1)%N; }
		queue_cost[q_i] = L-l;
		fprintf(stderr, "%d ", queue_cost[q_i]);
		if(++q_i == C){ cout << accumulate(queue_cost, queue_cost+C, 0) << endl; exit(0); }
	}
	fprintf(stderr, "\n");

	int idx_cir_s = mark[gp];
	int idx_cir_e = q_i;
	int cir_num = (C - idx_cir_s) / (idx_cir_e-idx_cir_s);
	int cir_left_num = (C - idx_cir_s) % (idx_cir_e-idx_cir_s);
	int cir_total = accumulate(queue_cost+idx_cir_s,queue_cost+idx_cir_e,0);

	fprintf(stderr, "idx_cir_s: %d\n", idx_cir_s);
	fprintf(stderr, "idx_cir_e: %d\n", idx_cir_e);
	fprintf(stderr, "cir_num: %d\n", cir_num);
	fprintf(stderr, "cir_left_num: %d\n", cir_left_num);
	fprintf(stderr, "cir_total: %d\n", cir_total);

	cout << \
		accumulate(queue_cost,queue_cost+idx_cir_s,0) + \
		cir_num * cir_total + \
		accumulate(queue_cost+idx_cir_s,queue_cost+idx_cir_s+cir_left_num,0) \
		<< endl;
}