// have not test. jcc.
//**********************************************************************
// 
//  This program demonstrates how to programmatically stop a service 
//  by first stopping its dependencies.
// 
//  THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
//  ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED
//  TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
//  PARTICULAR PURPOSE.
// 
//  Copyright (C) 1999 Microsoft Corporation. All rights reserved.
// 
//**********************************************************************
 
#include <windows.h>
#include <tchar.h>
#include <stdio.h>
 
 
//**********************************************************************
// 
//  StopService()
// 
//  PURPOSE :     This function attempts to stop a service. It allows
//                the caller to specify whether dependent services
//                should also be stopped. It also allows a timeout
//                value to be passed, to prevent a scenario in which a
//                service shutdown hangs, and in turn the application
//                stopping the service hangs.
// 
//  PARAMETERS:   hSCM - open handle to the service control manager
//                hService - open handle to the service to be stopped
//                fStopDependencies - flag indicating whether to stop
//                   dependent services
//                dwTimeout - maximum time (in milliseconds) to wait
//                   for the service and its dependencies to stop
// 
//  RETURN VALUE: If the operation is successful, ERROR_SUCCESS is 
//                returned. Otherwise, a Win32 error code is returned.
// 
//**********************************************************************
 
DWORD StopService( SC_HANDLE hSCM, SC_HANDLE hService, 
      BOOL fStopDependencies, DWORD dwTimeout ) {
 
   SERVICE_STATUS ss;
   DWORD dwStartTime = GetTickCount();
 
   // Make sure the service is not already stopped
   if ( !QueryServiceStatus( hService, &ss ) )
      return GetLastError();
 
   if ( ss.dwCurrentState == SERVICE_STOPPED ) 
      return ERROR_SUCCESS;
 
   // If a stop is pending, just wait for it
   while ( ss.dwCurrentState == SERVICE_STOP_PENDING ) {
 
      Sleep( ss.dwWaitHint );
      if ( !QueryServiceStatus( hService, &ss ) )
         return GetLastError();
 
      if ( ss.dwCurrentState == SERVICE_STOPPED )
         return ERROR_SUCCESS;
 
      if ( GetTickCount() - dwStartTime > dwTimeout )
         return ERROR_TIMEOUT;
   }
 
   // If the service is running, dependencies must be stopped first
   if ( fStopDependencies ) {
 
      DWORD i;
      DWORD dwBytesNeeded;
      DWORD dwCount;
 
      LPENUM_SERVICE_STATUS   lpDependencies = NULL;
      ENUM_SERVICE_STATUS     ess;
      SC_HANDLE               hDepService;
 
      // Pass a zero-length buffer to get the required buffer size
      if ( EnumDependentServices( hService, SERVICE_ACTIVE, 
         lpDependencies, 0, &dwBytesNeeded, &dwCount ) ) {
 
         // If the Enum call succeeds, then there are no dependent
         // services so do nothing
 
      } else {
         
         if ( GetLastError() != ERROR_MORE_DATA )
            return GetLastError(); // Unexpected error
 
         // Allocate a buffer for the dependencies
         lpDependencies = (LPENUM_SERVICE_STATUS) HeapAlloc( 
               GetProcessHeap(), HEAP_ZERO_MEMORY, dwBytesNeeded );
 
         if ( !lpDependencies )
            return GetLastError();
 
         __try {
 
            // Enumerate the dependencies
            if ( !EnumDependentServices( hService, SERVICE_ACTIVE, 
                  lpDependencies, dwBytesNeeded, &dwBytesNeeded,
                  &dwCount ) )
               return GetLastError();
 
            for ( i = 0; i < dwCount; i++ ) {
 
               ess = *(lpDependencies + i);
 
               // Open the service
               hDepService = OpenService( hSCM, ess.lpServiceName, 
                     SERVICE_STOP | SERVICE_QUERY_STATUS );
               if ( !hDepService )
                  return GetLastError();
 
               __try {
 
                  // Send a stop code
                  if ( !ControlService( hDepService, SERVICE_CONTROL_STOP,
                        &ss ) )
                     return GetLastError();
 
                  // Wait for the service to stop
                  while ( ss.dwCurrentState != SERVICE_STOPPED ) {
 
                     Sleep( ss.dwWaitHint );
                     if ( !QueryServiceStatus( hDepService, &ss ) )
                        return GetLastError();
 
                     if ( ss.dwCurrentState == SERVICE_STOPPED )
                        break;
 
                     if ( GetTickCount() - dwStartTime > dwTimeout )
                        return ERROR_TIMEOUT;
                  }
 
               } __finally {
 
                  // Always release the service handle
                  CloseServiceHandle( hDepService );
 
               }
 
            }
 
         } __finally {
 
            // Always free the enumeration buffer
            HeapFree( GetProcessHeap(), 0, lpDependencies );
 
         }
      } 
   }
 
   // Send a stop code to the main service
   if ( !ControlService( hService, SERVICE_CONTROL_STOP, &ss ) )
      return GetLastError();
 
   // Wait for the service to stop
   while ( ss.dwCurrentState != SERVICE_STOPPED ) {
 
      Sleep( ss.dwWaitHint );
      if ( !QueryServiceStatus( hService, &ss ) )
         return GetLastError();
 
      if ( ss.dwCurrentState == SERVICE_STOPPED )
         break;
 
      if ( GetTickCount() - dwStartTime > dwTimeout )
         return ERROR_TIMEOUT;
   }
 
   // Return success
   return ERROR_SUCCESS;
}
 
 
//**********************************************************************
// 
//  DisplayError()
// 
//  PURPOSE :     This is a helper function to display an error message 
//                if a function in _tmain() fails.
// 
//  PARAMETERS:   szAPI - the name of the function that failed
// 
//                dwError - the Win32 error code indicating why the
//                function failed
// 
//  RETURN VALUE: None
// 
//**********************************************************************
 
void DisplayError( LPTSTR szAPI, DWORD dwError ) {
 
   LPTSTR lpBuffer = NULL;
 
   FormatMessage( FORMAT_MESSAGE_ALLOCATE_BUFFER |
         FORMAT_MESSAGE_FROM_SYSTEM, NULL, dwError,
         MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
         (LPTSTR) &lpBuffer, 0, NULL );
 
   _tprintf( TEXT("%s failed:\n"), szAPI );
   _tprintf( TEXT("    error code = %u\n"), dwError );
   _tprintf( TEXT("    message    = %s\n"), lpBuffer );
 
   LocalFree( lpBuffer );
}
 
 
//**********************************************************************
// 
//  _tmain() -- becomes main() for ANSI or wmain() for Unicode
// 
//  PURPOSE :     This is the entry point for the program. This function
//                contains sample code demonstrating how to use the
//                StopService() function implemented above.
// 
//  PARAMETERS:   argc - the number of command-line arguments
//                argv[] - an array of command-line arguments
// 
//  RETURN VALUE: None
// 
//**********************************************************************
 
void _tmain( int argc, TCHAR *argv[] ) {
 
   SC_HANDLE hSCM;
   SC_HANDLE hService;
   DWORD     dwError;
 
   if ( argc < 2 ) {
      _tprintf( TEXT("usage: \"%s\" <ServiceName>\n"), argv[0] );
      return;
   }
 
   __try {
 
      // Open the SCM database
      hSCM = OpenSCManager( NULL, NULL, SC_MANAGER_CONNECT );
      if ( !hSCM ) {
         DisplayError( TEXT("OpenSCManager()"), GetLastError() );
         __leave;
      }
 
      // Open the specified service
      hService = OpenService( hSCM, argv[1], SERVICE_STOP
            | SERVICE_QUERY_STATUS | SERVICE_ENUMERATE_DEPENDENTS );
      if ( !hService ) {
         DisplayError( TEXT("OpenService()"), GetLastError() );
         __leave;
      }
 
      // Try to stop the service, specifying a 30 second timeout
      dwError = StopService( hSCM, hService, TRUE, 30000 ) ;
      if ( dwError == ERROR_SUCCESS )
         _tprintf( TEXT("Service stopped.\n") );
      else
         DisplayError( TEXT("StopService()"), dwError );
 
   } __finally {
 
      if ( hService )
         CloseServiceHandle( hService );
 
      if ( hSCM )
         CloseServiceHandle( hSCM );
   }
}

