/* https://www.codingame.com/ide/puzzle/graffiti-on-the-fence */
#include <bits/stdc++.h>
using namespace std;

int main()
{
    int L;
    cin >> L; cin.ignore();
    int N;
    cin >> N; cin.ignore();
    vector<pair<int,int>> painted;
    for (int i = 0; i < N; i++) {
        int st, ed;
        cin >> st >> ed; cin.ignore();
        painted.push_back(pair<int,int>(st, ed));
        //cout << st << ' ' << ed << endl;
    }
    sort(painted.begin(), painted.end());
    int left=-1, right=-1;
    for(auto p: painted){
        if(left == -1){
            if(p.first > 0) printf("%d %d\n", 0, p.first);
            left = p.first, right = p.second;
        }else{
            if(p.first > right){
                printf("%d %d\n", right, p.first);
                left = p.first;
            }
            right = max(right, p.second);
        }
    }
    if(right < L){
        printf("%d %d\n", right, L);
    }else if(left == 0 && right == L){
        puts("All painted");
    }
}