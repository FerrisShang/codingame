#include <iostream>
#include <stdio.h>
#include <sys/time.h>
#include <cmath>
#include <algorithm>
#include <vector>
#include <queue>
#include <deque>
#include <list>
#include <map>
#include <set>
using namespace std;
#define debug(args...) fprintf(stderr, args)
#define FOR(_I_, _N_) for(int _I_=0;_I_<_N_;_I_++)
#define FORBE(_I_, _T_) for(auto _I_=_T_.begin();_I_!=_T_.end();_I_++)
#define R2D(R) ((R) * 180.0 / 3.1415926536)
#define D2R(D) ((D) * 3.1415926536 / 180.0)
#define PII pair<int, int>
class P{
	public: int x, y;
	P(int x=0, int y=0){this->x = x; this->y = y;}
	friend ostream& operator << (ostream& out, const P& p){ out << "(" << p.x << ", " << p.y << ")"; return out; }
	friend istream& operator >> (istream& in, P& p){ in >> p.x; in >> p.y; return in;}
	inline bool operator == (const P& p){ return this->x == p.x && this->y == p.y; }
	inline P operator * (const int& d){ return P(this->x * d, this->y * d); }
	inline P operator / (const int& d){ return P(this->x / d, this->y / d); }
	inline P operator + (const P& p){ return P(this->x + p.x, this->y + p.y); }
	inline P operator - (const P& p){ return P(this->x - p.x, this->y - p.y); }
	inline void operator += (const P& p){ this->x += p.x; this->y += p.y; }
	inline void operator -= (const P& p){ this->x -= p.x; this->y -= p.y; }
};
class C // const
{
	public:
	const static int UP = 0;	const static int DOWN = 1;	const static int LEFT = 2;	const static int RIGHT = 3;
};
class M // math
{
	public:
	static float points_distance(P p1, P p2){return sqrt((p1.x-p2.x)*(p1.x-p2.x) + (p1.y-p2.y)*(p1.y-p2.y));}
	static float points_distance(P p1){return sqrt(p1.x*p1.x + p1.y*p1.y);}
	static P points_offset(P src, P dest){return P(dest.y - src.y, dest.x - src.x);}
	static int length_about(float length, float match_length, float deviation){return length >=match_length - deviation and length <  match_length + deviation;}
	static int length_about(float length, float match_length){return M::length_about(length, match_length, 3);}
};
class U // utils
{
	public:
	template <class T>
	class Graph{public:
		class Node {public: int id; vector<int> edge; T info; };
		typedef bool (*search_callback_t)(const Node& nd, void* pdata);
		int node_num;
		vector<bool> visited;
		search_callback_t search_callback;
		void* search_pdata;
		vector<PII> search_path; //next point & distance
		vector<int> path_cost;
		inline bool is_visited(int n){ bool ret = visited[n]; visited[n] = true; return ret; }
		inline Node* __dfs__(int node_idx){
			if(is_visited(node_idx)) return NULL;
			if(search_callback(n[node_idx], search_pdata)) return &n[node_idx];
			for(auto it = n[node_idx].edge.begin(); it != n[node_idx].edge.end(); ++it){
				Node* ret = __dfs__(*it);
				if(ret) return ret;
			}
			return NULL;
		}
		inline Node* __dfs__(int node_idx, int& max_deep){
			if(is_visited(node_idx) || max_deep == 0) return NULL;
			if(search_callback(n[node_idx], search_pdata)) return &n[node_idx];
			for(auto it = n[node_idx].edge.begin(); it != n[node_idx].edge.end(); ++it){
				max_deep--;
				Node* ret = __dfs__(*it, max_deep);
				max_deep++;
				if(ret) return ret;
			}
			return NULL;
		}

		public:
		vector<Node> n;
		Graph(int size=0){ set_size(size); }
		inline void set_size(int size){
			node_num = size; n.resize(node_num); visited.resize(node_num, false);
			FOR(i, n.size()){ n[i].id = i; }
		}
		inline void add_edge(int s, int d){ n[s].edge.push_back(d); }
		inline void add_edge_both(int v1, int v2){ add_edge(v1, v2); add_edge(v2, v1); }
		inline Node* dfs(int node_idx, search_callback_t cb, void *pdata){
			search_callback = cb; search_pdata = pdata; visited.resize(0); visited.resize(node_num, false);
			return __dfs__(node_idx);
		}
		inline Node* dfs(int node_idx, int max_deep, search_callback_t cb, void *pdata){
			search_callback = cb; search_pdata = pdata; visited.resize(0); visited.resize(node_num, false);
			return __dfs__(node_idx, max_deep);
		}
		inline vector<PII> bfs(int node_idx, int max_deep, search_callback_t cb, void *pdata){
			search_callback = cb; search_pdata = pdata; visited.resize(0); visited.resize(node_num, false);
			list<PII> queue;
			int deep_cnt = 0;
			search_path.resize(node_num);
			is_visited(node_idx);
			queue.push_back(PII(node_idx, deep_cnt));
			search_path[node_idx] = PII(node_idx, deep_cnt);
			while(!queue.empty()){
				node_idx = queue.front().first;
				deep_cnt = queue.front().second + 1;
				if(search_callback && search_callback(n[node_idx], search_pdata)){
					vector<PII> res;
					int dist = 0;
					while(search_path[node_idx].first != node_idx){
						res.push_back(PII(node_idx, dist++));
						node_idx = search_path[node_idx].first;
					}
					FOR(i, res.size()/2){ swap(res[i], res[res.size() - i - 1]); }
					return res;
				}
				queue.pop_front();
				if(max_deep == deep_cnt) continue;
				for (auto i=n[node_idx].edge.begin(); i != n[node_idx].edge.end(); ++i){
					if (!is_visited(*i)){
						queue.push_back(PII(*i, deep_cnt));
						search_path[*i] = PII(node_idx, deep_cnt);
					}
				}
			}
			return vector<PII>(0);
		}
		inline vector<PII> bfs(int node_idx, search_callback_t cb, void *pdata){ return bfs(node_idx, 1e5, cb , pdata); }
		inline vector<PII> ass(int s, int d, search_callback_t h_cb, void *pdata){
			class PR{public: int first; int second;
				PR(const int& a, const int& b){ this->first = a; this->second = b; }
				inline bool operator <(const PR& p) const { return this->first < p.first; }
			};

			priority_queue<PR> frontier;
			frontier.push(PR(0, s));
			search_path.resize(node_num);
			search_path[s] = PII(s, 0);
			path_cost.resize(0);
			path_cost.resize(node_num, -1);
			path_cost[s] = 0;
			while(!frontier.empty()){
				int node_idx = frontier.top().second;
				if(node_idx == d) break;
				frontier.pop();
				for (auto i=n[node_idx].edge.begin(); i != n[node_idx].edge.end(); ++i){
					int new_cost = path_cost[node_idx] + 1;
					if(path_cost[*i] < 0 || new_cost < path_cost[*i]){
						path_cost[*i] = new_cost;
						if(h_cb){ frontier.push(PR(-(new_cost + h_cb(n[*i], pdata)), *i)); }
						else { frontier.push(PR(-(new_cost + (d - *i)), *i)); }
						search_path[*i] = PII(node_idx, 0);
					}
				}
			}
			vector<PII> res;
			int dist = 0;
			while(search_path[d].first != d){
				res.push_back(PII(d, dist++));
				d = search_path[d].first;
			}
			FOR(i, res.size()/2){ swap(res[i], res[res.size() - i - 1]); }
			return res;
		}
		inline vector<PII> get_bfs_path(void){ return search_path; }
	};

	template <class T>
	class Cartesian{
		public:
		class Node{public: P p; T info;};
		typedef int (*search_callback_t)(const Node& nd, void *pdata);
		typedef pair<P, int> PPI;
		P size;
		vector<vector<Node>> n;
		vector<vector<bool>> visited;
		vector<vector<int>> path_cost;
		vector<vector<PPI>> search_path; // next point & distance
		search_callback_t search_callback;
		void* search_pdata;
		Cartesian(int x=0, int y=0){ set_size(x, y); }
		inline void set_size(int x, int y){
			size = P(x, y);
			n.resize(y); visited.resize(y); path_cost.resize(y); search_path.resize(y);
			FOR(i, y){ n[i].resize(x); FOR(j, x){ n[i][j].p = P(j, i); } }
			FOR(i, y){ visited[i].resize(x); }
			FOR(i, y){ path_cost[i].resize(x); FOR(j, x){ path_cost[i][j] = -1; } }
			FOR(i, y){ search_path[i].resize(x); }
		}
		inline vector<PPI> ass(P s, P d, search_callback_t is_blocked, void *pdata){
			vector<P> tmp_visited;
			class PR{public: int first; P second;
				PR(const int& a, const P& b){first=a;second=b;}
				inline bool operator <(const PR& p)const{return first < p.first;}
			};
			priority_queue<PR> frontier;
			frontier.push(PR(0, s)); tmp_visited.push_back(s);
			search_path[s.y][s.x] = PPI(s, 0);
			path_cost[s.y][s.x] = 0;
			while(!frontier.empty()){
				P cn_pos = frontier.top().second;
				if(cn_pos == d) break;
				frontier.pop();
				const static vector<P> offset = {P(0,1), P(0,-1), P(1,0), P(-1,0)};
				for(auto i: offset){
					P pos = i + cn_pos;
					if(pos.y < 0 || pos.y >= size.y || pos.x < 0 || pos.x >= size.x){ continue; }
					if(is_blocked(n[pos.y][pos.x], pdata)){ continue; }
					int new_cost = path_cost[cn_pos.y][cn_pos.x] + 1;
					if(path_cost[pos.y][pos.x] < 0 || new_cost < path_cost[pos.y][pos.x]){
						path_cost[pos.y][pos.x] = new_cost;
						frontier.push(PR(-(new_cost + abs(pos.x-d.x)+abs(pos.y-d.y)), pos));
						tmp_visited.push_back(pos);
						search_path[pos.y][pos.x] = PPI(cn_pos, 0);
					}
				}
			}
			vector<PPI> res;
			int dist = 0;
			while(!(search_path[d.y][d.x].first == d)){
				res.push_back(PPI(d, dist++));
				d = search_path[d.y][d.x].first;
			}
			FOR(i, res.size()/2){ swap(res[i], res[res.size() - i - 1]); }
			for(auto i: tmp_visited){ visited[i.y][i.x] = false; path_cost[i.y][i.x] = -1; }
			return res;
		}
	};
};
class GCOM // game common environment
{
	class Time
	{
		public: long max_time, time_rec;
		Time(int max_time=100){this->max_time = max_time; this->time_rec = get_time();}
		inline long get_time(void){ struct timeval tv; gettimeofday(&tv, NULL); return tv.tv_sec * 1000 + tv.tv_usec / 1000; }
		inline void update(void){ time_rec = get_time(); }
		inline bool is_time_up(void){ return get_time() - time_rec > max_time; }
		inline bool is_time_up(long max_time){ return get_time() - time_rec > max_time; }
		inline long get(void){ return get_time() - time_rec; } // Time spend
	};
	public:
	int round;
	string action_str;
	GCOM::Time *T;
	GCOM(long round_time_max){
		this->round = 0;
		T = new GCOM::Time(round_time_max);
		/* Here is for Initialization input */
	}
	void round_update(void) {
		T->update();
		this->round++;
		action_str = "";
		/* Here is for Input for one game turn */
	}
};
class S //simulation
{
};
class G : public GCOM // game custom
{
	public:
	/* Custom variables */
	G(long round_time_ms_max=100):GCOM(round_time_ms_max){
		/* Custom Initialization */
	}
	void process(void){
		while(!T->is_time_up()); debug("Time spend: %ld \n", T->get());
	}
};
void _D_E_B_U_G_(){
}
int main(int argc, char** argv) {
	_D_E_B_U_G_();
	auto g = G();
	for(;;){
		g.round_update();
		g.process();
	}
}
