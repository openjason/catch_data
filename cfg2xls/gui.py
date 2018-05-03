from tkinter import *

def show_entry_fields():
   print("First Name: %s\nLast Name: %s" % (e1.get(), e2.get()))
   e1.delete(0,END)
   e2.delete(0,END)

master = Tk()
Label(master, text="Username:").grid(row=0)
Label(master, text="Password:").grid(row=1)

e1 = Entry(master)
e2 = Entry(master)
e1.insert(10,"admin")
e2.insert(10,"")

e1.grid(row=0, column=1)
e2.grid(row=1, column=1)

Button(master, text='Quit', command=master.quit).grid(row=3, column=0, sticky=W, pady=4)
Button(master, text='获取配置文本', command=show_entry_fields).grid(row=3, column=1, sticky=W, pady=4)

mainloop( )