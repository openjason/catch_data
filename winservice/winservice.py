'''

 Author: Alex Baker
 Date: 7th July 2008
 Description : Simple python program to generate wrap as a service based on example on the web, see link below.

 http://essiene.blogspot.com/2005/04/python-windows-services.html

 Usage : python aservice.py install
 Usage : python aservice.py start
 Usage : python aservice.py stop
 Usage : python aservice.py remove

 C:\>python aservice.py  --username <username> --password <PASSWORD> --startup auto install

'''

import win32service
import win32serviceutil
import win32api
import win32con
import win32event
import win32evtlogutil
import os


class aservice(win32serviceutil.ServiceFramework):
    _svc_name_ = "aservice"
    _svc_display_name_ = "a service - it does nothing"
    _svc_description_ = "Tests Python service framework by receiving and echoing messages over a named pipe"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        import servicemanager
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))

        self.timeout = 3000

        while 1:
            # Wait for service stop signal, if I timeout, loop again
            rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
            # Check to see if self.hWaitStop happened
            if rc == win32event.WAIT_OBJECT_0:
                # Stop signal encountered
                servicemanager.LogInfoMsg("aservice - STOPPED")
                break
            else:
                servicemanager.LogInfoMsg("aservice - is alive and well")


def ctrlHandler(ctrlType):
    return True


if __name__ == '__main__':
    win32api.SetConsoleCtrlHandler(ctrlHandler, True)
    win32serviceutil.HandleCommandLine(aservice)
#
#
#
# #ZPF
# #encoding=utf-8
# import win32serviceutil
# import win32service
# import win32event
# import os
# import sys
# import logging
# import inspect
# import time
#
# class PythonService(win32serviceutil.ServiceFramework):
#
#     _svc_name_ = "PythonService"
#     _svc_display_name_ = "Python Service Test"
#     _svc_description_ = "This is a python service test code "
#
#     def __init__(self, args):
#         win32serviceutil.ServiceFramework.__init__(self, args)
#         self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
#         self.logger = self._getLogger()
#         self.run = True
#
#     def _getLogger(self):
#
#         logger = logging.getLogger('[PythonService]')
#
#         this_file = inspect.getfile(inspect.currentframe())
#         dirpath = os.path.abspath(os.path.dirname(this_file))
#         handler = logging.FileHandler(os.path.join(dirpath, "service.log"))
#
#         formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
#         handler.setFormatter(formatter)
#
#         logger.addHandler(handler)
#         logger.setLevel(logging.INFO)
#
#         return logger
#
#     def SvcDoRun(self):
#         self.logger.info("service is run....")
#         while self.run:
#             self.logger.info("I am runing....")
#             time.sleep(2)
#
#     def SvcStop(self):
#         self.logger.info("service is stop....")
#         self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
#         win32event.SetEvent(self.hWaitStop)
#         self.run = False
#
# if __name__=='__main__':
#     win32serviceutil.HandleCommandLine(PythonService)
#
#
