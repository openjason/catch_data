# -*- coding: utf-8 -*-  
''' 
    ftp自动检测源文件夹的更新，将源文件夹更新的内容拷贝到目标文件夹中 
    使用树的层序遍历算法，支持深度目录拷贝 
版本: V1.01
功能：ftp同步完成后，将新同步的文件复制到指定文件夹，用于印刷系统。

配置文件.ini
[ftp配置]
# ftp服务器  
ftphostaddr = 192.168.7.51
# 用户名
ftpusername = itcheck
# 密码
ftppassword = itcheck
#ftp远程路径
ftpremotedir = \
#本地文件夹
ftplocaldir = F:\test\
'''

from tkinter import Tk
from configparser import ConfigParser
from tkinter import messagebox,scrolledtext,Canvas,PhotoImage,Label,StringVar,Entry, Button,END, DISABLED, Toplevel  # 导入滚动文本框的模块
from os.path import exists as os_path_exists
from openpyxl import load_workbook,Workbook
import logging
from logging import getLogger
from logging.handlers import RotatingFileHandler
import ftplib
import os,sys,string,datetime,time  
import shutil  
import socket  


#设置日志文件配置参数
def set_logging():
    global logger
    logger = getLogger('balance_logger')
    handler = RotatingFileHandler('日志记录.log', maxBytes=5000000, backupCount=6)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    formatter = logging.Formatter('%(asctime)-12s %(filename)s %(lineno)d %(message)s')
    handler.setFormatter(formatter)

#定义类，脚本主要更能
class App():
    def __init__(self, master):

        self.master = master
        self.customer_sname = ''
        self.curr_month = ''
        self.autorun = ''
        self.filesymbol = ''
        self.pendingdir = ''
        self.savefilename = ''
        self.initWidgets(master)

    # def ftp_init(self,hostaddr):
    #     ftp = ftplib.FTP()
    #     ftp.connect(hostaddr,  port = 21)
 
    def compare_file(self,LocalFile, RemoteFile,fmodify,fsize):
        pass
 
    def DownLoadFile(self, ftpclient, LocalFile, RemoteFile,modify,fsize):  # 下载当个文件
        mtime8h = float(8*3600)#无法修改时区，临时解决办法，手动 +8小时 time.mktime(time.strptime("8","%H"))
        mtime_t = time.mktime(time.strptime(modify, "%Y%m%d%H%M%S"))
        mtime_t = mtime_t + mtime8h
        print(mtime_t)
        mtime_t_str = time.strftime("%Y%m%d%H%M%S", mtime_t)

        if os.path.exists(LocalFile):
            lfilemt= time.localtime(os.stat(LocalFile).st_mtime)
            lfilemt_str = time.strftime("%Y%m%d%H%M%S", lfilemt)
            lfsize = os.path.getsize(LocalFile)
            if lfilemt_str == mtime_t_str:
                if fsize == lfsize:
                    print('file_time n size is same: ',LocalFile)
        
        file_handler = open(LocalFile, 'wb')
        ftpclient.retrbinary('RETR ' + RemoteFile, file_handler.write)
        file_handler.close()


        atime_t = mtime_t
        os.utime(LocalFile, (atime_t, mtime_t))
        self.scr.insert(1.0,datetime.datetime.now().strftime('%m-%d %H:%M:%S')+'下载： '+RemoteFile+'\n')
        logger.info('DownLoadFile: ')
        logger.info(RemoteFile)
        return True
 
    def DownLoadFileTree(self, ftpclient, LocalDir, RemoteDir):  # 下载整个目录下的文件
        print("remoteDir:", RemoteDir)
        ftpclient.cwd(RemoteDir)
        RemoteNames = ftpclient.mlsd()
        for items in RemoteNames:
            fname=items[0]
            fother = items[1]
            if fother['type'] == 'file':
                fsize=fother['size']
                fmodify=fother['modify']#print('size',tempsize)
                logger.info('Download...')
                self.DownLoadFile(ftpclient,os.path.join(LocalDir,fname),os.path.join(RemoteDir,fname),fmodify,fsize)
                logger.info(os.path.join(LocalDir,fname))
            else:
                dirname=items[0]
                remote_dirname = os.path.join(RemoteDir,dirname)
                local_dirname = os.path.join(LocalDir,dirname)
                if not os.path.exists(local_dirname):
                    print('mkdir: ',local_dirname)
                    logger.info('mkdir: ' + local_dirname)
                    os.mkdir(local_dirname)
                    self.scr.insert(1.0,"新建文件夹： "+ local_dirname +'\n')
                self.DownLoadFileTree(ftpclient,local_dirname, remote_dirname)
            # if file.find(".") == -1:
            # else:
            #     self.DownLoadFile(ftpclient,Local, file)
        return
 
    #按字符查找符合条件文件名，返回文件列表
    def find_filename(self, curr_path, curr_filename_path):
        list_files = []
        for parent, dirnames, filenames in os.walk(curr_path, followlinks=True):
            for filename in filenames:
                file_path = os.path.join(parent, filename)
                if curr_filename_path in filename:
                    print('文件名：%s' % file_path)
                    list_files.append(file_path)
        if len(list_files) > 0:
            return (list_files)
        else:
            return (None)


# 程序主gui界面。
    def initWidgets(self, fm1):

        cp = ConfigParser()
        cp.read('配置文件.ini', encoding='gbk')
        try:
            self.ftphostaddr  = cp.get('ftp配置', 'ftphostaddr')
            self.ftpusername  = cp.get('ftp配置', 'ftpusername')
            self.ftppassword  = cp.get('ftp配置', 'ftppassword')
            self.ftpremotedir  = cp.get('ftp配置', 'ftpremotedir')
            self.ftplocaldir   = cp.get('ftp配置', 'ftplocaldir')
        except Exception as err_message:
            print(err_message)
            return_message = messagebox.showinfo(title='提示',message='无法打开配置文件.ini或配置有误!' )
            exit(2)

        label_author = Label(fm1, text='by流程与信息化部IT. March,2020', font=('Arial', 9))
        label_author.place(x=500, y=777)

        self.scr = scrolledtext.ScrolledText(fm1, width=131, height=58)
        self.scr.place(x=10, y=10)

        btn_barcode_init = Button(fm1, text='文件合并', command=self.command_btn_run)
        btn_barcode_init.place(x=946, y=160)

        btn_barcode_init = Button(fm1, text=' 退  出 ', command=self.command_btn_exit)
        btn_barcode_init.place(x=946, y=270)

    # 退出键
    def command_btn_exit(self):
        self.master.destroy()

    # 主功能键
    def command_btn_run(self):
        self.scr.delete(1.0,END)
        ftpclient = ftplib.FTP()
        ftpclient.encoding = 'utf-8'
        try:
            ftpclient.connect(self.ftphostaddr,  port = 21)
        except Exception as err_message:
            print(err_message)
            self.scr.insert(1.0, err_message )
            self.scr.update()
            logger.error(err_message.__str__())
            logger.exception(sys.exc_info())
            return (1)
        #self.ftp = self.ftp_init(self.ftphostaddr)
        ftpclient.login(self.ftpusername, self.ftppassword)
        ftpmessage = ftpclient.getwelcome()
        logger.info(ftpmessage)
        self.scr.insert(1.0,ftpmessage)

        self.DownLoadFileTree(ftpclient, self.ftplocaldir, self.ftpremotedir)  # 从目标目录下载到本地目录d盘
        ftpclient.close()
        print("ok!")

        return 0

if __name__ == '__main__':
    
    os.environ['TZ'] = 'Asia/Shanghai'
    set_logging()
    main_window = Tk()
    main_window.title('FTP文件更新发送小工具  v.20200324')

    # 设定窗口的大小(长 * 宽)，显示窗体居中，winfo_xxx获取系统屏幕分辨率。
    sw = main_window.winfo_screenwidth()
    sh = main_window.winfo_screenheight()
    ww = 1024
    wh = 800
    x = (sw - ww) / 2
    y = (sh - wh) / 2
    main_window.geometry("%dx%d+%d+%d" % (ww, wh, x, y))  # 这里的乘是小x
    display = App(main_window)
    main_window.mainloop()
