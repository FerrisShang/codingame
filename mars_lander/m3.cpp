/* https://www.codingame.com/ide/puzzle/mars-lander-episode-3 */
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
	int surfaceN;
	vector<P> land;
	P pos, speed;
	int fuel, rotate, power;
	GCOM::Time *T;
	GCOM(long round_time_max){
		this->round = 0;
		cin >> this->surfaceN; cin.ignore();
		this->land.resize(this->surfaceN);
		FOR(i, this->surfaceN){
			cin >> this->land[i]; cin.ignore();
			cerr << this->land[i] << " ";
		}
		cerr << endl;
		T = new GCOM::Time(round_time_max);
		/* Here is for Initialization input */
	}
	void round_update(void) {
		T->update();
		this->round++;
		action_str = "";
		/* Here is for Input for one game turn */
		cin >> pos >> speed >> fuel >> rotate >> power; cin.ignore();
		rotate = D2R(rotate + 90);
	}
};
class S //simulation
{
	public:
	static constexpr float GRAVITY = 3.711;
	static const int MVY = -40;
	static const int MVX = 20;
	typedef struct {int X; int Y; float vx; float vy; int fuel; float rotate; int power;}state_t;
	state_t state;
	S(int X, int Y, float vx, float vy, int fuel, float rotate, int power){
		state.X = X; state.Y = Y; state.fuel = fuel; state.rotate = rotate;
		state.vx = vx; state.vy = vy; state.power = power;
	}
	S::state_t* update(float rotate, int power){
		if(power - state.power > 1) state.power++;
		else if(power - state.power < -1) state.power--;
		else state.power = power;
		state.fuel -= state.power * 10;
		if(rotate - state.rotate > D2R(15)) state.rotate += D2R(15);
		else if(rotate - state.rotate < -D2R(15)) state.rotate -= D2R(15);
		else state.rotate = rotate;
		float ax = state.power * cos(state.rotate);
		state.X += round(state.vx + ax / 2);
		state.vx += ax;
		float ay = state.power * sin(state.rotate) - GRAVITY;
		state.Y += round(state.vy + ay / 2);
		state.vy += ay;
		//cout << state.X << ' ' << state.Y << ' ' << state.vx << ' ' << state.vy << ' ' << state.power << ' ' << R2D(state.rotate) << endl;
		return &this->state;
	}
	S::state_t* update(float rotate, int power, int t){
		while(t > 0 && (power != state.power || rotate != state.rotate)){ update(rotate, power); t--; }
		state.fuel -= state.power * 10 * t;
		float ax = state.power * cos(state.rotate);
		state.X += round(state.vx*t + t*t*ax / 2);
		state.vx += ax * t;
		float ay = state.power * sin(state.rotate) - GRAVITY;
		state.Y += round(state.vy*t + t*t*ay / 2);
		state.vy += ay * t;
		//cout << state.X << ' ' << state.Y << ' ' << state.vx << ' ' << state.vy << endl;
		return &this->state;
	}
};
class G : public GCOM // game custom
{
	public:
	/* Custom variables */
	static const int MAX_W = 7000, MAX_H = 3000;
	static const int MVX = 20, MVY = -40;
	static constexpr float GRAVITY = -3.711, MAX_R = D2R(15);
	deque<P> landing_path;
	P target_m, target_l, target_r, path_target;
	int land_height[MAX_W];

	G(long round_time_ms_max=100):GCOM(round_time_ms_max){
		/* Custom Initialization */
		int idx = get_landing_zone_Idx(land);
		target_l = land[idx];
		target_r = land[idx+1];
		target_m = (target_l + target_r) / 2;
		FOR(px, MAX_W){
			int i;
			while(i < land.size()-1 && !(land[i].x <= px && px <= land[i+1].x)) i++;
			land_height[px] = land[i].y + (px - land[i].x) * (land[i+1].y - land[i].y) / (land[i+1].x - land[i].x);
		}
	}

	vector<P> get_landing_path(vector<P>& land, P init_point, int scale)
	{
		U::Cartesian<int> c(70, 30);
		P landing_point;
		FOR(i, land.size()-1){
			if(land[i+1].y == land[i].y && land[i+1].x > land[i].x){
				landing_point = P((land[i+1].x + land[i].x) / 2, land[i].y + 100);
			}
			for(int x=land[i].x;x<land[i+1].x;x++){
				int y = land[i].y + (x - land[i].x) * (land[i+1].y - land[i].y) / (land[i+1].x - land[i].x);
				c.n[y/scale][x/scale].info = -1;
			}
		}
		auto r = c.ass(init_point / scale, landing_point / scale,
							[](const U::Cartesian<int>::Node& nd, void *pdata){return int(nd.info < 0);},
							NULL);
		for(int x=1;x<3;x++){
			for(auto& i: r){
				if(i.first.x-x >= 0 && c.n[i.first.y][i.first.x-x].info < 0){ i.first.x+=x; }
				if(i.first.x+x < c.size.x && c.n[i.first.y][i.first.x+x].info < 0){ i.first.x-=x; }
				if(i.first.y-x >= 0 && c.n[i.first.y-x][i.first.x].info < 0){ i.first.y+=x; }
				if(i.first.y+x < c.size.y && c.n[i.first.y+x][i.first.x].info < 0){ i.first.y-=x; }
			}
		}
		vector<P> res(r.size());
		FOR(i, r.size()){ res[i] = r[i].first * scale; }
		for(int x=2;x>0;x--){
			FOR(_, 2){
				auto r = res;
				for(int i=x;i<res.size()-x;i++){
					res[i] = ((r[i-x] + r[i+x]) / 2 + r[i]) / 2;
				}
			}
		}
		return res;
	}
	static int get_landing_zone_Idx(vector<P> &land){
		FOR(i, land.size() - 1){ if(land[i].y == land[i+1].y) return i; }
		return -1;
	}
	inline int cur_height(P& p){ return p.y - land_height[p.x]; }
	inline static bool in_range(int x, int y){return 0<=x && x<G::MAX_W && 0<=y && y<= G::MAX_H;}
	inline static int safe_limit_height(float vy){ return (vy-MVY) / (4+GRAVITY) * (MVY + (vy - MVY) / 2); }  // the higher the better
	inline static int safe_drop_height(float vy){ return (vy-MVY) / (GRAVITY) * (MVY + (vy - MVY) / 2); }  //the lower the better
	inline pair<float, int> is_drop_vectory(P& p, P& speed){
		int value = 1e9;
		pair<float, int> action(0, -1);
		FOR(i, 5){
			S s(pos.x, pos.y, speed.x, speed.y, fuel, rotate, power);
			FOR(j, 100){
				if(target_l.x < s.state.X && s.state.X < target_r.x && s.state.Y < target_m.y && abs(s.state.vx) < 19 && s.state.vy > -38){
					action.first = D2R(90); action.second = i;
					return action;
				}
				s.update(D2R(90), i);
			}
		}
		FOR(i, 5){
			FOR(j, 3){
				float r = D2R(15) * j + D2R(75);
				{
					S s(pos.x, pos.y, speed.x, speed.y, fuel, rotate, power);
					FOR(k, 15){
						s.update(r, i);
						if(target_l.x < s.state.X && s.state.X < target_r.x && s.state.Y < target_m.y && abs(s.state.vx) < 20 && s.state.vy > -40){
							S ss(pos.x, pos.y, speed.x, speed.y, fuel, rotate, power);
							s.update(r, i, k - 2);
							FOR(l, 3){
								if(target_l.x < s.state.X && s.state.X < target_r.x && s.state.Y < target_m.y && abs(s.state.vx) < 19 && s.state.vy > -40){
									action.first = r; action.second = i;
									return action;
								}
								s.update(D2R(90), i);
							}
						}
					}
				}
			}
		}
		return action;
	}
	inline pair<float, int> is_drop_vectory(void){ return is_drop_vectory(pos, speed); }
	inline int state_score(P& pos, P& speed, int fuel){
		const int mvx = 50, mvy = 40 ;
		const int mvx_len = 3000, mvy_len = 300 ;
		P target_pos = path_target;
		int l = min(pos.x, target_m.x), r = max(pos.x, target_m.x);
		P pos_d = target_pos - pos;
		P target_speed(0, -20);
		int tmp = 4;
		if(landing_path.size() >= tmp){
			target_speed.x = (landing_path[tmp].x - pos.x) * 20;
			target_speed.y = (landing_path[tmp].y - pos.y) * 20;
		}
		P speed_d = target_speed - speed;
		return abs(pos_d.y *1) + abs(pos_d.x * 1) + abs(speed_d.y * 1) + abs(speed_d.x * 1);
	}

	void process(void){
		if(round == 1){
			auto path = get_landing_path(land, pos, 100);
			landing_path.insert(landing_path.begin(), path.begin(), path.end());
		}
		int i;
		for(i=0;i<landing_path.size()-1;i++){
			if(M::points_distance(pos, landing_path[i]) < M::points_distance(pos, landing_path[i+1])){ break; }
		}
		path_target = landing_path[i+1];
		FOR(_, i) landing_path.pop_front();
		cerr << "R: " << this->round << " H: " << cur_height(pos) << " T: " << path_target << " | " << landing_path.size() << endl;
		pair<float, int> r = is_drop_vectory();
		if(r.second >= 0){
			cerr << "Drop_vectory: " << int(R2D(r.first) -90) << ' ' << r.second << endl;
			cout << int(R2D(r.first) -90) << ' ' << r.second << endl;
			return;
		}

		int value = 1e9;
		pair<float, int> action;
		FOR(i, 5){
			FOR(j, 6){
				float r = D2R(30) * j;
				{
					S s(pos.x, pos.y, speed.x, speed.y, fuel, rotate, power);
					s.update(r, i, 25);
					P _pos(s.state.X, s.state.Y); P _speed(s.state.vx, s.state.vy);
					auto score = state_score(_pos, _speed, s.state.fuel);
					if(score < value){
						value = score;
						action = pair<float, int>(r, i);
					}
				}
				{
					S s(pos.x, pos.y, speed.x, speed.y, fuel, rotate, power);
					s.update(r, i, 20);
					P _pos(s.state.X, s.state.Y); P _speed(s.state.vx, s.state.vy);
					auto score = state_score(_pos, _speed, s.state.fuel);
					if(score < value){
						value = score;
						action = pair<float, int>(r, i);
					}
				}
				{
					S s(pos.x, pos.y, speed.x, speed.y, fuel, rotate, power);
					s.update(D2R(90), 0);s.update(D2R(90), 0); //while(D2R(90) != s.state.rotate){ s.update(D2R(90) , 0); }
					s.update(r, i, 25);
					P _pos(s.state.X, s.state.Y); P _speed(s.state.vx, s.state.vy);
					auto score = state_score(_pos, _speed, s.state.fuel);
					if(score < value){
						value = score;
						action = pair<float, int>(r, i);
					}
				}
				{
					S s(pos.x, pos.y, speed.x, speed.y, fuel, rotate, power);
					s.update(D2R(90), 0);s.update(D2R(90), 0); //while(D2R(90) != s.state.rotate){ s.update(D2R(90) , 0); }
					s.update(r, i, 20);
					P _pos(s.state.X, s.state.Y); P _speed(s.state.vx, s.state.vy);
					auto score = state_score(_pos, _speed, s.state.fuel);
					if(score < value){
						value = score;
						action = pair<float, int>(r, i);
					}
				}
			}
		}
		cout << int(R2D(action.first) -90) << ' ' << action.second << endl;
		//while(!T->is_time_up());
	}
};
void _D_E_B_U_G_(){
#if 0
	vector<P> p = {P(0, 450),P(300, 750),P(1000, 450),P(1500, 650),P(1800, 850),P(2000, 1950),P(2200, 1850),P(2400, 2000),P(3100, 1800),P(3150, 1550),P(2500, 1600),P(2200, 1550),P(2100, 750),P(2200, 150),P(3200, 150),P(3500, 450),P(4000, 950),P(4500, 1450),P(5000, 1550),P(5500, 1500),P(6000, 950),P(6999, 1750)};
	auto landing_path = get_landing_path(p, P(1, 2500), 100);
	FOR(i, landing_path.size()){
		if(!(i % 8)) cout << endl;
		cerr << landing_path[i] << ",";
	}
	exit(0);
#endif
}
int main(int argc, char** argv) {
	_D_E_B_U_G_();
	auto g = G();
	for(;;){
		g.round_update();
		g.process();
	}
}
