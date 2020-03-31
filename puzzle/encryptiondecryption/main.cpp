/* https://www.codingame.com/ide/puzzle/encryptiondecryption-of-enigma-machine */
#include <bits/stdc++.h>
using namespace std;

int main()
{
    string Operation;
    cin >> Operation;
    int offset;
    cin >> offset;
    char rotor[3][100], message[100];
    for(int i=0;i<3;i++) scanf("%s", rotor[i]);
    scanf("%s", message);
    if(Operation == string("ENCODE")){
        for(int i=0;i<strlen(message);i++){
            message[i] = 'A' + ((message[i] - 'A' + i+offset) % 26);
            for(int j=0;j<3;j++) message[i] = rotor[j][message[i]-'A'];
        }
    }else{
        char derotor[3][100];
        for(int i=0;i<3;i++) for(int j=0;j<26;j++){
            derotor[2-i][rotor[i][j]-'A'] = j + 'A';
        }
        for(int i=0;i<strlen(message);i++){
            for(int j=0;j<3;j++) message[i] = derotor[j][message[i]-'A'];
            message[i] = 'A' + ((message[i] - 'A' +26*100-(i+offset)) % 26);
        }
    }
    puts(message);
}