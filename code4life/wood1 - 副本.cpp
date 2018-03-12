#include <iostream>
#include <cstring>
#include <string>
#include <list>
#include <algorithm>

using namespace std;

typedef struct {
	string target;
	int eta;
	int score;
	int storageA;
	int storageB;
	int storageC;
	int storageD;
	int storageE;
	int expertiseA;
	int expertiseB;
	int expertiseC;
	int expertiseD;
	int expertiseE;
}currentInfo;

typedef struct {
	int sampleId;
	int carriedBy;
	int rank;
	string expertiseGain;
	int health;
	int costA;
	int costB;
	int costC;
	int costD;
	int costE;
}sampleInfo;

class R{
	public:
	currentInfo me, op;
	int roundAvaMol[5];
	int sampleCount;
	list<sampleInfo*> samples;
	R(){
		cin >> me.target >> me.eta >> me.score >> me.storageA >> me.storageB >> me.storageC >> me.storageD >> me.storageE >> me.expertiseA >> me.expertiseB >> me.expertiseC >> me.expertiseD >> me.expertiseE; cin.ignore();
		cin >> op.target >> op.eta >> op.score >> op.storageA >> op.storageB >> op.storageC >> op.storageD >> op.storageE >> op.expertiseA >> op.expertiseB >> op.expertiseC >> op.expertiseD >> op.expertiseE; cin.ignore();
        cin >> roundAvaMol[0] >> roundAvaMol[1] >> roundAvaMol[2] >> roundAvaMol[3] >> roundAvaMol[4]; cin.ignore();
        cin >> sampleCount; cin.ignore();
		for(int i=0;i<sampleCount;i++){
			sampleInfo *s = new sampleInfo;
			cin >> s->sampleId >> s->carriedBy >> s->rank >> s->expertiseGain >> s->health >> s->costA >> s->costB >> s->costC >> s->costD >> s->costE; cin.ignore();
			cerr << "|" << s->sampleId << "|" << s->carriedBy << "|" << s->rank << "|" << s->expertiseGain << "|" << s->health << "|" << s->costA << "|" << s->costB << "|" << s->costC << "|" << s->costD << "|" << s->costE << endl;
			samples.push_back(s);
		}
	}
	~R(){
		for(int i=0;i<samples.size();i++){
			sampleInfo *s = samples.front();
			delete s;
			samples.pop_front();
		}	
	}
};
	
class Rbt{
	public:
	Rbt(){}
};

class G{
	public: 
	R *roundInfo = NULL;
	Rbt *rbt;
	int roundSampleCount;
	int target;
	int holdId;
	int sample_flag;
	int costs[5];
	char action[256];
	G(){ 
		Rbt *rbt = new Rbt();
		target = -1;
		holdId = -1;
		sample_flag = -1;
		int projectCount;
    	cin >> projectCount; cin.ignore();
		globalInit();
	}
	~G(){delete rbt;}
	void globalInit(void){}
	void roundUpdate(void){
		if(roundInfo){delete roundInfo;}
		roundInfo = new R();
	}
	void process(void);
 	void output(void){cout << action << endl;}
};

void G::process(void)
{
	currentInfo *me = &roundInfo->me;
	list<sampleInfo*> samples = roundInfo->samples;
	if(target == -1){
		int maxValue = -1;
		int sampleId = -1;
		for (list<sampleInfo*>::iterator it=samples.begin(); it != samples.end(); ++it){
			if((*it)->carriedBy != 0){
				continue;
			}
			float tmp = (float)(*it)->health / (float)((*it)->costA+(*it)->costB+(*it)->costC+(*it)->costD+(*it)->costE);
			if(tmp > maxValue){
				maxValue = tmp;sampleId = (*it)->sampleId;
				costs[0] = (*it)->costA;costs[1] = (*it)->costB;costs[2] = (*it)->costC;costs[3] = (*it)->costD;costs[4] = (*it)->costE;
			}
		}
		target = sampleId;
		cerr << "Debug " << "New sample ID: " << target << endl;
	}
	if(sample_flag == -1){
		if(me->target.compare("SAMPLES")){sprintf(action, "GOTO SAMPLES");}
		else{
			sprintf(action, "CONNECT 2");
			sample_flag = 1;
		}
	}else if(holdId == -1){
		if(me->target.compare("DIAGNOSIS")){sprintf(action, "GOTO DIAGNOSIS");}
		else{
			sprintf(action, "CONNECT %d", target);
			holdId = target;
		}
	}else if(costs[0] != 0 or costs[1] != 0 or costs[2] != 0 or costs[3] != 0 or costs[4] != 0){
		if(me->target.compare("MOLECULES")){
			sprintf(action, "GOTO MOLECULES");
			for (list<sampleInfo*>::iterator it=samples.begin(); it != samples.end(); ++it){
				if((*it)->sampleId != target){continue;}
				costs[0] = (*it)->costA;costs[1] = (*it)->costB;costs[2] = (*it)->costC;costs[3] = (*it)->costD;costs[4] = (*it)->costE;
				break;
			}
		}else{
				 if(costs[0] > 0){sprintf(action, "CONNECT A");costs[0]--;}
			else if(costs[1] > 0){sprintf(action, "CONNECT B");costs[1]--;}
			else if(costs[2] > 0){sprintf(action, "CONNECT C");costs[2]--;}
			else if(costs[3] > 0){sprintf(action, "CONNECT D");costs[3]--;}
			else if(costs[4] > 0){sprintf(action, "CONNECT E");costs[4]--;}
			else{sprintf(action, "GOTO LABORATORY");}
		}
	}else{
		if(me->target.compare("LABORATORY")){sprintf(action, "GOTO LABORATORY");}
		else{
			sprintf(action, "CONNECT %d", holdId);
			target = -1;
			holdId = -1;
			sample_flag = -1;
		}
	}
}

int main(int argc, char *argv[])
{
	G *g = new G();
	while(1){
		g->roundUpdate();
		g->process();
		g->output();
	}
	delete g;
	return 0;
}
