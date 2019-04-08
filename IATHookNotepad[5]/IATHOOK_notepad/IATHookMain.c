#include <windows.h>

LONG IATHook(
	__in_opt void* pImageBase,
	__in_opt char* pszImportDllName,
	__in char* pszRoutingName,
	__in void* pFakeRouting,
	__out HANDLE* phHook
);

LONG UnIATHook(__in HANDLE hHook);

void* GetIATHookOrign(__in HANDLE hHook);

//__stdcall WindowsAPI调用方式
typedef BOOL(__stdcall *LPFN_WriteFile)(
	HANDLE hFile, 
	LPCVOID lpBuffer, 
	DWORD nNumberOfBytesToWrite,
	LPDWORD lpNumberOfBytesWritten,
	LPOVERLAPPED lpOverlapped
);

HANDLE g_hHook_WriteFile = NULL;

BOOL __stdcall Fake_WriteFile(
	HANDLE hFile,
	LPCVOID lpBuffer,
	DWORD nNumberOfBytesToWrite,
	LPDWORD lpNumberOfBytesWritten,
	LPOVERLAPPED lpOverlapped
)
{
	LPFN_WriteFile fnOrigin = (LPFN_WriteFile)GetIATHookOrign(g_hHook_WriteFile);
	
	char Buffer[] = "you have been hacked!\n";
	DWORD NumberOfBytesToWrite = (DWORD)strlen(Buffer);
	DWORD NumberOfBytesWritten = 0;

	return fnOrigin(hFile, Buffer, NumberOfBytesToWrite, &NumberOfBytesWritten, lpOverlapped);
}

BOOL WINAPI DllMain(HINSTANCE hinstDll, DWORD dwReason, LPVOID lpvRevered) {
	switch (dwReason) {
	case DLL_PROCESS_ATTACH:
		IATHook(
			GetModuleHandle(NULL),
			"kernel32.dll",
			"WriteFile",
			Fake_WriteFile,
			&g_hHook_WriteFile
		);
		break;
	case DLL_PROCESS_DETACH:
		UnIATHook(g_hHook_WriteFile);
		break;
	}
	return TRUE;
}