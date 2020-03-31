// https://www.codingame.com/ide/puzzle/the-resistance
#include <iostream>
#include <fstream>
#include <string.h>
#define FOR(i,a,b) for(int i=a;i<b;i++)
using namespace std;

long long dp[100000];
char m[100000];
char w[100000][100];
int N;
char *d[] = {
	(char*)".-", (char*)"-...", (char*)"-.-.", (char*)"-..", (char*)".", (char*)"..-.",
	(char*)"--.", (char*)"....", (char*)"..", (char*)".---", (char*)"-.-", (char*)".-..",
	(char*)"--", (char*)"-.", (char*)"---", (char*)".--.", (char*)"--.-", (char*)".-.",
	(char*)"...", (char*)"-", (char*)"..-", (char*)"...-", (char*)".--", (char*)"-..-", (char*)"-.--", (char*)"--.."
};

char* scmp(char *const_str, char *search_str)
{
	while(*search_str){
		if(*const_str != *search_str){ return NULL; }
		search_str++;
		const_str++;
	}
	return const_str;
}

long long cal(int pos, char *p, long long *dp)
{
  	if (pos == strlen(m)){
    	return 1;
  	}
	if (dp[pos] >= 0){
		return dp[pos];
	}
	long long res = 0;
	FOR(i, 0, N){
		if (scmp(&p[pos], w[i])) {
			res+= cal(pos + strlen(w[i]), p, dp);
		}
	}
	dp[pos] = res;
	return res;
}
int main(int argc, char *argv[])
{
//	ifstream in__("in.txt");cin.rdbuf(in__.rdbuf());
	cin >> m;
	cin >> N;
	FOR(i, 0, N){
		char t[20], *p = t, *q = w[i];
		cin >> t;
		while(*p){
			char *r = d[*p - 'A'];
			while(*r){ *q = *r; q++; r++; }
			p++;
		}
		*q = '\0';
	}
	cerr << "-----------" << endl;
	FOR(i, 0, 100000) dp[i] = -1;
	cout << cal(0, m, dp) << endl;
}