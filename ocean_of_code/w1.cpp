#include <bits/stdc++.h>
#include <sys/time.h>
using namespace std;
#define debug(args...) fprintf(stderr, "-" args)
#define FOR(_I_, _N_) for(int _I_=0;_I_<_N_;_I_++)
#define FORBE(_I_, _T_) for(auto _I_=_T_.begin();_I_!=_T_.end();_I_++)
#define SIZE 15
#define OP(n) (!n)
#define DIST(P1, P2) (abs((P1).y - (P2).y) + abs((P1).x - (P2).x))
#define PT2SECTOR(p) ((p).x/5+(p).y/5*3+1)
class P{
	public: int x, y;
	P(int x=0, int y=0){this->x = x; this->y = y;}
	friend ostream& operator << (ostream& out, const P& p){ out << "(" << p.x << ", " << p.y << ")"; return out; }
	inline bool operator == (const P& p)const{ return this->x == p.x && this->y == p.y; }
	inline P operator + (const P& p){ return P(this->x + p.x, this->y + p.y); }
	inline bool operator < (const P& p)const{ return ((this->x<<16)+this->y) < ((p.x<<16)+p.y); }
};
typedef enum {CR_TORP, CR_SILENCE, CR_SONAR, CR_MINE}charge_t;
typedef struct {
	int round; int myLife; int oppLife; int sonar; P torpedo; char silence; char silence_len;
	char surface; char move; charge_t charge; char sonar_res;
	void reset(int r=-1){
		round = r; sonar = -1; torpedo = P(-1, -1); silence = '\0';
		surface = false; move = '\0'; charge = CR_TORP; sonar_res = -1;
		myLife = 6; oppLife = 6;
	}
} action_t;
map<char, P> c_d2p = { {'N', P(0,-1)}, {'S', P(0,1)}, {'W', P(-1,0)}, {'E', P(1,0)} };
map<char, P> c_rd2p = { {'N', P(0,1)}, {'S', P(0,-1)}, {'W', P(1,0)}, {'E', P(-1,0)} };
map<P, char> c_p2d = { {P(0,-1), 'N'}, {P(0,1), 'S'}, {P(-1,0), 'W'}, {P(1,0), 'E'} };

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
	int width, height, myId;
	int x, y, myLife, oppLife, myLifeDiff, oppLifeDiff;
	int torpedoCooldown, sonarCooldown, silenceCooldown, mineCooldown;
	char grid[SIZE][SIZE];
	vector<action_t> recAction[2];
	action_t action;
	char sonarResult[128], opponentOrders[128];
	GCOM::Time *T;
	GCOM(long round_time_max){
		this->round = 0;
		T = new GCOM::Time(round_time_max);
		/* Here is for Initialization input */
		cin >> width >> height >> myId; cin.ignore();
		FOR(i, height){
			string line; getline(cin, line);
			FOR(j, width){ grid[i][j] = line.c_str()[j]; }
		}
		myLife = oppLife = 6;
		choose_init_pos();
		FOR(i, 2){
			action_t act;
			act.reset();
			recAction[i].push_back(act);
		}
	}
	void round_update(void) {
		debug("round:%d, MyId=%d\n", this->round, this->myId);
		T->update();
		this->round++;
		action.reset(round);
		/* Here is for Input for one game turn */
		action_t op_action;
		op_action.reset(round);
		int oMyLife = myLife, oOppLife = oppLife;
		cin >> x >> y >> myLife >> oppLife >> torpedoCooldown >> sonarCooldown >> \
			silenceCooldown >> mineCooldown; cin.ignore();
		myLifeDiff = myLife - oMyLife;
		oppLifeDiff = oppLife - oOppLife;
		string _______;
		getline(cin, _______); do{
		cerr << "RAW_S: " << sonarResult << endl;
			strcpy(sonarResult, _______.c_str());
			if(!strcmp(sonarResult, "NA")){ break; }
			else{
				op_action.sonar_res = sonarResult[0]=='Y';
				debug("sonarResult: %c\n", sonarResult[0]);
			}
		}while(0);
		getline(cin, _______); do{
			strcpy(opponentOrders, _______.c_str());
			cerr << "RAW_O: " << opponentOrders << endl;
			if(!strcmp(opponentOrders, "NA")){ break; }
			char *token = strtok(opponentOrders, "|");
			while (token != NULL) {
				if(char *sp = strstr(token, "TORPEDO ")){
					sp = strstr(sp+sizeof("TORPEDO ")-1, " ");
					assert(sp);
					*sp = 0;
					op_action.torpedo = P(atoi(token+sizeof("TORPEDO ")-1), atoi(sp+1));
					debug("last TORPEDO :%d %d(round:%d)\n", op_action.torpedo.x, op_action.torpedo.y, op_action.round);
				}else if(char *sp = strstr(token, "MOVE ")){
					sp += sizeof("MOVE ")-1;
					op_action.move = *sp;
					debug("oppMove :%c\n", op_action.move);
				}else if(char *sp = strstr(token, "SURFACE ")){
					sp += sizeof("SURFACE ")-1;
					op_action.surface = atoi(sp);
					debug("surface :sector-%d\n", op_action.surface);
				}else if(char *sp = strstr(token, "SONAR ")){
					sp += sizeof("SONAR ")-1;
					op_action.sonar = atoi(sp);
					debug("sonar :p-%d\n", op_action.sonar);
				}else if(strstr(token, "SILENCE")){
					op_action.silence = 'Y';
					debug("op silence !!\n");
				}
				token = strtok(NULL, "|");
			}
		}while(0);
		op_action.myLife = oppLife; op_action.oppLife = myLife;
		action.myLife = myLife, action.oppLife = oppLife;
		recAction[OP(myId)].push_back(op_action);
		debug("Life: %d(%d), %d(%d)\n", myLife, myLifeDiff, oppLife, oppLifeDiff);
	}
	void choose_init_pos(void){
		while(1){
			x = rand() % SIZE, y = rand() % SIZE;
			if(grid[y][x] == '.'){
				cout << x << ' ' << y << endl;
				break;
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
	char my_visited[SIZE][SIZE];
	inline bool isV(int x, int y){ return x>=0&&y>=0&&x<SIZE&&y<SIZE && my_visited[y][x]==0; }
	inline void dump_grid(void){ FOR(i, SIZE){ FOR(j, SIZE){ debug("%d", my_visited[i][j]); } cerr<<endl; } }
	inline void output(void){
		char action_str[512] = {0};
		if(action.torpedo.x >= 0){
			sprintf(action_str, "%s | TORPEDO %d %d", action_str, action.torpedo.x, action.torpedo.y);
		}
		if(action.sonar > 0){
			sprintf(action_str, "%s | SONAR %d", action_str, action.sonar);
		}
		if(action.silence != '\0'){
			sprintf(action_str, "%s | SILENCE %c %d", action_str, action.silence, action.silence_len);
		}
		if(action.surface){
			sprintf(action_str, "%s | SURFACE", action_str);
		}
		if(action.move != '\0'){
			const char *ps[] = {"TORPEDO", "SILENCE", "SONAR", "MINE"};
			sprintf(action_str, "%s | MOVE %c %s", action_str, action.move, ps[action.charge]);
		}
		puts(&action_str[3]);
	}
	class CPosSim{
		char grid[SIZE][SIZE]; // 0-empty,1-visited,2-island
		inline bool isV(const P &p){ return p.x>=0&&p.y>=0&&p.x<SIZE&&p.y<SIZE&&grid[p.y][p.x]==0; }
		void _avaTor(P target, P cp, set<P>& setp){
			vector<P> pl = {cp+P(1,0), cp+P(-1,0), cp+P(0,1), cp+P(0,-1)};
			for(auto p: pl){
				if(DIST(p, target)<=4 && p.x>=0&&p.y>=0&&p.x<SIZE&&p.y<SIZE&&grid[p.y][p.x]!=2){
					setp.insert(p);
					grid[p.y][p.x] |= 0x80;
					_avaTor(target, p, setp);
				}
			}
		}
		inline void avaTor(P cp, set<P>& setp, P target=P{-1,-1}, set<P>visited=set<P>{}){
			// TODO: Path maybe invalid.
			for(int y=cp.y-4;y<=cp.y+4;y++){
				for(int x=cp.x-4;x<=cp.x+4;x++){
					if(x>=0&&y>=0&&x<SIZE&&y<SIZE&&grid[y][x]!=2){
						setp.insert(P(x,y));
					}
				}
			}
		}
		/*
		inline void avaTor(P target, set<P>& setp, set<P>visited=set<P>{}){
			_avaTor(target, target, setp);
			// clean mark
			for(int y=-4;y<=4;y++){
				for(int x=-4;x<=4;x++){
					if(x>=0&&y>=0&&x<SIZE&&y<SIZE){
						grid[target.y+y][target.x+x] &= ~0x80;
					}
				}
			}
		}
		*/
		public:
		const G *g; int id;
		list<P> psbPos;
		CPosSim(){ FOR(i, SIZE) FOR(j, SIZE){ psbPos.push_back(P(i,j)); } }
		void init(const G *g, int id){
			this->g = g; this->id = id;
			FOR(i, SIZE) FOR(j, SIZE){ if(this->g->grid[i][j]=='x') grid[i][j] = 2; else grid[i][j] = 0; }
			for(auto it=psbPos.begin();it!=psbPos.end();){
				if(grid[it->y][it->x] != 2){ it++; }
				else { it = psbPos.erase(it); }
			}
		}
		void update(void){
			action_t ac = g->recAction[id].back();
			// Filter impossable op position
			if(ac.sonar_res >= 0){
				char req = g->recAction[OP(id)][g->recAction[OP(id)].size()-1].sonar;
				filter_sonar_res(req, ac.sonar_res);
			}
			int lifeDiff = ac.myLife - g->recAction[id][g->recAction[id].size()-2].myLife;
			// TODO: lifeDiff changed only by torpedo, maybe need update on next level..
			if(g->myId == id && g->recAction[id][g->recAction[id].size()-2].surface>0){ lifeDiff++; }
			if(g->myId != id && ac.surface>0){ lifeDiff++; }
			if(lifeDiff < 0){
				debug("Tmp log: lifeDiff:%d\n", lifeDiff);
				filter_hit(ac, g->recAction[OP(id)].back(), lifeDiff);
				if(!psbPos.size()){ dump_grid(); } assert(psbPos.size());
			}
			if(ac.torpedo.x >= 0){ filter_torpedo(ac.torpedo); }
			if(!psbPos.size()){ dump_grid(); cerr << ac.torpedo << endl; } assert(psbPos.size());
			if(ac.surface > 0){ filter_surface(ac.surface); }
			if(!psbPos.size()){ dump_grid(); cerr << ac.surface << endl; } assert(psbPos.size());
			if(ac.silence != '\0'){ filter_silence(); }
			if(!psbPos.size()){ dump_grid(); } assert(psbPos.size());
			if(ac.move != '\0') filter_move(ac.move);
			if(!psbPos.size()){ dump_grid(); cerr << ac.move << endl; } assert(psbPos.size());
			if(psbPos.size() == 1){ update_visited_path(g->recAction[id]); }
			dump();
		}
		void filter_torpedo(const P& p){
			set<P> setp; avaTor(p, setp);
			for(auto it=psbPos.begin();it!=psbPos.end();){
				if(setp.count(*it)){ it++; }
				else { it = psbPos.erase(it); }
			}
		}
		void filter_surface(int n){
			assert(1<=n&&n<10);
			const P pm[10] = {{0,0},{0,0},{5,0},{10,0},{0,5},{5,5},{10,5},{0,10},{5,10},{10,10}};
			for(auto it=psbPos.begin();it!=psbPos.end();){
				if(!(it->x<pm[n].x||it->x>pm[n].x+4||it->y<pm[n].y||it->y>pm[n].y+4)){ it++; }
				else { it = psbPos.erase(it); }
			}
			FOR(i, SIZE) FOR(j, SIZE){ if(this->g->grid[i][j]=='x') grid[i][j] = 2; else this->grid[i][j] = 0; }
		}
		void filter_silence(void){
			set<P> new_pos;
			FORBE(it, psbPos){
				for(int x=1;x<=4;x++){
					auto p = P(it->x+x,it->y);
					if(this->isV(p)){ new_pos.insert(p); }else{ break; }
				}
				for(int x=1;x<=4;x++){
					auto p = P(it->x-x,it->y);
					if(this->isV(p)){ new_pos.insert(p); }else{ break; }
				}
				for(int y=1;y<=4;y++){
					auto p = P(it->x,it->y+y);
					if(this->isV(p)){ new_pos.insert(p); }else{ break; }
				}
				for(int y=1;y<=4;y++){
					auto p = P(it->x,it->y-y);
					if(this->isV(p)){ new_pos.insert(p); }else{ break; }
				}
			}
			psbPos.clear();
			FORBE(it, new_pos){
				psbPos.push_back(*it);
			}
		}
		void filter_move(char move){
			assert(c_d2p.count(move));
			for(auto it=psbPos.begin();it!=psbPos.end();){
				P p = c_d2p[move] + *it;
				if(this->isV(p)){ *it = p; it++; }
				else{ it = psbPos.erase(it); }
			}
		}
		void filter_sonar_res(int n, char res){
			assert(1<=n&&n<10&&res>=0);
			const P pm[10] = {{0,0},{0,0},{5,0},{10,0},{0,5},{5,5},{10,5},{0,10},{5,10},{10,10}};
			for(auto it=psbPos.begin();it!=psbPos.end();){
				if((res>0) ^ (it->x<pm[n].x||it->x>pm[n].x+4||it->y<pm[n].y||it->y>pm[n].y+4)){ it++; }
				else { it = psbPos.erase(it); }
			}
		}
		void update_visited_path(const vector<action_t> &act){
			assert(psbPos.size()==1);
			P p = psbPos.back();
			grid[p.y][p.x] = 1;
			for(auto it=act.crbegin();it!=act.crend();it++){
				if(it->move > '\0'){
					p = c_rd2p[it->move] + p;
					if(grid[p.y][p.x] == 0){ grid[p.y][p.x] = 1; }
					else if(grid[p.y][p.x] == 1){ break; }
					else { debug("ID: %d. Error: (%d,%d), %d\n", id, p.x, p.y, grid[p.y][p.x]); assert(0); }
				}else{ break; }
			}
			//dump_grid();
		}
		void filter_hit(const action_t& at_me, const action_t& at_op, int lifeDiff){
			if(at_me.torpedo.x>=0 && at_op.torpedo.x>=0){ return; } // Both fire
			P p = at_me.torpedo.x>=0?at_me.torpedo:at_op.torpedo;
			if(lifeDiff == -2){
				psbPos.clear(); psbPos.push_back(p);
			}else if(lifeDiff == -1){
				for(auto it=psbPos.begin();it!=psbPos.end();){
					debug("Tmp_log: p(%d %d) T:(%d %d) : %d %d\n", it->x, it->y, p.x, p.y,
							!(it->x<p.x-1||it->x>p.x+1||it->y<p.y-1||it->y>p.y+1),
							(it->x!=p.x&&it->y!=p.y));
					if(!(it->x<p.x-1||it->x>p.x+1||it->y<p.y-1||it->y>p.y+1) && (it->x!=p.x||it->y!=p.y)){ it++; }
					else { it = psbPos.erase(it); }
				}
			}else{
				debug("meT:(%d,%d) opT:(%d,%d) me_surface(%d) lifeDiff:%d\n",
					at_me.torpedo.x, at_me.torpedo.y, at_op.torpedo.x, at_op.torpedo.y,
					at_me.surface, lifeDiff); assert(0);
			}
		}
		void hit_target(const P& p, int x){
			if(x == 2){
				for(auto it=psbPos.begin();it!=psbPos.end();){
					if(it->x==p.x&&it->y<p.y){ it++; }
					else { it = psbPos.erase(it); }
				}
			}else if(x == 1){
				for(auto it=psbPos.begin();it!=psbPos.end();){
					if(!(it->x<p.x-1||it->x>p.x+1||it->y<p.y-1||it->y>p.y+1) \
									&& (it->x!=p.x&&it->y!=p.y)){ it++; }
					else { it = psbPos.erase(it); }
				}
			}else if(x == 0){
				for(auto it=psbPos.begin();it!=psbPos.end();){
					if(it->x<p.x-1||it->x>p.x+1||it->y<p.y-1||it->y>p.y+1){ it++; }
					else { it = psbPos.erase(it); }
				}
			}
		}
		void dump(void){
			debug("psbPos: %lld\n", psbPos.size());
			FORBE(i, psbPos){ debug("(%d,%d) ", i->x, i->y); } debug("\n");
		}
		void dump_grid(void){debug("ID: %d\n", id); FOR(i, SIZE){ FOR(j, SIZE){ debug("%d", grid[i][j]); } cerr<<endl; } }
		void simReset(P p){}
		void simMove(P p){}
	};

	inline void surface(void){
		FOR(i, SIZE) FOR(j, SIZE){
			if(my_visited[i][j]==1) my_visited[i][j] = 0;
		}
		my_visited[y][x]=1;
	}
	G(long round_time_ms_max=10):GCOM(round_time_ms_max){
		/* Custom Initialization */
		FOR(i, SIZE) FOR(j, SIZE){
			if(i==y&&x==j){ my_visited[i][j] = 1; }
			else if(grid[i][j] == 'x'){ my_visited[i][j] = 2; }
			else{ my_visited[i][j] = 0; }
		}
		mySim.init(this, myId), opSim.init(this, OP(myId));
	}
	CPosSim mySim, opSim;
	void nextMove(void) {
		const vector<P> ps = {{1,0}, {-1,0}, {0,1}, {0,-1}, };
		const char d[4] = {'E', 'W', 'S', 'N'};
		debug("I'm here (%d,%d)\n", x, y);
		int nx = -1, ny = -1;
		if(silenceCooldown){ action.charge = CR_SILENCE; }
		else if(torpedoCooldown){ action.charge = CR_TORP; }
		else if(sonarCooldown){ action.charge = CR_SONAR; }
		if(!sonarCooldown && opSim.psbPos.size() > 5){
			action.sonar = PT2SECTOR(opSim.psbPos.back());
		}
		if(!torpedoCooldown && opSim.psbPos.size() < 5){
			FORBE(it, opSim.psbPos){
				 if(DIST(*it, P(x,y)) <= 5){
					const vector<P> pos = {*it+P(0,0),*it+P(1,0),*it+P(-1,0),*it+P(0,1),*it+P(0,-1)};
					for(auto p: pos){
						int d = DIST(p, P(x,y));
						if(2 < d && d <= 4){ action.torpedo = p; break; }
					}
				 }
				 if(action.torpedo.x >= 0){ break; }
			}
		}
		FOR(i, 4){
			nx = ps[i].x+x, ny = ps[i].y+y;
			if(isV(nx, ny)){
				if(!silenceCooldown && \
						(mySim.psbPos.size() < 10 || myLifeDiff<0)){
					action.silence = d[i];
					action.silence_len = 1;
				}else{
					action.move = d[i];
				}
				my_visited[ny][nx]=1;
				return;
			}
		}
		action.surface = PT2SECTOR(P(x,y));
		surface();
		debug("My surface!\n");
	}
#if 0
#define P_PSB_CNT_LEVEL 3
	void nextMove(void) {
		const vector<P> ps = {{1,0}, {-1,0}, {0,1}, {0,-1}, };
		const char d[4] = {'E', 'W', 'S', 'N'};
		debug("I'm here (%d,%d)\n", x, y);
		int nx = -1, ny = -1, max_dis=-1, min_dis=10000, max_dp, min_dp;
		vector<int> validMove;
		assert(opPos.psbPos.size());
		FOR(i, 4){
			nx = ps[i].x+x, ny = ps[i].y+y;
			if(isMV(nx, ny)){
				validMove.push_back(i);
				if(opPos.psbPos.size() < P_PSB_CNT_LEVEL){
					P p = *next(opPos.psbPos.begin(), opPos.psbPos.size()/2);
					if(abs(p.x-nx)+abs(p.y-ny) > max_dis){
						max_dis = abs(p.x-nx)+abs(p.y-ny);
						max_dp = i;
					}
					if(abs(p.x-nx)+abs(p.y-ny) < min_dis){
						min_dis = abs(p.x-nx)+abs(p.y-ny);
						min_dp = i;
					}
				}
			}
		}
		if(validMove.size()){
			int choose = min_dp;
			if(!(opPos.psbPos.size() < P_PSB_CNT_LEVEL)){
				choose = validMove[rand()%validMove.size()];
			}else if(torpedoCooldown || strstr(action_str, "TORPEDO")){
				choose = max_dp;
			}
			if(strlen(action_str)){
				sprintf(action_str, "%s | MOVE %c TORPEDO", action_str, d[choose]);
			}else{
				sprintf(action_str, "MOVE %c TORPEDO", d[choose]);
			}
			debug("Move to (%d,%d)\n", ps[choose].x+x, ps[choose].y+y);
			my_visited[ps[choose].y+y][ps[choose].x+x] = 1;
		}else{
			// no where to move
			strcpy(action_str, "SURFACE");
			surface();
		}
	}
	void attack(void) {
		if(torpedoCooldown) return;
		if(opPos.psbPos.size() == 1){
			auto target = *opPos.psbPos.begin();
			if(abs(target.x-x)+abs(target.y-y) <= 4){
				sprintf(action_str, "TORPEDO %d %d", target.x, target.y);
			}else if(abs(target.x-x)+abs(target.y-y) == 5){
				for(int i=-1;i<=1;i++){ for(int j=-1;j<=1;j++){
					if(abs(target.x+i-x)+abs(target.y+j-y) == 4){
						sprintf(action_str, "TORPEDO %d %d", target.x+i, target.y+j);
						break;
					}
				}}
			}
		}else if(opPos.psbPos.size() < P_PSB_CNT_LEVEL){
			vector<P> ps;
			FORBE(it, opPos.psbPos){
				if(abs(it->x-x)+abs(it->y-y) < 4){
					if(abs(it->x-x)+abs(it->y-y) >= 2){
						ps.push_back(P(it->x, it->y));
					}
				}
			}
			if(ps.size()){
				sprintf(action_str, "TORPEDO %d %d", ps[ps.size()/2].x, ps[ps.size()/2].y);
			}
		}
	}
#endif
	void process(void){
		opSim.update();
		//while(0 && !T->is_time_up()); debug("Time spend: %ld \n", T->get());
		nextMove();
		recAction[myId].push_back(action);
		mySim.update();
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
		debug("Time speed: %ld\n", g.T->get());
		g.output();
	}
}

