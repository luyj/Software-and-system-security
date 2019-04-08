#include <Windows.h>
#include <stdio.h>
#include <TlHelp32.h>
#include <stddef.h>


// find the target process
bool FindProcess(char process[], int &processId)
{
	bool procRunning = false;
	//get process id
	HANDLE hProcessSnap;
	PROCESSENTRY32 pe32;
	//get processes snapshot
	hProcessSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);

	if (hProcessSnap == INVALID_HANDLE_VALUE)
	{
		procRunning = false;
	}
	else
	{
		pe32.dwSize = sizeof(PROCESSENTRY32);
		if (Process32First(hProcessSnap, &pe32)) //Get First Process
		{
			if (strcmp(process, pe32.szExeFile) == 0)
			{
				procRunning = true;
				processId = pe32.th32ProcessID;
			}
			else
			{
				//loop through all processes looking for target
				while (Process32Next(hProcessSnap, &pe32))
				{
					if (strcmp(process, pe32.szExeFile) == 0)
					{
						procRunning = true;
						processId = pe32.th32ProcessID;
						break;
					}
				}
			}
			// clean the snapshot object
			CloseHandle(hProcessSnap);
		}

	}
	return procRunning;
}
int main()
{
	char DLL[] = "C:\\MyDLL.dll";
	char process[] = "notepad.exe";
	int processId;
	//Find the id of process
	if (false == FindProcess(process, processId))
	{
		printf("failed to find the process\n");
		return 1;
	}
	//Try to open the process
	HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, processId);
	if (NULL == hProcess)
	{
		printf("failed to open the process\n");
		return 1;
	}

	//Allocate memory
	size_t lengthOfDllPath = 1 + strlen(DLL);
	char* processMemory = (char*)VirtualAllocEx(hProcess, NULL, lengthOfDllPath, MEM_COMMIT, PAGE_READWRITE);
	if (NULL == processMemory)
	{
		printf("failed to allocate memory\n");
		return 1;
	}

	//Write path to DLL
	if (NULL == WriteProcessMemory(hProcess, processMemory, (PVOID)DLL, lengthOfDllPath, NULL))
	{
		printf("failed to write path to dll\n");
		return 1;
	}

	//get the address of LoadLibrary fuction
	PTHREAD_START_ROUTINE loadLibraryFunction = (PTHREAD_START_ROUTINE)GetProcAddress(GetModuleHandle(("kernel32")), "LoadLibraryA");
	if (NULL == loadLibraryFunction)
	{
		printf("failed to get the address of LoadLibrary\n");
		return 1;
	}

	//use LoadLibrary to create a remote thread 
	HANDLE remoteThread = CreateRemoteThread(hProcess, NULL, 0, loadLibraryFunction, (PVOID)processMemory, 0, NULL);
	if (NULL == remoteThread)
	{
		printf("failed to create remote thread\n");
		return 1;
	}

	// Wait for the remote thread to terminate
	WaitForSingleObject(remoteThread, INFINITE);
	printf("successful\n");

	VirtualFreeEx(hProcess, (PVOID)processMemory, 0, MEM_RELEASE);
	CloseHandle(remoteThread);
	CloseHandle(hProcess);

	return 0;

}