#include <iostream>
#include <stdio.h>
#include <sys/time.h>
#include <cmath>
#include <algorithm>
#include <vector>
#include <queue>
#include <list>
#include <map>
#include <set>
using namespace std;
#define debug(args...) fprintf(stderr, args)
#define FOR(_I_, _N_) for(int _I_=0;_I_<_N_;_I_++)
#define R2D(R) ((R) * 180.0 / 3.1415926536)
#define D2R(D) ((D) * 3.1415926536 / 180.0)
class P{
	public: int x, y;
	P(int x=0, int y=0){this->x = x; this->y = y;}
	friend ostream& operator << (ostream& out, const P& p){ out << "(" << p.x << ", " << p.y << ")"; return out; }
	friend istream& operator >> (istream& in, P& p){ in >> p.x; in >> p.y; return in;}
	inline bool operator == (const P& p){ return this->x == p.x && this->y == p.y; }
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
		class node {public: int id; vector<int> edge; T info; };
		typedef bool (*search_callback_t)(const node& nd, void* pdata);
		int node_num;
		vector<bool> visited;
		search_callback_t search_callback;
		void* search_pdata;
		vector<int> search_path;
		inline bool is_visited(int n){ bool ret = visited[n]; visited[n] = true; return ret; }
		inline node* __dfs__(int node_idx){
			if(is_visited(node_idx)) return NULL;
			if(search_callback(n[node_idx], search_pdata)) return &n[node_idx];
			for(auto it = n[node_idx].edge.begin(); it != n[node_idx].edge.end(); ++it){
				node* ret = __dfs__(*it);
				if(ret) return ret;
			}
			return NULL;
		}
		inline node* __dfs__(int node_idx, int& max_deep){
			if(is_visited(node_idx) || max_deep == 0) return NULL;
			if(search_callback(n[node_idx], search_pdata)) return &n[node_idx];
			for(auto it = n[node_idx].edge.begin(); it != n[node_idx].edge.end(); ++it){
				max_deep--;
				node* ret = __dfs__(*it, max_deep);
				max_deep++;
				if(ret) return ret;
			}
			return NULL;
		}
		inline vector<int> __dfs_get_path_from_search_path__(int n){
			vector<int> res;
			while(search_path[n] != n){
				res.push_back(n);
				n = search_path[n];
			}
			FOR(i, res.size()/2){ swap(res[i], res[res.size() - i - 1]); }
			return res;
		}

		public:
		vector<node> n;
		Graph(int size=0){ node_num = size; n.resize(node_num); }
		inline void set_size(int size){
			node_num = size; n.resize(node_num); visited.resize(node_num);
			FOR(i, n.size()){ n[i].id = i; }
		}
		inline void add_edge(int s, int d){ n[s].edge.push_back(d); }
		inline void add_edge_both(int v1, int v2){ add_edge(v1, v2); add_edge(v2, v1); }
		inline node* dfs(int node_idx, search_callback_t cb, void *pdata){
			search_callback = cb; search_pdata = pdata; visited.resize(node_num, false);
			return __dfs__(node_idx);
		}
		inline node* dfs(int node_idx, int max_deep, search_callback_t cb, void *pdata){
			search_callback = cb; search_pdata = pdata; visited.resize(node_num, false);
			return __dfs__(node_idx, max_deep);
		}
		inline vector<int> bfs(int node_idx, int max_deep, search_callback_t cb, void *pdata){
			search_callback = cb; search_pdata = pdata; visited.resize(node_num, false);
			list<pair<int, int>> queue;
			int deep_cnt = 0;
			search_path.resize(node_num);
			is_visited(node_idx);
			queue.push_back(pair<int, int>(node_idx, deep_cnt));
			search_path[node_idx] = node_idx;
			while(!queue.empty()){
				node_idx = queue.front().first;
				deep_cnt = queue.front().second + 1;
				if(search_callback(n[node_idx], search_pdata)){
					return __dfs_get_path_from_search_path__(node_idx);
				}
				queue.pop_front();
				if(max_deep == deep_cnt) continue;
				for (auto i=n[node_idx].edge.begin(); i != n[node_idx].edge.end(); ++i)
					if (!is_visited(*i)){
						queue.push_back(pair<int, int>(*i, deep_cnt));
						search_path[*i] = node_idx;
					}
			}
			return vector<int>(0);
		}
		inline vector<int> bfs(int node_idx, search_callback_t cb, void *pdata){ return bfs(node_idx, 1e5, cb , pdata); }
		inline vector<int> ass(int s, int d, search_callback_t h_cb, void *pdata){
			class PR: public pair<int, int>{
				inline bool operator <(const PR& pr){ return this->first < pr.first; }
			};
			//TODO: Unfinished
		}
		inline vector<int> get_search_path(void){ return search_path; }
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
	auto g = G(99);
	for(;;){
		g.round_update();
		g.process();
	}
}
