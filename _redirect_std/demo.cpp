#include <stdio.h>
#include<windows.h>
#include<string.h>
#include "redirect_std.h"

#if 1
int main(int argc, char *argv[])
{
	struct redirect_std * rd = CreateRedirect((char*)"D:\\child.exe");
	for(int i=0;i<10;i++){
		char buf[64];
		Sleep(1000);
		sprintf(buf, "num=%d\n", i);
		WriteRedirect(rd, buf);
		ReadRedirect(rd, buf, sizeof(buf));
		printf(buf);
	}
	CloseRedirect(rd);
}
#else // child.exe
int main ()
{
  FILE*    fp;
  CHAR     szInput[1024];
  fp = fopen("CON", "w");
  ZeroMemory(szInput,1024);
  while (TRUE){
     gets(szInput);
     printf("Child echoing [%s]\n",szInput);
     fflush(NULL);  // Must flush output buffers or else redirection will be problematic.
     if (!_stricmp(szInput,"Exit") )
        break;
     ZeroMemory(szInput,strlen(szInput) );
  }
}
#endif
