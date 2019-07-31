#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author:洪卫

import tkinter as tk  # 使用Tkinter前需要先导入
import tkinter.messagebox
import pickle
from tkinter import scrolledtext # 导入滚动文本框的模块

# 第1步，实例化object，建立窗口window
window = tk.Tk()

# 第2步，给窗口的可视化起名字
window.title('二维码扫码检测内容匹配工具')

# 第3步，设定窗口的大小(长 * 宽)
window.geometry('800x600')  # 这里的乘是小x

# 第4步，加载 wellcome image
canvas = tk.Canvas(window, width=180, height=125, bg='green')
image_file = tk.PhotoImage(file='c:\\bak\\ep.png')
image = canvas.create_image(90, 0, anchor='n', image=image_file)
canvas.pack(side='top')
canvas.place(x=500,y=0)
tk.Label(window, text='Wellcome', font=('Arial', 16)).pack()

# 第5步，用户信息
tk.Label(window, text='User name:', font=('Arial', 14)).place(x=10, y=170)
tk.Label(window, text='Password:', font=('Arial', 14)).place(x=10, y=210)

# 第6步，用户登录输入框entry
# 用户名
var_usr_name = tk.StringVar()
var_usr_name.set('采样')
entry_usr_name = tk.Entry(window, textvariable=var_usr_name, font=('Arial', 14))
entry_usr_name.place(x=120, y=175)
# 用户密码
scrolW = 170 # 设置文本框的长度
scrolH = 344 # 设置文本框的高度
#scr = scrolledtext.ScrolledText(win, width=scrolW, height=scrolH, wrap=tk.WORD)
scr = scrolledtext.ScrolledText(window)
scr.place(x=120, y=375)



entry_context = ''

# 第8步，定义用户登录功能
def usr_login():
    # 这两行代码就是获取用户输入的usr_name和usr_pwd
    usr_name = var_usr_name.get()
    usr_pwd = var_usr_pwd.get()

    # 这里设置异常捕获，当我们第一次访问用户信息文件时是不存在的，所以这里设置异常捕获。
    # 中间的两行就是我们的匹配，即程序将输入的信息和文件中的信息匹配。
    try:
        with open('usrs_info.pickle', 'rb') as usr_file:
            usrs_info = pickle.load(usr_file)
    except FileNotFoundError:
        # 这里就是我们在没有读取到`usr_file`的时候，程序会创建一个`usr_file`这个文件，并将管理员
        # 的用户和密码写入，即用户名为`admin`密码为`admin`。
        with open('usrs_info.pickle', 'wb') as usr_file:
            usrs_info = {'admin': 'admin'}
            pickle.dump(usrs_info, usr_file)
            usr_file.close()  # 必须先关闭，否则pickle.load()会出现EOFError: Ran out of input

    # 如果用户名和密码与文件中的匹配成功，则会登录成功，并跳出弹窗how are you? 加上你的用户名。
    if usr_name in usrs_info:
        if usr_pwd == usrs_info[usr_name]:
            tkinter.messagebox.showinfo(title='Welcome', message='How are you? ' + usr_name)
        # 如果用户名匹配成功，而密码输入错误，则会弹出'Error, your password is wrong, try again.'
        else:
            tkinter.messagebox.showerror(message='Error, your password is wrong, try again.')
    else:  # 如果发现用户名不存在
        is_sign_up = tkinter.messagebox.askyesno('Welcome！ ', 'You have not sign up yet. Sign up now?')
        # 提示需不需要注册新用户
        if is_sign_up:
            usr_sign_up()


# 第9步，定义用户注册功能
def usr_sign_up():
    def button_caiyang():
        entry_new_name.selection_range(0,len(entry_new_name.get()))
        entry_new_name.focus_set()
        # 这里是打开我们记录数据的文件，将注册信息读出

    def button_return():
        # 以下三行就是获取我们注册时所输入的信息
        #global entry_context
        entry_context = entry_new_name.get()
        # 然后销毁窗口。
        var_usr_name.set(entry_context)
        window_sign_up.destroy()

    # 定义长在窗口上的窗口
    window_sign_up = tk.Toplevel(window)
    window_sign_up.geometry('600x480')
    window_sign_up.title('标准卡二维码内容采样')

    new_name = tk.StringVar()  # 将输入的注册名赋值给变量
    new_name.set('345678')  # 将最初显示定为'example@python.com'
    tk.Label(window_sign_up, text='User name: ').place(x=10, y=10)  # 将`User name:`放置在坐标（10,10）。
    entry_new_name = tk.Entry(window_sign_up, textvariable=new_name)  # 创建一个注册名的`entry`，变量为`new_name`
    entry_new_name.place(x=130, y=10)  # `entry`放置在坐标（150,10）.

    # 下面的 button_caiyang
    btn_comfirm_sign_up = tk.Button(window_sign_up, text='开始采样', command=button_caiyang)
    btn_comfirm_sign_up.place(x=180, y=120)
    btn_comfirm_sign_up = tk.Button(window_sign_up, text='采样结束', command=button_return)
    btn_comfirm_sign_up.place(x=380, y=120)


# 第7步，login and sign up 按钮
btn_login = tk.Button(window, text='Login', command=usr_login)
btn_login.place(x=120, y=240)
btn_sign_up = tk.Button(window, text='Sign up', command=usr_sign_up)
btn_sign_up.place(x=200, y=240)

# 第10步，主窗口循环显示
window.mainloop()
