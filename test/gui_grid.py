# Grid(网格)布局管理器会将控件放置到一个二维的表格里。主控件被分割成一系列的行和列，表格中的每个单元(cell)都可以放置一个控件。
# 什么时候使用Grid管理器
# grid管理器是Tkinter里面最灵活的几何管理布局器。如果你不确定什么情况下从三种布局管理中选择，你至少要保证自己会使用grid。
# 当你设计对话框的时候，grid布局管理器是一个非常方便的工具。如果你之前使用pack进行布局的话，你会被使用grid后的简洁而震惊。与适应很多frame来让pack工作不同，在大多数情况下，你只需要将所有控件放置到容器中，然后使用grid将它们布局到任何你想要布局的地方。
# 参考下面这个例子：
# 使用pack进行布局的话，你不得不使用一些额外的frame控件，而且还需要花费一些功夫让他们变得好看。如果你使用grid的话，你只需要对每个控件使用grid,所有的东西都会以合适的方式显示。
# 注意：不要试图在一个主窗口中混合使用pack和grid。
# 使用grid进行布局管理非常容易。只需要创建控件，然后使用grid方法去告诉布局管理器在合适的行和列去显示它们。你不用事先指定每个网格的大小，布局管理器会自动根据里面的控件进行调节。

from tkinter import *

master = Tk()
var = IntVar()

Label(master, text="First").grid(sticky=E)
Label(master, text="Second").grid(sticky=E)

e1 = Entry(master)
e2 = Entry(master)

e1.grid(row=0, column=1)
e2.grid(row=1, column=1)

checkbutton = Checkbutton(master, text='Preserve aspect', variable=var)
checkbutton.grid(columnspan=2, sticky=W)

photo = PhotoImage(file='e:\\test\\tt.png')
label = Label(image=photo)
label.image = photo
label.grid(row=0, column=2, columnspan=2, rowspan=2, sticky=W+E+N+S, padx=5, pady=5)

button1 = Button(master, text='Zoom in')
button1.grid(row=2, column=2)

button2 = Button(master, text='Zoom out')
button2.grid(row=2, column=3)

mainloop()