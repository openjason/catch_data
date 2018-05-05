import tkinter
from tkinter import ttk


def setUp(self):
    support.root_deiconify()
    self.nb = ttk.Notebook()
    self.child1 = ttk.Label()
    self.child2 = ttk.Label()
    self.nb.add(self.child1, text='a')
    self.nb.add(self.child2, text='b')

root = tkinter.Tk()

style = ttk.Style()
style.map("C.TButton",
    foreground=[('pressed', 'red'), ('active', 'blue')],
    background=[('pressed', '!disabled', 'black'), ('active', 'white')]
    )

colored_btn = ttk.Button(text="Test", style="C.TButton").pack()
setUp(self)


root.mainloop()
