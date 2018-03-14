#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <cstring>
#include <string>
#include <list>
#include <algorithm>

#define MSG(fmt, ...) fprintf(stderr, "DEBUG: " fmt, __VA_ARGS__)
using namespace std;
class Time{
	private:
		static int mark;
	public:
		static void set(){mark = clock();}
		static void get(){MSG("%d ms\n", clock() - mark);}
};
int Time::mark = 0;

enum {ME=0,OP=1,CL=-1};
enum {A=0,B,C,D,E,MOL_NUM};
enum {START_POS=0, SAMPLES, DIAGNOSIS, MOLECULES, LABORATORY,};
enum {UNDIAGNOSED=0, DIAGNOSED,};
int distence[5][5] = {{0, 2, 2, 2, 2}, {2, 0, 3, 3, 3}, {2, 3, 0, 3, 4}, {2, 3, 3, 0, 3}, {2, 3, 4, 3, 0},};

class Robot {
	string str_target;
	public:
	int target;int eta;int score;int storage[MOL_NUM];int expertise[MOL_NUM];
	Robot(){
		cin >> str_target >> eta >> score >> storage[A] >> storage[B] >> storage[C] >> storage[D] >> storage[E] >> expertise[0] >> expertise[1] >> expertise[2] >> expertise[3] >> expertise[4]; cin.ignore();
		if(!str_target.compare("START_POS")){target = START_POS;}else if(!str_target.compare("SAMPLES")){target = SAMPLES;}
		else if(!str_target.compare("DIAGNOSIS")){target = DIAGNOSIS;} else if(!str_target.compare("MOLECULES")){target = MOLECULES;} else if(!str_target.compare("LABORATORY")){target = LABORATORY;}
	}
	int leftSlot(){int cnt; for(int i=0;i<MOL_NUM;i++){cnt += storage[i];} return 10-cnt;}
	int sumExp(){int cnt; for(int i=0;i<MOL_NUM;i++){cnt += expertise[i];} return cnt;}
	void debug(void){MSG("%0d %d %d %d %d | %d %d %d %d %d\n", storage[0], storage[1], storage[2], storage[3], storage[4], expertise[0], expertise[1], expertise[2], expertise[3], expertise[4]);}
};

class Sample {
	string str_expertiseGain;
	public:
	int sampleId;int carriedBy;int rank;int expertiseGain;int health;int cost[MOL_NUM];int status;
	Sample(){
		cin >> sampleId >> carriedBy >> rank >> str_expertiseGain >> health >> cost[A] >> cost[B] >> cost[C] >> cost[D] >> cost[E]; cin.ignore(); status = cost[A]<0?UNDIAGNOSED:DIAGNOSED;
		if(!str_expertiseGain.compare("A")){expertiseGain = A;}else if(!str_expertiseGain.compare("B")){expertiseGain = B;} else if(!str_expertiseGain.compare("C")){expertiseGain = C;} else if(!str_expertiseGain.compare("D")){expertiseGain = D;} else if(!str_expertiseGain.compare("E")){expertiseGain = E;}
	}
	void debug(void){MSG("%02d %d %d %d %2d %2d %2d %2d %2d %2d %d\n", sampleId, carriedBy, rank, expertiseGain, health, cost[A], cost[B], cost[C], cost[D], cost[E], status);}
};

class Poject {
	public:
	int molecule[MOL_NUM];
	Poject(){cin >> molecule[A] >> molecule[B] >> molecule[C] >> molecule[D] >> molecule[E]; cin.ignore();}
};

class Round{
	public:
	Robot *rbt_me, *rbt_op;
	int roundAvaMol[MOL_NUM];
	int sampleCount;
	Sample **sample_list;
	Round(){
		rbt_me = new Robot(); rbt_op = new Robot();
        cin >> roundAvaMol[A] >> roundAvaMol[B] >> roundAvaMol[C] >> roundAvaMol[D] >> roundAvaMol[E]; cin.ignore();
        cin >> sampleCount; cin.ignore();
		sample_list = (Sample**)malloc(sampleCount * sizeof(void*));
		for(int i=0;i<sampleCount;i++){ sample_list[i] = new Sample(); sample_list[i]->debug();}
	}
	~Round(){
		delete rbt_me; delete rbt_op;
		for(int i=0;i<sampleCount;i++){ delete sample_list[i]; }
		free(sample_list);
	}
};

class G{
	public:
	int projectCount;
	Poject **project_list;
	Round *roundInfo = NULL;
	G(){
		cin >> projectCount; cin.ignore();
		project_list = (Poject**)malloc(projectCount * sizeof(void*));
		for(int i=0;i<projectCount;i++){ project_list[i] = new Poject(); }
	}
	void roundUpdate(void){ if(roundInfo){delete roundInfo;} roundInfo = new Round(); }
};

class P{
	public:
	char action[256];
	G *g;
	Robot *me;
	Round *roundInfo;
	P(){ strcpy(action, ""); }
	void update(G *g){this->g = g; me = g->roundInfo->rbt_me; roundInfo = g->roundInfo;}
	void process(void);
	void output(void){cout << action << endl;}
};

char *getPosStr(int pos){char *s[5] = {"START", "SAMPLES", "DIAGNOSIS", "MOLECULES", "LABORATORY"}; return s[pos];}
void getStrPosGoto(char *act, int pos){strcpy(act, "GOTO "); strcat(act, getPosStr(pos));}
void getStrIdConn(char *act, int id){sprintf(act, "CONNECT %d", id);}
void getStrMolConn(char *act, int mol){sprintf(act, "CONNECT %c", mol+'A');}
int getNumHold(Sample **sample_list, int sample_num){int cnt=0;for(int i=0;i<sample_num;i++){if(sample_list[i]->carriedBy==ME){cnt++;}}return cnt;}
int getUndiaNum(Sample **sample_list, int sample_num){for(int i=0;i<sample_num;i++){if(sample_list[i]->carriedBy==ME && sample_list[i]->status==UNDIAGNOSED){return sample_list[i]->sampleId;}}return -1;}
int getMulByNum(G *g){
	Sample **sample_list = g->roundInfo->sample_list;
	Round *roundInfo = g->roundInfo; // roundAvaMol[MOL_NUM];
	Robot *me = g->roundInfo->rbt_me; //storage[MOL_NUM]; expertise[MOL_NUM];
	if(me->leftSlot() == 0){ return -1;}
	for(int i=0;i<g->roundInfo->sampleCount;i++){
		if(sample_list[i]->carriedBy==ME && sample_list[i]->status==DIAGNOSED){
			int enough_flag = true;
			int finish_flag = true;
			int short_mol = -1;
			int min_num = 10;
			for(int j=0;j<MOL_NUM;j++){
				if(sample_list[i]->cost[j] > me->expertise[j] + me->storage[j]){finish_flag = false;}
				if(roundInfo->roundAvaMol[j] < sample_list[i]->cost[j] - me->expertise[j] - me->storage[j]){
					enough_flag = false;
					break;
				}else{
					int ava = roundInfo->roundAvaMol[j];
					int need = sample_list[i]->cost[j] - me->expertise[j] - me->storage[j];
					if(ava > 0 && need > 0 && ava - need < min_num){ min_num = ava - need; short_mol = j;}
				}
			}
			if(enough_flag && !finish_flag){ return short_mol; } // get mol
		}
	}
	return -1;
}
int getFinishSample(G *g){
	Sample **sample_list = g->roundInfo->sample_list;
	Round *roundInfo = g->roundInfo; // roundAvaMol[MOL_NUM];
	Robot *me = g->roundInfo->rbt_me; //storage[MOL_NUM]; expertise[MOL_NUM];
	for(int i=0;i<g->roundInfo->sampleCount;i++){
		if(sample_list[i]->carriedBy==ME && sample_list[i]->status==DIAGNOSED){
			int finish_flag = true;
			for(int j=0;j<MOL_NUM;j++){
				if(sample_list[i]->cost[j] > me->expertise[j] + me->storage[j]){finish_flag = false;break;}
			}
			if(finish_flag){ return sample_list[i]->sampleId; }
		}
	}
	return -1;
}

enum {ST_READ, ST_AUTH, ST_WRITE, ST_DELETE};
void P::process(void){
	static int state = ST_READ;
	if(me->eta > 0){strcpy(action, ""); return;}
	MSG("Position:%s \n", getPosStr(me->target));
	while(1){switch(state){
	case ST_READ:
		if(me->target != SAMPLES) { getStrPosGoto(action, SAMPLES); }
		else{
			int num = getNumHold(roundInfo->sample_list, roundInfo->sampleCount);
			if(num < 3){ int x = (me->sumExp()+(rand()%4)); getStrIdConn(action, x>12?3:x>3?2:1); }
			else{ state = ST_AUTH; break;}
		}
		return;
	case ST_AUTH:
		if(me->target != DIAGNOSIS) { getStrPosGoto(action, DIAGNOSIS); }
		else{
			int num = getUndiaNum(roundInfo->sample_list, roundInfo->sampleCount);
			if(num < 0){ state = ST_WRITE; break; }
			else{ getStrIdConn(action, num); }
		}
		return;
	case ST_WRITE:
		if(me->target != MOLECULES) { getStrPosGoto(action, MOLECULES); }
		else{
			int num = getMulByNum(g);
			if(num < 0){
				if(getFinishSample(g) >= 0){
					state = ST_DELETE; break;
				}else{
					if(getNumHold(roundInfo->sample_list, roundInfo->sampleCount) < 3){
						state = ST_READ; break;
					}else{
						strcpy(action, "WAIT");
					}
				}
			}
			else{ getStrMolConn(action, num); }
		}
		return;
	case ST_DELETE:
		int num = getFinishSample(g);
		MSG("FINISH: %d\n", num);
		if(num >= 0){
			if(me->target != LABORATORY) { getStrPosGoto(action, LABORATORY); }
			else{ getStrIdConn(action, num); }
		}else{
			if(getNumHold(roundInfo->sample_list, roundInfo->sampleCount) > 0){
				state = ST_WRITE; break;
			}else{
				state = ST_READ; break;
			}
		}
		return;
	}}
}

int main(int argc, char *argv[]){
	G *g = new G();
	P *p = new P();
	while(1){
		g->roundUpdate();
		Time::set();
		p->update(g);
		g->roundInfo->rbt_me->debug();
		p->process();
		Time::get();
		p->output();
	}
}

