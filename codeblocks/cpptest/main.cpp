// Windows Service main application
// Add your code where necessary to create your own windows service application.
/*
sc create SERVICE_NAME binPath= FULL_PATH_TO_EXE_FILE
To uninstall it:

sc delete SERVICE_NAME
To control your service - start it, stop it or query its status - use commands:

sc start SERVICE_NAME
sc stop SERVICE_NAME
sc query SERVICE_NAME
*/

#include <windows.h>
#include <stdio.h>

#include "RcLogInfo.h"

// Some global vars
SERVICE_STATUS          gStatus;
SERVICE_STATUS_HANDLE   gStatusHandle;
HANDLE                  ghStopEvent = NULL;

RcLogInfo rl;
timeb aTime;

RcLogInfo::RcLogInfo(void)
{
    m_pfLogFile = NULL;
    memset(m_cInfo,NULL,sizeof(m_cInfo));
}

RcLogInfo::~RcLogInfo(void)
{
    if (NULL != m_pfLogFile)
    {
        fclose(m_pfLogFile);
        m_pfLogFile = NULL;
    }
}

int RcLogInfo::SetLogFile(FILE *pfLogFile)
{
    m_pfLogFile=pfLogFile;
    return 0;
}

int RcLogInfo::WriteLogInfo(const char *pInfo)
{
    if(NULL != m_pfLogFile)
    {
        fprintf(m_pfLogFile,"%s",pInfo);
        fflush(m_pfLogFile);
        return 0;
    }
    return 1;


}

// Replace with your own
#define NAME_IN_SERVICES TEXT("AMService")
#define MY_SERVICE_DESC TEXT("AutoMailService.work OK.")
#define DAEMON_EXE_NAME "C:\\test\\notepad.exe"
SERVICE_STATUS_HANDLE g_ServiceStatusHandle;
HANDLE g_StopEvent;
DWORD g_CurrentState = 0;
bool g_SystemShutdown = false;


void ReportStatus(DWORD state)
{
    g_CurrentState = state;
    SERVICE_STATUS serviceStatus = {
        SERVICE_WIN32_OWN_PROCESS,
        g_CurrentState,
        state == SERVICE_START_PENDING ? 0 : SERVICE_ACCEPT_STOP | SERVICE_ACCEPT_SHUTDOWN,
        NO_ERROR,
        0,
        0,
        0,
    };
    SetServiceStatus(g_ServiceStatusHandle, &serviceStatus);
}


// Handler for service control events.
DWORD WINAPI HandlerEx(DWORD control, DWORD eventType, void *eventData, void *context)
{
    switch (control)
    {
    // Entrie system is shutting down.
    case SERVICE_CONTROL_SHUTDOWN:
        g_SystemShutdown = true;
        // continue...
    // Service is being stopped.
    case SERVICE_CONTROL_STOP:
        ReportStatus(SERVICE_STOP_PENDING);
        SetEvent(g_StopEvent);
        break;
    // Ignoring all other events, but we must always report service status.
    default:
        ReportStatus(g_CurrentState);
        break;
    }
    return NO_ERROR;
}
void ReportErrorStatus(DWORD errorCode)
{
    g_CurrentState = SERVICE_STOPPED;
    SERVICE_STATUS serviceStatus = {
        SERVICE_WIN32_OWN_PROCESS,
        g_CurrentState,
        0,
        ERROR_SERVICE_SPECIFIC_ERROR,
        errorCode,
        0,
        0,
    };
    SetServiceStatus(g_ServiceStatusHandle, &serviceStatus);
}

void ReportProgressStatus(DWORD state, DWORD checkPoint, DWORD waitHint)
{
    g_CurrentState = state;
    SERVICE_STATUS serviceStatus = {
        SERVICE_WIN32_OWN_PROCESS,
        g_CurrentState,
        state == SERVICE_START_PENDING ? 0 : SERVICE_ACCEPT_STOP | SERVICE_ACCEPT_SHUTDOWN,
        NO_ERROR,
        0,
        checkPoint,
        waitHint,
    };
    SetServiceStatus(g_ServiceStatusHandle, &serviceStatus);
}


// Main function to be executed as entire service code.
void WINAPI ServiceMain(DWORD argc, LPTSTR *argv)
{
    // Must be called at start.
    g_ServiceStatusHandle = RegisterServiceCtrlHandlerEx("aSERVICENAME", &HandlerEx, NULL);

    // Startup code.
    ReportStatus(SERVICE_START_PENDING);
    g_StopEvent = CreateEvent(NULL, TRUE, FALSE, NULL);
    /* Here initialize service...
    Load configuration, acquire resources etc. */
    ReportStatus(SERVICE_RUNNING);

    /* Main service code
    Loop, do some work, block if nothing to do,
    wait or poll for g_StopEvent... */
    while (WaitForSingleObject(g_StopEvent, 4000) != WAIT_OBJECT_0)
    {
        // This sample service does "BEEP!" every 4 seconds.
        //Beep(1000, 100);
        ftime(&aTime);
        sprintf(rl.m_cInfo,"%s am running..",ctime(&(aTime.time)));
        rl.WriteLogInfo(rl.m_cInfo);
    WinExec("c:\\windows\\notepad.exe",SW_NORMAL);
    }

    ReportStatus(SERVICE_STOP_PENDING);
    /* Here finalize service...
    Save all unsaved data etc., but do it quickly.
    If g_SystemShutdown, you can skip freeing memory etc. */
    CloseHandle(g_StopEvent);
    ReportStatus(SERVICE_STOPPED);
}
// Standard console application entry point.
int main(int argc, char **argv)
{
    char cPath[MAX_PATH];
    memset(cPath,0,MAX_PATH);
    if (!GetModuleFileName(NULL,cPath,MAX_PATH))
    {
        return false;
    }
    char *FileName = cPath + strlen(cPath)-1;
    while(*FileName !='\\')
    {
        --FileName;
    }
    *FileName = '\0';
    char cFileName[MAX_PATH]={'\0'};
    sprintf(cFileName,"%s\\%s",cPath,"TestLog.log");

    FILE *m_pfLogFile=NULL;
    if(NULL != m_pfLogFile)
    {
        fclose(m_pfLogFile);
    }
    m_pfLogFile = fopen(cFileName,"at+");
    if(NULL == m_pfLogFile)
    {
        return 1;
    }


    rl.SetLogFile(m_pfLogFile);

    ftime(&aTime);
    sprintf(rl.m_cInfo,"%s am start...",ctime(&(aTime.time)));
    rl.WriteLogInfo(rl.m_cInfo);




    SERVICE_TABLE_ENTRY serviceTable[] = {
        { "", &ServiceMain },
        { NULL, NULL }
    };

    if (StartServiceCtrlDispatcher(serviceTable))
        return 0;
    else if (GetLastError() == ERROR_FAILED_SERVICE_CONTROLLER_CONNECT)
        return -1; // Program not started as a service.
    else
        return -2; // Other error.
}
