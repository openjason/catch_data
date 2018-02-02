import win32serviceutil
import win32service
import win32event
import os, sys, shutil, time
from ftplib import FTP
import configparser
import zipfile
import datetime
import servicemanager


# this_day = time.strftime('%Y%m%d-%H%M%S', time.localtime(time.time()))
# 日志存储位置
# logname = open("E:\\日志同步\\log.txt", "a+")



class PythonService(win32serviceutil.ServiceFramework):
    # class PythonService():
    _svc_name_ = "aaPythonService222"
    # 服务显示名称
    _svc_display_name_ = "Production LOG"
    # 服务描述
    _svc_description_ = "Python service demo."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.logger = self._getLogger()
        self.isAlive = True
        self.ftp = None
        self.logger.info('init...')
        self.newfile_path = ''

        #        self.logname = open("E:\\日志同步\\log.txt", "a+")
        self.rootdir = "D:\\日志同步"
        self.this_day = time.strftime('%Y%m%d-%H%M%S', time.localtime(time.time()))

        self.config = configparser.ConfigParser()
        # 读取配置文件
        self.config.read("D:\\日志同步\\config rizhitongbu.ini")

        # 获取日志路径
        # MX6100\MX6000设备的日志
        self.path_1 = self.config.get("MX_6000_path", "path1")
        self.path_2 = self.config.get("MX_6000_path", "path2")
        self.path_3 = self.config.get("MX_6000_path", "path3")
        self.path_4 = self.config.get("MX_6000_path", "path4")
        self.path_5 = self.config.get("MX_6000_path", "path5")
        self.path_23 = self.config.get("MX_6000_path", "path23")
        self.path_24 = self.config.get("MX_6000_path", "path24")

        # MX6100\MX6000设备输出日志
        self.path_13 = self.config.get("MX_6000_path", "path13")

        # 明森HDP5000设备路径
        self.path_6 = self.config.get("MINGSHEN_path", "path6")
        self.path_7 = self.config.get("MINGSHEN_path", "path7")

        # 明森HDP5000设备输出路径
        self.path_14 = self.config.get("MINGSHEN_path", "path14")

        # 明森MS5000设备路径
        self.path_8 = self.config.get("MINGSHEN5000_path", "path8")
        self.path_9 = self.config.get("MINGSHEN5000_path", "path9")
        self.path_10 = self.config.get("MINGSHEN5000_path", "path10")
        self.path_11 = self.config.get("MINGSHEN5000_path", "path11")
        self.path_12 = self.config.get("MINGSHEN5000_path", "path12")
        self.path_16 = self.config.get("MINGSHEN5000_path", "path16")
        self.path_17 = self.config.get("MINGSHEN5000_path", "path17")
        self.path_18 = self.config.get("MINGSHEN5000_path", "path18")
        self.path_19 = self.config.get("MINGSHEN5000_path", "path19")
        self.path_20 = self.config.get("MINGSHEN5000_path", "path20")
        self.path_21 = self.config.get("MINGSHEN5000_path", "path21")
        self.path_22 = self.config.get("MINGSHEN5000_path", "path22")

        # 明森MS5000设备输出路径
        self.path_15 = self.config.get("MINGSHEN5000_path", "path15")

        # 日志转移后存储路径
        self.mov_des = self.config.get("MX_6000_des", "des_folder")

        # 获取FTP的登陆信息
        self.FTP_IP = self.config.get("FTP_info", "IP")
        self.FTP_USER = self.config.get("FTP_info", "user")
        self.FTP_PASSWORD = self.config.get("FTP_info", "password")
        self.FTP_PORT = self.config.get("FTP_info", "port")

        self._XFER_FILE = 'FILE'
        self._XFER_DIR = 'DIR'
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
        handler = logging.FileHandler(os.path.join(dirpath, "service.log"))

        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        return logger

    def datafloder(self):
        #        global self.newfile_path
        self.this_day = time.strftime('%Y%m%d-%H%M%S', time.localtime(time.time()))
        self.newfile_path = os.path.join(self.mov_des, self.this_day)
        print('creat newfile_path:' + self.newfile_path)
        self.logger.info(self.newfile_path)
        os.makedirs(self.newfile_path)
        print(self.this_day, ":", "新建日期文件成功", file=self.logname)

    def shenjilog_MX6000(self, path_1):
        if self.path_1=="":
            return

        file_list = os.listdir(self.path_1)  # 该文件夹下所有的文件（包括文件夹）

        shenji = "制卡审计日志_MX6000"
        #    self.newfile_path+"\\"+shenji
        folder_name1 = os.path.join(self.newfile_path, shenji)

        os.mkdir(folder_name1)  # 新建一个名称为“制卡审计日志”的文件夹
        print(self.this_day, ":", "新建‘制卡审计日志_MX6000’文件夹成功", file=self.logname)
        for file_obj1 in file_list:  # 遍历所有文件
            file_path1 = os.path.join(self.path_1, file_obj1)  # 原来的文件路径
            try:
                shutil.move(file_path1, folder_name1)
            except:
                print("file was used!", file_path1)
                pass
            print(self.this_day, ":", "制卡审计日志_MX6000移动成功", "文件名为:", file_path1, file=self.logname)

    def IClog_MX6000(self, path_2):
        if self.path_2=="":
            return
        # 移动“D:\Mx6KPersoLogFile\”目录下的“生产程序IC制卡日志（.log)”需要对文件的扩展名进行筛选后移动
        file_list = os.listdir(self.path_2)  # 该文件夹下所有的文件（包括文件夹）

        shengchanchengxu = "生产程序IC制卡日志_MX6000"
        folder_name1 = os.path.join(self.newfile_path, shengchanchengxu)
        os.mkdir(folder_name1)  # 新建一个名称为“制生产程序IC制卡日志”的文件夹

        print(self.this_day, ":", "新建‘生产程序IC制卡日志_MX6000’文件夹成功", file=self.logname)
        for file_obj in file_list:  # 遍历所有文件
            file_path = os.path.join(self.path_2, file_obj)  # 原来的文件路径
            if os.path.isdir(file_path):  # 如果是文件夹则跳过
                continue
            file_extend = os.path.splitext(file_obj)[1]
            if file_extend.find(".log") >= 0:  # 如果文件后缀中含有.log和.fdx
                try:
                    shutil.move(file_path, folder_name1)
                except:
                    print("file was used!", file_path)
                    pass
            if file_extend.find(".LOG") >= 0:  # 如果文件后缀中含有.log和.fdx
                try:
                    shutil.move(file_path, folder_name1)
                except:
                    print("file was used!", file_path)
                    pass
            if file_extend.find(".Log") >= 0:  # 如果文件后缀中含有.log和.fdx
                try:
                    shutil.move(file_path, folder_name1)
                except:
                    print("file was used!", file_path)
                    pass
                print(self.this_day, ":", "生产程序IC制卡日志_MX6000（.log格式）移动成功", "文件名为:", file_path, file=self.logname)

    def IClog_MX6000_2_win7(self, path_23):
        if self.path_23=="":
            return
        # 移动“D:\Mx6KPersoLogFile\”目录下的“生产程序IC制卡日志（.log)”需要对文件的扩展名进行筛选后移动
        file_list = os.listdir(self.path_23)  # 该文件夹下所有的文件（包括文件夹）

        shengchanchengxu1 = "生产程序IC制卡日志_MX6000(win7系统C盘）"
        folder_name1 = os.path.join(self.newfile_path, shengchanchengxu1)
        os.mkdir(folder_name1)  # 新建一个名称为“制生产程序IC制卡日志”的文件夹

        print(self.this_day, ":", "新建‘生产程序IC制卡日志_MX6000(win7系统C盘）’文件夹成功", file=self.logname)
        for file_obj in file_list:  # 遍历所有文件
            file_path = os.path.join(self.path_23, file_obj)  # 原来的文件路径
            if os.path.isdir(file_path):  # 如果是文件夹则跳过
                continue
            file_extend = os.path.splitext(file_obj)[1]
            if file_extend.find(".log") >= 0:  # 如果文件后缀中含有.log和.fdx
                try:
                    shutil.move(file_path, folder_name1)
                except:
                    print("file was used!", file_path)
                    pass
            if file_extend.find(".LOG") >= 0:  # 如果文件后缀中含有.log和.fdx
                try:
                    shutil.move(file_path, folder_name1)
                except:
                    print("file was used!", file_path)
                    pass
            if file_extend.find(".Log") >= 0:  # 如果文件后缀中含有.log和.fdx
                try:
                    shutil.move(file_path, folder_name1)
                except:
                    print("file was used!", file_path)
                    pass
                print(self.this_day, ":", "生产程序IC制卡日志_MX6000(win7系统C盘）（.log格式）移动成功", "文件名为:", file_path, file=self.logname)

    def IClog_MX6000_3_winXP(self, path_24):
        if self.path_24 == "":
            return
        # 移动“D:\Mx6KPersoLogFile\”目录下的“生产程序IC制卡日志（.log)”需要对文件的扩展名进行筛选后移动
        file_list = os.listdir(self.path_24)  # 该文件夹下所有的文件（包括文件夹）

        shengchanchengxu2 = "生产程序IC制卡日志_MX6000(winXP系统C盘）"
        folder_name1 = os.path.join(self.newfile_path, shengchanchengxu2)
        os.mkdir(folder_name1)  # 新建一个名称为“制生产程序IC制卡日志”的文件夹

        print(self.this_day, ":", "新建‘生产程序IC制卡日志_MX6000(winXP系统C盘）’文件夹成功", file=self.logname)
        for file_obj in file_list:  # 遍历所有文件
            file_path = os.path.join(self.path_24, file_obj)  # 原来的文件路径
            if os.path.isdir(file_path):  # 如果是文件夹则跳过
                continue
            file_extend = os.path.splitext(file_obj)[1]
            if file_extend.find(".log") >= 0:  # 如果文件后缀中含有.log和.fdx
                try:
                    shutil.move(file_path, folder_name1)
                except:
                    print("file was used!", file_path)
                    pass
            if file_extend.find(".LOG") >= 0:  # 如果文件后缀中含有.log和.fdx
                try:
                    shutil.move(file_path, folder_name1)
                except:
                    print("file was used!", file_path)
                    pass
            if file_extend.find(".Log") >= 0:  # 如果文件后缀中含有.log和.fdx
                try:
                    shutil.move(file_path, folder_name1)
                except:
                    print("file was used!", file_path)
                    pass
                print(self.this_day, ":", "生产程序IC制卡日志_MX6000(winXP系统C盘）（.log格式）移动成功", "文件名为:", file_path,file=self.logname)

    def HSMlog_MX6000(self, path_3):
        if self.path_3=="":
            return
        # 移动“D:\Mx6KPersoLogFile\”目录下的“加密机日志（.Fdx）”文件，需要对文件的扩展名进行筛选后移动
        file_list = os.listdir(self.path_3)  # 该文件夹下所有的文件（包括文件夹）
        self.logger.info(self.path_3)
        jiamiji = "加密机日志_MX6000"
        folder_name2 = os.path.join(self.newfile_path, jiamiji)
        self.logger.info(folder_name2)
        os.mkdir(folder_name2)  # 新建一个名称为“加密机日志”的文件夹
        print(self.this_day, ":", "新建‘加密机日志_MX6000’文件夹成功", file=self.logname)
        self.logger.info(self.this_day)
        for file_obj in file_list:  # 遍历所有文件
            file_path = os.path.join(self.path_3, file_obj)  # 原来的文件路径
            if os.path.isdir(file_path):  # 如果是文件夹则跳过
                continue
            file_extend = os.path.splitext(file_obj)[1]
            if file_extend.find(".fdx") >= 0:  # 如果文件后缀中含有.log和.fdx
                try:
                    shutil.move(file_path, folder_name2)
                except:
                    print("file was used!", file_path)
                    pass
            if file_extend.find(".FDX") >= 0:  # 如果文件后缀中含有.log和.fdx
                try:
                    shutil.move(file_path, folder_name2)
                except:
                    print("file was used!", file_path)
                    pass
            if file_extend.find(".Fdx") >= 0:  # 如果文件后缀中含有.log和.fdx
                try:
                    shutil.move(file_path, folder_name2)
                except:
                    print("file was used!", file_path)
                    pass
                print(self.this_day, ":", "加密机日志（.Fdx格式）_MX6000移动成功", "文件名为:", file_path, file=self.logname)

    def gonghangIClog_MX6000(self, path_4):
        if self.path_4=="":
            return
        # 移动“E:\Program Files\DataCard\”目录下的“社保（工行）金融IC日志（MakeCard_Log开头）”，需要对文件名称进行筛选后移动

        file_list2 = os.listdir(self.path_4)  # 该文件夹下所有的文件（包括文件夹）

        gonghang = "社保（工行）金融IC日志_MX6000"
        folder_name3 = os.path.join(self.newfile_path, gonghang)
        os.mkdir(folder_name3)  # 新建一个名称为“社保（工行）金融IC日志”的文件夹
        print(self.this_day, ":", "新建‘社保（工行）金融IC日志_MX6000’文件夹成功", file=self.logname)
        for file_obj2 in file_list2:  # 遍历所有文件
            file_path2 = os.path.join(self.path_4, file_obj2)  # 原来的文件路径
            if os.path.isdir(file_path2):  # 如果是文件夹则跳过
                continue
            file_name2 = os.path.splitext(file_obj2)[0]

            if file_name2.find("MakeCard_Log") >= 0:  # 如果文件中含有MakeCard_Log
                try:
                    shutil.move(file_path2, folder_name3)
                except:
                    print("file was used!", file_path2)
                    pass
                print(self.this_day, ":", "社保（工行）金融IC日志_MX6000（MakeCard_Log开头的文件）移动成功", "文件名为:", file_path2,file=self.logname)

    def OCRlog_MX6000(self, path_5):
        if self.path_5=="":
            return
        # 移动“E:\”目录下的“OCR扫描日志”，该日志文件的内容会累积，所以移动时可能存在文件占用的问题。。。。。。。。。。。。。。。。。
        file_list3 = os.listdir(self.path_5)  # 该文件夹下所有的文件（包括文件夹）

        OCR = "OCR扫描日志_MX6000"
        folder_name4 = os.path.join(self.newfile_path, OCR)
        os.mkdir(folder_name4)  # 新建一个名称为“OCR扫描日志”的文件夹
        print(self.this_day, ":", "新建‘OCR扫描日志_MX6000’文件夹成功", file=self.logname)

        for file_obj3 in file_list3:  # 遍历所有文件
            file_path3 = os.path.join(self.path_5, file_obj3)  # 原来的文件路径
            if os.path.isdir(file_path3):  # 如果是文件夹则跳过
                continue

            if "OCR_Record.tex" in file_obj3:
                try:
                    shutil.move(file_path3, folder_name4)
                except:
                    print("file was used!", file_path3)
                    pass
                print(self.this_day, ":", "OCR扫描日志_MX6000（OCR_Record.tex）移动成功", "文件名为:", file_path3, file=self.logname)

    def IClog_HDP5000(self, path_6):
        if self.path_6=="":
            return
        self.logger.info(self.path_6)
        file_list = os.listdir(self.path_6)  # 该文件夹下所有的文件（包括文件夹）
        shenji = "生产程序IC制卡日志_HDP5000"
        #    self.newfile_path+"\\"+shenji
        folder_name = os.path.join(self.newfile_path, shenji)
        self.logger.info(folder_name)
        os.mkdir(folder_name)  # 新建一个名称为“生产程序IC制卡日志”的文件夹
        print(self.this_day, ":", "新建‘生产程序IC制卡日志_HDP5000’文件夹成功", file=self.logname)
        for file_obj0 in file_list:  # 遍历所有文件
            file_path0 = os.path.join(self.path_6, file_obj0)  # 原来的文件路径
            try:
                shutil.move(file_path0, folder_name)
            except:
                print("file was used!", file_path0)
                pass
            print(self.this_day, ":", "生产程序IC制卡日志_HDP5000移动成功", "文件名为:", file_path0, file=self.logname)

    def OCRlog_HDP5000(self, path_7):
        if self.path_7=="":
            return
        file_list = os.listdir(self.path_7)  # 该文件夹下所有的文件（包括文件夹）
        shenji = "OCR扫描写磁日志_HDP5000"
        #    self.newfile_path+"\\"+shenji
        folder_name = os.path.join(self.newfile_path, shenji)
        os.mkdir(folder_name)  # 新建一个名称为“OCR扫描\写磁日志”的文件夹
        print(self.this_day, ":", "新建‘OCR扫描写磁日志_HDP5000’文件夹成功", file=self.logname)
        for file_obj0 in file_list:  # 遍历所有文件
            file_path0 = os.path.join(self.path_7, file_obj0)  # 原来的文件路径
            try:
                shutil.move(file_path0, folder_name)
            except:
                print("file was used!", file_path0)
                pass
            print(self.this_day, ":", "OCR扫描写磁日志_HDP5000移动成功", "文件名为:", file_path0, file=self.logname)

    def SCIClog_MS5000(self, path_8):
        if self.path_8=="":
            return
        file_list = os.listdir(self.path_8)  # 该文件夹下所有的文件（包括文件夹）
        shenji = "生产程序IC制卡日志_MS5000"
        #    self.newfile_path+"\\"+shenji
        folder_name = os.path.join(self.newfile_path, shenji)
        os.mkdir(folder_name)  # 新建一个名称为“生产程序IC制卡日志”的文件夹
        print(self.this_day, ":", "新建‘生产程序IC制卡日志_MS5000’文件夹成功", file=self.logname)
        for file_obj0 in file_list:  # 遍历所有文件
            file_path0 = os.path.join(self.path_8, file_obj0)  # 原来的文件路径
            try:
                shutil.move(file_path0, folder_name)
            except:
                print("file was used!", file_path0)
                pass
            print(self.this_day, ":", "生产程序IC制卡日志_MS5000移动成功", "文件名为:", file_path0, file=self.logname)

    def OCRlog_MS5000(self, path_9):
        if self.path_9=="":
            return
        file_list = os.listdir(self.path_9)  # 该文件夹下所有的文件（包括文件夹）
        shenji = "OCR扫描写磁日志_MS5000"
        #    self.newfile_path+"\\"+shenji
        folder_name = os.path.join(self.newfile_path, shenji)
        os.mkdir(folder_name)  # 新建一个名称为“生产程序IC制卡日志”的文件夹
        print(self.this_day, ":", "新建‘OCR扫描写磁日志_MS5000’文件夹成功", file=self.logname)
        for file_obj0 in file_list:  # 遍历所有文件
            file_path0 = os.path.join(self.path_9, file_obj0)  # 原来的文件路径
            try:
                shutil.move(file_path0, folder_name)
            except:
                print("file was used!", file_path0)
                pass
            print(self.this_day, ":", "OCR扫描写磁日志_MS5000移动成功", "文件名为:", file_path0, file=self.logname)

    def tuaomalog_MS5000(self, path_10):
        if self.path_10=="":
            return
        file_list = os.listdir(self.path_10)  # 该文件夹下所有的文件（包括文件夹）
        shenji = "凸码凹码打印日志_MS5000"
        #    self.newfile_path+"\\"+shenji
        folder_name = os.path.join(self.newfile_path, shenji)
        os.mkdir(folder_name)  # 新建一个名称为“生产程序IC制卡日志”的文件夹
        print(self.this_day, ":", "新建‘凸码凹码打印日志_MS5000’文件夹成功", file=self.logname)
        for file_obj0 in file_list:  # 遍历所有文件
            file_path0 = os.path.join(self.path_10, file_obj0)  # 原来的文件路径
            try:
                shutil.move(file_path0, folder_name)
            except:
                print("file was used!", file_path0)
                pass
            print(self.this_day, ":", "凸码凹码打印日志_MS5000移动成功", "文件名为:", file_path0, file=self.logname)

    def UGlog_MS5000(self, path_11):
        if self.path_11=="":
            return
        file_list = os.listdir(self.path_11)  # 该文件夹下所有的文件（包括文件夹）
        shenji = "UG打印日志_MS5000"
        #    self.newfile_path+"\\"+shenji
        folder_name = os.path.join(self.newfile_path, shenji)
        os.mkdir(folder_name)  # 新建一个名称为“生产程序IC制卡日志”的文件夹
        print(self.this_day, ":", "新建‘UG打印日志_MS5000’文件夹成功", file=self.logname)
        for file_obj0 in file_list:  # 遍历所有文件
            file_path0 = os.path.join(self.path_11, file_obj0)  # 原来的文件路径
            try:
                shutil.move(file_path0, folder_name)
            except:
                print("file was used!", file_path0)
                pass
            print(self.this_day, ":", "UG打印日志_MS5000移动成功", "文件名为:", file_path0, file=self.logname)

    def SBIClog_MS5000(self, path_12):
        if self.path_12=="":
            return
        file_list = os.listdir(self.path_12)  # 该文件夹下所有的文件（包括文件夹）
        shenji = "设备IC站制卡日志_MS5000"
        #    self.newfile_path+"\\"+shenji
        folder_name = os.path.join(self.newfile_path, shenji)
        os.mkdir(folder_name)  # 新建一个名称为“生产程序IC制卡日志”的文件夹
        print(self.this_day, ":", "新建‘设备IC站制卡日志_MS5000’文件夹成功", file=self.logname)
        for file_obj0 in file_list:  # 遍历所有文件
            file_path0 = os.path.join(self.path_12, file_obj0)  # 原来的文件路径
            try:
                shutil.move(file_path0, folder_name)
            except:
                print("file was used!", file_path0)
                pass
            print(self.this_day, ":", "设备IC站制卡日志_MS5000移动成功", "文件名为:", file_path0, file=self.logname)

    def tumamokuailog1_MS5000(self, path_16):
        
        if self.path_16=="":
            return
        file_list = os.listdir(self.path_16)  # 该文件夹下所有的文件（包括文件夹）
        shenji1 = "凸码模块服务日志1号_MS5000"
        #    self.newfile_path+"\\"+shenji
        folder_name = os.path.join(self.newfile_path, shenji1)
        os.mkdir(folder_name)  # 新建一个名称为“生产程序IC制卡日志”的文件夹
        print(self.this_day, ":", "新建‘凸码模块服务日志1号_MS5000’文件夹成功", file=self.logname)
        for file_obj0 in file_list:  # 遍历所有文件
            file_path0 = os.path.join(self.path_16, file_obj0)  # 原来的文件路径
            try:
                shutil.move(file_path0, folder_name)
            except:
                print("file was used!", file_path0)
                pass
            print(self.this_day, ":", "凸码模块服务日志1号_MS5000移动成功", "文件名为:", file_path0, file=self.logname)


    def tumamokuailog2_MS5000(self, path_17):
        if self.path_17=="":
            return
        file_list = os.listdir(self.path_17)  # 该文件夹下所有的文件（包括文件夹）
        shenji2 = "凸码模块服务日志2号_MS5000"
        #    self.newfile_path+"\\"+shenji
        folder_name = os.path.join(self.newfile_path, shenji2)
        os.mkdir(folder_name)  # 新建一个名称为“生产程序IC制卡日志”的文件夹
        print(self.this_day, ":", "新建‘凸码模块服务日志2号_MS5000’文件夹成功", file=self.logname)
        for file_obj0 in file_list:  # 遍历所有文件
            file_path0 = os.path.join(self.path_17, file_obj0)  # 原来的文件路径
            try:
                shutil.move(file_path0, folder_name)
            except:
                print("file was used!", file_path0)
                pass
            print(self.this_day, ":", "凸码模块服务日志2号_MS5000移动成功", "文件名为:", file_path0, file=self.logname)

    def tumamokuailog3_MS5000(self, path_18):
        if self.path_18=="":
            return
        file_list = os.listdir(self.path_18)  # 该文件夹下所有的文件（包括文件夹）
        shenji3 = "凸码模块服务日志3号_MS5000"
        #    self.newfile_path+"\\"+shenji
        folder_name = os.path.join(self.newfile_path, shenji3)
        os.mkdir(folder_name)  # 新建一个名称为“生产程序IC制卡日志”的文件夹
        print(self.this_day, ":", "新建‘凸码模块服务日志3号_MS5000’文件夹成功", file=self.logname)
        for file_obj0 in file_list:  # 遍历所有文件
            file_path0 = os.path.join(self.path_18, file_obj0)  # 原来的文件路径
            try:
                shutil.move(file_path0, folder_name)
            except:
                print("file was used!", file_path0)
                pass
            print(self.this_day, ":", "凸码模块服务日志3号_MS5000移动成功", "文件名为:", file_path0, file=self.logname)

    def pingyinmokuailog1_MS5000(self, path_19):
        if self.path_19=="":
            return
        file_list = os.listdir(self.path_19)  # 该文件夹下所有的文件（包括文件夹）
        shenji4 = "平印模块服务日志1号_MS5000"
        #    self.newfile_path+"\\"+shenji
        folder_name = os.path.join(self.newfile_path, shenji4)
        os.mkdir(folder_name)  # 新建一个名称为“生产程序IC制卡日志”的文件夹
        print(self.this_day, ":", "新建‘平印模块服务日志1号_MS5000’文件夹成功", file=self.logname)
        for file_obj0 in file_list:  # 遍历所有文件
            file_path0 = os.path.join(self.path_19, file_obj0)  # 原来的文件路径
            try:
                shutil.move(file_path0, folder_name)
            except:
                print("file was used!", file_path0)
                pass
            print(self.this_day, ":", "平印模块服务日志1号_MS5000移动成功", "文件名为:", file_path0, file=self.logname)

    def pingyinmokuailog2_MS5000(self, path_20):
        if self.path_20=="":
            return
        file_list = os.listdir(self.path_20)  # 该文件夹下所有的文件（包括文件夹）
        shenji5 = "平印模块服务日志2号_MS5000"
        #    self.newfile_path+"\\"+shenji
        folder_name = os.path.join(self.newfile_path, shenji5)
        os.mkdir(folder_name)  # 新建一个名称为“生产程序IC制卡日志”的文件夹
        print(self.this_day, ":", "新建‘平印模块服务日志2号_MS5000’文件夹成功", file=self.logname)
        for file_obj0 in file_list:  # 遍历所有文件
            file_path0 = os.path.join(self.path_20, file_obj0)  # 原来的文件路径
            try:
                shutil.move(file_path0, folder_name)
            except:
                print("file was used!", file_path0)
                pass
            print(self.this_day, ":", "平印模块服务日志2号_MS5000移动成功", "文件名为:", file_path0, file=self.logname)

    def VPPkongzhilog_MS5000(self, path_21):
        if self.path_21=="":
            return
        file_list = os.listdir(self.path_21)  # 该文件夹下所有的文件（包括文件夹）
        shenji6 = "VPP系统\设备控制日志_MS5000"
        #    self.newfile_path+"\\"+shenji
        folder_name = os.path.join(self.newfile_path, shenji6)
        os.mkdir(folder_name)  # 新建一个名称为“生产程序IC制卡日志”的文件夹
        print(self.this_day, ":", "新建‘PP系统\设备控制日志_MS5000’文件夹成功", file=self.logname)
        for file_obj0 in file_list:  # 遍历所有文件
            file_path0 = os.path.join(self.path_21, file_obj0)  # 原来的文件路径
            try:
                shutil.move(file_path0, folder_name)
            except:
                print("file was used!", file_path0)
                pass
            print(self.this_day, ":", "PP系统\设备控制日志_MS5000移动成功", "文件名为:", file_path0, file=self.logname)

    def VPP_VISOshujukulog_MS5000(self, path_22):
        if self.path_22=="":
            return
        file_list = os.listdir(self.path_22)  # 该文件夹下所有的文件（包括文件夹）
        shenji7 = "VPP_VISO数据库日志_MS5000"
        #    self.newfile_path+"\\"+shenji
        folder_name = os.path.join(self.newfile_path, shenji7)
        os.mkdir(folder_name)  # 新建一个名称为“生产程序IC制卡日志”的文件夹
        print(self.this_day, ":", "新建‘VPP_VISO数据库日志_MS5000’文件夹成功", file=self.logname)
        for file_obj0 in file_list:  # 遍历所有文件
            file_path0 = os.path.join(self.path_22, file_obj0)  # 原来的文件路径
            try:
                shutil.move(file_path0, folder_name)
            except:
                print("file was used!", file_path0)
                pass
            print(self.this_day, ":", "VPP_VISO数据库日志_MS5000移动成功", "文件名为:", file_path0, file=self.logname)

    def outputlog_MX6000(self, path_13):
        if self.path_13=="":
            return
        file_list = os.listdir(self.path_13)  # 该文件夹下所有的文件（包括文件夹）
        MX_shuchu = "MX6000MX6100输出日志"
        folder_name2 = os.path.join(self.newfile_path, MX_shuchu)
        os.mkdir(folder_name2)  # 新建一个名称为“加密机日志”的文件夹
        print(self.this_day, ":", "新建‘MX6000MX6100输出日志’文件夹成功", file=self.logname)
        for file_obj in file_list:  # 遍历所有文件
            file_path = os.path.join(self.path_13, file_obj)  # 原来的文件路径
            if os.path.isdir(file_path):  # 如果是文件夹则跳过
                continue
            file_extend = os.path.splitext(file_obj)[1]
            if file_extend.find(".OUTPUT") >= 0:  # 如果文件后缀中含有.log和.fdx
                try:
                    shutil.move(file_path, folder_name2)
                except:
                    print("file was used!", file_path)
                    pass
            if file_extend.find(".output") >= 0:  # 如果文件后缀中含有.log和.fdx
                try:
                    shutil.move(file_path, folder_name2)
                except:
                    print("file was used!", file_path)
                    pass
            if file_extend.find(".Output") >= 0:  # 如果文件后缀中含有.log和.fdx
                try:
                    shutil.move(file_path, folder_name2)
                except:
                    print("file was used!", file_path)
                    pass
                print(self.this_day, ":", "MX6000MX6100输出日志（.output格式）移动成功", "文件名为:", file_path, file=self.logname)

    def outputlog_HDP5000(self, path_14):
        if self.path_14=="":
            return
        file_list = os.listdir(self.path_14)  # 该文件夹下所有的文件（包括文件夹）
        MX_shuchu = "明森HDP5000设备输出日志"
        folder_name2 = os.path.join(self.newfile_path, MX_shuchu)
        os.mkdir(folder_name2)  # 新建一个名称为“加密机日志”的文件夹
        print(self.this_day, ":", "新建‘明森HDP5000设备输出日志’文件夹成功", file=self.logname)
        for file_obj in file_list:  # 遍历所有文件
            file_path = os.path.join(self.path_14, file_obj)  # 原来的文件路径
            if os.path.isdir(file_path):  # 如果是文件夹则跳过

                if "OUTFILE" in file_path:
                    shutil.move(file_path, folder_name2)
            else:
                file_extend = os.path.splitext(file_obj)[1]
                if file_extend.find(".output") >= 0:  # 如果文件后缀中含有.log和.fdx
                    try:
                        shutil.move(file_path, folder_name2)
                    except:
                        print("file was used!", file_path)
                        pass
                if file_extend.find(".OUTPUT") >= 0:  # 如果文件后缀中含有.log和.fdx
                    try:
                        shutil.move(file_path, folder_name2)
                    except:
                        print("file was used!", file_path)
                        pass
                if file_extend.find(".Output") >= 0:  # 如果文件后缀中含有.log和.fdx
                    try:
                        shutil.move(file_path, folder_name2)
                    except:
                        print("file was used!", file_path)
                        pass
                    print(self.this_day, ":", "明森HDP5000设备输出日志（.output格式）移动成功", "文件名为:", file_path, file=self.logname)

    def outputlog_MS5000(self, path_15):
        if self.path_15=="":
            return
        file_list = os.listdir(self.path_15)  # 该文件夹下所有的文件（包括文件夹）
        MX_shuchu = "明森MS5000设备输出日志"
        folder_name2 = os.path.join(self.newfile_path, MX_shuchu)
        os.mkdir(folder_name2)  # 新建一个名称为“加密机日志”的文件夹
        print(self.this_day, ":", "新建‘明森MS5000设备输出日志’文件夹成功", file=self.logname)
        for file_obj in file_list:  # 遍历所有文件
            file_path = os.path.join(self.path_15, file_obj)  # 原来的文件路径
            if os.path.isdir(file_path):  # 如果是文件夹则跳过

                if "OUTFILE" in file_path:
                    shutil.move(file_path, folder_name2)
            else:
                file_extend = os.path.splitext(file_obj)[1]
                if file_extend.find(".output") >= 0:  # 如果文件后缀中含有.output
                    try:
                        shutil.move(file_path, folder_name2)
                    except:
                        print("file was used!", file_path)
                        pass
                if file_extend.find(".OUTPUT") >= 0:  # 如果文件后缀中含有.output
                    try:
                        shutil.move(file_path, folder_name2)
                    except:
                        print("file was used!", file_path)
                        pass
                if file_extend.find(".Output") >= 0:  # 如果文件后缀中含有.output
                    try:
                        shutil.move(file_path, folder_name2)
                    except:
                        print("file was used!", file_path)
                        pass
                    print(self.this_day, ":", "明森MS5000设备输出日志（.output格式）移动成功", "文件名为:", file_path, file=self.logname)

    def yasuo(self):
        filelist = []
        self.this_day2 = time.strftime('%Y%m%d-%H%M%S', time.localtime(time.time()))
        zipfilename = self.this_day2 + ".zip"
        folder_name2= os.path.join("D:\\日志同步",self.this_day2)
        os.mkdir(folder_name2)
        # sourceFiles = os.listdir(self.newfile_path)
        # if sourceFiles == None or len(sourceFiles) < 1:
        #     print (">>>>>> 待压缩的文件目录：" + self.newfile_path + " 里面不存在文件,无需压缩. <<<<<<",file=self.logname)
        if os.path.isfile(self.mov_des):
            filelist.append(self.mov_des)
        else:
            for root, dirs, files in os.walk(self.mov_des):
                for name in files:
                    filelist.append(os.path.join(root, name))
                if len(files) == 0:
                    # print(root)
                    filelist.append(root)

        zf = zipfile.ZipFile(zipfilename, "w", zipfile.zlib.DEFLATED)
        for tar in filelist:
            # print(tar)
            arcname = tar[len(self.mov_des):]
            # print(arcname)
            if arcname == "":
                pass
            # print arcname
            else:
                zf.write(tar, arcname)
        print(">>>>>> 待压缩的文件目录：" + self.mov_des + " 压缩成功. <<<<<<", file=self.logname)
        zf.close()
        
        shutil.move(zipfilename, "D:\\日志同步\\FTP上传目录")
        filelist = os.listdir(self.mov_des)
        for f in filelist:
            filepath = os.path.join(self.mov_des,f)
            shutil.move(filepath,folder_name2)
            

    def getDirList(self, p):
        # 遍历指定文件夹内的文件夹名称，不含文件名及子文件夹名
        p = str(p)
        if p == "":
            return []
        p = p.replace("/", "\\")
        if p[-1] != "\\":
            p = p + "\\"
        a = os.listdir(p)
        b = [x for x in a if os.path.isdir(p + x)]
        return b

    def is_valid_date(self, str):
        '''判断是否是一个有效的日期字符串'''
        tString = str
        if len(tString) < 8:
            return False
        tString = str[:8]
        try:
            datetime.datetime.strptime(tString, "%Y%m%d")
            return True
        except:
            return False

    def is_expire(self, str):
        try:
            currdate = datetime.date.today()
            checkdate = datetime.date(int(str[:4]), int(str[4:6]), int(str[6:8]))
        except:
            return False
        interval = (currdate - checkdate).days
        if interval > 3:
            return True
        else:
            return False

    def removed(self, str):
        # 删除符合条件的文件夹（含文件夹内的子文件夹和文件）
        # 没有对文件及文件夹锁定情况进行判断。

        self.rootdir = str

        for parent, dirnames, filenames in os.walk(self.rootdir, False):
            for name in filenames:
                print(self.this_day, ":", "清理文件", '文件名为：' + parent + '\\' + name, file=self.logname)
                try:
                    os.remove(os.path.join(parent, name))
                except:
                    print(self.this_day, ":", "清理文件失败", '文件名为：' + parent + '\\' + name, file=self.logname)
            for name in dirnames:
                print(self.this_day, ":", "清理文件夹", '文件夹名为：' + parent + '\\' + name, file=self.logname)
                try:
                    os.rmdir(os.path.join(parent, name))
                except:
                    print(self.this_day, ":", "清理文件夹失败", '文件夹名为：' + parent + '\\' + name, file=self.logname)
        os.rmdir(str)

    def clear_expired_dir(self):
        dir_list = os.listdir(self.rootdir)  
        for str in dir_list:
            if not ('.' in str):
                if self.is_expire(str):  
                    try:
                        shutil.rmtree(self.rootdir + '\\' + str)  # 删除符合条件的文件夹（含文件夹内的子文件夹和文件）
                        print(self.this_day, ":", "删除文件夹", '文件夹名为：' + self.rootdir + '\\' + str, file=self.logname)
                    except:
                        print(self.this_day, ":", "删除文件夹出错", '文件夹名为：' + self.rootdir + '\\' + str, file=self.logname)
                else:
                    print(self.this_day, ":", "保留文件夹", '文件夹名为：' + self.rootdir + '\\' + str, file=self.logname)

    def setFtpParams(self, ip, uname, pwd, port, timeout=60):
        self.ip = ip
        self.uname = uname
        self.pwd = pwd
        self.port = port
        self.timeout = timeout

    def initEnv(self):
        if self.ftp is None:
            self.ftp = FTP()
            print("connect ftp server: %s ..." % self.ip, file=self.logname)
            try:
                self.ftp.connect(self.ip, self.port, self.timeout)
                self.ftp.encoding = "UTF-8"
                print("connect success", file=self.logname)
            except:
                print("conncet failed!", file=self.logname)

            else:
                try:
                    self.ftp.login(self.uname, self.pwd)
                    print("login success", file=self.logname)
                    print(self.ftp.getwelcome(), file=self.logname)
                except:
                    print("login failed!", file=self.logname)

    def clearEnv(self):
        if self.ftp:
            self.ftp.close()
            print("### disconnect ftp server: %s!" % self.ip, file=self.logname)
            self.ftp = None

    def clearFTP(self, FTPDir):
        # shutil.rmtree(FTPDir)  # 删除FTP文件
        # os.mkdir(FTPDir)  # 新建被删除的根目录

        filelist = os.listdir(FTPDir)
        for f in filelist:
            filepath = os.path.join(FTPDir, f)
            if os.path.isfile(filepath):
                os.remove(filepath)
                print(filepath + " removed!")
            elif os.path.isdir(filepath):
                shutil.rmtree(filepath)
                print("dir " + filepath + " removed!")

    def uploadDir(self, localdir='./', remotedir='./'):
        if not os.path.isdir(localdir):
            print("Local file doesn't exists", file=self.logname)
            return
        self.ftp.cwd(remotedir)
        for file in os.listdir(localdir):
            src = os.path.join(localdir, file)
            if os.path.isfile(src):
                self.uploadFile(src, file)
            if os.path.isdir(src):
                try:

                    self.ftp.mkd(file)
                    if os.path.isfile(src):
                        self.uploadFile(src, file)

                        if os.path.isdir(src):
                            try:
                                self.ftp.mkd(file)
                            except:
                                sys.stderr.write('the dir is exists %s' % file)

                except:
                    sys.stderr.write('the dir is exists %s' % file)
                self.uploadDir(src, file)
        self.ftp.cwd('..')

    def uploadFile(self, localpath, remotepath='./'):
        self.this_day1 = time.strftime('%H%M%S', time.localtime(time.time()))
        if not os.path.isfile(localpath):
            return
        print("+++ upload %s to %s:%s" % (localpath, self.ip, remotepath), file=self.logname)
        self.ftp.storbinary('STOR ' + remotepath+ "-" + self.this_day1 + ".zip", open(localpath, 'rb'))

    def __filetype(self, src):
        if os.path.isfile(src):
            index = src.rfind('\\')
            if index == -1:
                index = src.rfind('/')
            return self._XFER_FILE, src[index + 1:]
        elif os.path.isdir(src):
            return self._XFER_DIR, ''

    def upload(self, src):
        filetype, filename = self.__filetype(src)

        self.initEnv()
        if filetype == self._XFER_DIR:
            self.srcDir = src
            self.uploadDir(self.srcDir)
        elif filetype == self._XFER_FILE:
            self.uploadFile(src, filename)
        self.clearEnv()

    def SvcDoRun(self):
        #        import time
        self.logger.error("svc do run....")
        self.logger.error("0")

        while self.isAlive:
            self.logname = open("D:\\日志同步\\log.txt", "a+")
            self.logger.error("1")
            self.logger.error("I am alive！！！！！！！！！.")
            # self.mov_log()
            self.datafloder()
            self.logger.error("2")
            self.shenjilog_MX6000(self.path_1)
            self.logger.error("3")
            self.IClog_MX6000(self.path_2)

            self.logger.error("24")
            self.IClog_MX6000_2_win7(self.path_23)
            self.logger.error("25")
            self.IClog_MX6000_3_winXP(self.path_24)

            self.logger.error("4")
            self.HSMlog_MX6000(self.path_3)
            self.logger.error("5")
            self.gonghangIClog_MX6000(self.path_4)
            self.logger.error("6")
            self.OCRlog_MX6000(self.path_5)
            self.logger.error("7")
            self.IClog_HDP5000(self.path_6)
            self.logger.error("8")
            self.OCRlog_HDP5000(self.path_7)
            self.logger.error("9")
            self.SCIClog_MS5000(self.path_8)
            self.logger.error("10")
            self.OCRlog_MS5000(self.path_9)
            self.logger.error("11")
            self.tuaomalog_MS5000(self.path_10)
            self.logger.error("12")
            self.UGlog_MS5000(self.path_11)
            self.logger.error("13")
            self.SBIClog_MS5000(self.path_12)
            self.logger.error("14")
            self.outputlog_MX6000(self.path_13)
            self.logger.error("15")
            self.outputlog_HDP5000(self.path_14)
            self.logger.error("16")
            self.outputlog_MS5000(self.path_15)
            self.logger.error("26")
            self.tumamokuailog1_MS5000(self.path_16)
            self.logger.error("27")
            self.tumamokuailog2_MS5000(self.path_17)
            self.logger.error("28")
            self.tumamokuailog3_MS5000(self.path_18)
            self.logger.error("29")
            self.pingyinmokuailog1_MS5000(self.path_19)
            self.logger.error("30")
            self.pingyinmokuailog2_MS5000(self.path_20)
            self.logger.error("31")
            self.VPPkongzhilog_MS5000(self.path_21)
            self.logger.error("32")
            self.VPP_VISOshujukulog_MS5000(self.path_22)

            
            self.logger.error("17")
            self.yasuo()
            self.logger.error("18")
            # xfer = Xfer()
            self.setFtpParams(str(self.FTP_IP), str(self.FTP_USER), str(self.FTP_PASSWORD), int(self.FTP_PORT))
            self.logger.error("19")
            # srcDir = mov_des
            try:
                self.upload("D:\\日志同步\\FTP上传目录")
            except:
                time.sleep(1800)
                continute
                
            self.logger.error("20")
            self.clearFTP("D:\\日志同步\\FTP上传目录")
            self.logger.error("21")
            self.clear_expired_dir()
            self.logger.error("22")
            # #print("1")
            # self.logger.error("23")
            # #time.sleep(60)
            # self.logger.error("24")
            # # 等待服务被停止
            # #win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            # self.logger.error("25")
            time.sleep(14400)
            
            self.logger.error("23")
            self.logname.close()

    def SvcStop(self):
        # 先告诉SCM停止这个过程
        self.logger.error("svc do stop....")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        # 设置事件
        win32event.SetEvent(self.hWaitStop)
        self.isAlive = False


if __name__ == '__main__':
    # while (1==1):
    win32serviceutil.HandleCommandLine(PythonService)
    # time.sleep(5)


