// https://www.codingame.com/ide/puzzle/dwarfs-standing-on-the-shoulders-of-giants
#include "bits/stdc++.h"
using namespace std;

#define N 10000
vector<vector<int>> m;
int flag[N];

int bfs(vector<int> vec)
{
    int res = 1;
    for(auto i : vec){
        if(flag[i]) res = max(res, flag[i]);
        else if(m[i].size() == 0){ flag[i] = 1; res = max(res, 1); }
        else{
            res = max(res, 1+bfs(m[i]));
        }
    }
    return res;
}

int main(void)
{
    m.resize(N);
    int n; cin >> n;
    for(int i=0;i<n;i++){
        int a, b;
        cin >> a >> b;
        m[a].push_back(b);
    }
    for(int i=0;i<N;i++){
        vector<int> vec = {i};
        flag[i] = bfs(vec);
    }
    cout << *max_element(flag, flag+N) << endl;
}