# -*- coding: utf-8 -*-
# author:jasonc
# August 2019
# 条码枪读取内容匹配工具：
# 对待检测内容采样，作为匹配比对样本
# 读取条码枪扫码结果，与样本进行匹配，正确提示，出差错提示。

from tkinter import * # 使用Tkinter前需要先导入
import tkinter.messagebox
from tkinter import scrolledtext # 导入滚动文本框的模块
import time
import logging
from logging.handlers import RotatingFileHandler
import os.path
import sys

#初始化 检测匹配内容 检测次数清零
time_barcode_read_time = time.time()
sampling_entry_context = ''
sampling_entry_context_len = 2
str_test_catch_ch = ''
int_compare_count =0
int_compare_ok =0
int_compare_diff =0


class Watch(Frame):
    msec = 1000
    def __init__(self, parent=None, **kw):
            Frame.__init__(self, parent, kw)
            self._running = False
            self.timestr1 = StringVar()
            self.timestr2 = StringVar()
            self.makeWidgets()
            self.flag  = True
    def makeWidgets(self):
        l1 = Label(self, textvariable = self.timestr1)
        l2 = Label(self, textvariable = self.timestr2)
        l1.pack()
        l2.pack()
    def _update(self):
        self._settime()
        self.timer = self.after(self.msec, self._update)
    def _settime(self):
        global str_test_catch_ch
        #today1 = str(time.strftime('%Y-%m-%d', time.localtime(time.time())))
        time_delta = time.time()-time_barcode_read_time
        today1 = str(time_delta)
        time1 = str(time.strftime('%H:%M:%S', time.localtime(time.time())))
        print('str_test_catch_ch',len(str_test_catch_ch),time_delta)
        
        if time_delta > 1 and len(str_test_catch_ch)> 0 :
            string_compare(entry_sampling_curr.get())
            print(entry_sampling_curr.get())
            entry_sampling_curr.delete(0,tkinter.END)
            str_test_catch_ch = ''
            print('time_delta: ',time_delta)
            svar_label_prompt.set('等待扫码...')

        self.timestr1.set(today1)
        self.timestr2.set(time1)
    def start(self):
        self._update()
        #self.pack(side = TOP)

#设置日志文件，可循环文件大小。
def set_logging(logfile_path):
    global logger
    logger = logging.getLogger('my_logger')
    handler = RotatingFileHandler(logfile_path + '\\barcode_check.log', maxBytes=5000000, backupCount=6)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    formatter = logging.Formatter('%(asctime)-12s  %(message)s')
    handler.setFormatter(formatter)

# 实例化object，建立窗口window
window = tkinter.Tk()

# 给窗口的可视化起名字
window.title('二维码内容检测匹配工具 v.19080609')

# 设定窗口的大小(长 * 宽)，显示窗体居中，winfo_xxx获取系统屏幕分辨率。
sw = window.winfo_screenwidth()
sh = window.winfo_screenheight()
ww = 900
wh = 600
x = (sw-ww)/2
y = (sh-wh)/2
window.geometry("%dx%d+%d+%d"%(ww,wh,x,y))  # 这里的乘是小x

# 加载 wellcome image
canvas = tkinter.Canvas(window, width=175, height=120, bg='green')
image_file = tkinter.PhotoImage(file='ep.png')
image = canvas.create_image(90, 0, anchor='n', image=image_file)
canvas.pack(side='top')
canvas.place(x=650,y=5)

tkinter.Label(window, text='二维码检测内容:', font=('Arial', 14)).place(x=20, y=25)



# 扫码标准样本输入框entry
svar_sampling_standard = tkinter.StringVar()
svar_sampling_standard.set('请先点击初始化二维码内容...')
entry_sampling_standard = tkinter.Entry(window, textvariable=svar_sampling_standard, width= 64, font=('Arial', 12))
entry_sampling_standard.place(x=20, y=55)

# 当次扫码检测处理输入框entry
svar_sampling_curr = tkinter.StringVar()
svar_sampling_curr.set('采样...')
entry_sampling_curr = tkinter.Entry(window, textvariable=svar_sampling_curr, width= 64, font=('Arial', 12))
entry_sampling_curr.place(x=20, y=120)

# 提示label
svar_label_prompt = tkinter.StringVar()
svar_label_prompt.set('等待扫码...')
label_prompt = tkinter.Label(window, textvariable=svar_label_prompt, font=('Arial', 10))
label_prompt.place(x=20, y=145)
label_author = tkinter.Label(window, text='by流程与信息化部ITjc. August,2019', font=('Arial', 9))
label_author.place(x=20, y=580)

# 扫码结果输出框scrolledtext初始化
scr = scrolledtext.ScrolledText(window)
scr.place(x=20, y=170)

# 扫码结果汇总label
svar_label_checkok = tkinter.StringVar()
svar_label_checkok.set('检测匹配正确 0次。')
label_checkok = tkinter.Label(window, textvariable=svar_label_checkok, font=('Arial', 15))
label_checkok.place(x=650, y=205)

svar_label_checkfailed = tkinter.StringVar()
svar_label_checkfailed.set('检测匹配失败 0次。')
label_checkfailed = tkinter.Label(window, textvariable=svar_label_checkfailed, font=('Arial', 15), fg='red')
label_checkfailed.place(x=650, y=245)


# 扫码按键功能
def barcode_check():
    svar_sampling_curr.set('等待扫码')
    entry_sampling_curr.focus_set()
    entry_sampling_curr.selection_range(0,len(entry_sampling_curr.get()))
    entry_sampling_curr.bind(sequence="<KeyRelease>", func=processKeyboardEvent)
    btn_barcode_check.config(state = tkinter.DISABLED)
    #btn_barcode_check_next.config(state= tkinter.NORMAL)

# 重新扫码按键，重新开始功能按键
def barcode_check_next():
    global str_test_catch_ch
    global entry_sampling_curr
    entry_sampling_curr.delete(0, tkinter.END)
    str_test_catch_ch = ''
    svar_label_prompt.set('等待扫码...')

# 键盘按键事件获取
def processKeyboardEvent(ke):
    if ke.keycode < 14:
        return
    global sampling_entry_context_len
    global str_test_catch_ch
    global svar_label_prompt
    global time_barcode_read_time

    time_barcode_read_time = time.time()

    str_test_catch_ch = str_test_catch_ch + ke.char
    
    if len(str_test_catch_ch)> 0 :
        svar_label_prompt.set('内容长度不足...等待中...')

#这种方式读取entry控件的方法，在按键快的时候出错，不可使用
#    if len(str_sampling_curr) > (sampling_entry_context_len - 1) : 
#        #str_sampling_curr = str_sampling_curr + ke.char
#        logger.info("chars:" + str_sampling_curr)  # 按键对应的字符
#        string_compare(str_sampling_curr)
#        entry_sampling_curr.selection_range(0,len(entry_sampling_curr.get()))

    if len(str_test_catch_ch) > (sampling_entry_context_len -1):
        string_compare(entry_sampling_curr.get())
        #string_compare(str_test_catch_ch)
        #entry_sampling_curr.selection_range(0,len(entry_sampling_curr.get()))
        entry_sampling_curr.delete(0,tkinter.END)
        str_test_catch_ch = ''
        svar_label_prompt.set('等待扫码...')
    # 
    #else:
    #    logger.info("ch, len:" + str_sampling_curr + str(len(str_sampling_curr)))
    
# 字符串比较
def string_compare(str_curr):
    global sampling_entry_context
    global int_compare_ok
    global int_compare_count
    global int_compare_diff
    global svar_label_checkok
    global svar_label_checkfailed

    str_action_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print(sampling_entry_context,str_curr)
    int_compare_count = int_compare_count +1

    # 一奇怪的情况，扫码结果将： 转为了 ； ，原因不明，替换，
    # 存在隐患，扫描内容含‘；’‘\’ 将出错；
    #str_curr = str_curr.replace(';',':')
    #str_curr = str_curr.replace('\\','|')

    if sampling_entry_context == str_curr:
        print(sampling_entry_context ,str_curr)
        int_compare_ok = int_compare_ok +1
        #scr.insert(tkinter.INSERT,str_action_time+': compare ok\n')
        scr.insert(1.0, str_action_time + ': compare ok\n')
        logger.info(': compare ok')
        svar_label_checkok.set('检测匹配正确 '+str(int_compare_ok)+'次。')

    else:
        int_compare_diff = int_compare_diff +1
        #scr.insert(tkinter.INSERT, ': 注意：扫码内容与样本不匹配.\n')
        scr.insert(1.0, str_action_time+': 注意,扫码内容与样本不匹配:' + str_curr + '\n')
        logger.info(':注意：扫码内容与样本不匹配.' +str_curr )
        svar_label_checkfailed.set('检测匹配失败 ' + str(int_compare_diff) + '次。')
    if int_compare_count % 4444 == 0:
        scr.delete(444.0,tkinter.END)
        logger.info('excute delete scrolledtext content.') 

# 扫码标准内容获取功能
def get_standard_content():
    def button_caiyang():
        entry_new_name.selection_range(0,len(entry_new_name.get()))
        entry_new_name.focus_set()

    def button_return():
        global sampling_entry_context_len
        global sampling_entry_context

        sampling_entry_context = entry_new_name.get()
        svar_sampling_standard.set(sampling_entry_context)
        logger.info('样本: ' + sampling_entry_context)
        sampling_entry_context_len = len(sampling_entry_context)
        svar_sampling_curr.set(sampling_entry_context_len)
        svar_sampling_curr.set('请点击二维码内容检测')
        print(sampling_entry_context)
        window_sign_up.destroy()

    # 定义长在窗口上的窗口
    sw = window.winfo_screenwidth()
    sh = window.winfo_screenheight()
    ww = 540
    wh = 300
    x = (sw - ww) / 2
    y = (sh - wh) / 2
    window_sign_up = tkinter.Toplevel(window)
    window_sign_up.geometry("%dx%d+%d+%d" % (ww, wh, x, y))
    window_sign_up.title('标准卡二维码内容采样')

    new_name = tkinter.StringVar()  # 将输入的注册名赋值给变量
    new_name.set('等待扫码...')  # 将最初显示定为'example@python.com'
    tkinter.Label(window_sign_up, text='二维码内容: ').place(x=10, y=10)  # 将`User name:`放置在坐标（10,10）。
    entry_new_name = tkinter.Entry(window_sign_up, textvariable=new_name, width= 64,)  # 创建一个注册名的`entry`，变量为`new_name`
    entry_new_name.place(x=10, y=30)  # `entry`放置在坐标（150,10）.

    btn_comfirm_sign_up = tkinter.Button(window_sign_up, text='采样结束', command=button_return)
    btn_comfirm_sign_up.place(x=440, y=210)
    button_caiyang()


btn_barcode_check = tkinter.Button(window, text='开始检测二维码', command=barcode_check)
btn_barcode_check.place(x=650, y=460)
btn_barcode_init = tkinter.Button(window, text='初始化检测内容', command=get_standard_content)
btn_barcode_init.place(x=650, y=400)
btn_barcode_check_next = tkinter.Button(window, text=' 重新开始检测 ', command=barcode_check_next)
btn_barcode_check_next.place(x=770, y=460)

os.path.abspath(sys.argv[0])
dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
realpathname, realfilename = os.path.split(os.path.realpath(sys.argv[0]))

set_logging(realpathname)

mw = Watch(window)
mw.start()

window.mainloop()
