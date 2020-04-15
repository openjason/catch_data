# -*- coding: utf-8 -*-  
''' 
    自动检测源文件夹的更新，将源文件夹更新的内容拷贝到目标文件夹中 
    使用树的层序遍历算法，支持深度目录拷贝 
版本: V1.02
功能：
开发时间：2020 04 15 16 12
配置文件.ini
[F配置]
#本地文件夹
localdir = F:\testt\
#目标文件夹
targetdir = F:\target\

'''

from tkinter import Tk
from configparser import ConfigParser
from tkinter import MULTIPLE,Message,Listbox,messagebox,Label,StringVar,Scrollbar, Button,END, DISABLED, Toplevel,SUNKEN,LEFT,Y  # 导入滚动文本框的模块

from os.path import exists as os_path_exists
#from openpyxl import load_workbook,Workbook
#import logging
from logging import getLogger,DEBUG,Formatter
from logging.handlers import RotatingFileHandler
import os,sys,string,datetime,time  
import socket  
import hashlib
from shutil import copy as shutil_copy

#设置日志文件配置参数
def set_logging():
    global logger
  
    logger = getLogger('balance_logger')
    handler = RotatingFileHandler('日志记录.log', maxBytes=5000000, backupCount=4)
    logger.setLevel(DEBUG)
    logger.addHandler(handler)
    formatter = Formatter('%(asctime)-12s %(filename)s %(lineno)d %(message)s')
    handler.setFormatter(formatter)

#定义类，脚本主要更能
class App():
    def __init__(self, master):

        self.md5filename = 'filelist.md5'
        self.master = master
        self.svar_tips = StringVar()
        self.svar_file_detail_tips = StringVar() 
        self.ftplocaldir = ''
        self.customer_sname = ''
        self.targetdir = ''
        self.label_tips = Label()
        self.list_sample = Listbox()
        self.filesymbol = ''
        self.pendingdir = ''
        self.savefilename = ''
        self.btn_download_init = None #Button()
        self.file_md5_list = []
        self.file_detail_tips = []
        self.scr_history_have_clean = False
        self.initWidgets(master)

    def get_md5file(self):
        if self.file_md5_list == []:
            try:
                with open(self.md5filename,'r',encoding='utf-8') as read_filelines:
                    for read_line in read_filelines:
                        if len(read_line) < 9:  #行小于9个字符，不再向下读MD5信息
                            break
                        logger.info(read_line.strip())
                        one_line_to_list = read_line.split('|')
                        self.file_md5_list.append([one_line_to_list[0],one_line_to_list[1],one_line_to_list[2]])
            except Exception as err_message:
                print(err_message)
                logger.error(err_message.__str__())
                logger.exception(sys.exc_info())
                messagebox.showinfo(title='MD5 file not found',message='MD5 file not found.')
                exit()

            
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

    def file_list_add_md5(self,filename):
        md5sum_result = self.md5sum(filename)
        for i in self.file_md5_list:
            md5_value = i[1]
            if md5sum_result == md5_value:
                msg = Message(text='重复发送: \n' + i[0] + ' \n ' + i[2])
                msg.config(bg='red', font=('times', 20, 'italic'))
                msg.pack(padx=40,pady=160)
                msg.update()
                time.sleep(3)
                msg.destroy()
                self.svar_tips.set('重复发送: ' + i[0] +' '+i[2].strip())
                logger.info('重复发送: ' + i[0] +' '+i[2].strip())
                return(False)

        curr_time = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        str_return = curr_time + "|" + md5sum_result+"|"+filename
        return(str_return)        

    def clean_journal(self):
        logger.info('run clean_journal...')
        d1 = datetime.datetime.now()
        md5up_file = open(self.md5filename+'.bak','w',encoding='utf-8')
        with open(self.md5filename,'r',encoding='utf-8') as read_filelines:
            for i in read_filelines:
                one_list = i.split("|") 
                format = '%Y-%m-%d %H:%M:%S'
                d2 = datetime.datetime.strptime(one_list[0], format)
                int_temp = (d1 - d2).days
                if int_temp < 180:
                    md5up_file.writelines(i)
        md5up_file.close()
        
        shutil_copy(self.md5filename,self.md5filename+'.old')
        shutil_copy(self.md5filename+'.bak',self.md5filename)

        self.get_md5file()

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

            md5sum_result = self.md5sum(LocalFile)
            is_not_dup_file = True
            for i in range(0,len(self.file_md5_list)):
                md5_one_rec_temp = self.file_md5_list[i]
                if md5sum_result == md5_one_rec_temp[1]:
                    #self.scr.insert(1.0,'\nMD5检测:文件重复(ftp： '+RemoteFile+' >>><<< 本地：'+md5_one_rec_temp[0]+')\n')
                    is_not_dup_file = False
                    break
            if is_not_dup_file:
                shutil_copy(LocalFile,os.path.join(self.targetdir,os.path.basename(LocalFile)))
                logger.info('拷贝文件：' + LocalFile + ' > '+ str(self.targetdir))
                #self.scr.insert(1.0,'\n拷贝文件：' + LocalFile + ' > '+ str(self.targetdir))
                self.file_md5_list.append([LocalFile,md5sum_result])
                logger.info(self.file_md5_list)
            #self.scr.update()


            #logger.info('DownLoadFile: ')
            logger.info(RemoteFile)
            return True
 
    def Fresh_local_dir(self, LocalDir ,file_list,dir_list):  # 下载整个目录下的文件
        
        #获取该目录下所有的文件名称和目录名称
        dir_or_files = os.listdir(LocalDir)
        for dir_file in dir_or_files:
            #获取目录或者文件的路径
            dir_file_path = os.path.join(LocalDir,dir_file)
            #判断该路径为文件还是路径
            if os.path.isdir(dir_file_path):
                dir_list.append(dir_file_path)
                #递归获取所有文件和目录的路径
                self.Fresh_local_dir(dir_file_path,file_list,dir_list)
            else:
                file_list.append(dir_file_path)
        return(file_list)

    def check_filename_match(self,filename):
        return(True)

    # 程序主gui界面。
    def initWidgets(self, fm1):

        cp = ConfigParser()
        cp.read('配置文件.ini', encoding='gbk')
        try:
            #self.ftpremotedir  = cp.get('F配置', 'ftpremotedir')
            self.ftplocaldir   = cp.get('F配置', 'localdir')
            self.targetdir     = cp.get('F配置', 'targetdir')
        
        except Exception as err_message:
            print(err_message)
            return_message = messagebox.showinfo(title='提示',message='无法打开配置文件.ini或配置有误!' )
            exit(2)

        label_author = Label(fm1, text='by流程与信息化部IT. April,2020', font=('Arial', 9))
        label_author.place(x=500, y=777)

        self.btn_download_init = Button(fm1, text='  刷  新  ', command=self.command_download_btn_run)
        self.btn_download_init.place(x=929, y=100)

        self.btn_sendfile_init = Button(fm1, text='发送文件', command=self.command_refresh_md5_btn_run)
        self.btn_sendfile_init.place(x=929, y=210)
        #btn_download_init.configure(state=DISABLED)

        btn_app_exit_init = Button(fm1, text='  退  出  ', command=self.command_btn_exit)
        btn_app_exit_init.place(x=929, y=270)

        self.sbar_lr = Scrollbar(fm1,width=20)
        self.list_sample = Listbox(selectmode = MULTIPLE,relief=SUNKEN,width =127,height=40,yscrollcommand=self.sbar_lr.set,font=('Arial', 10))
        self.list_sample.place(x=30, y=33)
        self.list_sample.bind('<Double-Button-1>',self.click_left_printList) #双击 <Double-Button-1>
        
        self.sbar_lr.config(command=self.list_sample.yview)                
        self.sbar_lr.pack(side=LEFT, fill=Y)                     
        self.sbar_lr.pack(padx=10,pady=40)

        str_tips = '刷新，请先点选要发送的文件       '
        self.label_tips = Label(textvariable=self.svar_tips, font=('Arial', 11))
        self.label_tips.place(x=30, y=7)
        self.svar_tips.set(str_tips)
        
        str_file_detail_tips = '双击, 查看文件大小和时间'
        self.label_file_detail_tips = Label(textvariable=self.svar_file_detail_tips, font=('Arial', 10))
        self.label_file_detail_tips.place(x=30, y=725)
        self.svar_file_detail_tips.set(str_file_detail_tips)


        self.get_md5file()
        #读取MD5 文件

    def click_left_printList(self,event):
        click_index = self.list_sample.curselection()
        if click_index:
            #print(self.file_detail_tips[click_index[0]])
            self.svar_file_detail_tips.set(self.file_detail_tips[click_index[0]])

        #self.list_sample.geti


    def runCommand(self, selection):                   
        print('You selected:', selection)    
    
    # 退出键
    def command_btn_exit(self):

        self.master.destroy()

    def command_refresh_md5_btn_run(self):
        #self.scr.insert(1.0,'\n开始更新全部文件MD5值...')
        selected = self.list_sample.curselection()
        #print(selected)
        if len(selected) < 1:
            logger.info('pls select file.')
            str_tips = '刷新，请先点选要发送的文件                               '
            self.svar_tips.set(str_tips)
            return -1

        indexs_selected = self.list_sample.curselection()
        logger.info(indexs_selected)
        
        bool_all_file_new = True
        md5_list_temp = []
        for index in indexs_selected:        
            #index = int(self.list_sample.curselection()[0])
            str_trans_filename = self.list_sample.get(index)
            get_pos_temp = str_trans_filename.find(':')
            #logger.info('get_pos_temp:'+str(get_pos_temp))
            str_trans_filename = str_trans_filename[get_pos_temp+2:]
            str_trans_filename = self.ftplocaldir + str_trans_filename
            logger.info(str_trans_filename)
            
            file_md5_get_return = self.file_list_add_md5(str_trans_filename)
            if file_md5_get_return:
                md5_list_temp.append(file_md5_get_return)
            else:
                bool_all_file_new = False
                break

        if bool_all_file_new:
            try:
                with open(self.md5filename,'a+',encoding='utf-8') as writetofile:
                    for w_one_line in md5_list_temp:
                        writetofile.writelines(w_one_line+"\n")
                        one_md5_str_to_list = w_one_line.split('|')
                        self.file_md5_list.append([one_md5_str_to_list[0],one_md5_str_to_list[1],one_md5_str_to_list[2]])
                        logger.info(one_md5_str_to_list)

                for index in indexs_selected:
                    str_trans_filename = self.list_sample.get(index)
                    get_pos_temp = str_trans_filename.find(':')
                    str_trans_filename = str_trans_filename[get_pos_temp+2:]
                    str_trans_filename = self.ftplocaldir + str_trans_filename
                    logger.info('shuil_copy: '+str_trans_filename)
                    shutil_copy(str_trans_filename,os.path.join(self.targetdir,os.path.basename(str_trans_filename)))
                str_tips = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) +'  ' +str(len(indexs_selected))+ '个文件已发送:' 
                self.svar_tips.set(str_tips)
                self.svar_file_detail_tips.set(' ')
            except Exception as err_message:
                logger.error(err_message.__str__())
                logger.exception(sys.exc_info())                

        # 8：00 清理MD5文件，将180天前添加的记录删除
        curr_time_str = datetime.datetime.now().strftime('%H%M')
        if curr_time_str > '1601':
            if self.scr_history_have_clean:
                self.clean_journal()
                self.scr_history_have_clean = False
        else:
            self.scr_history_have_clean = True

    def run_ftp_fresh(self):
        
        str_tips = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        str_tips = '更新时间：' + str_tips 
        self.svar_tips.set(str_tips)

        dir_list = []
        file_list  =[]
        self.file_detail_tips = []
        self.Fresh_local_dir(self.ftplocaldir,file_list,dir_list)  # 从目标目录下载到本地目录d盘

        self.list_sample.delete(0,END)
        file_list.sort()

        pos=1
        for file_one in file_list:
            lfilemt= time.localtime(os.stat(file_one).st_mtime) #获取文件大小等属性
            lfilemt_str = time.strftime("%Y-%m-%d %H:%M:%S", lfilemt)
            lfsize = str(round((os.path.getsize(file_one))/1000,1)) +'k'            #获取文件修改时间

            file_one = file_one[len(self.ftplocaldir):] #截取不含默认路径的文件名
            self.list_sample.insert(pos,str(pos)+': '+file_one )
            self.file_detail_tips.append(file_one+'   size: '+str(lfsize) +'   时间:'+lfilemt_str)
            pos += 1


        # except Exception as err_message:
        #     print(err_message)
        #     #self.scr.insert(1.0, err_message )
        #     #self.scr.update()
        #     logger.error(err_message.__str__())
        #     logger.exception(sys.exc_info())

    # 主功能键
    def command_download_btn_run(self):
        
        logger.info("Run file list fresh...")
        self.run_ftp_fresh()
        
if __name__ == '__main__':
    
    os.environ['TZ'] = 'Asia/Shanghai'
    set_logging()
    main_window = Tk()
    main_window.title('文件传输检验小工具  v.20200416')

    #main_window.option_add('*Dialog.msg.font', 'Arial 22')

    # 设定窗口的大小(长 * 宽)，显示窗体居中，winfo_xxx获取系统屏幕分辨率。
    sw = main_window.winfo_screenwidth()
  
    sh = main_window.winfo_screenheight()
    ww = 1000
    wh = 760
    x = (sw - ww) / 2
    y = (sh - wh) / 2
    main_window.geometry("%dx%d+%d+%d" % (ww, wh, x, y))  # 这里的乘是小x
    logger.info('程序启动，program restart...')
    display = App(main_window)
    main_window.mainloop()
