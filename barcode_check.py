#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author:jason

import tkinter as tk  # 使用Tkinter前需要先导入
import tkinter.messagebox
import pickle
from tkinter import scrolledtext # 导入滚动文本框的模块

# 第1步，实例化object，建立窗口window
window = tk.Tk()

# 第2步，给窗口的可视化起名字
window.title('二维码扫码检测内容匹配工具')

# 第3步，设定窗口的大小(长 * 宽)
window.geometry('900x600')  # 这里的乘是小x

# 第4步，加载 wellcome image
canvas = tk.Canvas(window, width=180, height=125, bg='green')
image_file = tk.PhotoImage(file='c:\\bak\\ep.png')
image = canvas.create_image(90, 0, anchor='n', image=image_file)
canvas.pack(side='top')
canvas.place(x=700,y=0)
#tk.Label(window, text='Wellcome', font=('Arial', 16)).pack()
# 第5步，用户信息
tk.Label(window, text='标准条码内容:', font=('Arial', 14)).place(x=20, y=25)

sampling_entry_context = ''
sampling_entry_context_len = 2
global str_sampling_curr


# 第6步，用户登录输入框entry
# 用户名
svar_sampling_standard = tk.StringVar()
svar_sampling_standard.set('1234')
entry_sampling_standard = tk.Entry(window, textvariable=svar_sampling_standard, width= 70, font=('Arial', 12))
entry_sampling_standard.place(x=20, y=55)

svar_sampling_curr = tk.StringVar()
svar_sampling_curr.set('采样...')

entry_sampling_curr = tk.Entry(window, textvariable=svar_sampling_curr, width= 70, font=('Arial', 12))
entry_sampling_curr.place(x=20, y=140)


scr = scrolledtext.ScrolledText(window)
scr.place(x=20, y=170)



# 第8步，定义用户登录功能
def barcode_check():
    entry_sampling_curr.focus_set()
    entry_sampling_curr.selection_range(0,len(entry_sampling_curr.get()))
    entry_sampling_curr.bind(sequence="<Key>", func=processKeyboardEvent)


def processKeyboardEvent(ke):
    str_sampling_curr =  entry_sampling_curr.get() #ke.char  # 按键对应的字符
    print(str_sampling_curr)
    if sampling_entry_context_len < len(str_sampling_curr):
        print("char:", sampling_entry_context_len,len(str_sampling_curr))  # 按键对应的字符
    else:
        print("len:",sampling_entry_context_len)
        str_sampling_curr=''


def get_standard_content():
    def button_caiyang():
        entry_new_name.selection_range(0,len(entry_new_name.get()))
        entry_new_name.focus_set()
        # 这里是打开我们记录数据的文件，将注册信息读出

    def button_return():
        # 以下三行就是获取我们注册时所输入的信息
        #global sampling_entry_context
        sampling_entry_context = entry_new_name.get()
        # 然后销毁窗口。
        svar_sampling_standard.set(sampling_entry_context)
        sampling_entry_context_len = len(sampling_entry_context)
        svar_sampling_curr.set(sampling_entry_context_len)
        print(sampling_entry_context_len)
        window_sign_up.destroy()

    # 定义长在窗口上的窗口
    window_sign_up = tk.Toplevel(window)
    window_sign_up.geometry('600x480')
    window_sign_up.title('标准卡二维码内容采样')

    new_name = tk.StringVar()  # 将输入的注册名赋值给变量
    new_name.set('1234')  # 将最初显示定为'example@python.com'
    tk.Label(window_sign_up, text='二维码内容: ').place(x=10, y=10)  # 将`User name:`放置在坐标（10,10）。
    entry_new_name = tk.Entry(window_sign_up, textvariable=new_name)  # 创建一个注册名的`entry`，变量为`new_name`
    entry_new_name.place(x=130, y=10)  # `entry`放置在坐标（150,10）.

    # 下面的 button_caiyang
    btn_comfirm_sign_up = tk.Button(window_sign_up, text='开始采样', command=button_caiyang)
    btn_comfirm_sign_up.place(x=80, y=70)
    btn_comfirm_sign_up = tk.Button(window_sign_up, text='采样结束', command=button_return)
    btn_comfirm_sign_up.place(x=180, y=70)


# 第7步，login and sign up 按钮
btn_login = tk.Button(window, text='开始检测', command=barcode_check)
btn_login.place(x=20, y=100)
btn_sign_up = tk.Button(window, text='读标准样卡', command=get_standard_content)
btn_sign_up.place(x=120, y=100)


# 第10步，主窗口循环显示
window.mainloop()
