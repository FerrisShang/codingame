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
#define FORBE(_I_, _T_) for(auto _I_=_T_.begin();_I_!=_T_.end();_I_++)
#define R2D(R) ((R) * 180.0 / 3.1415926536)
#define D2R(D) ((D) * 3.1415926536 / 180.0)
#define PII pair<int ,int>
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
		vector< pair<int, int> > search_path; //next point & distance
		vector<int> path_cost;
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

		public:
		vector<node> n;
		Graph(int size=0){ set_size(size); }
		inline void set_size(int size){
			node_num = size; n.resize(node_num); visited.resize(node_num, false);
			FOR(i, n.size()){ n[i].id = i; }
		}
		inline void add_edge(int s, int d){ n[s].edge.push_back(d); }
		inline void add_edge_both(int v1, int v2){ add_edge(v1, v2); add_edge(v2, v1); }
		inline node* dfs(int node_idx, search_callback_t cb, void *pdata){
			search_callback = cb; search_pdata = pdata; visited.resize(0); visited.resize(node_num, false);
			return __dfs__(node_idx);
		}
		inline node* dfs(int node_idx, int max_deep, search_callback_t cb, void *pdata){
			search_callback = cb; search_pdata = pdata; visited.resize(0); visited.resize(node_num, false);
			return __dfs__(node_idx, max_deep);
		}
		inline vector< pair<int, int> > bfs(int node_idx, int max_deep, search_callback_t cb, void *pdata){
			search_callback = cb; search_pdata = pdata; visited.resize(0); visited.resize(node_num, false);
			list<pair<int, int>> queue;
			int deep_cnt = 0;
			search_path.resize(node_num);
			is_visited(node_idx);
			queue.push_back(pair<int, int>(node_idx, deep_cnt));
			search_path[node_idx] = pair<int, int>(node_idx, deep_cnt);
			while(!queue.empty()){
				node_idx = queue.front().first;
				deep_cnt = queue.front().second + 1;
				if(search_callback && search_callback(n[node_idx], search_pdata)){
					vector<pair<int, int>> res;
					int dist = 0;
					while(search_path[node_idx].first != node_idx){
						res.push_back(pair<int, int>(node_idx, dist++));
						node_idx = search_path[node_idx].first;
					}
					FOR(i, res.size()/2){ swap(res[i], res[res.size() - i - 1]); }
					return res;
				}
				queue.pop_front();
				if(max_deep == deep_cnt) continue;
				for (auto i=n[node_idx].edge.begin(); i != n[node_idx].edge.end(); ++i){
					if (!is_visited(*i)){
						queue.push_back(pair<int, int>(*i, deep_cnt));
						search_path[*i] = pair<int, int>(node_idx, deep_cnt);
					}
				}
			}
			return vector<pair<int, int>>(0);
		}
		inline vector< pair<int, int> > bfs(int node_idx, search_callback_t cb, void *pdata){ return bfs(node_idx, 1e5, cb , pdata); }
		inline vector< pair<int, int> > ass(int s, int d, search_callback_t h_cb, void *pdata){
			class PR{public: int first; int second;
				PR(const int& a, const int& b){ this->first = a; this->second = b; }
				inline bool operator <(const PR& p) const { return this->first < p.first; }
			};

			priority_queue<PR> frontier;
			frontier.push(PR(0, s));
			search_path.resize(node_num);
			search_path[s] = pair<int, int>(s, 0);
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
						if(h_cb){ frontier.push(PR(-(new_cost + h_cb(n[*i], search_pdata)), *i)); }
						else { frontier.push(PR(-(new_cost + (d - *i)), *i)); }
						search_path[*i] = pair<int, int>(node_idx, 0);
					}
				}
			}
			vector<pair<int, int>> res;
			int dist = 0;
			while(search_path[d].first != d){
				res.push_back(pair<int, int>(d, dist++));
				d = search_path[d].first;
			}
			FOR(i, res.size()/2){ swap(res[i], res[res.size() - i - 1]); }
			return res;
		}
		inline vector< pair<int, int> > get_bfs_path(void){ return search_path; }
	};
};
int player_count, my_id, op_id, zone_count, link_count, platinum_num;
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
	struct Zone{public:
		int pods[2]; int z_id; int owner_id; int visible; int platinum;
		friend ostream& operator << (ostream& out, const Zone& z){
			out << "ID:" << z.z_id << " Owner:" << z.owner_id << " p0:" << z.pods[0] << " p1:" << z.pods[1] << " V:" << z.visible; return out;
		}
	};
	int round;
	GCOM::Time *T;
	vector<int> visiable_zones, my_pods_zones, op_pods_zones, my_plat_zone;
	U::Graph<Zone> zones;
	GCOM(long round_time_max){
		this->round = 0;
		T = new GCOM::Time(round_time_max);
		/* Here is for Initialization input */
		cin >> player_count >> my_id >> zone_count >> link_count;
		op_id = 1 - my_id;
		zones.set_size(zone_count);
		FOR(i, zone_count){
			int z, p; cin >> z >> p;
			cin.ignore();
			zones.n[i].info.visible = -1;
			zones.n[i].info.platinum = 0;
		}
		FOR(i, link_count){ int z1, z2; cin >> z1 >> z2; cin.ignore(); zones.add_edge_both(z1, z2); }
	}
	void round_update(void) {
		T->update();
		this->round++;
		/* Here is for Input for one game turn */
		visiable_zones.resize(0);
		my_pods_zones.resize(0);
		op_pods_zones.resize(0);
		cin >> platinum_num; cin.ignore();
		FOR(i, zone_count){
			Zone *z = &zones.n[i].info;
			int owner_id, platinum;
			cin >> z-> z_id >> owner_id >> z->pods[0] >> z->pods[1] >> z->visible >> platinum; cin.ignore();
			//cin >> z-> z_id >> z->owner_id >> z->pods[0] >> z->pods[1] >> z->visible >> z->platinum; cin.ignore();
			if(z->visible > 0){ z->owner_id = owner_id; z->platinum = platinum; }
			if(z->visible > 0){ visiable_zones.push_back(i); }else{continue;}
			if(z->pods[my_id] > 0){ my_pods_zones.push_back(i); if(z->platinum > 0){ my_plat_zone.push_back(i); }}
			if(z->pods[op_id] > 0){ op_pods_zones.push_back(i); }
		}
	}
};
class S //simulation
{
};
class G : public GCOM // game custom
{
	class Pmonitor{
		public:
		Pmonitor(){last_round_num = 0; round_inc = 0;}
		int last_round_num;
		int round_inc;
		int cur_predict;
		int cur_spawn_num;
		set<int> getting_set;
		inline void update_num(G* g){
			int predict_add = 0;
			for(int i: getting_set){
				if(g->zones.n[i].info.owner_id == my_id){
					predict_add += g->zones.n[i].info.platinum;
				}
			}
			cur_spawn_num = last_round_num / 20;
			cur_predict = (last_round_num % 20) + round_inc + predict_add;
			round_inc = platinum_num - (last_round_num % 20);
			last_round_num = platinum_num;
			getting_set.clear();
		}
		inline void capturing(G* g, int id){
			if(g->zones.n[id].info.owner_id != my_id && g->zones.n[id].info.platinum > 0){
				getting_set.insert(id);
			}
		}
		inline int get_round_inc(void){ return round_inc; }
		inline int lost_num(void){ return cur_predict - platinum_num; }
	};
	public:
	/* Custom variables */
	//int player_count, my_id, op_id, zone_count, link_count, platinum_num;
	//GCOM::Time *T;
	//vector<int> visiable_zones, my_pods_zones, op_pods_zones;
	//U::Graph<Zone> zones;
	vector<pair<int, int>> my_base_path, op_base_path;
	int my_base_id, op_base_id;
	vector<priority_queue<PII>> action_map;
	vector<int> my_pods_valid;
	Pmonitor pmonitor;
	#define MP_DEFEND		0
	#define MP_ATTACK		1
	#define MP_PROTECT		2
	#define MP_CAPTRURE		3
	#define MP_SEARCH		4
	#define MP_MIN			4

	G(long round_time_ms_max=100):GCOM(round_time_ms_max){
		/* Custom Initialization */
		action_map.resize(zone_count);
		my_pods_valid.resize(zone_count);
	}
	inline void move(int num, int s, int d){ pmonitor.capturing(this, d);cout << num << " " << s << " " << d << " " ; }
	inline void move(int num, int s, int d, int priority){
		FOR(i, num){ action_map[s].push(PII(priority, d)); my_pods_valid[s]--; }
	}
	static bool is_zone_not_visited(const U::Graph<Zone>::node& node, void* pdata){
		set<int>* handled_zone = (set<int>*)pdata;
		if(!handled_zone->count(node.id) && node.info.owner_id != my_id){ return true; }
		else return false;
	}
	inline void process(void){
		pmonitor.update_num(this);
		if(round == 1){
			my_base_id = my_pods_zones.back();
			op_base_id = op_pods_zones.back();
			zones.bfs(my_base_id, NULL, NULL);
			my_base_path = zones.get_bfs_path();
			zones.bfs(op_base_id, NULL, NULL);
			op_base_path = zones.get_bfs_path();
		}
		for(auto i : my_pods_zones){
			my_pods_valid[i] = max(zones.n[i].info.pods[my_id] - zones.n[i].info.pods[op_id], 0);
			if(zones.n[i].info.pods[op_id] > 0 && zones.n[i].info.platinum > 0){ pmonitor.capturing(this, i);}
		}
		if(pmonitor.lost_num() > 0) debug("Platinum lost: %d\n", pmonitor.lost_num());
		__process__();
		bool move_flag = false;
		for(auto it : my_pods_zones){
			auto *pq = &action_map[it];
			my_pods_valid[it] = 0;
			while(!pq->empty()){
				int d = pq->top().second;
				if(it != d){ move(1, it, d); move_flag = true; }
				pq->pop();
			}
		}
		if(!move_flag) cout << "WAIT";
		cout<< endl << "WAIT" << endl;
	}
	inline void __process__(void){
		//while(!T->is_time_up()); debug("Time spend: %ld \n", T->get());
		set<int> handled_zone;
		for(auto z_id: my_pods_zones){
			handled_zone.insert(z_id);
			for(int i = my_pods_valid[z_id];i>0;i--){
#if 1
				vector<pair<int, int>> dest_path;
				#define SHORT_DIST 10
				if(op_base_path[my_base_id].second < SHORT_DIST){
					int dest_dist = op_base_path[z_id].second-1;
					int target[6], target_num = 0;
					for(auto j: zones.n[z_id].edge){
						if(op_base_path[j].second == dest_dist){
							target[target_num++] = j;
						}
					}
					move(1, z_id, target[rand()%target_num], MP_ATTACK);
					continue;
				}
				if(op_base_path[z_id].second < 3){ move(1, z_id, op_base_path[z_id].first, MP_ATTACK); continue; }
				if(zones.n[z_id].info.platinum > 0 && zones.bfs(z_id, 2, [](auto node, void* p){return node.info.pods[op_id] > 0;}, NULL).size() > 0){
					move(1, z_id, z_id, MP_ATTACK);
					continue;
				}
				dest_path = zones.bfs(z_id, 2,
						[](auto node, void* p){
							set<int>* hz = (set<int>*)p;
							return (!hz->count(node.id) && node.info.owner_id != my_id && node.info.platinum > 0); },
						&handled_zone);
				if(dest_path.size() > 0){
					handled_zone.insert(dest_path.back().first);
					move(1, z_id, dest_path[0].first, MP_CAPTRURE);
					continue;
				}
				dest_path = zones.bfs(z_id, 2, is_zone_not_visited, &handled_zone);
				if(dest_path.size() > 0){
					handled_zone.insert(dest_path.back().first);
					move(1, z_id, dest_path[0].first, MP_SEARCH);
					continue;
				}
				dest_path = zones.bfs(z_id, 3, is_zone_not_visited, &handled_zone);
				if(dest_path.size() > 0){
					move(1, z_id, dest_path[0].first, MP_SEARCH);
					continue;
				}
#endif
				{
					FOR(_, i){
						int dest_dist = op_base_path[z_id].second-1;
						int target[6], target_num = 0;
						for(auto j: zones.n[z_id].edge){
							if(op_base_path[j].second == dest_dist){
								target[target_num++] = j;
							}
						}
						move(1, z_id, target[rand()%target_num], MP_ATTACK);
					}
					break;
				}
			}
		}
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

