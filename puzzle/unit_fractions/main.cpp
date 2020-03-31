/* https://www.codingame.com/ide/puzzle/unit-fractions */
#include <bits/stdc++.h>
using namespace std;

int main()
{
    long long n;
    cin >> n; cin.ignore();
    for(int i=n+1;i<=n*2;i++){
        long long up = i - n;
        long long down = i*n;
        if(!(down % up)){
            printf("1/%lld = 1/%lld + 1/%lld\n", n, down/up, i);
        }
    }
}