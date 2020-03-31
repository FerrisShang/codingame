https://www.codingame.com/ide/puzzle/unflood-the-world
#include <iostream>
#include <fstream>
#define FOR(i,a,b) for(int i=a;i<b;i++)
using namespace std;

int w, h, hmap[128][128], mmap[128][128];

static int isSafe(int x, int y){ return x>=0 && x<w && y>=0 && y<h; }

static void _find_low(int hmap[128][128], int mark[128][128], int x, int y, int &lowest, int &lx, int &ly)
{
	if(!isSafe(x,y) || mark[y][x] || hmap[y][x] > lowest) return;
	lowest=hmap[y][x]; lx = x; ly = y;
	mark[y][x]=1;
	_find_low(hmap, mark, x+1, y, lowest, lx, ly);
	_find_low(hmap, mark, x-1, y, lowest, lx, ly);
	_find_low(hmap, mark, x, y+1, lowest, lx, ly);
	_find_low(hmap, mark, x, y-1, lowest, lx, ly);
}
static int find_low(int hmap[128][128], int x, int y)
{
	int mark[128][128] = {0};
	int lowest = hmap[y][x], lx, ly;
	_find_low(hmap, mark, x, y, lowest, lx, ly);
	cerr << lx << " " << ly << " " << lowest << endl;
	return (lx<<8) + ly;
}
static void mark_high(int hmap[128][128], int mmap[128][128], int x, int y){
	if(!isSafe(x,y) || mmap[y][x]) return;
	mmap[y][x]=1;
	if(hmap[y][x+1] >= hmap[y][x])mark_high(hmap, mmap, x+1, y);
	if(hmap[y][x-1] >= hmap[y][x])mark_high(hmap, mmap, x-1, y);
	if(hmap[y+1][x] >= hmap[y][x])mark_high(hmap, mmap, x, y+1);
	if(hmap[y-1][x] >= hmap[y][x])mark_high(hmap, mmap, x, y-1);
}
int main(int argc, char *argv[])
{
	//ifstream in__("in.txt");cin.rdbuf(in__.rdbuf());
	cin >> w >> h;
	FOR(i,0,h){
		FOR(j,0,w){ cin >> hmap[i][j]; }
	}
	int res = 0;
	FOR(i,0,h){
		FOR(j,0,w){
			if(mmap[i][j] == 0){
				int t = find_low(hmap, j, i);
				mark_high(hmap, mmap, (t>>8)&0xFF, t&0xFF);
				res++;
			}
		}
	}
	cout << res << endl;
	return 0;
}