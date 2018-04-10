/* ref: https://support.microsoft.com/en-us/help/190351/how-to-spawn-console-processes-with-redirected-standard-handles */
#include <windows.h>
#include <stdio.h>
#define DisplayError(msg) do{puts("ERROR: " msg); system("pause"); exit(0);}while(0)

struct redirect_std {
	HANDLE hOutputRead,hOutputWrite;
	HANDLE hInputRead,hInputWrite;
};
static HANDLE PrepAndLaunchRedirectedChild(HANDLE hChildStdOut,
								  HANDLE hChildStdIn,
								  HANDLE hChildStdErr,
								  char *path);

HANDLE hStdIn = NULL; // Handle to parents std input.


struct redirect_std* CreateRedirect(char *path)
{
	struct redirect_std *redirect_std = (struct redirect_std*)malloc(sizeof(struct redirect_std));
	HANDLE hOutputReadTmp;
	HANDLE hInputWriteTmp;
	HANDLE hErrorWrite;
	SECURITY_ATTRIBUTES sa;


	// Set up the security attributes struct.
	sa.nLength= sizeof(SECURITY_ATTRIBUTES);
	sa.lpSecurityDescriptor = NULL;
	sa.bInheritHandle = TRUE;


	// Create the child output pipe.
	if (!CreatePipe(&hOutputReadTmp,&redirect_std->hOutputWrite,&sa,0)) {
		DisplayError("CreatePipe");
	}


	// Create a duplicate of the output write handle for the std error
	// write handle. This is necessary in case the child application
	// closes one of its std output handles.
	if (!DuplicateHandle(GetCurrentProcess(),redirect_std->hOutputWrite,
						 GetCurrentProcess(),&hErrorWrite,0,
						 TRUE,DUPLICATE_SAME_ACCESS)) {
		DisplayError("DuplicateHandle");
	}


	// Create the child input pipe.
	if (!CreatePipe(&redirect_std->hInputRead,&hInputWriteTmp,&sa,0)) {
		DisplayError("CreatePipe");
	}


	// Create new output read handle and the input write handles. Set
	// the Properties to FALSE. Otherwise, the child inherits the
	// properties and, as a result, non-closeable handles to the pipes
	// are created.
	if (!DuplicateHandle(GetCurrentProcess(),hOutputReadTmp,
						 GetCurrentProcess(),
						 &redirect_std->hOutputRead, // Address of new handle.
						 0,FALSE, // Make it uninheritable.
						 DUPLICATE_SAME_ACCESS)) {
		DisplayError("DupliateHandle");
	}

	if (!DuplicateHandle(GetCurrentProcess(),hInputWriteTmp,
						 GetCurrentProcess(),
						 &redirect_std->hInputWrite, // Address of new handle.
						 0,FALSE, // Make it uninheritable.
						 DUPLICATE_SAME_ACCESS)) {
		DisplayError("DupliateHandle");
	}


	// Close inheritable copies of the handles you do not want to be
	// inherited.
	if (!CloseHandle(hOutputReadTmp)) {
		DisplayError("CloseHandle");
	}
	if (!CloseHandle(hInputWriteTmp)) {
		DisplayError("CloseHandle");
	}


	// Get std input handle so you can close it and force the ReadFile to
	// fail when you want the input thread to exit.
	if ( (hStdIn = GetStdHandle(STD_INPUT_HANDLE)) ==
		 INVALID_HANDLE_VALUE ) {
		DisplayError("GetStdHandle");
	}

	PrepAndLaunchRedirectedChild(redirect_std->hOutputWrite,redirect_std->hInputRead,hErrorWrite, path);
	// Close pipe handles (do not continue to modify the parent).
	// You need to make sure that no handles to the write end of the
	// output pipe are maintained in this process or else the pipe will
	// not close when the child process exits and the ReadFile will hang.
	if (!CloseHandle(redirect_std->hOutputWrite)) {
		DisplayError("CloseHandle");
	}
	if (!CloseHandle(redirect_std->hInputRead )) {
		DisplayError("CloseHandle");
	}
	if (!CloseHandle(hErrorWrite)) {
		DisplayError("CloseHandle");
	}
	return redirect_std;
}

void CloseRedirect(struct redirect_std *redirect_std)
{
	// Force the read on the input to return by closing the stdin handle.
	if (!CloseHandle(hStdIn)) {
		DisplayError("CloseHandle");
	}
//	if (WaitForSingleObject(hThread,INFINITE) == WAIT_FAILED) {
//		DisplayError("WaitForSingleObject");
//	}
	if (!CloseHandle(redirect_std->hOutputRead)) {
		DisplayError("CloseHandle");
	}
	if (!CloseHandle(redirect_std->hInputWrite)) {
		DisplayError("CloseHandle");
	}
	free(redirect_std);
}

///////////////////////////////////////////////////////////////////////
// PrepAndLaunchRedirectedChild
// Sets up STARTUPINFO structure, and launches redirected child.
///////////////////////////////////////////////////////////////////////
static HANDLE PrepAndLaunchRedirectedChild(HANDLE hChildStdOut,
								  HANDLE hChildStdIn,
								  HANDLE hChildStdErr,
								  char *path)
{
	PROCESS_INFORMATION pi;
	STARTUPINFO si;

	// Set up the start up info struct.
	ZeroMemory(&si,sizeof(STARTUPINFO));
	si.cb = sizeof(STARTUPINFO);
	si.dwFlags = STARTF_USESTDHANDLES;
	si.hStdOutput = hChildStdOut;
	si.hStdInput  = hChildStdIn;
	si.hStdError  = hChildStdErr;
	// Use this if you want to hide the child:
	//     si.wShowWindow = SW_HIDE;
	// Note that dwFlags must include STARTF_USESHOWWINDOW if you want to
	// use the wShowWindow flags.


	// Launch the process that you want to redirect (in this case,
	// Child.exe). Make sure Child.exe is in the same directory as
	// redirect.c launch redirect from a command line to prevent location
	// confusion.
	if (!CreateProcess(NULL,path,NULL,NULL,TRUE,
					   CREATE_NEW_CONSOLE,NULL,NULL,&si,&pi)) {
		DisplayError("CreateProcess");
	}


	// Set global child process handle to cause threads to exit.
	HANDLE hChildProcess = pi.hProcess;


	// Close any unnecessary handles.
	if (!CloseHandle(pi.hThread)) {
		DisplayError("CloseHandle");
	}
	return hChildProcess;
}


///////////////////////////////////////////////////////////////////////
// ReadAndHandleOutput
// Monitors handle for input. Exits when child exits or pipe breaks.
///////////////////////////////////////////////////////////////////////
int ReadRedirect(struct redirect_std *redirect_std, char *lpBuffer, int len)
{
	DWORD nBytesRead;
	DWORD nCharsWritten;
	if (!ReadFile(redirect_std->hOutputRead,lpBuffer,len,
				  &nBytesRead,NULL) || !nBytesRead) {
		if (GetLastError() == ERROR_BROKEN_PIPE) {
			DisplayError("pipe done");    // pipe done - normal exit path.
		} else {
			DisplayError("ReadFile");    // Something bad happened.
		}
	}
	return nBytesRead;
}


///////////////////////////////////////////////////////////////////////
// GetAndSendInputThread
// Thread procedure that monitors the console for input and sends input
// to the child process through the input pipe.
// This thread ends when the child application exits.
///////////////////////////////////////////////////////////////////////
int WriteRedirect(struct redirect_std *redirect_std, char *str)
{
	DWORD nBytesWrote;
	if (!WriteFile(redirect_std->hInputWrite,str,strlen(str),&nBytesWrote,NULL)) {
		if (GetLastError() == ERROR_NO_DATA) {
			DisplayError("Pipe was closed");
		} else {
			DisplayError("WriteFile");
		}
	}
	return nBytesWrote;
}


