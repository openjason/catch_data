# -*- coding: utf-8 -*-  
''' 
    ftp自动检测源文件夹的更新，将源文件夹更新的内容拷贝到目标文件夹中 
    使用树的层序遍历算法，支持深度目录拷贝 
版本: V1.01
功能：ftp同步完成后，将新同步的文件复制到指定文件夹，用于印刷系统。
开发时间：2020 04 07 08 51
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
localdir = F:\test\
#匹配字符串，‘空’则匹配所有
matchstring = .pdf
#目标文件夹
targetdir = F:\target\
#刷新时间间隔-秒
gaptime = 60
#清理文件超过时间-小时4320如果本地文件被清理ftp上文件旧文件将重新copy到本地，可能造成误打印。
cleanoftime = 43200
'''

from tkinter import Tk
from configparser import ConfigParser
from tkinter import messagebox,scrolledtext,Canvas,PhotoImage,Label,StringVar,Entry, Button,END, DISABLED, Toplevel  # 导入滚动文本框的模块
from os.path import exists as os_path_exists
#from openpyxl import load_workbook,Workbook
#import logging
from logging import getLogger,DEBUG,Formatter
from logging.handlers import RotatingFileHandler
import ftplib
import os,sys,string,datetime,time  
import shutil  
import socket  
import hashlib
from shutil import copy as shutil_copy

#设置日志文件配置参数
def set_logging():
    global logger
  
    logger = getLogger('balance_logger')
    handler = RotatingFileHandler('日志记录.log', maxBytes=5000000, backupCount=6)
    logger.setLevel(DEBUG)
    logger.addHandler(handler)
    formatter = Formatter('%(asctime)-12s %(filename)s %(lineno)d %(message)s')
    handler.setFormatter(formatter)

#定义类，脚本主要更能
class App():
    def __init__(self, master):

        self.master = master
        self.ftplocaldir = ''
        self.customer_sname = ''
        self.targetdir = ''
        self.gaptime = 3
        self.matchstring_list = []
        self.clean_of_time = 4320
        self.filesymbol = ''
        self.pendingdir = ''
        self.savefilename = ''
        self.btn_download_init = None #Button()
        self.file_md5_list = []
        self.scr_history_have_clean = False

        self.initWidgets(master)


    # def ftp_init(self,hostaddr):
    #     ftp = ftplib.FTP()
    #     ftp.connect(hostaddr,  port = 21)
    def md5sum(self,fname):
        """ 计算文件的MD5值
        """
        def read_chunks(fh):
            fh.seek(0)
            chunk = fh.read(8096)
            while chunk:
                yield chunk
                chunk = fh.read(8096)
            else: #最后要将游标放回文件开头
                fh.seek(0)
        m = hashlib.md5()
        if os.path.exists(fname):
            with open(fname, "rb") as fh:
                for chunk in read_chunks(fh):
                    m.update(chunk)
        else:
            return ""
        return m.hexdigest()        

    def file_list_md5_refresh(self,LocalFileL):
        self.file_md5_list = []
        list = os.listdir(LocalFileL) #列出文件夹下所有的目录与文件
        
        for i in range(0,len(list)):
            path = os.path.join(LocalFileL,list[i])
            if os.path.isfile(path):
                md5sum_result = self.md5sum(path)
                self.file_md5_list.append([path,md5sum_result])
                #self变量 file_md5_list
        logger.info(self.file_md5_list)

    def clean_dir(self, work_dir, dtime, filepatten_list):
        source_dir = work_dir

        if not os.path.exists(source_dir):
            logger.info('无法打开文件夹：' + source_dir)
        else:
            have_jdb_file = False
            for i in os.listdir(source_dir):
                fullname = os.path.join(source_dir,i)
                statinfo = os.stat(fullname)
                howlong  = statinfo.st_ctime - time.time()
                file_ctime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(statinfo.st_ctime))
                #print(fullname + ' 文件创建时间:' + file_ctime)
                logger.info(fullname + ' 文件创建时间:' + file_ctime)
                if abs(howlong/3600) > dtime :
                    for j in range(len(filepatten_list)):
                        if filepatten_list[j] in os.path.basename(fullname):
                            print(fullname + ' match patten:' + filepatten_list[j])
                            try:
                                os.remove(fullname)
                                logger.info('删除文件' + fullname + ' 文件创建时间:' + file_ctime)
                            except:
                                logger.info(fullname + ' 文件删除失败')
        
 
    def DownLoadFile(self, ftpclient, LocalFile, RemoteFile,modify,fsize):  # 下载当个文件
        mtime8h = float(8*3600)#无法修改时区，临时解决办法，手动 +8小时 time.mktime(time.strptime("8","%H"))
        mtime_t = time.mktime(time.strptime(modify, "%Y%m%d%H%M%S"))
        mtime_t = mtime_t + mtime8h
        #print(mtime_t)
        mtime_t_str = time.strftime("%Y%m%d%H%M%S", time.localtime(mtime_t))

        file_is_new = True
        if os.path.exists(LocalFile):
            lfilemt= time.localtime(os.stat(LocalFile).st_mtime)
            lfilemt_str = time.strftime("%Y%m%d%H%M%S", lfilemt)
            lfsize = str(os.path.getsize(LocalFile))
            if lfilemt_str == mtime_t_str:
                if fsize == lfsize:
                    #logger.info('大小日期相同，不下载: ' + str(LocalFile))
                    file_is_new = False
                    
        if file_is_new:
            file_handler = open(LocalFile, 'wb')
            ftpclient.retrbinary('RETR ' + RemoteFile, file_handler.write)
            file_handler.close()

            atime_t = mtime_t
            os.utime(LocalFile, (atime_t, mtime_t))
            logger.info('\n新文件下载： '+RemoteFile+'\n')
            self.scr.insert(1.0,'\n'+datetime.datetime.now().strftime('%m-%d %H:%M:%S')+' 新文件下载： '+RemoteFile+'\n')

            md5sum_result = self.md5sum(LocalFile)
            is_not_dup_file = True
            for i in range(0,len(self.file_md5_list)):
                md5_one_rec_temp = self.file_md5_list[i]
                if md5sum_result == md5_one_rec_temp[1]:
                    self.scr.insert(1.0,'\nMD5检测:文件重复(ftp： '+RemoteFile+' >>><<< 本地：'+md5_one_rec_temp[0]+')\n')
                    is_not_dup_file = False
                    break
            if is_not_dup_file:
                shutil_copy(LocalFile,os.path.join(self.targetdir,os.path.basename(LocalFile)))
                logger.info('拷贝文件：' + LocalFile + ' > '+ str(self.targetdir))
                self.scr.insert(1.0,'\n拷贝文件：' + LocalFile + ' > '+ str(self.targetdir))
                self.file_md5_list.append([LocalFile,md5sum_result])
                logger.info(self.file_md5_list)
            self.scr.update()


            #logger.info('DownLoadFile: ')
            logger.info(RemoteFile)
            return True
 
    def DownLoadFileTree(self, ftpclient, LocalDir, RemoteDir):  # 下载整个目录下的文件
        
        if self.file_md5_list == []:
            self.command_refresh_md5_btn_run()

        ftpclient.cwd(RemoteDir)
        RemoteNames = ftpclient.mlsd()
        for items in RemoteNames:
            fname=items[0]
            fother = items[1]
            if fother['type'] == 'file':
                fsize=fother['size']
                fmodify=fother['modify']#print('size',tempsize)
                
                if self.check_filename_match(fname):
                    #logger.info('匹配文件: ' + fname)
                    self.DownLoadFile(ftpclient,os.path.join(LocalDir,fname),os.path.join(RemoteDir,fname),fmodify,fsize)
                #logger.info(os.path.join(LocalDir,fname))
            else:
                dirname=items[0]
                remote_dirname = os.path.join(RemoteDir,dirname)
                local_dirname = os.path.join(LocalDir,dirname)
                if not os.path.exists(local_dirname):
                    print('mkdir: ',local_dirname)
                    logger.info('mkdir: ' + local_dirname)
                    os.mkdir(local_dirname)
                    self.scr.insert(1.0,"新建文件夹： "+ local_dirname +'\n')
                    self.scr.update()
                self.DownLoadFileTree(ftpclient,local_dirname, remote_dirname)
        return

    def check_filename_match(self,filename):
        if len(self.matchstring_list) < 1:
            return (True)
        for mstring in self.matchstring_list:
            if mstring in filename:
                return (True)
        return (False)

    # 程序主gui界面。
    def initWidgets(self, fm1):

        cp = ConfigParser()
        cp.read('配置文件.ini', encoding='gbk')
        try:
            self.ftphostaddr  = cp.get('ftp配置', 'ftphostaddr')
            self.ftpusername  = cp.get('ftp配置', 'ftpusername')
            self.ftppassword  = cp.get('ftp配置', 'ftppassword')
            self.ftpremotedir  = cp.get('ftp配置', 'ftpremotedir')
            self.ftplocaldir   = cp.get('ftp配置', 'localdir')
            self.targetdir     = cp.get('ftp配置', 'targetdir')
            self.gaptime       = cp.get('ftp配置', 'gaptime')
            matchstring       = cp.get('ftp配置', 'matchstring')
            clean_of_time_str = cp.get('ftp配置', 'cleanoftime')

            if matchstring != '':
                self.matchstring_list = matchstring.split('|')
            self.clean_of_time = int(clean_of_time_str)
        
        except Exception as err_message:
            print(err_message)
            return_message = messagebox.showinfo(title='提示',message='无法打开配置文件.ini或配置有误!' )
            exit(2)

        label_author = Label(fm1, text='by流程与信息化部IT. April,2020', font=('Arial', 9))
        label_author.place(x=500, y=777)

        self.scr = scrolledtext.ScrolledText(fm1, width=131, height=58)
        self.scr.place(x=10, y=10)

        self.btn_download_init = Button(fm1, text='刷新FTP', command=self.command_download_btn_run)
        self.btn_download_init.place(x=946, y=160)
        #btn_download_init.configure(state=DISABLED)

        #btn_fresh_init = Button(fm1, text='刷新MD5', command=self.command_refresh_md5_btn_run)
        #btn_fresh_init.place(x=946, y=360)

        btn_app_exit_init = Button(fm1, text=' 退  出 ', command=self.command_btn_exit)
        btn_app_exit_init.place(x=946, y=270)

    # 退出键
    def command_btn_exit(self):
        self.master.destroy()

    def command_refresh_md5_btn_run(self):
        self.scr.insert(1.0,'\n开始更新全部文件MD5值...')
        self.file_list_md5_refresh(self.ftplocaldir)    #更新本地文件md5列表
      
        #logger.info(self.file_md5_list)
        self.scr.insert(1.0,'\n已更新文件MD5值...')
        self.scr.update()

    def run_ftp_fresh(self):
        
        #curr_time_str = datetime.datetime.now().strftime('%H%M%S')
        curr_time_str = datetime.datetime.now().strftime('%H%M')
        # 8：00 进行屏幕清理



        if curr_time_str > '0800':
            if self.scr_history_have_clean:

                self.clean_dir(self.ftplocaldir,self.clean_of_time,self.matchstring_list)
                self.file_list_md5_refresh(self.ftplocaldir)    #更新本地文件md5列表

                logger.info("scr屏幕清理: "+ curr_time_str)
                self.scr.delete(1.0,END)
                self.scr.insert(1.0, "\nscr屏幕清理: "+curr_time_str)
                self.scr_history_have_clean = False
        else:
            self.scr_history_have_clean = True

        
        ftpclient = ftplib.FTP()
        ftpclient.encoding = 'utf-8'
        try:
            ftpclient.connect(self.ftphostaddr,  port = 21)
            #self.ftp = self.ftp_init(self.ftphostaddr)
            ftpclient.login(self.ftpusername, self.ftppassword)
            ftpmessage = ftpclient.getwelcome()
            logger.info(ftpmessage)
            #self.scr.insert(1.0,ftpmessage)
            #self.scr.update()
            self.DownLoadFileTree(ftpclient, self.ftplocaldir, self.ftpremotedir)  # 从目标目录下载到本地目录d盘

        except Exception as err_message:
            print(err_message)
            self.scr.insert(1.0, err_message )
            self.scr.update()
            logger.error(err_message.__str__())
            logger.exception(sys.exc_info())
            if ftpclient:
                ftpclient.close()

    # 主功能键
    def command_download_btn_run(self):
        logger.info("Process is running...")
        self.run_ftp_fresh()
        self.scr.insert(1.0, "\nFTP文件刷新时间: "+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.btn_download_init.configure(state=DISABLED)
        
        gap = int(self.gaptime) * 1000
        
        self.master.after(gap,self.command_download_btn_run)

if __name__ == '__main__':
    
    os.environ['TZ'] = 'Asia/Shanghai'
    set_logging()
    main_window = Tk()
    main_window.title('东信和平FTP文件更新&传输小工具  v.20200407')

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
