import tkinter as tk
from tkinter import *
import time

def current_time_str():
    """Get current date and time in ISO8601"""
    # https://en.wikipedia.org/wiki/ISO_8601
    # https://xkcd.com/1179/
    return time.strftime("%b %d %H:%M:%S", time.localtime())

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        self.now = tk.StringVar()
        self.label_time = tk.Label(root, textvariable=self.now,font=('Helvetica', 11)).grid(column=0, row=0)
        self.label_company = tk.Label(root, text="Eastcompeace.com").grid(column=1, row=0)

        self.label_c = tk.Label(root, text="安全部").grid(column=2, row=0)

#        self.QUIT = tk.Button(root, text="退出", fg="red", command=root.destroy).grid(column=3, row=0)

        self._scrolW = 170
        self._scrolH = 54

        self.txt = tk.Text(root, width=self._scrolW, height=self._scrolH)
        self.txt.grid(column=0, columnspan=3)
        self.txt_scrollbar = tk.Scrollbar(root)
        # S.grid(column=4,row = 1,sticky=tk.E+tk.W)
        self.txt_scrollbar.grid(sticky=E, row=1, rowspan=1, column=3, ipady=330)
        self.txt_scrollbar.config(command=self.txt.yview)
        self.txt.config(yscrollcommand=self.txt_scrollbar)

        global last_record
        self.f = "e:\\automail\\automail.log"
        self.fllist = ""

        self.onUpdate()

    def onUpdate(self):
        self.now.set(current_time_str())
        self.reload_logfile()
        self.after(1000, self.onUpdate)

    def get_last_n_lines(self,logfile, n):
        blk_size_max = 4096

        with open(logfile, 'r') as fp:
            lines = fp.readlines()
        n_lines = lines[len(lines)-n:len(lines)]
        return n_lines

    def  reload_logfile(self):
        self.fl = self.get_last_n_lines(self.f, 400)

        last_record = self.fl[len(self.fl)-1]
        for i in range(len(self.fl) - 1, 0, -1):
            self.fllist += self.fl[i]
        self.txt.delete(1.0,tk.END)
        self.txt.insert(tk.INSERT,self.fllist)
        self.txt.insert(tk.END,"本日志查看器只查看最近400行日志，如要查看之前日志，可直接查看源文件.ok.")


if __name__=="__main__":
    root = tk.Tk()
    root.title("AutoMail Log file Viewer")
    app = Application(master=root)
    root.mainloop()

















# def current_iso8601():
#     """Get current date and time in ISO8601"""
#     # https://en.wikipedia.org/wiki/ISO_8601
#     # https://xkcd.com/1179/
#     return time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
#
# class Application(tk.Frame):
#     def __init__(self, master=None):
#         tk.Frame.__init__(self, master)
#         self.pack()
#         self.createWidgets()
#
#     def createWidgets(self):
#         self.now = tk.StringVar()
#         self.time = tk.Label(self, font=('Helvetica', 24))
#         self.time.pack(side="top")
#         self.time["textvariable"] = self.now
#
#         self.QUIT = tk.Button(self, text="QUIT", fg="red",
#                                             command=root.destroy)
#         self.QUIT.pack(side="bottom")
#
#         # initial time display
#         self.onUpdate()
#
#     def onUpdate(self):
#         # update displayed time
#         self.now.set(current_iso8601())
#         # schedule timer to call myself after 1 second
#         self.after(1000, self.onUpdate)
#
# root = tk.Tk()
# app = Application(master=root)
# root.mainloop()
