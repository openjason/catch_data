#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
ZetCode Tkinter tutorial

In this program, we use the
tkFileDialog to select a file from
a filesystem.

author: Jan Bodnar
last modified: July 2017
website: www.zetcode.com
"""

from tkinter import Frame, Tk, BOTH, Text, Menu, END
from tkinter import filedialog
import re

class Example(Frame):

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):

        self.master.title("File dialog")
        self.pack(fill=BOTH, expand=1)

        menubar = Menu(self.master)
        self.master.config(menu=menubar)

        fileMenu = Menu(menubar)
        fileMenu.add_command(label="Open", command=self.onOpen)
        menubar.add_cascade(label="File", menu=fileMenu)

        self.txt = Text(self)
        self.txt.pack(fill=BOTH, expand=1)


    def onOpen(self):

        ftypes = [('Python files', '*.py'), ('All files', '*')]
        dlg = filedialog.Open(self, filetypes = ftypes)
        fl = dlg.show()

        if fl != '':
            text = self.readFile(fl)
            self.txt.insert(END, text)


    def readFile(self, filename):

        with open(filename, "r") as f:
            text = f.read()

        return text

def get_customer_mail_list(toaddr):
    _mail_list =[]
    _to_addr = toaddr.split("|")
    for i in range(len(_to_addr)):
        if len(_to_addr[i]) > 7:
            if re.match(
                    '^[\w\d]+[\d\w\-\.]+@([\d\w-]+)\.([\d\w-]+)(?:\.[\d\w-]+)?$|^(?:\+86)?(\d{3})\d{8}$|^(?:\+86)?(0\d{2,3})\d{7,8}$',
                    _to_addr[i]) != None:
                _mail_list.append(_to_addr[i])
            else:
                print("邮件地址有误："+_to_addr[i])
    return _mail_list



if __name__ == '__main__':
    tstr= "ab-c@abc.com|dit@jx-bank.com|d_dd@163.com|ac_c.dd@di_r.com"
    ts = get_customer_mail_list(tstr)
    print(ts)