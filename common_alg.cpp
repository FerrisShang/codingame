#include <iostream>
#include <stdio.h>
#include <sys/time.h>
#include <cmath>
#include <algorithm>
#include <vectory>
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
	friend ostream& operator << (ostream& out, P& p){ out << "(" << p.x << ", " << p.y << ")"; return out; }
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
		inline long get(void){ return get_time() - time_rec; } // Time speed
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
