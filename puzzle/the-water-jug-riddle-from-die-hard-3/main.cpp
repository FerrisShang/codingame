// https://www.codingame.com/ide/puzzle/the-water-jug-riddle-from-die-hard-3
#include <iostream>
#include <iomanip>
#include <fstream>
#include <stdio.h>
#include <set>
#define FOR(i,a,b) for(int i=a;i<b;i++)
using namespace std;
int W, N, C[5], res;
typedef int c_t[5];
set<long long> all;

void dump(long long s){c_t c; cerr << "DUMP: ";FOR(i, 0, N){ c[N-1-i]=((s>>i*8)&0xFF); cerr << c[N-1-i] << ' ';} cerr << endl;}
long long pour(long long s, int from, int to)
{
	c_t c; FOR(i, 0, N) c[N-1-i]=((s>>i*8)&0xFF);
	if(c[from] > C[to]-c[to]){
		c[from] -= C[to]-c[to];
		c[to] = C[to];
	}else{
		c[to] += c[from];
		c[from] = 0;
	}
	s=0; FOR(i, 0, N) s|=(long long)c[N-1-i]<<i*8;
	return s;
}
long long fill(long long s, int n)
{
	s &= ~(0xFFull << (N-1-n)*8);
	s |= (long long)C[n] << (N-1-n)*8;
	return s;
}
long long empty(long long s, int n)
{
	s &= ~(0xFFull << (N-1-n)*8);
	return s;
}
void check(long long s, int sum, char flag){
	#define GET(s, i) (((s)>>(i)*8)&0xFF)
	FOR(i,0,N){if(GET(s, i) == W){ cout << res << endl; exit(0); } }
}
void cal(set<long long> &s)
{
	set<long long> ss;
	set<long long>::iterator it;
	if(res > 100 || s.size()== 0) return;
	cerr << res << endl;
	all.insert(s.begin(), s.end());
	for(it=s.begin();it!=s.end();++it){
		dump(*it);
		check(*it, 0, ~0); c_t c; FOR(i, 0, N){c[N-1-i]=((*it>>i*8)&0xFF);}
		for(int i=0;i<N;i++){
			if(c[i] < C[i]){
				ss.insert(fill(*it, i));
			}
			if(c[i] > 0){
				ss.insert(empty(*it, i));
				for(int j=0;j<N;j++){
					if(i == j) continue;
					if(c[j] < C[j]){
						ss.insert(pour(*it, i, j));
					}
				}
			}
		}
	}
	res++;
	for(it=all.begin();it!=all.end();++it){  if(ss.count(*it)){ ss.erase(*it); } }
	cal(ss);
}
int main(int argc, char *argv[])
{
#if defined(__WIN32__)
	ifstream in__("in.txt");cin.rdbuf(in__.rdbuf());
#endif
	cin >> W;
	cin >> N;
	FOR(i, 0, N) cin >> C[i];
	set<long long> init;
	init.insert(0x0000000000);
	cal(init);
}
