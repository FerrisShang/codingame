// https://www.codingame.com/ide/puzzle/music-scores
#include <iostream>
#include <fstream>
#include <cmath>
#define FOR(i,a,b) for(int i=a;i<b;i++)
using namespace std;

struct staff{
	int base_y;
	int diff;
	int height;
}staff;
struct tail{
	int x, y1, y2;
	int next_x;
};
int w, h, cnt;

struct staff getLine(char map[300][5000], int w, int h){
	struct staff staff;
	int mark[3] = {0}, i, j;
	for(i=0;i<w;i++){
		for(j=0;j<h;j++){
			if(map[j][i]) { mark[0] = j; break; }
		}
		if(mark[0]) break;
	}
	for(;j<h;j++){ if(map[j][i]==0) { mark[1] = j; break; } }
	for(;j<h;j++){ if(map[j][i]) { mark[2] = j; break; } }
	staff.base_y = mark[0];
	staff.height = mark[1] - mark[0];
	staff.diff = mark[2] - mark[0];
	return staff;
}
struct tail findTail(char map[300][5000], int basex, int tail_len)
{
	int i, j, xl, xr;
	struct tail tail = {-1};
	for(i=basex;i<w;i++){
		for(j=0;j<h;j++){
			if(map[j][i]) {
				int cnt = 0;
				tail.y1 = j;
				for(;j<h;j++){ if(map[j][i]) { cnt++; } else{break;} }
				if(cnt > tail_len){ tail.x = i; tail.y2 = j-1; break;}
			}
		}
		if(tail.x > 0) break;
	}
	if(tail.x < 0) return tail;
	for(i=tail.x+1;i<w;i++){
		for(j=tail.y1+staff.diff/2;j<tail.y2-staff.diff/2;j++){
			if(!map[j][i]){
				tail.next_x = i;
				return tail;
			}
		}
	}
}
int direct(char map[300][5000], struct tail *ref_tail)
{
	int res;
	res = 1;
	for(int j=ref_tail->y1;j<ref_tail->y2;j++){
		if(j<staff.base_y)continue;
		if(map[j][ref_tail->x-1] != (((j-staff.base_y)%staff.diff)<staff.height)) {res = 0;break;}
	}
	if(res) return res;
	res = -1;
	for(int j=ref_tail->y1;j<ref_tail->y2;j++){
		if(j<staff.base_y)continue;
		if(map[j][ref_tail->next_x] != (((j-staff.base_y)%staff.diff)<staff.height)) {res = 0;break;}
	}
	return res;
}
static int isOnline(char map[300][5000], int baseY)
{
	return !(abs((abs(baseY - staff.base_y+staff.height/2) % staff.diff) - staff.diff/2.0) < staff.diff/4.0);
}
static char getLevel(int baseY)
{
	const char *str = "CDEFGAB";
	int res = (int)(((staff.base_y+staff.diff*5.0+staff.height/2.0) - baseY + staff.diff/4.0) / (staff.diff/2.0)) % 7;
	return str[res];
}
static int isQ(char map[300][5000], struct tail *ref_tail, int dir)
{
	int flag;
	int noteBaseX = dir<0?((ref_tail->next_x + ref_tail->x)/2.0)-staff.diff/2.0:((ref_tail->next_x + ref_tail->x)/2.0)+staff.diff/2.0;
	flag = 1;
	for(int j=ref_tail->y1-staff.diff/4;j<ref_tail->y1+staff.diff/4;j++){
		if(!map[j][noteBaseX]){ flag = 0; break; }
	}
	if(flag) return ref_tail->y1+((ref_tail->next_x-ref_tail->x)/2+1);
	flag = 1;
	for(int j=ref_tail->y2-staff.diff/4;j<ref_tail->y2+staff.diff/4;j++){
		if(!map[j][noteBaseX]){ flag = 0; break; }
	}
	if(flag) return ref_tail->y2-((ref_tail->next_x-ref_tail->x)/2+1);
	return -1;
}
static void adjust(int &refY, int ext)
{
	if(((refY-staff.base_y) % (staff.diff / 2)) > 2){
		refY += ext * staff.height/2;
	}
}
static int isH(char map[300][5000], struct tail *ref_tail, int dir)
{
	int flag, isOnl;
	int noteBaseX = dir<0?((ref_tail->next_x + ref_tail->x)/2)-staff.diff/2:((ref_tail->next_x + ref_tail->x)/2)+staff.diff/2;
	adjust(ref_tail->y1, 1);
	isOnl = isOnline(map, ref_tail->y1);
	if(isOnl){
		flag = 1;
		for(int j=ref_tail->y1-staff.diff/5;j<ref_tail->y1+staff.diff/5;j++){
			if(map[j][noteBaseX]){ flag = 0; break; }
		}
		if(flag) return ref_tail->y1+((ref_tail->next_x-ref_tail->x)/2+1);
		else return ref_tail->y2-((ref_tail->next_x-ref_tail->x)/2+1);
	}
	adjust(ref_tail->y2, -1);
	isOnl = isOnline(map, ref_tail->y2);
	if(isOnl){
		flag = 1;
		for(int j=ref_tail->y2-staff.diff/5;j<ref_tail->y2+staff.diff/5;j++){
			if(map[j][noteBaseX]){ flag = 0; break; }
		}
		if(flag) return ref_tail->y2-((ref_tail->next_x-ref_tail->x)/2+1);
		else return ref_tail->y1+((ref_tail->next_x-ref_tail->x)/2+1);
	}
	for(int x=noteBaseX;;x+=dir){
		if(map[ref_tail->y1][x]) return ref_tail->y1+((ref_tail->next_x-ref_tail->x)/2+1);
		if(map[ref_tail->y2][x]) return ref_tail->y2-((ref_tail->next_x-ref_tail->x)/2+1);
	}
	return -1;
}
int main(int argc, char *argv[])
{
//	ifstream in__("in.txt");cin.rdbuf(in__.rdbuf());
	char C, map[300][5000];
	int W, p=0;
	cin >> w >> h;
	cerr << w << ' ' << h << ' ' << endl;
	while(cin >> C){
		cin >> W;
		FOR(i, 0, W){
			map[p/w][p%w] = (C=='B');
			p++;
		}
	}
	// get staff info
	staff = getLine(map, w, h);
	cerr << staff.base_y<< ' '  << staff.diff << ' ' << staff.height << ' ' << endl;
	int tail_len = staff.height * 1.5;
	struct tail tail = {0, 0, 0, 0};
	int firstFlag = 1;
	while(1){
		tail = findTail(map, tail.next_x, staff.diff * 1.5);
		if(tail.x < 0) break;
		cnt++;
		if(firstFlag) { firstFlag = 0; } else { cout << ' '; }
		int dir = direct(map, &tail);
		int iQ = isQ(map, &tail, dir);
		if(iQ > 0){
			char lev = getLevel(iQ);
			cout << lev << 'Q';
			continue;
		}
		int iH = isH(map, &tail, dir);
		char lev = getLevel(iH);
		cout << lev << 'H';
	}
	cout << endl;
	return 0;
	FOR(j, 0, h){
		FOR(i, w/3, w*3/4){
			if(map[j][i]) cout << '*'; else cout << ' ';
		}
		cout << endl;
	}
	cout << "-----------" << endl;
}