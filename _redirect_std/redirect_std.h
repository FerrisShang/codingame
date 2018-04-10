/* ref: https://support.microsoft.com/en-us/help/190351/how-to-spawn-console-processes-with-redirected-standard-handles */
#ifndef __REDIRECT_STD_H__
#define __REDIRECT_STD_H__

struct redirect_std;

struct redirect_std* CreateRedirect(char *path);
int WriteRedirect(struct redirect_std *redirect_std, char *str);
int ReadRedirect(struct redirect_std *redirect_std, char *lpBuffer, int len);
void CloseRedirect(struct redirect_std *redirect_std);

#endif
