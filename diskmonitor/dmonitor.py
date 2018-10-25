#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wmi
import time
import win32serviceutil
import win32service
import win32event
import win32api
import configparser
import easygui



config = configparser.ConfigParser()
# 读取配置文件
config.read("c:\\dmonitor\\disk monitor.ini")
scan_time = int(config.get("DISK_MONITOR", "scan_time"))
Alarm_threshold = config.get("DISK_MONITOR", "Alarm threshold")



def disk_process():
    logname = open("c:\\dmonitor\\scanlog.txt", "a+")
    print(time.asctime(time.localtime(time.time())),file=logname)
    try:
        c = wmi.WMI()
        # 获取硬盘使用百分情况
        for disk in c.Win32_LogicalDisk(DriveType=3):
            a = round(int(disk.FreeSpace) / (1024 * 1024 * 1024), 2)
            b = "%0.2f%%" % (100.0 * float(disk.FreeSpace) / float(disk.Size))
            print("盘符：",disk.Caption,"剩余磁盘空间：", a, "G","剩余磁盘磁盘空间百分比：",b,file=logname)
            #win32api.MessageBox(0, duplicated, "磁盘空间容量过低告警")
            if b <= "%0.2f%%" % float(Alarm_threshold):
                #win32api.MessageBox(0, duplicated, "磁盘空间容量过低告警")
                duplicated = "盘符：" + disk.Caption + "剩余磁盘空间：" + str(a) + "G" + "剩余磁盘磁盘空间百分比：" + str(b)
                easygui.msgbox("", u"磁盘空间容量过低告警", image ="c:\\dmonitor\\alarm.png")
                win32api.MessageBox(0, duplicated, "磁盘空间容量过低告警")
        logname.close()
    except Exception as e:
        print(e,file=logname)
        logname.close()
    




class PythonService(win32serviceutil.ServiceFramework):
    # class PythonService():
    _svc_name_ = "DiskServicea"
    # 服务显示名称
    _svc_display_name_ = "Disk monitor servicea"
    # 服务描述
    _svc_description_ = "Disk monitora"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.logger = self._getLogger()
        self.isAlive = True
        self.ftp = None
        self.logger.info('init...')


        self.logger.info('init.OK..')

    def __del__(self):
        pass

    def _getLogger(self):
        import logging
        import os
        import inspect

        logger = logging.getLogger('[PythonService]')

        this_file = inspect.getfile(inspect.currentframe())
        dirpath = os.path.abspath(os.path.dirname(this_file))
        handler = logging.FileHandler(os.path.join(dirpath, "disk_service.log"))

        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        return logger



    def SvcDoRun(self):
        #        import time
        self.logger.error("svc do run....")
        self.logger.error("0")

        while self.isAlive:
            self.logger.error("I am alive！！！！！！！！！.")
            self.logger.error("1,start scan")
            disk_process()
#            self.logname.close()
            self.logger.error("2,sleep")
            time.sleep(5)

    def SvcStop(self):
        # 先告诉SCM停止这个过程
        self.logger.error("svc do stop....")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        # 设置事件
        win32event.SetEvent(self.hWaitStop)
        self.isAlive = False

if __name__ == '__main__':
    while True:
        #print(scan_time)
        time.sleep(scan_time)
        disk_process()
