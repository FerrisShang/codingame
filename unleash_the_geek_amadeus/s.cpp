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
#define PII pair<int, int>
#define PPI pair<P, int>

#define TYPE_MY_ROBOT 0
#define TYPE_OP_ROBOT 1
#define TYPE_RADAR    2
#define TYPE_TRAP     3
#define ITEM_NONE    -1
#define ITEM_RADAR    2
#define ITEM_TRAP     3
#define ITEM_ORE      4
#define ACT_NONE      0
#define ACT_TRAP_GET  1
#define ACT_TRAP_SET  2
#define ACT_RADAR_GET 3
#define ACT_RADAR_SET 4
#define ACT_MINING    5
#define ACT_UNLOAD    6

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
	inline bool operator < (const P& p)const{ return ((this->x<<16)+this->y) < ((p.x<<16)+p.y); }
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
	static int points_length(P src, P dest){return abs(dest.y - src.y) + abs(dest.x - src.x);}
	static int move_round(P src, P dest){return (points_length(src, dest) + 3) / 4;}
	static int length_about(float length, float match_length, float deviation){return length >=match_length - deviation and length <  match_length + deviation;}
	static int length_about(float length, float match_length){return M::length_about(length, match_length, 3);}
};

class NodeInfo{
	public:
	int ore, pre_ore;
	int hole, pre_hole;
	int ore_dec, new_hole;
	int pdt_ore;
	int visible;
	void update(int ore, int hole){
		pre_ore = this->ore;
		pre_hole = this->hole;
		this->ore = ore;
		this->hole = hole;
		if(hole && !pre_hole) new_hole = true;
		else new_hole = false;
		if(pre_ore > 0 && ore == pre_ore - 1) ore_dec = true;
		else ore_dec = false;
	}
	friend ostream& operator << (ostream& out, const NodeInfo& n){ out << "(" << n.ore << ", " << n.hole << ")"; return out; }
};
class Entity{
	public:
	int id; // unique id of the entity
	int type; // 0 for your robot, 1 for other robot, 2 for radar, 3 for trap
	int x, y; // position of the entity
	int item; // if this entity is a robot, the item it is carrying (-1 for NONE, 2 for RADAR, 3 for TRAP, 4 for ORE)
	friend ostream& operator << (ostream& out, const Entity& e){ out << e.id << " " << "(" << e.x << ", " << e.y << ")" << " " << e.type << " " << e.item; return out; }
	friend istream& operator >> (istream& in, Entity& e){ in >> e.id >> e.type >> e.x >> e.y >> e.item; return in;}
};
class Robot:public Entity{
	public:
	P last_pos;
	int move_len;
	bool has_item;
	bool mining;
	void update(const Entity& e){
		last_pos.x = this->x; last_pos.y = this->y;
		this->id = e.id;
		this->x = e.x; this->y = e.y;
		this->item = e.item;
		move_len = M::points_length(last_pos, P(e.x, e.y));
		if(last_pos.x != 0 && e.x == 0){
			has_item = false;
		}else if(move_len == 0 && e.x == 0){
			has_item = true;
		}
	}
	inline bool is_alive(void){ return this->x >= 0; }
};
/*
1 If DIG commands would trigger Traps, they go off.
2 The other DIG commands are resolved.
3 REQUEST commands are resolved.
4 Request timers are decremented.
5 MOVE and WAIT commands are resolved.
6 Ore is delivered to the headquarters.
*/
PPI NEARBY[] = {
	PPI(P(0,0),0), PPI(P(0,1),1), PPI(P(0,-1),1), PPI(P(1,0),1), PPI(P(-1,0),1),
	PPI(P(0,2),2), PPI(P(0,-2),2), PPI(P(2,0),2), PPI(P(-2,0),2),
	PPI(P(1,1),2), PPI(P(1,-1),2), PPI(P(-1,-1),2), PPI(P(-1,1),2),
	PPI(P(0,3),3), PPI(P(0,-3),3), PPI(P(3,0),3), PPI(P(-3,0),3),
	PPI(P(1,2),3), PPI(P(2,1),3), PPI(P(2,-1),3), PPI(P(1,-2),3),
	PPI(P(-1,-2),3), PPI(P(-2,-1),3), PPI(P(-2,1),3), PPI(P(-1,2),3),
	PPI(P(0,4),4), PPI(P(0,-4),4), PPI(P(4,0),4), PPI(P(-4,0),4),
	PPI(P(1,3),4), PPI(P(2,2),4), PPI(P(3,1),4), PPI(P(3,-1),4), PPI(P(2,-2),4), PPI(P(1,-3),4),
	PPI(P(-1,-3),4), PPI(P(-2,-2),4), PPI(P(-3,-1),4), PPI(P(-3,1),4), PPI(P(-2,2),4), PPI(P(-1,3),4),
};
class U // utils
{
	public:
	template <class T>
	class Cartesian{
		public:
		class Node{public: P p; T info;};
		typedef int (*search_callback_t)(const Node& nd, void *pdata);
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
		Time(int max_time=100){this->max_time = max_time; this->time_rec = get_time();}//srand(time_rec);}
		inline long get_time(void){ struct timeval tv; gettimeofday(&tv, NULL); return tv.tv_sec * 1000 + tv.tv_usec / 1000; }
		inline void update(void){ time_rec = get_time(); }
		inline bool is_time_up(void){ return get_time() - time_rec > max_time; }
		inline bool is_time_up(long max_time){ return get_time() - time_rec > max_time; }
		inline long get(void){ return get_time() - time_rec; } // Time spend
	};
	public:
	int round;
	vector<PPI> action;
	int width, height;
	int myScore, enemyScore;
	int entityCount; // number of entities visible to you
	int radarCooldown; // turns left until a new radar can be requested
	int trapCooldown; // turns left until a new trap can be requested
	U::Cartesian<NodeInfo> m;
	vector<U::Cartesian<NodeInfo>::Node> ores;
	vector<Entity> entities;
	set<P> traps, traps_valid, op_traps, radars;
	vector<Robot> my_rbt;
	vector<Robot> op_rbt;
	GCOM::Time *T;
	GCOM(long round_time_max){
		this->round = 0;
		T = new GCOM::Time(round_time_max);
		/* Here is for Initialization input */
		cin >> width >> height;
		m.set_size(width, height);
		action.resize(5);
		my_rbt.resize(5);
		op_rbt.resize(5);
		FOR(i, 5){
			action[i].second = ACT_NONE;
			my_rbt[i].x = -1; my_rbt[i].y = -1;
			op_rbt[i].x = -1; op_rbt[i].y = -1;
		}
	}
	void update_map_visible(P radar_pos){
		FOR(i, sizeof(NEARBY) / sizeof(NEARBY[0])){
			auto p = NEARBY[i].first + radar_pos;
			if(0<p.x && p.x < width && 0 <= p.y && p.y < height){
				m.n[p.y][p.x].info.visible = true;
				m.n[p.y][p.x].info.pdt_ore = m.n[p.y][p.x].info.ore;
			}
		}
	}
	void round_update(void) {
		T->update();
		this->round++;
		/* Here is for Input for one game turn */
		cin >> myScore >> enemyScore;
		debug("round:%d radar:%d trap:%d/%d score: %d : %d\n", round, radars.size(), traps_valid.size(), traps.size(), myScore, enemyScore);
		ores.resize(0);
		for (int i = 0; i < height; i++) {
			for (int j = 0; j < width; j++) {
				string s; int n;
				cin >> s >> n;
				m.n[i][j].info.update(s == "?"?-1:stoi(s), n);
				if(m.n[i][j].info.ore > 0){
					ores.push_back(m.n[i][j]);
				}
				m.n[i][j].info.visible = false;
			}
		}
		cin >> entityCount >> radarCooldown >> trapCooldown;
		entities.resize(entityCount);
		auto tmp_traps = traps_valid;
		radars.clear();
		traps.clear();
		traps_valid.clear();
		for (int i = 0; i < entityCount; i++) {
			cin >> entities[i];
			//cerr << entities[i] << endl;
			if(entities[i].type == TYPE_MY_ROBOT){
				my_rbt[entities[i].id % 5].update(entities[i]);
			}else if(entities[i].type == TYPE_OP_ROBOT){
				op_rbt[entities[i].id % 5].update(entities[i]);
			}else if(entities[i].type == TYPE_TRAP){
				traps.insert(P(entities[i].x, entities[i].y));
				if(tmp_traps.count(P(entities[i].x, entities[i].y))){
					traps_valid.insert(P(entities[i].x, entities[i].y));
				}
			}else if(entities[i].type == TYPE_RADAR){
				radars.insert(P(entities[i].x, entities[i].y));
				update_map_visible(P(entities[i].x, entities[i].y));
			}
		}
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
	vector<U::Cartesian<NodeInfo>::Node>::iterator get_nearest_ore(P p, vector<U::Cartesian<NodeInfo>::Node>& ores){
		auto it_nearest = ores.end();
		int min_len = 1e8;
		FORBE(it, ores){
			if(traps.count(it->p) == 0 && op_traps.count(it->p) == 0){
				if( it->info.ore / (it->info.visible?1:1) > 0){
					int len = (2+M::points_length(it->p, p))/4 + (3+it->p.x)/4;
					if(len < min_len){
						it_nearest = it;
						min_len = len;
					}
				}
			}
		}
		return it_nearest;
	}
	vector<U::Cartesian<NodeInfo>::Node>::iterator get_trap_hole(P p, vector<U::Cartesian<NodeInfo>::Node>& ores){
		auto it_nearest = ores.end();
		int max_len = 0;
		FORBE(it, ores){
			if(traps.count(it->p) == 0 && op_traps.count(it->p) == 0 && m.n[it->p.y][it->p.x].info.ore > 0){
				int len = (2+M::points_length(it->p, p))/4;
				if(len > max_len && it->info.ore >= 2 && it->info.hole && it->info.visible){
					it_nearest = it;
					max_len = len;
				}
			}
		}
		return it_nearest;
	}
	void process(void){
		//while(!T->is_time_up()); debug("Time spend: %ld \n", T->get());
		/* Mark the opponent's trap */
		FOR(i, 5){
			Robot *er = &op_rbt[i];
			if(er->move_len == 0 && er->has_item && er->x > 0){ /* It's a bomber */
				bool danger = false, confused = false;
				FOR(n, 5){
					auto p = NEARBY[n].first + P(er->x, er->y);
					if(0<p.x && p.x<width && 0<=p.y && p.y<height && m.n[p.y][p.x].info.new_hole){
						op_traps.insert(p);
						danger = true;
						/* Check if other op near the hole */
						FOR(r, 5){
							if(i == r) continue;
							if(M::points_length(P(op_rbt[r].x, op_rbt[r].y), p) <= 1 &&
								op_rbt[r].move_len == 0 && op_rbt[r].x > 0){
								confused = true;
								break;
							}
						}
					}
					if(confused){ danger = false; break; } /* All holes nearby maybe trap */
				}
				/* Mark all nearby hole as danger */
				if(!danger){
					FOR(n, 5){
						auto p = NEARBY[n].first + P(er->x, er->y);
						if(0<p.x && p.x<width && 0<=p.y && p.y<height && m.n[p.y][p.x].info.hole){
							op_traps.insert(p);
						}
					}
				}
			}
		}
		FOR(i, 5){
			Robot *mr = &my_rbt[i];
			/* update predict ores */
			if(action[i].second == ACT_MINING && mr->mining){
				if(mr->item == ITEM_ORE){
					m.n[action[i].first.y][action[i].first.x].info.pdt_ore--;
				}else{
					m.n[action[i].first.y][action[i].first.x].info.pdt_ore = 0;
				}
			}
			/* update valid traps */
			if(action[i].second == ACT_TRAP_SET && mr->item != ITEM_TRAP){
				if(m.n[action[i].first.y][action[i].first.x].info.pdt_ore > 0){
					traps_valid.insert(action[i].first);
				}
			}
		}
		/* update ores as predict ores */
		ores.clear();
		for (int ii = 0; ii < height; ii++) {
			for (int jj = 0; jj< width; jj++) {
				if(m.n[ii][jj].info.pdt_ore > 0){
					ores.push_back(m.n[ii][jj]);
					((ores.end()-1))->info.ore = ((ores.end()-1))->info.pdt_ore;
				}
			}
		}
		/* remove ores on traps*/
		bool remove_ores;
		do{
			remove_ores = false;
			FORBE(it, ores){
				if(traps.count(it->p) || op_traps.count(it->p)){
					ores.erase(it);
					remove_ores = true;
					break;
				}
			}
		}while(remove_ores);

		/* Dump info */
		FORBE(it, my_rbt){ debug("ID:%d (%2d %2d),  L:%2d,  I:%d,  M:%d\n", it->id, it->x, it->y, it->move_len, it->has_item, it->mining); }
		FORBE(it, op_rbt){ debug("ID:%d (%2d %2d),  L:%2d,  I:%d,  M:%d\n", it->id, it->x, it->y, it->move_len, it->has_item, it->mining); }
		//FORBE(it, op_traps){debug("op_traps: (%2d %2d)\n", it->x, it->y);}

		FOR(i, 5){
			Robot *mr = &my_rbt[i];
			/* update action status */
			if(mr->item == ITEM_NONE){
				if(action[i].second != ACT_MINING && action[i].second != ACT_RADAR_GET){
					action[i].second = ACT_NONE;
				}
			}

			/* Adjust trapping */
			if(action[i].second == ACT_TRAP_SET){
				bool no_resource = true;
				FORBE(ore, ores){
					if(action[i].first == ore->p && ore->info.ore > 1){
						no_resource = false;
						if(M::points_length(ore->p, P(mr->x, mr->y)) <= 5){
							ore->info.ore = 0;
						}
						break;
					}
				}
				if(no_resource || traps.count(action[i].first) || op_traps.count(action[i].first)){
					action[i].second = ACT_NONE;
					auto it = get_trap_hole(P(mr->x, mr->y), ores);
					if(it != ores.end()){
						action[i] = PPI(it->p, ACT_TRAP_SET);
						//it->info.ore = 0;
					}
				}
			}

			/* Adjust radaring */
			if(action[i].second == ACT_RADAR_SET){
				FOR(n, 40){
					P p = NEARBY[n].first + action[i].first;
					if(!traps.count(p) && !op_traps.count(p)){
						action[i] = PPI(p, ACT_RADAR_SET);
						break;
					}
				}
			}
			/* Adjust mining */
			if(action[i].second == ACT_MINING){
				bool no_resource = true;
				FORBE(ore, ores){
					if(action[i].first == ore->p && ore->info.ore > 0){
						no_resource = false;
						ore->info.ore--;
						break;
					}
				}
				//if(round >= 0) debug("Id(%d) no_resource=%d %d (%d %d)\n",i%5, no_resource, op_traps.count(action[i].first), action[i].first.x, action[i].first.y);
				if(no_resource || traps.count(action[i].first) || op_traps.count(action[i].first)){
					action[i].second = ACT_NONE;
					auto it = get_nearest_ore(P(mr->x, mr->y), ores);
					if(it != ores.end()){
						action[i] = PPI(it->p, ACT_MINING);
						it->info.ore--;
					}
				}
			}
			////////////////////////////////////////////////////////////////////////////////////
			/**/
			int ore_count = 0;
			FORBE(it, ores){ ore_count += it->info.ore; }
			if((mr->item == ITEM_NONE || mr->item == ITEM_ORE) && action[i].second != ACT_MINING &&
				radarCooldown <= 1 && (radars.size() < 0 || ore_count < 8) && radars.size() <= 10){
				radarCooldown = 999;
				action[i] = PPI(P(0, mr->y), ACT_RADAR_GET);
			}else if(mr->item == ITEM_RADAR && action[i].second != ACT_RADAR_SET){
				//static vector<P> p = {P(5, 4), P(8, 10), P(13, 6), P(12, 2), P(17, 11), P(19, 4), P(24, 8), P(26, 12), P(27, 2), };
				static vector<P> p = {P(6, 11), P(6, 3), P(10, 7), P(14, 3), P(14, 11), P(19, 7), P(24, 3), P(24, 11), P(26, 7), P(18, 14)};
				if(p.size()){
					action[i] = PPI(p[0], ACT_RADAR_SET);
					p.erase(p.begin());
				}else{
					action[i] = PPI(P(3+(rand()%(width-6)), 3+(rand()%(height-6))), ACT_RADAR_SET);
				}
			}else if((mr->item == ITEM_NONE || mr->item == ITEM_ORE) &&
				trapCooldown <= 1 && ores.size() > 5 && traps_valid.size() < 0 && traps.size() - traps_valid.size() < 1){
				trapCooldown = 999;
				action[i] = PPI(P(0, mr->y), ACT_TRAP_GET);
			}else if(mr->item == ITEM_TRAP && action[i].second != ACT_TRAP_SET){
				auto it = get_trap_hole(P(mr->x, mr->y), ores);
				if(it != ores.end()){
					action[i] = PPI(it->p, ACT_TRAP_SET);
				}else{
					auto it = get_nearest_ore(P(mr->x, mr->y), ores);
					if(it != ores.end()){
						action[i] = PPI(it->p, ACT_TRAP_SET);
						it->info.ore--;
					}else{
						action[i].second == ACT_NONE;
					}
				}
			}else if(mr->item == ITEM_NONE && action[i].second == ACT_NONE){
				auto it = get_nearest_ore(P(mr->x, mr->y), ores);
				if(it != ores.end()){
					action[i] = PPI(it->p, ACT_MINING);
					it->info.ore--;
				}
				if(action[i].second == ACT_NONE){
					FOR(j, 5){
						auto p = NEARBY[j].first + P(mr->x, mr->y);;
						if(0 < p.x && p.x<width && 0<=p.y && p.y < height && !m.n[p.y][p.x].info.hole){
							auto it = radars.begin();
							for(;it!=radars.end();it++){
								if(P(it->x, it->y) == p){ break; }
							}
							if(it == radars.end()){
								action[i] = PPI(p, ACT_MINING);
								m.n[p.y][p.x].info.hole = true;
							}
						}
					}
					if(action[i].second == ACT_NONE){
						auto it = find_if(action.begin(), action.end(), [](auto &act){
							return act.second == ACT_RADAR_SET;
						});
						if(it != action.end()){
							P p;
							do{
								p = P(it->first.x + (rand()%9) - 4, it->first.y + (rand()%9) - 4);
								action[i] = PPI(p, ACT_MINING);
							}while(!(0<p.x && p.x<width && 0<=p.y && p.y<=height));
						}else{
							action[i] = PPI(P(2+(rand()%(width-3)), 1+(rand()%(height-2))), ACT_MINING);
						}
					}

				}
			}else if(mr->item == ITEM_ORE){
				action[i].first = P(0, mr->y);
				action[i].second = ACT_UNLOAD;
			}
			mr->mining = false;
			switch(action[i].second){
				case ACT_TRAP_GET:{
					trapCooldown = 999;
					printf("REQUEST TRAP GET TRAP\n"); break;
				}
				case ACT_TRAP_SET:{
					trapCooldown = 999;
					printf("DIG %d %d TRAP SET\n", action[i].first.x, action[i].first.y); break;
				}
				case ACT_RADAR_GET:{
					radarCooldown = 999;
					printf("REQUEST RADAR GET RADAR\n"); break;
				}
				case ACT_RADAR_SET:{
					printf("DIG %d %d RADAR SET\n", action[i].first.x, action[i].first.y); break;
				}
				case ACT_MINING:{
					if(M::points_length(action[i].first, P(mr->x, mr->y)) <= 1){
						mr->mining = true;
					}
					printf("DIG %d %d MINING\n", action[i].first.x, action[i].first.y); break;
				}
				case ACT_UNLOAD:{
					printf("DIG %d %d UNLOAD\n", 0, action[i].first.y); break;
				}
				case ACT_NONE:
				default:{
					printf("WAIT\n");
					break;
				}
			};
			//printf("WAIT\n");continue;
		}
	}
};
void _D_E_B_U_G_(){
}
int main(int argc, char** argv) {
	_D_E_B_U_G_();
	auto g = G(50);
	for(;;){
		g.round_update();
		g.process();
	}
}


