#  -*- coding: utf-8 -*-
#auther: jason chan

import collections
import threading
import time
import os
import tkinter as tk
from tkinter import *
from tkinter.messagebox import askyesno
from tkinter import scrolledtext # 导入滚动文本框的模块
last_record = 'none'
def tail(filename, n=10):
    'Return the last n lines of a file'
    return collections.deque(open(filename), n)

def get_last_n_lines(logfile, n):
    blk_size_max = 4096

    with open(logfile, 'r') as fp:
        lines = fp.readlines()
    n_lines = lines[len(lines)-n:len(lines)]
    return n_lines


win = tk.Tk()
win.title("AutoMail Log file Viewer") # 添加标题
tk.Label(win, text="安全部").grid(column=1, row=0)
# 添加一个标签，并将其列设置为1，行设置为0
tk.Label(win, text="Eastcompeace.com").grid(column=0, row=0)
# 设置其在界面中出现的位置 column代表列 row 代表行 # button被点击之后会被执行
def clickMe(): # 当acction被点击时,该函数则生效
    ans = askyesno(title='Warning',message='Close the window?')
    if ans:
#        timer.cancel()
        win.destroy()
    else:
        return
# 按钮
action = tk.Button(win, text="退出", command=clickMe)
# 创建一个按钮, text：显示按钮上面显示的文字, command：当这个按钮被点击之后会调用command函数
action.grid(column=2, row=0) # 设置其在界面中出现的位置 column代表列 row 代表行 # 文本框
name = tk.StringVar() # StringVar是Tk库内部定义的字符串变量类型，在这里用于管理部件上面的字符；不过一般用在按钮button上。改变StringVar，按钮上的文字也随之改变。
nameEntered = tk.Entry(win, width=12, textvariable=name) # 创建一个文本框，定义长度为12个字符长度，并且将文本框中的内容绑定到上一句定义的name变量上，方便clickMe调用 nameEntered.grid(column=0, row=1) # 设置其在界面中出现的位置 column代表列 row 代表行 nameEntered.focus() # 当程序运行时,光标默认会出现在该文本框中 # 创建一个下拉列表
number = tk.StringVar()
chVarDis = tk.IntVar() # 用来获取复选框是否被勾选，通过chVarDis.get()来获取其的状态,其状态值为int类型 勾选为1 未勾选为0

radVar = tk.IntVar() # 通过tk.IntVar() 获取单选按钮value参数对应的值

scrolW = 170 # 设置文本框的长度
scrolH = 54 # 设置文本框的高度
#scr = scrolledtext.ScrolledText(win, width=scrolW, height=scrolH, wrap=tk.WORD)
txt = tk.Text(win,width= scrolW,height=scrolH)
txt.grid(column=0,columnspan  = 3)
S = tk.Scrollbar(win)
#S.grid(column=4,row = 1,sticky=tk.E+tk.W)
S.grid(sticky=E, row = 1, rowspan = 1, column = 3, ipady = 340)
S.config(command=txt.yview)
txt.config(yscrollcommand=S.set)
#scr = scrolledtext.ScrolledText(win, width=scrolW, height=scrolH)
#scr.grid(column=0, columnspan=3)  # columnspan 个人理解是将3列合并成一列 也可以通过 sticky=tk.W 来控制该文本框的对齐方式

def fun_timeer():
#    print("hello timeer.")
    global timer
    reload_logfile()
#    timer = threading.Timer(5,fun_timeer)
#    timer.start()
    win.after(1000,fun_timeer)

# timer = threading.Timer(1,fun_timeer)
# timer.start()

#time.sleep(20)#20秒后停止定时器
#timer.cancel()

def  reload_logfile():
    global last_record
    f = "e:\\automail\\automail.log"
    fl = get_last_n_lines(f, 400)
    fllist = ""
#    if not (fl[len(fl)-1] == last_record):
    last_record = fl[len(fl)-1]
    for i in range(len(fl) - 1, 0, -1):
        fllist += fl[i]
    txt.delete(1.0,tk.END)
    txt.insert(tk.INSERT,fllist)
    txt.insert(tk.END,"本日志查看器只查看最近400行日志，如要查看之前日志，可直接查看源文件.ok.")

if __name__=="__main__":
    reload_logfile()
    win.mainloop() # 当调用mainloop()时,窗口才会显示出来
