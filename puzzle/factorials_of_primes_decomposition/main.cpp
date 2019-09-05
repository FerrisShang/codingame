//https://www.codingame.com/training/hard/factorials-of-primes-decomposition
#include <iostream>
#include <map>
#include <list>
#include <string>
using namespace std;
#define M map<int, int>
class V{
	public:
		M m;
		inline void operator += (const V& v){
			for(auto it=v.m.begin(); it!=v.m.end(); ++it){
				if(this->m.find(it->first) != this->m.end()){
					this->m[it->first] += it->second;
					if(this->m[it->first] == 0){
						this->m.erase(it->first);
					}
				}else{
					this->m[it->first] = it->second;
				}
			}
		}
		inline void operator -= (const V& v){
			for(auto it=v.m.begin(); it!=v.m.end(); ++it){
				if(this->m.find(it->first) != this->m.end()){
					this->m[it->first] -= it->second;
					if(this->m[it->first] == 0){
						this->m.erase(it->first);
					}
				}else{
					this->m[it->first] = -it->second;
				}
			}
		}
		friend ostream& operator << (ostream& out, V& v){
			for(auto it=v.m.begin(); it!=v.m.end(); ++it){ out << it->first << "[" << it->second << "]" << " "; }
			return out; 
		}
};

int factor[20001];
V factorials[2001];

void __cal(list<int>& l, int n){
	if(n == 1) return;
	l.push_back(factor[n]);
	__cal(l, n / factor[n]);
}
V cal_f(int n){
	V v;
	list<int> l;
	__cal(l, n);
	if(l.front() == n){
		v.m[n] = 1;
		return v;
	}
	v += factorials[n-1];
	for(auto it=l.begin();it!=l.end();it++){
		v += factorials[*it];
		v -= factorials[*it-1];
	}
	return v;
}

V cal_n(int n){
	V v;
	list<int> l;
	__cal(l, n);
	if(l.front() == n){
		v.m[n] = 1;
		v -= factorials[n-1];
		return v;
	}
	for(auto it=l.begin();it!=l.end();it++){
		v += factorials[*it];
		v -= factorials[*it-1];
	}
	return v;
}
void output(V& v)
{
	auto it=v.m.end();
	do{
		it--;
		cout << it->first << "#" << it->second;
		if(it != v.m.begin()) cout << " ";
	}while(it != v.m.begin());
	cout << endl;
}

int main () {
	for(int i=0;i<=20000;i++) factor[i] = -1;
	for(int i=2;i<=20000;i++){
		for(int j=i;j<=20000;j+=i){
			if(j == i && factor[j] > 0) break;
			factor[j] = i;
		}
	}

	for(int i=2;i<=2000;i++){
		factorials[i] = cal_f(i);
	}

	string n;
	getline(cin, n);
	cerr << n << endl;
	int pos = n.find("/");
	V v1, v2;
	if(pos < 0){
		v1 = cal_n(stoi(n));
	}else{
		char n1[32], n2[32];
		n.copy(n1, pos, 0);
		n.copy(n2, n.size()-pos-1, pos+1);
		v1 = cal_n(atoi(n1));
		v2 = cal_n(atoi(n2));
	}
	v1 -= v2;
	output(v1);
}
