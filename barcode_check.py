#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author:jason

import tkinter as tk  # 使用Tkinter前需要先导入
import tkinter.messagebox
import pickle
from tkinter import scrolledtext # 导入滚动文本框的模块
import time
import logging
from logging.handlers import RotatingFileHandler
import os.path
import sys


def set_logging(logfile_path):
    global logger
    logger = logging.getLogger('my_logger')
    handler = RotatingFileHandler(logfile_path + '\\barcode_check.log', maxBytes=5000000, backupCount=6)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    formatter = logging.Formatter('%(asctime)-12s  %(message)s')
    handler.setFormatter(formatter)


# 第1步，实例化object，建立窗口window
window = tk.Tk()

# 第2步，给窗口的可视化起名字
window.title('二维码内容检测工具')

# 第3步，设定窗口的大小(长 * 宽)
sw = window.winfo_screenwidth()
sh = window.winfo_screenheight()
ww = 900
wh = 600
x = (sw-ww)/2
y = (sh-wh)/2
window.geometry("%dx%d+%d+%d"%(ww,wh,x,y))  # 这里的乘是小x

# 第4步，加载 wellcome image
canvas = tk.Canvas(window, width=175, height=120, bg='green')
image_file = tk.PhotoImage(file='ep.png')
image = canvas.create_image(90, 0, anchor='n', image=image_file)
canvas.pack(side='top')
canvas.place(x=700,y=5)
#tk.Label(window, text='Wellcome', font=('Arial', 16)).pack()
# 第5步，用户信息
tk.Label(window, text='标准二维码内容:', font=('Arial', 14)).place(x=20, y=25)

sampling_entry_context = ''
sampling_entry_context_len = 2

int_compare_count =0
int_compare_ok =0
int_compare_diff =0


# 第6步，用户登录输入框entry
# 用户名
svar_sampling_standard = tk.StringVar()
svar_sampling_standard.set('请先点击初始化二维码内容...')
entry_sampling_standard = tk.Entry(window, textvariable=svar_sampling_standard, width= 64, font=('Arial', 12))
entry_sampling_standard.place(x=20, y=55)

svar_sampling_curr = tk.StringVar()
svar_sampling_curr.set('采样...')

entry_sampling_curr = tk.Entry(window, textvariable=svar_sampling_curr, width= 64, font=('Arial', 12))
entry_sampling_curr.place(x=20, y=140)


scr = scrolledtext.ScrolledText(window)
scr.place(x=20, y=170)

svar_label_checkok = tk.StringVar()
svar_label_checkok.set('二维码检测匹配正确 0次。')
label_checkok = tk.Label(window, textvariable=svar_label_checkok, font=('Arial', 12))
label_checkok.place(x=640, y=205)

svar_label_checkfailed = tk.StringVar()
svar_label_checkfailed.set('二维码检测匹配失败 0次。')
label_checkfailed = tk.Label(window, textvariable=svar_label_checkfailed, font=('Arial', 12), fg='red')
label_checkfailed.place(x=640, y=245)


# 第8步，定义用户登录功能
def barcode_check():
    svar_sampling_curr.set('等待扫码')
    entry_sampling_curr.focus_set()
    entry_sampling_curr.selection_range(0,len(entry_sampling_curr.get()))
    entry_sampling_curr.bind(sequence="<KeyRelease>", func=processKeyboardEvent)


def processKeyboardEvent(ke):
    global sampling_entry_context_len
    str_sampling_curr =  entry_sampling_curr.get() #ke.char  # 按键对应的字符
    #logger.info('s_len ' + str(sampling_entry_context_len))
    if len(str_sampling_curr) > (sampling_entry_context_len - 1) :
        #str_sampling_curr = str_sampling_curr + ke.char
        logger.info("chars:" + str_sampling_curr)  # 按键对应的字符
        string_compare(str_sampling_curr)
        entry_sampling_curr.selection_range(0,len(entry_sampling_curr.get()))
    #else:
    #    logger.info("ch, len:" + str_sampling_curr + str(len(str_sampling_curr)))
    
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
    if sampling_entry_context == str_curr:
        int_compare_ok = int_compare_ok +1
        #scr.insert(tk.INSERT,str_action_time+': compare ok\n')
        scr.insert(1.0, str_action_time + ': compare ok\n')
        logger.info(': compare ok')
        svar_label_checkok.set('二维码检测匹配正确 '+str(int_compare_ok)+'次。')

    else:
        int_compare_diff = int_compare_diff +1
        #scr.insert(tk.INSERT, ': 注意：扫码内容与样本不匹配.\n')
        scr.insert(1.0, str_action_time+': 注意：扫码内容与样本不匹配.\n')
        logger.info(str_curr + ' :注意：扫码内容与样本不匹配.')
        svar_label_checkfailed.set('二维码检测匹配失败 ' + str(int_compare_diff) + '次。')
        

def get_standard_content():
    def button_caiyang():
        entry_new_name.selection_range(0,len(entry_new_name.get()))
        entry_new_name.focus_set()
        # 这里是打开我们记录数据的文件，将注册信息读出

    def button_return():
        global sampling_entry_context_len
        global sampling_entry_context

        
        sampling_entry_context = entry_new_name.get()
        # 然后销毁窗口。
        svar_sampling_standard.set(sampling_entry_context)
        logger.info('svar_sampling_standard： ' + sampling_entry_context)
        sampling_entry_context_len = len(sampling_entry_context)
        svar_sampling_curr.set(sampling_entry_context_len)
        svar_sampling_curr.set('请点击二维码内容检测')
        print(sampling_entry_context_len)
        window_sign_up.destroy()

    # 定义长在窗口上的窗口
    sw = window.winfo_screenwidth()
    sh = window.winfo_screenheight()
    ww = 540
    wh = 300
    x = (sw - ww) / 2
    y = (sh - wh) / 2
    window_sign_up = tk.Toplevel(window)
    window_sign_up.geometry("%dx%d+%d+%d" % (ww, wh, x, y))
    window_sign_up.title('标准卡二维码内容采样')

    new_name = tk.StringVar()  # 将输入的注册名赋值给变量
    new_name.set('等待扫码...')  # 将最初显示定为'example@python.com'
    tk.Label(window_sign_up, text='二维码内容: ').place(x=10, y=10)  # 将`User name:`放置在坐标（10,10）。
    entry_new_name = tk.Entry(window_sign_up, textvariable=new_name, width= 64,)  # 创建一个注册名的`entry`，变量为`new_name`
    entry_new_name.place(x=10, y=30)  # `entry`放置在坐标（150,10）.

    # 下面的 button_caiyang
    #btn_comfirm_sign_up = tk.Button(window_sign_up, text='开始采样', command=button_caiyang)
    #btn_comfirm_sign_up.place(x=380, y=150)
    btn_comfirm_sign_up = tk.Button(window_sign_up, text='采样结束', command=button_return)
    btn_comfirm_sign_up.place(x=440, y=210)
    button_caiyang()





# 第7步，login and sign up 按钮
btn_login = tk.Button(window, text='  二维码内容检测  ', command=barcode_check)
btn_login.place(x=650, y=460)
btn_sign_up = tk.Button(window, text='初始化二维码内容', command=get_standard_content)
btn_sign_up.place(x=650, y=400)

os.path.abspath(sys.argv[0])
dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
realpathname, realfilename = os.path.split(os.path.realpath(sys.argv[0]))

set_logging(realpathname)

# 第10步，主窗口循环显示
window.mainloop()
