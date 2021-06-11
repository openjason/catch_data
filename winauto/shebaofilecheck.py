# -*- coding: utf-8 -*-  
''' 
    刷新指定文件夹，含文件夹内所有文件，没有对文件名/扩展名进行筛选，listbox显示，
    选择文件，发送到指定文件夹，发送前检测md5list文件内是否存在记录，存在发送记录的，
    平台提示重复发送，停止发送文件，不存在记录的，copy到指定文件夹。
    
    
版本: V1.02
功能：ftp同步完成后，将新同步的文件复制到指定文件夹，用于印刷系统。
开发时间：2020 10 22 13 34
配置文件.ini
[F配置]
#本地文件夹
localdir = F:\testt\
#目标文件夹
targetdir = F:\target\

'''

from tkinter import Tk
from tkinter.ttk import Treeview,Style
from configparser import ConfigParser
from tkinter import MULTIPLE,Message,Listbox,messagebox,Label,StringVar,Scrollbar, Button,END, DISABLED, Toplevel,SUNKEN,LEFT,Y  # 导入滚动文本框的模块
#from openpyxl import load_workbook,Workbook
import sys,os
from logging import getLogger,DEBUG,Formatter
from logging.handlers import RotatingFileHandler
import string,datetime,time  
import socket  
import hashlib
from shutil import copy as shutil_copy


def set_logging(base_dir):
    ##设置日志文件配置参数
    ##设置全局logger
    global logger
    logger = getLogger('balance_logger')
    handler = RotatingFileHandler(base_dir+'\\日志记录.log', maxBytes=5000000, backupCount=4)
    logger.setLevel(DEBUG)
    logger.addHandler(handler)
    formatter = Formatter('%(asctime)-12s %(filename)s %(lineno)d %(message)s')
    handler.setFormatter(formatter)

#定义类，脚本主要更能
class App():
    def __init__(self, master):

        self.master = master
        self.svar_tips = StringVar()
        self.svar_file_detail_tips = StringVar() 
        self.ftplocaldir = ''
        self.customer_sname = ''
        self.targetdir = ''
        self.label_tips = Label()
        #self.list_treeview = ttk.Treeview()
        self.filesymbol = ''
        self.pendingdir = ''
        self.savefilename = ''
        self.btn_download_init = None #Button()
        self.file_detail_tips = []
        self.scr_history_have_clean = False
        self.initWidgets(master)

 
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

    # 程序主gui界面。
    def initWidgets(self, fm1):

        base_dir=os.path.dirname(__file__)

        cp = ConfigParser()
        cp.read(base_dir+'\\配置文件.ini', encoding='gbk')
        try:
            #self.ftpremotedir  = cp.get('F配置', 'ftpremotedir')
            self.ftplocaldir   = cp.get('F配置', 'localdir')
            self.targetdir     = cp.get('F配置', 'targetdir')
        
        except Exception as err_message:
            print(err_message)
            return_message = messagebox.showinfo(title='提示',message='无法打开配置文件.ini或配置有误!' )
            exit(2)

        label_author = Label(fm1, text='by流程与信息化部IT. June,2020', font=('Arial', 9))
        label_author.place(x=814, y=717)

        self.btn_download_init = Button(fm1, text='  检  测  ', command=self.command_download_btn_run)
        self.btn_download_init.place(x=929, y=100)

        #self.btn_sendfile_init = Button(fm1, text='发送文件', command=self.command_refresh_md5_btn_run)
        #self.btn_sendfile_init.place(x=929, y=210)
        #btn_download_init.configure(state=DISABLED)

        btn_app_exit_init = Button(fm1, text='  退  出  ', command=self.command_btn_exit)
        btn_app_exit_init.place(x=929, y=270)

        self.sbar_lr = Scrollbar(fm1,width=20)


        self.style = Style()
        aktualTheme = self.style.theme_use()
        self.style.theme_create("dummy", parent=aktualTheme)
        self.style.theme_use("dummy")

        self.list_treeview = Treeview(fm1, columns=('F1', 'F2','F3'), show='headings',height=20)
        
        self.list_treeview.heading('F1', text='序号')
        self.list_treeview.heading('F2', text='内容')
        self.list_treeview.heading('F3', text='状态')
        self.list_treeview.column(0, width=40, stretch=True)
        self.list_treeview.column(1, width=730, stretch=True)
        self.list_treeview.column(2, width=40, stretch=True)
        self.list_treeview.pack()

        self.list_treeview.tag_configure('odd', background='#E6B3FF')
        self.list_treeview.tag_configure('even', background='yellow', foreground='red')
        self.list_treeview.tag_configure('A10', background='#E6B3FF', font='Arial 12')
        self.list_treeview.tag_configure('S', background='#E6B3FF', font=('Calibri', 9, 'bold'))


        #selectmode list多选模式multiple
        self.list_treeview.place(x=30, y=33)

        self.list_treeview.insert('', END, values=(str(1),'待检测',"Pass"), tags = ('even', 'A10'))


        self.sbar_lr.config(command=self.list_treeview.yview)                
        self.sbar_lr.pack(side=LEFT, fill=Y)                     
        self.sbar_lr.pack(padx=10,pady=40)

        str_tips = '刷新，请先点选检测 '
        self.label_tips = Label(textvariable=self.svar_tips, font=('Arial', 11))
        self.label_tips.place(x=30, y=7)
        self.svar_tips.set(str_tips)
        
        str_file_detail_tips = '双击, 查看文件大小和时间'
        self.label_file_detail_tips = Label(textvariable=self.svar_file_detail_tips, font=('Arial', 10))
        self.label_file_detail_tips.place(x=30, y=704)
        self.svar_file_detail_tips.set(str_file_detail_tips)


    def command_btn_exit(self):
        # 退出键
        self.master.destroy()


    def run_ftp_fresh(self):
        
        str_tips = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        str_tips = '检测时间：' + str_tips 
        self.svar_tips.set(str_tips)

        dir_list = []
        file_list  =[]
        self.file_detail_tips = []
        self.Fresh_local_dir(self.ftplocaldir,file_list,dir_list)  # 从目标目录下载到本地目录d盘

        #self.list_treeview.t.delete(1.0,END)
        obj = self.list_treeview.get_children()  # 获取所有对象
        for o in obj:
            self.list_treeview.delete(o)  # 删除对象


        pos=1
        for file_one in file_list:
            lfilemt= time.localtime(os.stat(file_one).st_mtime) #获取文件大小等属性
            lfilemt_str = time.strftime("%Y-%m-%d %H:%M:%S", lfilemt)
            lfsize = str(round((os.path.getsize(file_one))/1000,1)) +'k'            #获取文件修改时间

            file_one = file_one[len(self.ftplocaldir):] #截取不含默认路径的文件名
            #self.list_treeview.insert(pos,str(pos)+': '+file_one )
            self.list_treeview.insert('', END, values=(str(pos),file_one,'Pass'), tags = ('S'))
            self.list_treeview.insert('', END, values=(str(pos),file_one,"失败"), tags = ('even', 'A10'))
            #self.tree.insert('', tk.END, values=(f'first {n}', f'last {n}', f'email{n}@example.com'), tags = ('S'))
            self.list_treeview.update()
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
        
        logger.info("Run file list refresh...")
        self.run_ftp_fresh()

def onFormEvent(event):
    #for key in dir( event ):
    #    if not key.startswith( '_' ):
    #        print('%s=%s' % ( key, getattr( event, key ) ))
    #if getattr( event, 'widget' ) == '.':
    #print(dir(event))
    #print(type(event.type),event.type)
    if (len(str(event.widget))) == 1:
        print('%s=%s' % ( event.width,event.height ))

        #if getattr( event, key ) == '.':
        #print('event.type=  ',event.type)
            

if __name__ == '__main__':

    base_dir=os.path.dirname(__file__)
    print(base_dir)  #临时修改环境变量    

    #os.environ['TZ'] = 'Asia/Shanghai'
    set_logging(base_dir)
    main_window = Tk()
    main_window.title('三代社保文件检验小工具 - Eastcompeace v.20210609')

    #main_window.option_add('*Dialog.msg.font', 'Arial 22')

    # 设定窗口的大小(长 * 宽)，显示窗体居中，winfo_xxx获取系统屏幕分辨率。
    sw = main_window.winfo_screenwidth()
  
    sh = main_window.winfo_screenheight()
    ww = 1000
    wh = 740
    x = (sw - ww) / 2
    y = (sh - wh) / 2
    main_window.geometry("%dx%d+%d+%d" % (ww, wh, x, y))  # 这里的乘是小x
    main_window.bind( '<Configure>', onFormEvent )
    logger.info('program restart...')
    display = App(main_window)
    main_window.mainloop()
    #SW_SHOWMAXIMIZED\SW_MINIMIZE\WM_DELETE_WINDOW
