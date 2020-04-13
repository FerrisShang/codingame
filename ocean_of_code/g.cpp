/* https://www.codingame.com/ide/challenge/ocean-of-code */
#include <bits/stdc++.h>
#include <sys/time.h>
//#define __DEBUG__
using namespace std;
#define debug(args...) fprintf(stderr, "-" args)
#define FOR(_I_, _N_) for(int _I_=0;_I_<_N_;_I_++)
#define FORBE(_I_, _T_) for(auto _I_=_T_.begin();_I_!=_T_.end();_I_++)
#define SIZE 15
#define OP(n) (!n)
#define DIST(P1, P2) (abs((P1).y - (P2).y) + abs((P1).x - (P2).x))
#define BHURT(P1, P2) ((P1)==(P2)?2:(abs((P1).y-(P2).y)>1||abs((P1).x-(P2).x)>1)?0:1)
#define PT2SECTOR(p) ((p).x/5+(p).y/5*3+1)
class P{
	public: int x, y; float e;
			P(int x=0, int y=0, float e=1.0){this->x = x; this->y = y; this->e = e; }
			friend ostream& operator << (ostream& out, const P& p){ out << "(" << p.x << ", " << p.y << ")"; return out; }
			inline bool operator == (const P& p)const{ return this->x == p.x && this->y == p.y; }
			inline P operator + (const P& p){
				return P(this->x + p.x, this->y + p.y, abs(this->e-1)>abs(p.e)?this->e:p.e);
			}
			inline bool operator < (const P& p)const{ return ((this->x<<16)+this->y) < ((p.x<<16)+p.y); }
};
typedef enum {CR_TORP, CR_SILENCE, CR_SONAR, CR_MINE}charge_t;
typedef enum {AC_MOVE, AC_SILENCE, AC_SURFACE, AC_TORP, AC_SONAR, AC_MINE, AC_TRIGGER}subact_t;
typedef struct {
	int round; int myLife; int oppLife; int sonar; P torpedo; char silence; char silence_len;
	char surface; char move; charge_t charge; char sonar_res; char mine; P trigger; P pos;
	char self_hurt_torp; char self_hurt_mine; char self_hurt_sum; char myLifeDiff; char oopLifeDiff;
	list<subact_t> subact;

	void reset(int r=-1){
		round = r; sonar = -1; torpedo = P(-1, -1); silence = '\0';
		surface = false; move = '\0'; charge = CR_TORP; sonar_res = -1;
		mine = '\0'; trigger = P(-1,-1); myLife = 6; oppLife = 6;
		pos = {-1, -1}; self_hurt_torp = -1; self_hurt_mine = -1; int self_hurt_sum = -1;
		myLifeDiff = 0; oopLifeDiff = 0;
		subact.clear();
	}
	void update(void){
		if(torpedo.x>=0){
			if(pos.x>=0){ self_hurt_torp = BHURT(torpedo, pos); }
			else{ self_hurt_torp = -1; }
		}else{

			self_hurt_torp = 0;
		}
		if(trigger.x>=0){
			if(pos.x>=0){ self_hurt_mine = BHURT(trigger, pos); }
			else{ self_hurt_mine = -1; }
		}else{

			self_hurt_mine = 0;
		}
		if(self_hurt_torp >= 0 && self_hurt_mine >= 0){
			self_hurt_sum = self_hurt_torp + self_hurt_mine + surface;
		}else{
			self_hurt_sum = -1;
		}
	}
} action_t;
map<char, P> c_d2p = { {'N', P(0,-1)}, {'S', P(0,1)}, {'W', P(-1,0)}, {'E', P(1,0)} };
map<char, P> c_rd2p = { {'N', P(0,1)}, {'S', P(0,-1)}, {'W', P(1,0)}, {'E', P(-1,0)} };
map<P, char> c_p2d = { {P(0,-1), 'N'}, {P(0,1), 'S'}, {P(-1,0), 'W'}, {P(1,0), 'E'} };
vector<P> c_4d = { {P(0,-1)}, {P(0,1)}, {P(-1,0)}, {P(1,0)} };

class GCOM // game common environment
{
	class Time
	{
		public: long max_time, time_rec;
				Time(int max_time=100){this->max_time = max_time; this->time_rec = get_time();}//srand(time_rec);
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
	action_t op_action;
	char sonarResult[128], opponentOrders[128];
	GCOM::Time *T;
	GCOM(long round_time_max){
		this->round = 0;
		/* Here is for Initialization input */
		cin >> width >> height >> myId; cin.ignore();
		FOR(i, height){
			string line; getline(cin, line);
			FOR(j, width){ grid[i][j] = line.c_str()[j]=='x'?'x':'\0'; }
		}
		myLife = oppLife = 6;
		T = new GCOM::Time(round_time_max);
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
		/* Here is for Input for one game turn */
		action.reset(round);
		op_action.reset(round);
		int oMyLife = myLife, oOppLife = oppLife;
		cin >> x >> y >> myLife >> oppLife >> torpedoCooldown >> sonarCooldown >> \
			silenceCooldown >> mineCooldown; cin.ignore();
		myLifeDiff = myLife - oMyLife;
		oppLifeDiff = oppLife - oOppLife;
		string _______;
		getline(cin, _______); do{
			strcpy(sonarResult, _______.c_str());
			cerr << "RAW_S: " << sonarResult << endl;
			if(!strcmp(sonarResult, "NA")){ break; }
			else{
				op_action.sonar_res = sonarResult[0]=='Y'; // sonar_res not in subact.
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
					op_action.subact.push_back(AC_TORP);
					debug("last TORPEDO :%d %d(round:%d)\n", op_action.torpedo.x, op_action.torpedo.y, op_action.round);
				}else if(char *sp = strstr(token, "TRIGGER ")){
					sp = strstr(sp+sizeof("TRIGGER ")-1, " ");
					assert(sp);
					*sp = 0;
					op_action.trigger = P(atoi(token+sizeof("TRIGGER ")-1), atoi(sp+1));
					op_action.subact.push_back(AC_TRIGGER);
					debug("last TRIGGER :%d %d(round:%d)\n", op_action.trigger.x, op_action.trigger.y, op_action.round);
				}else if(char *sp = strstr(token, "MOVE ")){
					sp += sizeof("MOVE ")-1;
					op_action.move = *sp;
					op_action.subact.push_back(AC_MOVE);
					debug("oppMove :%c\n", op_action.move);
				}else if(char *sp = strstr(token, "SURFACE ")){
					sp += sizeof("SURFACE ")-1;
					op_action.surface = atoi(sp);
					op_action.subact.push_back(AC_SURFACE);
					debug("surface :sector-%d\n", op_action.surface);
				}else if(char *sp = strstr(token, "SONAR ")){
					sp += sizeof("SONAR ")-1;
					op_action.sonar = atoi(sp);
					op_action.subact.push_back(AC_SONAR);
					debug("sonar :p-%d\n", op_action.sonar);
				}else if(strstr(token, "SILENCE")){
					op_action.silence = 'Y';
					op_action.subact.push_back(AC_SILENCE);
					debug("op silence !!\n");
				}else if(strstr(token, "MINE")){
					op_action.mine = 'Y';
					op_action.subact.push_back(AC_MINE);
					debug("op mine !!\n");
				}
				token = strtok(NULL, "|");
			}
		}while(0);
		op_action.myLife = oppLife; op_action.oppLife = myLife;
		action.myLife = myLife, action.oppLife = oppLife;
		action.pos = P(x, y);
		op_action.update(); recAction[OP(myId)].push_back(op_action);
		debug("Life: %d(%d), %d(%d)\n", myLife, myLifeDiff, oppLife, oppLifeDiff);
	}

	void avaTor(P cp, set<P>& setp){
		vector<P> pos {cp};
		bfs(pos, grid, 4);
		FORBE(it, pos){ setp.insert(*it); }
	}

	static void bfs(vector<P> &res, char map[SIZE][SIZE], int dist_limit=64){// empty if map[x][x] == 0
		assert(res.size()==1);
		char mark[SIZE][SIZE]={0};
		vector<int> dist {dist_limit};
		FOR(idx, res.size()){
			P p = res[idx];
			mark[p.y][p.x] = 1;
			vector<P> pl = {p+P(1,0), p+P(-1,0), p+P(0,1), p+P(0,-1)};
			for(auto i: pl){
				if(i.y>=0&&i.x>=0&&i.y<SIZE&&i.x<SIZE){
					if(!mark[i.y][i.x] && !map[i.y][i.x] && dist[idx]){
						res.push_back(i);
						mark[i.y][i.x] = 1;
						dist.push_back(dist[idx]-1);
					}
				}
			}
			dist_limit--;
		}
	}
	static vector<pair<int, char>> move_rand_safe(P p, char map[SIZE][SIZE]){// empty if map[x][x] == 0
		vector<P> pl = {p+P(1,0), p+P(-1,0), p+P(0,1), p+P(0,-1)};
		const char d[4] = {'E', 'W', 'S', 'N'};
		vector<pair<int, char>> res;
		int best[4] = {0};
		FOR(i, 4){
			if(pl[i].x>=0&&pl[i].y>=0&&pl[i].x<SIZE&&pl[i].y<SIZE&&map[pl[i].y][pl[i].x]==0){
				vector<P> pos {pl[i]};
				map[pl[i].y][pl[i].x] |= 0x80;
				bfs(pos, map);
				map[pl[i].y][pl[i].x] &= ~0x80;
				best[i] = -(pos.size()-1);
			}
			res.push_back(pair<int,char>(best[i], d[i]));
		}
		return res;
	}
	void choose_init_pos(void){
		int max_cnt = 0;
		while(T->get() < 100){
			x = rand() % SIZE, y = rand() % SIZE;
			if(grid[y][x]){ continue; }
			vector<P> pos { P(x, y) };
			bfs(pos, grid);
			//cerr << pos.size() << endl;
			if(pos.size() > max_cnt){
				max_cnt = pos.size();
			}
		}
		cout << x << ' ' << y << endl;
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
		set<P> minePos;
		inline bool isV(int x, int y){ return x>=0&&y>=0&&x<SIZE&&y<SIZE && my_visited[y][x]==0; }
		inline void dump_grid(void){ FOR(i, SIZE){ FOR(j, SIZE){ debug("%d", my_visited[i][j]); } cerr<<endl; } }
		inline void output(void){
			char action_str[512] = {0};
			FORBE(it, action.subact){
				if(*it==AC_SONAR && action.sonar >= 0){
					sprintf(action_str, "%s | SONAR %d", action_str, action.sonar);
					debug("My sonar %d!\n", action.sonar);
				}else if(*it==AC_TORP && action.torpedo.x>=0){
					sprintf(action_str, "%s | TORPEDO %d %d", action_str, action.torpedo.x, action.torpedo.y);
					debug("My torpedo %d %d!\n", action.torpedo.x, action.torpedo.y);
				}else if(*it==AC_SILENCE && action.silence != '\0'){
					sprintf(action_str, "%s | SILENCE %c %d", action_str, action.silence, action.silence_len);
					debug("My silence %c %d!\n", action.silence, action.silence_len);
				}else if(*it==AC_SURFACE && action.surface){
					sprintf(action_str, "%s | SURFACE", action_str);
					debug("My surface!\n");
				}else if(*it==AC_MINE && action.mine){
					sprintf(action_str, "%s | MINE %c", action_str, action.mine);
					debug("My mine %c!\n", action.mine);
					minePos.insert(P(x,y)+c_d2p[action.mine]);
				}else if(*it==AC_TRIGGER && action.trigger.x>=0){
					sprintf(action_str, "%s | TRIGGER %d %d", action_str, action.trigger.x, action.trigger.y);
					debug("My trigger %d %d!\n", action.trigger.x, action.trigger.y);
					minePos.erase(action.trigger);
				}else if(*it==AC_MOVE && action.move != '\0'){
					const char *ps[] = {"TORPEDO", "SILENCE", "SONAR", "MINE"};
					sprintf(action_str, "%s | MOVE %c %s", action_str, action.move, ps[action.charge]);
					debug("My move %c %s!\n", action.move, ps[action.charge]);
				}else{ cerr << *it << endl; assert(0); }
			}
			debug("My act: %s\n", &action_str[3]);
			puts(&action_str[3]);
		}
		class CPosSim{
			char grid[SIZE][SIZE]; // 0-empty,1-visited,2-island
			inline bool isV(const P &p){ return p.x>=0&&p.y>=0&&p.x<SIZE&&p.y<SIZE&&grid[p.y][p.x]==0; }
			public:
			const G *g; int id;
			const CPosSim *opSim;
			list<P> psbPos, noSlcPos;
			list<P> prev_psbPos;
			list<P> *opPsbPos;
			set<P> minePos;
			list<P> simPos;
			int lastSonar, lastTorp, lastSilence, lastSurface, lastMine, mineCount;
			CPosSim(){
				FOR(i, SIZE) FOR(j, SIZE){ psbPos.push_back(P(i,j)); noSlcPos.push_back(P(i,j)); }
				lastSonar = lastTorp = lastSilence = lastSurface = lastMine = mineCount = 0;
			}
			void init(const G *g, int id, CPosSim &opSim){
				this->g = g; this->id = id; this->opSim = &opSim; this->opPsbPos = &opSim.psbPos;
				FOR(i, SIZE) FOR(j, SIZE){ if(this->g->grid[i][j]=='x') grid[i][j] = 2; else grid[i][j] = 0; }
				for(auto it=psbPos.begin();it!=psbPos.end();){
					if(grid[it->y][it->x] != 2){ it++; }
					else { it = psbPos.erase(it); }
				}
			}
			void update(void){
				auto crac = g->recAction[id].end()-1;
				auto opac = g->recAction[OP(id)].end()-1;
				prev_psbPos = psbPos;
				// yoyoyo~
				if(g->round > 1){
					FORBE(it, psbPos){ it->e = sqrt(it->e); }
					if(!crac->silence && crac->move && (crac-1)->move && !(crac-1)->silence){
						if(crac->move != (crac-1)->move){
							P good[2];
							if(crac->move == 'N' || crac->move == 'S'){ good[0] = P(-1, 0); good[1] = P(1, 0); }
							else{ good[0] = P(0, -1); good[1] = P(0, 1); }
							FORBE(it, psbPos){
								if(!isV(*it+good[0]) || !isV(*it+good[1])){
									it->e *= 1.6;
								}
							}
						}
					}else{
						FORBE(it, psbPos){ it->e = 1; }
					}
				}
				// Filter impossable op position

				// process last round result(ONLY myId needed)
				if(crac->sonar_res >= 0){
					filter_sonar_res(&psbPos, g->recAction[OP(id)].back().sonar, crac->sonar_res);
					if(!psbPos.size()){
						dump_grid();
						debug("Sector:%d, R:%d\n", g->recAction[OP(id)].back().sonar, crac->sonar_res);
					}
					assert(psbPos.size());
				}
				if(g->myId == OP(id)){
					//Life Diff OP(MyID)
					do{
						if(g->oppLifeDiff == 0){
							if(opac->torpedo.x>=0){
								for(auto it=psbPos.begin();it!=psbPos.end();){
									if(BHURT(*it, opac->torpedo)==0){ it++; } else { it = psbPos.erase(it); }
								}
							}
							if(opac->trigger.x>=0){
								for(auto it=psbPos.begin();it!=psbPos.end();){
									if(BHURT(*it, opac->trigger)==0){ it++; } else { it = psbPos.erase(it); }
								}
							}
						}
						if(crac->self_hurt_sum < 0){ break; }
						char op_hit=-g->oppLifeDiff-crac->self_hurt_sum;
						P p;
						if(opac->torpedo.x>=0 && opac->trigger.x<0){
							p = opac->torpedo;
						}else if(opac->torpedo.x<0 && opac->trigger.x>=0){
							p = opac->trigger;
						}else{ break; }
						assert(op_hit <= 2);
						int PsbPosSize = psbPos.size();
						if(op_hit==2){ psbPos.clear(); psbPos.push_back(p); } // headshot..
						else if(op_hit==1){
							for(auto it=psbPos.begin();it!=psbPos.end();){
								if(BHURT(*it, p)==1){ it++; } else { it = psbPos.erase(it); }
							}
						}else if(op_hit==0){
							for(auto it=psbPos.begin();it!=psbPos.end();){
								if(BHURT(*it, p)==0){ it++; } else { it = psbPos.erase(it); }
							}
						}
						if(PsbPosSize != psbPos.size()){ debug("HIT-OP(MyID):%d ",op_hit); dump(); }
						if(!psbPos.size()){ debug("op_hit: %d\n", op_hit); } assert(psbPos.size());
					}while(0);
					//Life Diff OP(MyID) - noSlcPos
					do{
						if(g->oppLifeDiff == 0){
							if(opac->torpedo.x>=0){
								for(auto it=noSlcPos.begin();it!=noSlcPos.end();){
									if(BHURT(*it, opac->torpedo)==0){ it++; } else { it = noSlcPos.erase(it); }
								}
							}
							if(opac->trigger.x>=0){
								for(auto it=noSlcPos.begin();it!=noSlcPos.end();){
									if(BHURT(*it, opac->trigger)==0){ it++; } else { it = noSlcPos.erase(it); }
								}
							}
						}
						if(crac->self_hurt_sum < 0){ break; }
						char op_hit=-g->oppLifeDiff-crac->self_hurt_sum;
						P p;
						if(opac->torpedo.x>=0 && opac->trigger.x<0){
							p = opac->torpedo;
						}else if(opac->torpedo.x<0 && opac->trigger.x>=0){
							p = opac->trigger;
						}else{ break; }
						assert(op_hit <= 2);
						int PsbPosSize = noSlcPos.size();
						if(op_hit==2){ noSlcPos.clear(); noSlcPos.push_back(p); } // headshot..
						else if(op_hit==1){
							for(auto it=noSlcPos.begin();it!=noSlcPos.end();){
								if(BHURT(*it, p)==1){ it++; } else { it = noSlcPos.erase(it); }
							}
						}else if(op_hit==0){
							for(auto it=noSlcPos.begin();it!=noSlcPos.end();){
								if(BHURT(*it, p)==0){ it++; } else { it = noSlcPos.erase(it); }
							}
						}
						if(PsbPosSize != noSlcPos.size()){ debug("HIT-OP(MyID):%d ",op_hit); }
					}while(0);
				}
				if(g->myId == OP(id)){
					//Life Diff MyID
					do{
						if(opac->self_hurt_sum < 0){ break; }
						char op_hit=-g->myLifeDiff-opac->self_hurt_sum;
						P p;
						if(crac->torpedo.x>=0 && crac->trigger.x<0){
							p = crac->torpedo;
						}else if(crac->torpedo.x<0 && crac->trigger.x>=0){
							p = crac->trigger;
						}else{ break; }
						assert(op_hit <= 2);
						int opPsbPosSize = opPsbPos->size();
						auto last_opAction = g->recAction[OP(id)].back();
						if(op_hit==2){
							opPsbPos->clear(); opPsbPos->push_back(p);  // headshot..
						}else if(op_hit==1){
							for(auto it=opPsbPos->begin();it!=opPsbPos->end();){
								if(BHURT(*it, p)==1){ it++; } else { it = opPsbPos->erase(it); }
							}
						}else if(op_hit==0){
							for(auto it=opPsbPos->begin();it!=opPsbPos->end();){
								if(BHURT(*it, p)==0){ it++; } else { it = opPsbPos->erase(it); }
							}
						}
						if(opPsbPosSize != opPsbPos->size()){ debug("HIT-MyID:%d ",op_hit); dump_op(); }
						if(!opPsbPos->size()){ debug("op_hit: %d\n", op_hit); } assert(opPsbPos->size());
					}while(0);
				}
				filter_noSlcPos(g, this);
				filter_all(g, this);
				dump();
			}
			static void filter_all(const G *g, class CPosSim* posSim){
				auto crac = g->recAction[posSim->id].end()-1;
				list<P> *psbPos = &posSim->psbPos;
				FORBE(it, crac->subact){
					if(*it == AC_TORP && crac->torpedo.x >= 0){
						posSim->lastTorp = g->round;
						posSim->filter_torpedo(psbPos, crac->torpedo);
						if(!psbPos->size()){ posSim->dump_grid(); cerr << crac->torpedo << endl; } assert(psbPos->size());
					}else if(*it == AC_SURFACE && crac->surface > 0){
						posSim->lastSurface = g->round;
						posSim->filter_surface(psbPos, crac->surface);
						if(!psbPos->size()){ posSim->dump_grid(); cerr << crac->surface << endl; } assert(psbPos->size());
					}else if(*it == AC_SILENCE && crac->silence != '\0'){
						posSim->lastSilence = g->round;
						posSim->filter_silence(psbPos);
						if(!psbPos->size()){ posSim->dump_grid(); } assert(psbPos->size());
					}else if(*it == AC_MOVE && crac->move != '\0'){
						posSim->filter_move(psbPos, crac->move);
						if(!psbPos->size()){ posSim->dump_grid(); cerr << crac->move << endl; } assert(psbPos->size());
					}else if(*it == AC_SONAR){ posSim->lastSonar = g->round;
					}else if(*it == AC_MINE && crac->mine != '\0'){
						posSim->lastMine = g->round;
						posSim->mineCount++;
						if(psbPos->size() == 1){ posSim->minePos.insert(psbPos->back() + c_d2p[crac->mine]); }
					}else if(*it == AC_TRIGGER && crac->trigger.x >= 0){
						posSim->mineCount--;
						posSim->minePos.erase(crac->trigger);
					}else{ cerr << *it << endl; assert(0); }
				}
				if(psbPos->size() == 1){
					(((G*)g)->recAction[posSim->id].end()-1)->pos = psbPos->back();
					posSim->update_visited_path(g->recAction[posSim->id]);
				}
			}
			static void filter_noSlcPos(const G *g, class CPosSim* posSim){
				list<P> *psbPos = &posSim->noSlcPos;
				if(psbPos->size() == 0) return;
				auto crac = g->recAction[posSim->id].end()-1;
				FORBE(it, crac->subact){
					if(*it == AC_TORP && crac->torpedo.x >= 0){
						posSim->filter_torpedo(psbPos, crac->torpedo);
					}else if(*it == AC_SURFACE && crac->surface > 0){
						posSim->filter_surface(psbPos, crac->surface);
					}else if(*it == AC_MOVE && crac->move != '\0'){
						posSim->filter_move(psbPos, crac->move);}
				}
			}
			void filter_torpedo(list<P> *psbPos, const P& p){
				set<P> setp; ((G*)g)->avaTor(p, setp);
				for(auto it=psbPos->begin();it!=psbPos->end();){
					if(setp.count(*it)){ it++; }
					else { it = psbPos->erase(it); }
				}
			}
			void filter_surface(list<P> *psbPos, int n){
				assert(1<=n&&n<10);
				const P pm[10] = {{0,0},{0,0},{5,0},{10,0},{0,5},{5,5},{10,5},{0,10},{5,10},{10,10}};
				for(auto it=psbPos->begin();it!=psbPos->end();){
					if(!(it->x<pm[n].x||it->x>pm[n].x+4||it->y<pm[n].y||it->y>pm[n].y+4)){ it++; }
					else { it = psbPos->erase(it); }
				}
				FOR(i, SIZE) FOR(j, SIZE){ if(g->grid[i][j]=='x') grid[i][j] = 2; else this->grid[i][j] = 0; }
			}
			void filter_silence(list<P> *psbPos){
				set<P> new_pos;
				for(auto it=psbPos->begin();it!=psbPos->end();it++){
					new_pos.insert(*it);
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
				psbPos->clear();
				FORBE(it, new_pos){
					psbPos->push_back(*it);
				}
			}
			void filter_move(list<P> *psbPos, char move){
				assert(c_d2p.count(move));
				for(auto it=psbPos->begin();it!=psbPos->end();){
					P p = c_d2p[move] + *it;
					if(this->isV(p)){ *it = p; it++; }
					else{ it = psbPos->erase(it); }
				}
				//dump_grid();
			}
			void filter_sonar_res(list<P> *psbPos, int n, char res){
				assert(1<=n&&n<10&&res>=0);
				const P pm[10] = {{0,0},{0,0},{5,0},{10,0},{0,5},{5,5},{10,5},{0,10},{5,10},{10,10}};
				for(auto it=psbPos->begin();it!=psbPos->end();){
					if((res>0) ^ (it->x<pm[n].x||it->x>pm[n].x+4||it->y<pm[n].y||it->y>pm[n].y+4)){ it++; }
					else { it = psbPos->erase(it); }
				}
			}
			void update_visited_path(const vector<action_t> &act){
				assert(psbPos.size()==1);
				P p = psbPos.back();
				grid[p.y][p.x] = 1;
				bool exit_flag = false;
				set<P> erase_mark;
				for(auto it=act.crbegin();it!=act.crend();it++){
					for(auto i=it->subact.rbegin();i!=it->subact.rend();i++){
						//@ref subact_t @WARNING: All type should be processed
						if(*i==AC_SILENCE){ exit_flag = true; break; }
						else if(*i==AC_SURFACE && it->surface){ exit_flag = true; break; }
						else if(*i==AC_MOVE && it->move > '\0'){
							p = c_rd2p[it->move] + p;
							if(grid[p.y][p.x] == 0){ grid[p.y][p.x] = 1; }
							else if(grid[p.y][p.x] == 1){ exit_flag = true; break; }
							else {
								debug("ID: %d. Error: (%d,%d), %d\n", id, p.x, p.y, grid[p.y][p.x]);
								dump_grid(); assert(0);
							}
						}else if(*i==AC_MINE){ if(!erase_mark.count(p)){minePos.insert(p);} }
						else if(*i==AC_TRIGGER){ erase_mark.insert(p); }
						else if(*i==AC_TORP || *i==AC_SONAR){ continue; }else{ break; }
					}
					if(exit_flag){ break; }
				}
				dump_grid();
			}
			void dump(void){
				debug("ID:%d psbPos: %lld\n", id, psbPos.size());
				auto it=psbPos.begin();
				for(int j=0;j<min(15,(int)psbPos.size());j++,it++){ debug("((%d,%d:%1.2f) ", it->x, it->y, it->e); } debug("\n");
			}
			void dump_op(void){
				debug("ID:%d psbPos: %lld\n", OP(id), opPsbPos->size());
				auto it=opPsbPos->begin();
				for(int j=0;j<min(15,(int)opPsbPos->size());j++,it++){ debug("(%d,%d:%1.2f) ", it->x, it->y, it->e); } debug("\n");
			}
			void dump_grid(void){debug("ID: %d\n", id); FOR(i, SIZE){ FOR(j, SIZE){ debug("%d", grid[i][j]); } cerr<<endl; } }
			void simReset(void){ simPos = psbPos; }
			int simMove(char move, bool peek=false){
				if(peek){ auto x=simPos; filter_move(&x, move); return x.size(); }
				filter_move(&simPos, move); return simPos.size();
			}
			int simTorp(const P& p, bool peek=false){
				if(peek){ auto x=simPos; filter_torpedo(&x, p); return x.size(); }
				filter_torpedo(&simPos, p); return simPos.size();
			}
			int simSilence(bool peek=false){
				if(peek){ auto x=simPos; filter_silence(&x); return x.size(); }
				filter_silence(&simPos); return simPos.size();
			}
		};

		inline void surface(void){
			FOR(i, SIZE) FOR(j, SIZE){
				if(my_visited[i][j]==1) my_visited[i][j] = 0;
			}
			my_visited[y][x]=1;
			dump_grid();
		}
		G(long round_time_ms_max=10):GCOM(round_time_ms_max){
			/* Custom Initialization */
			FOR(i, SIZE) FOR(j, SIZE){
				if(i==y&&x==j){ my_visited[i][j] = 1; }
				else if(grid[i][j] == 'x'){ my_visited[i][j] = 2; }
				else{ my_visited[i][j] = 0; }
			}
			mySim.init(this, myId, opSim), opSim.init(this, OP(myId), mySim);
		}
		CPosSim mySim, opSim;
		void nextMove(void) {
#ifndef __DEBUG__
			const vector<P> ps = {{1,0}, {-1,0}, {0,1}, {0,-1}, };
			const char d[4] = {'E', 'W', 'S', 'N'};
			debug("I'm here (%d,%d)\n", x, y);
			debug("noSlcPsb: %d", opSim.noSlcPos.size());
			if(opSim.noSlcPos.size() == 1){
				debug("(%d,%d)\n", opSim.noSlcPos.back().x, opSim.noSlcPos.back().y);
			}else{debug("%s","\n");}
			int nx = -1, ny = -1;
			set<P> pos; avaTor(P(x,y), pos);
			debug("minePos(%d/%d)\n", opSim.minePos.size(), opSim.mineCount);
			FORBE(it, opSim.minePos){ debug("(%d,%d) ", it->x, it->y); } debug("%s", "\n");
			//AC_TORP

			mySim.simReset();
			if(!torpedoCooldown && opSim.noSlcPos.size() == 1 && pos.count(opSim.noSlcPos.back()) && \
					DIST(opSim.noSlcPos.back(), P(x,y)) <= 4){
				action.torpedo = opSim.noSlcPos.back();
				action.subact.push_back(AC_TORP);
			}
			if(action.torpedo.x < 0 && !torpedoCooldown && opSim.psbPos.size() < 5){
				if(opSim.psbPos.size() == 1 && pos.count(opSim.psbPos.back()) && \
						DIST(opSim.psbPos.back(), P(x,y)) <= 4){
					action.torpedo = opSim.psbPos.back(); 
					action.subact.push_back(AC_TORP);
				}else{
#if 0
					FORBE(it, opSim.psbPos){
						if(DIST(*it, P(x,y)) <= 4){
							for(auto p: pos){
								if(BHURT(p, P(x,y))==0 && BHURT(p, *it)>1){
									action.torpedo = p;
									action.subact.push_back(AC_TORP);
									break;
								}
							}
						}
						if(action.torpedo.x >= 0){ break; }
					}
					if(action.torpedo.x < 0)
						FORBE(it, opSim.psbPos){
							if(DIST(*it, P(x,y)) <= 5){
								for(auto p: pos){
									int d = DIST(p, P(x,y));
									if((1<d && d<=4) && BHURT(p, *it)>0){
										action.torpedo = p; 
										action.subact.push_back(AC_TORP);
										break;
									}
								}
							}
							if(action.torpedo.x >= 0){ break; }
						}
#else

					map<P, float> x;
					FORBE(it, opSim.psbPos){
						for(int i=-1;i<=1;i++){
							for(int j=-1;j<=1;j++){
								P p = P(i,j) + *it;
								if(!x.count(p)){ x[p] = 1;}//p.e; }
								else x[p]+=1;//p.e;
							}
						}
					}
					vector<pair<int, P>> tar;
					FORBE(it, x){
						if(pos.count(it->first)){
							tar.push_back(pair<int,P>(-it->second, it->first));
						}
					}
					if(tar.size()){
						sort(tar.begin(), tar.end());
						P p = tar.front().second;
						action.torpedo = p;
						action.subact.push_back(AC_TORP);
					}
#endif
				}
				if(action.torpedo.x >= 0){ torpedoCooldown=3; }
			}
			if(action.torpedo.x >= 0){ mySim.simTorp(action.torpedo); assert(mySim.simPos.size()); }

			int nearest = 100;;
			FORBE(it, opSim.psbPos){
				if(DIST(*it, P(x, y)) < nearest){
					nearest = DIST(*it, P(x, y));
				}
			}
			do{ // triiger mine
				if(opSim.noSlcPos.size() == 1){
					FORBE(it, minePos){
						if(BHURT(*it, opSim.noSlcPos.back()) > BHURT(P(x,y), opSim.noSlcPos.back())){
							action.trigger = *it;
							action.subact.push_back(AC_TRIGGER);
							break;
						}
					}
				}

				if(action.trigger.x >= 0){ break; }
				set<P> opPos(opSim.psbPos.begin(), opSim.psbPos.end());
				float max_cnt = -1;
				FORBE(it, minePos){
					if(BHURT(*it, P(x,y))>0 || opPos.size()>50){ continue; }
					float cnt = 0;
					for(int i=-1;i<=1;i++){
						for(int j=-1;j<=1;j++){
							if(opPos.count(P(i,j)+(*it))){ cnt+=1; }//it->e; }
						}
					}
					if(cnt > max_cnt && (cnt > 4 || (cnt>0&&opPos.size()<3))){
						max_cnt = cnt;
						action.trigger = *it;
					}
				}
				if(action.trigger.x >= 0){ action.subact.push_back(AC_TRIGGER); }
			}while(0);
			do{ // place mine
				if(!mineCooldown){
					FORBE(it, c_4d){
						P p = *it + P(x, y);
						if(p.x>=0&&p.y>=0&&p.x<SIZE&&p.y<SIZE &&
								!minePos.count(p) && !grid[p.y][p.x]){
							action.mine = c_p2d[*it];
							action.subact.push_back(AC_MINE);
							break;
						}
					}
				}
			}while(0);
			do{ // next move
				vector<pair<int, char>> res = move_rand_safe(P(x, y), my_visited);
				do{ // op mine
					// MUST same in move_rand_safe
					P p=P(x,y); vector<P> pl = {p+P(1,0), p+P(-1,0), p+P(0,1), p+P(0,-1)};
					FOR(i, 4){
						FORBE(it, opSim.minePos){
							if(DIST(pl[i], *it) <= 3){
								res[i].first -= -1;
							}
						}
					}
				}while(0);
				sort(res.begin(), res.end());
				//FORBE(it, res){ cerr << it->first << ' ' << it->second << endl ;}
				FOR(i, 4) debug("%c(%d) ", res[i].second, res[i].first); cerr<<endl;
				int i=0;
				for(;i<4;i++){
					if(-res[i].first == 0 || -res[i].first < -res[0].first){ break; }
				}
				if(i == 0){ break; }
				int n = (rand() % 1);
				//cerr << "n: " << n << " i: " << i << endl;
				P p = c_d2p[res[n].second];
				if((action.torpedo.x>=0 && mySim.simPos.size() <= 5 &&
						!silenceCooldown && nearest < 5 && this->round - opSim.lastTorp >= 2)/* ||
						(!silenceCooldown && op_action.torpedo.x>=0 && myLifeDiff < 0)*/){
					P p = c_d2p[res[(rand() % i)].second];
					for(int i=4;i>=2;i--){
						bool valid = true;
						for(int j=1;j<=i;j++){
							if(!isV(x+p.x*j, y+p.y*j)){ valid = false; break; }
						}
						if(valid){
							action.silence = res[n].second;
							action.silence_len = i;
							action.subact.push_back(AC_SILENCE);
							for(int j=1;j<=i;j++){ my_visited[y+p.y*j][x+p.x*j]=1; }
							break;
						}
					}
				}
				int nx=p.x+x, ny=p.y+y;
				if(!action.move && !action.silence && isV(nx, ny)){
					if(!silenceCooldown && (nearest <= 6 || mySim.psbPos.size() < 5 || action.torpedo.x>=0) && \
							(mySim.psbPos.size() < 15 || myLifeDiff<0) && \
							(this->round - opSim.lastTorp >= 2)){
						action.silence = res[n].second;
						action.silence_len = 1;
						action.subact.push_back(AC_SILENCE);
					}else{
						action.move = res[n].second;
						action.subact.push_back(AC_MOVE);
					}
					my_visited[ny][nx]=1;
					break;
				}
			}while(0);
			do{ // sonar
				if(torpedoCooldown){ action.charge = CR_TORP; }
				else if(silenceCooldown){ action.charge = CR_SILENCE; }
				else if(mineCooldown){ action.charge = CR_MINE; }
				else if(sonarCooldown){ action.charge = CR_SONAR; }
				if(!sonarCooldown && opSim.psbPos.size() > 15){
					action.sonar = PT2SECTOR(opSim.psbPos.back());
					action.subact.push_back(AC_SONAR);
				}
			}while(0);

			if(!action.move && !action.silence){
				action.surface = PT2SECTOR(P(x,y));
				action.subact.push_back(AC_SURFACE);
				surface();
			}

#else
			action.charge = CR_TORP;
			action.subact.push_back(AC_MOVE);
			if(round == 1){
				action.move = myId==0?'N':'S';
			}else{
				action.move = 'W';
			}
			if(round==4){
				action.torpedo = P(7, myId==0?13:10);
				action.subact.push_back(AC_TORP);
			}
#endif
		}
		void process(void){
			opSim.update();
			//while(0 && !T->is_time_up()); debug("Time spend: %ld \n", T->get());
			nextMove();
			action.update(); recAction[myId].push_back(action);
			mySim.update();
		}
};
void _D_E_B_U_G_(){
	return;
	char map[15][15] = {0};
	auto res = G::move_rand_safe(P(1,0), map);
	FORBE(it, res){
		cout << it->first << ' ' << it->second << endl;
	}
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
