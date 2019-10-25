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
#define PPI pair<P, int>

#define PLAYER_NUM          3
#define LOOTER_RADIUS       400
#define SKILL_RANGE         2000
#define SKILL_RADIUS        1000
#define SKILL_DURATION      3
#define MAX_THROTTLE        300
#define TANKER_THROTTLE     500
#define TYPE_RAPER          0
#define TYPE_DESTROYER      1
#define TYPE_DOOF           2
#define TYPE_TANKER         3
#define TYPE_WRECK          4
#define MASS_RAPER          0.5
#define MASS_DESTROYER      1.5
#define MASS_DOOF           1
#define FRICTION_TANKER     2.5
#define FRICTION_RAPER      0.5
#define FRICTION_DESTROYER  1.5
#define FRICTION_DOOF       1
#define FRICTION_TANKER     2.5

class P{
	public: int x, y;
	P(int x=0, int y=0){this->x = x; this->y = y;}
	friend ostream& operator << (ostream& out, const P& p){ out << "(" << p.x << ", " << p.y << ")"; return out; }
	friend istream& operator >> (istream& in, P& p){ in >> p.x; in >> p.y; return in;}
	inline bool operator == (const P& p)const{ return this->x == p.x && this->y == p.y; }
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
	static int length_about(float length, float match_length, float deviation){return length >=match_length - deviation and length <  match_length + deviation;}
	static int length_about(float length, float match_length){return M::length_about(length, match_length, 3);}
};
class U // utils
{
	public:
};
class Unit{
	public:
	void in(void){ cin >> unitId >> unitType >> playerId >> mass >> radius >> \
			pos.x >> pos.y >> speed.x >> speed.y >> extra >> extra2; cin.ignore(); }
	int unitId, unitType, playerId;
	float mass;
	int radius;
	P pos, speed;
	int extra, extra2;
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
	string action_str;
	GCOM::Time *T;
	int max_rad, water_rad;
	int rage_skill_reaper, rage_skill_destroyer, rage_skill_doof;
	int score[PLAYER_NUM], rage[PLAYER_NUM], unitCount;
	vector<Unit> units;
	vector<Unit> raper;
	vector<Unit> destroyer;
	vector<Unit> doof;
	vector<Unit> tanker;
	vector<Unit> wreck;
	GCOM(long round_time_max){
		this->round = 0;
		T = new GCOM::Time(round_time_max);
		/* Here is for Initialization input */
		max_rad = 6000;
		water_rad = 3000;
		rage_skill_reaper = 30;
		rage_skill_destroyer = 60;
		rage_skill_doof = 30;
		raper.resize(PLAYER_NUM);
		destroyer.resize(PLAYER_NUM);
		doof.resize(PLAYER_NUM);
	}
	void round_update(void) {
		T->update();
		this->round++;
		action_str = "";
		/* Here is for Input for one game turn */
		units.resize(0);
		tanker.resize(0);
		wreck.resize(0);
		FOR(i, 3){ cin >> score[i]; cin.ignore(); }
		FOR(i, 3){ cin >> rage[i]; cin.ignore(); }
		cin >> unitCount; cin.ignore();
		FOR(i, unitCount){
			Unit unit;
			unit.in();
			if(unit.unitType == TYPE_RAPER){ raper[unit.playerId] = unit; }
			else if(unit.unitType == TYPE_DESTROYER){ destroyer[unit.playerId] = unit; }
			else if(unit.unitType == TYPE_DOOF){ doof[unit.playerId] = unit; }
			else if(unit.unitType == TYPE_TANKER){ tanker.push_back(unit); }
			else if(unit.unitType == TYPE_WRECK){ wreck.push_back(unit); }
			units.push_back(unit);
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
	void _round_update(void){
		debug("Score  %2d:%2d:%2d\n", score[0], score[1], score[2]);
	}
	void process(void){
		_round_update();
		//while(!T->is_time_up()); debug("Time spend: %ld \n", T->get());
		if(wreck.size() > 0)
			printf("%d %d %d ©»|£àO¡ä|©¿\n", wreck[0].pos.x, wreck[0].pos.y, 300);
		else
			printf("WAIT ¡ð|£þ|_ =3\n");
		printf("%d %d %d ¦Õ(¨R¦Ø¨Q*)¨s\n", raper[2].pos.x, raper[2].pos.y, 300);
		printf("%d %d %d ¦Õ(¨R¦Ø¨Q*)¨s\n", raper[2].pos.x, raper[2].pos.y, 300);
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
