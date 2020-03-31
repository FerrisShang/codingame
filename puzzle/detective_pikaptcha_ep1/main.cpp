/* https://www.codingame.com/ide/puzzle/detective-pikaptcha-ep1 */
#include <bits/stdc++.h>
using namespace std;
int main()
{
    int width;
    int height;
    char line[102][102];
    cin >> width >> height; cin.ignore();
        cerr << width << ' ' << height << endl;
    for (int i=0;i<height;i++) {
        scanf("%s", line[i]);
    }
    for (int i=0;i<height;i++) {
        for(int j=0;j<width;j++){
            if(line[i][j] == '#'){ printf("#"); continue; }
            int ans = 0;
            if((i-1)>=0&&(i-1)<height&&(j-0)>=0&&(j-0)<width && line[i-1][j-0] == '0') ans++;
            if((i-0)>=0&&(i-0)<height&&(j-1)>=0&&(j-1)<width && line[i-0][j-1] == '0') ans++;
            if((i+1)>=0&&(i+1)<height&&(j+0)>=0&&(j+0)<width && line[i+1][j+0] == '0') ans++;
            if((i+0)>=0&&(i+0)<height&&(j+1)>=0&&(j+1)<width && line[i+0][j+1] == '0') ans++;
            printf("%d", ans);
        }
        printf("\n");
    }
}