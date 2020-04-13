// https://www.codingame.com/ide/puzzle/skynet-revolution-episode-1
#include <bits/stdc++.h>
using namespace std;
#define debug(args...) fprintf(stderr, args)
#define FOR(_I_, _N_) for(int _I_=0;_I_<_N_;_I_++)
#define PPI pair<P, int>
class P{
	public: int x, y;
	P(int x=0, int y=0){this->x = x; this->y = y;}
	friend ostream& operator << (ostream& out, const P& p){ out << "(" << p.x << ", " << p.y << ")"; return out; }
	friend istream& operator >> (istream& in, P& p){ in >> p.x; in >> p.y; return in;}
	inline bool operator == (const P& p){ return this->x == p.x && this->y == p.y; }
	inline P operator + (const P& p){ return P(this->x + p.x, this->y + p.y); }
	inline bool operator < (const P&p)const{ return ((this->x<<16)+this->y) < ((p.x<<16)+p.y); }
};
class GCOM // game common environment
{
	public:
	int N; // the total number of nodes in the level, including the gateways
	int L; // the number of links
	int E; // the number of exit gateways
	set<int> EI; // the index of a gateway node
	vector<vector<int>> LL; // the index of a gateway node
	int SI; // agent position
	int round;
	GCOM(long round_time_max){
		this->round = 0;
		/* Here is for Initialization input */
		cin >> N >> L >> E; cin.ignore();
		LL.resize(N);
		FOR(i, L){
			int N1, N2;// N1 and N2 defines a link between these nodes
			cin >> N1 >> N2; cin.ignore();
			LL[N1].push_back(N2);
			LL[N2].push_back(N1);
		}
		FOR(i, E){
			int ei; cin >> ei; cin.ignore();
			EI.insert(ei);
		}
	}
	void round_update(void) {
		this->round++;
		/* Here is for Input for one game turn */
		cin >> SI; cin.ignore();
	}
};
class G : public GCOM // game custom
{
	public:
	/* Custom variables */
	#define LINK(x, y) ((x<y)?P(x,y):P(y,x))
	set<P> dis_link;
	G(long round_time_ms_max=100):GCOM(round_time_ms_max){
		/* Custom Initialization */
	}
	void process(void){
		vector<int> e_list(EI.begin(), EI.end());
		set<int> near, exit_node;
		for(int i=0;i<e_list.size();i++){
			int n = e_list[i];
			exit_node.insert(n);
			for(int x: LL[n]){
				if(dis_link.count(LINK(SI, x))){ continue; }
				if(near.count(x) && !exit_node.count(x)){
					e_list.push_back(x);
					exit_node.count(x);
				}else{
					near.insert(x);
				}
			}
		}
		int cut = LL[SI].back();
		for(int n: LL[SI]){
			if(exit_node.count(n)){ cut = n; break; }
		}
		dis_link.insert(LINK(SI, cut));
		cout << SI << ' ' << cut << endl;
	}
};
int main(int argc, char** argv) {
	auto g = G();
	for(;;){
		g.round_update();
		g.process();
	}
}

