# for python 3.x use 'tkinter' rather than 'Tkinter'
import tkinter as tk
import time

# class App():
#     def __init__(self):
#         self.root = tk.Tk()
#         self.label = tk.Label(text="")
#         self.label.pack()
#         self.update_clock()
#         self.root.mainloop()
#
#     def update_clock(self):
#         now = time.strftime("%H:%M:%S")
#         self.label.configure(text=now)
#         self.root.after(1000, self.update_clock)
#
# app=App()
#
#


########################333

#!/usr/bin/env python3

# Display UTC.
# started with https://docs.python.org/3.4/library/tkinter.html#module-tkinter

import tkinter as tk
import time

def current_iso8601():
    """Get current date and time """
    return time.strftime("%Y%m%d %H:%M:%S", time.localtime())

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        #        self.pack()
        self.f = "e:\\automail\\automail.log"

        self.createWidgets()
        self.fp

    def get_last_n_lines(logfile, n):
        with open(logfile, 'r') as fp:
            lines = fp.readlines()
        n_lines = lines[len(lines) - n:len(lines)]
        return n_lines

    def createWidgets(self):
        self.now = tk.StringVar()
        self.time = tk.Label(self, font=('Helvetica', 24))
        self.time.pack(side="top")
        self.time["textvariable"] = self.now

        self.QUIT = tk.Button(self, text="QUIT", fg="red",
                                            command=root.destroy)
        self.QUIT.pack(side="bottom")

        # initial time display
        self.onUpdate()

    def onUpdate(self):
        # update displayed time
        self.now.set(current_iso8601())
        # schedule timer to call myself after 1 second
        self.after(1000, self.onUpdate)

root = tk.Tk()
app = Application(master=root)
root.mainloop()
