#include <windows.h>
#include <stdio.h>

BOOL WINAPI DllMain(HINSTANCE hinstDll, DWORD dwReason, LPVOID lpvRevered) {
	switch (dwReason) {
	case DLL_PROCESS_ATTACH:
		MessageBoxA(NULL, "successful!", "test", NULL);
		break;
	}
	return TRUE;
}