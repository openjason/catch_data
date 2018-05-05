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
# logname = open("C:\\日志同步\\log.txt", "a+")


class PythonService(win32serviceutil.ServiceFramework):
    # class PythonService():
    _svc_name_ = "aaPythonService111"
    # 服务显示名称
    _svc_display_name_ = "aaPython Service Demo3333"
    # 服务描述
    _svc_description_ = "Python service demo."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.logger = self._getLogger()
        self.isAlive = True
        self.ftp = None

        self.newfile_path = ''

        self.rootdir = "C:\\日志同步"
        self.this_day = time.strftime('%Y%m%d-%H%M%S', time.localtime(time.time()))

        self.config = configparser.ConfigParser()
        # 读取配置文件
        self.config.read("C:\\日志同步\\config rizhitongbu.ini")

        # 获取日志路径
        # MX6100\MX6000设备的日志
        self.path_1 = self.config.get("MX_6000_path", "path1")
        self.path_2 = self.config.get("MX_6000_path", "path2")
        self.path_3 = self.config.get("MX_6000_path", "path3")
        self.path_4 = self.config.get("MX_6000_path", "path4")
        self.path_5 = self.config.get("MX_6000_path", "path5")

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
        os.makedirs(self.newfile_path)
        print(self.this_day, ":", "新建日期文件成功", file=self.logname)

    def shenjilog_MX6000(self, path_1):

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
                print(self.this_day, ":", "生产程序IC制卡日志_MX6000（.log格式）移动成功", "文件名为:", file_path, file=self.logname)

    def HSMlog_MX6000(self, path_3):
        # 移动“D:\Mx6KPersoLogFile\”目录下的“加密机日志（.Fdx）”文件，需要对文件的扩展名进行筛选后移动
        file_list = os.listdir(self.path_3)  # 该文件夹下所有的文件（包括文件夹）

        jiamiji = "加密机日志_MX6000"
        folder_name2 = os.path.join(self.newfile_path, jiamiji)
        os.mkdir(folder_name2)  # 新建一个名称为“加密机日志”的文件夹
        print(self.this_day, ":", "新建‘加密机日志_MX6000’文件夹成功", file=self.logname)
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
                print(this.this_day, ":", "加密机日志（.Fdx格式）_MX6000移动成功", "文件名为:", file_path, file=self.logname)

    def gonghangIClog_MX6000(self, path_4):
        # 移动“C:\Program Files\DataCard\”目录下的“社保（工行）金融IC日志（MakeCard_Log开头）”，需要对文件名称进行筛选后移动

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
                print(self.this_day, ":", "社保（工行）金融IC日志_MX6000（MakeCard_Log开头的文件）移动成功", "文件名为:", file_path2,
                      file=self.logname)

    def OCRlog_MX6000(self, path_5):
        # 移动“C:\”目录下的“OCR扫描日志”，该日志文件的内容会累积，所以移动时可能存在文件占用的问题。。。。。。。。。。。。。。。。。
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
        file_list = os.listdir(self.path_6)  # 该文件夹下所有的文件（包括文件夹）
        shenji = "生产程序IC制卡日志_HDP5000"
        #    self.newfile_path+"\\"+shenji
        folder_name = os.path.join(self.newfile_path, shenji)
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

    def outputlog_MX6000(self, path_13):
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
            if file_extend.find(".output") >= 0:  # 如果文件后缀中含有.log和.fdx
                try:
                    shutil.move(self.file_path, folder_name2)
                except:
                    print("file was used!", file_path)
                    pass
                print(this_day, ":", "MX6000MX6100输出日志（.output格式）移动成功", "文件名为:", file_path, file=self.logname)

    def outputlog_HDP5000(self, path_14):
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
                    print(self.this_day, ":", "明森HDP5000设备输出日志（.output格式）移动成功", "文件名为:", file_path, file=self.logname)

    def outputlog_MS5000(self, path_15):
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
                    print(self.this_day, ":", "明森MS5000设备输出日志（.output格式）移动成功", "文件名为:", file_path, file=self.logname)

    def yasuo(self):
        filelist = []
        zipfilename = self.newfile_path + ".zip"
        # sourceFiles = os.listdir(self.newfile_path)
        # if sourceFiles == None or len(sourceFiles) < 1:
        #     print (">>>>>> 待压缩的文件目录：" + self.newfile_path + " 里面不存在文件,无需压缩. <<<<<<",file=self.logname)
        if os.path.isfile(self.newfile_path):
            filelist.append(self.newfile_path)
        else:
            for root, dirs, files in os.walk(self.newfile_path):
                for name in files:
                    filelist.append(os.path.join(root, name))
                if len(files) == 0:
                    # print(root)
                    filelist.append(root)

        zf = zipfile.ZipFile(zipfilename, "w", zipfile.zlib.DEFLATED)
        for tar in filelist:
            # print(tar)
            arcname = tar[len(self.newfile_path):]
            # print(arcname)
            if arcname == "":
                pass
            # print arcname
            else:
                zf.write(tar, arcname)
        print(">>>>>> 待压缩的文件目录：" + self.newfile_path + " 压缩成功. <<<<<<", file=self.logname)
        zf.close()
        shutil.move(self.newfile_path, "C:\\日志同步")

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
        '''判断是否是 过期'''
        #    currdate = time.strftime('%Y%m%d',time.localtime(time.time()))
        currdate = datetime.date.today()
        checkdate = datetime.date(int(str[:4]), int(str[4:6]), int(str[6:8]))
        interval = currdate - checkdate
        rint = interval.days
        return rint

    def removed(self, str):
        # 删除符合条件的文件夹（含文件夹内的子文件夹和文件）
        # 没有对文件及文件夹锁定情况进行判断。
        self.rootdir = str

        for parent, dirnames, filenames in os.walk(self.rootdir, False):
            for name in filenames:
                print(this_day, ":", "清理文件", '文件名为：' + parent + '\\' + name, file=self.logname)
                try:
                    os.remove(os.path.join(parent, name))
                except:
                    print(this_day, ":", "清理文件失败", '文件名为：' + parent + '\\' + name, file=self.logname)
            for name in dirnames:
                print(this_day, ":", "清理文件夹", '文件夹名为：' + parent + '\\' + name, file=self.logname)
                try:
                    os.rmdir(os.path.join(parent, name))
                except:
                    print(this_day, ":", "清理文件夹失败", '文件夹名为：' + parent + '\\' + name, file=self.logname)
        os.rmdir(str)

    def clear_expired_dir(self):
        dirlists = self.getDirList(self.rootdir)  # 遍历指定文件夹内的文件夹，没有递归
        for str in dirlists:
            print(str)
            if self.is_valid_date(str):  # 判断是否符合日期型的文件夹'YYYYMMDD'
                if int(self.is_expire(str)) < 3:  # 文件夹名字 是否 与当前日期相差3天以上
                    print('is 3days floder')
                    print(self.this_day, ":", "保留文件夹", '文件夹名为：' + self.rootdir + '\\' + str, file=self.logname)
                else:
                    #                print(is_expire(str))
                    try:
                        self.removed(self.rootdir + '\\' + str)  # 删除符合条件的文件夹（含文件夹内的子文件夹和文件）
                    except:
                        print("我错了")
            else:
                print('not_valid_date')  # 非日期型的文件夹不做处理
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
        if not os.path.isfile(localpath):
            return
        print("+++ upload %s to %s:%s" % (localpath, self.ip, remotepath), file=self.logname)
        self.ftp.storbinary('STOR ' + remotepath, open(localpath, 'rb'))

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
            self.logname = open("C:\\日志同步\\log.txt", "a+")
            self.logger.error("1")
            self.logger.error("I am alive！！！！！！！！！.")
            # self.mov_log()
            self.datafloder()
            self.logger.error("2")
            self.shenjilog_MX6000(self.path_1)
            self.logger.error("3")
            self.IClog_MX6000(self.path_2)
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
            self.logger.error("17")
            self.yasuo()
            self.logger.error("18")
            # xfer = Xfer()
            self.setFtpParams(str(self.FTP_IP), str(self.FTP_USER), str(self.FTP_PASSWORD), int(self.FTP_PORT))
            self.logger.error("19")
            # srcDir = mov_des
            self.upload(self.mov_des)
            self.logger.error("20")
            self.clearFTP(self.mov_des)
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
            time.sleep(10)
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

    # if called without argvs, let's run !

    # if len(sys.argv) == 1:
    #     servicemanager.Initialize()
    #     servicemanager.PrepareToHostSingle(DataTransToMongoService)
    #     servicemanager.StartServiceCtrlDispatcher()
    # else:
    win32serviceutil.HandleCommandLine(PythonService)

