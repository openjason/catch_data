'''Tkinter教程之Grid篇'''
# Tkinter参考中最推荐使用的一个布局器。实现机制是将Widget逻辑上分割成表格，在指定的位置放置想要的Widget就可以了。
'''1.第一个Grid例子'''
# -*- coding: cp936 -*-
# 使用grid来布局组件
from tkinter import *
root = Tk()
# 创建两个Label
lb1 = Label(root,text = 'Hello')
lb2 = Label(root,text = 'Grid')

lb1.grid()
lb2.grid()

root.mainloop()
# grid有两个最为重要的参数，用来指定将组件放置到什么位置，一个是row,另一个是column。如果不指定row,会将组件放置到第一个可用的行上，如果不指定column，则使用第一列。
'''2.使用row和column来指定位置'''
# -*- coding: cp936 -*-
# 使用grid来布局组件
from Tkinter import *
root = Tk()
# 创建两个Label
lb1 = Label(root,text = 'Hello')
lb2 = Label(root,text = 'Grid')

lb1.grid()
# 指定lb2为第一行（使用索引0开始），第二列（使用索引0开始）
lb2.grid(row = 0,column = 1)

root.mainloop()
# grid有两个最为重要的参数，用来指定将组件放置到什么位置，一个是row,另一个是column。如果不指定row,会将组件放置到第一个可用的行上，如果不指定column，则使用第一列。注意这里使用grid时不需要创建，直接使用行列就可以。
'''3.为其它组件预定位置'''
# 可以使用row/column来指定组件的放置位置，并预先留出空间，以务其它需要。
# -*- coding: cp936 -*-
# 使用grid来布局组件
from Tkinter import *
root = Tk()
# 创建两个Label
Label(root,text = 'Hello').pack()
# 在第一行，第10列放置lb2
Label(root,text = 'Grid').grid(row = 0,column = 10)
# Lable(root,text = '3').grid(row = 0,column = 5)
root.mainloop()
# 这个例子中将lb2放置到第1行，第11列位置上，但运行结果与上一例从效果上看不出太大的区别。原因是：如果这个位置没有组件的话，它是看不可见的。
'''4.将组件放置到预定位置上去'''
# -*- coding: cp936 -*-
# 使用grid来布局组件
from Tkinter import *
root = Tk()
# 创建两个Label
Label(root,text = '1').grid()
# 在第1行，第11列放置lb2
Label(root,text = '2').grid(row = 0,column = 10)
Label(root,text = '3').grid(row = 0,column = 5)
root.mainloop()
# 可以看到Label('3')是位置Label('1')和Label('2')之间了，即Label('2')是在11列，Label('3')位于第3列
'''5.将两个或多个组件同一个位置'''
# -*- coding: cp936 -*-
# 多个组件同时grid到同一个表格位置
from Tkinter import *
root = Tk()
# 创建两个Label
lb1 = Label(root,text = '1')
lb2 = Label(root,text = '2')

# 将lb1和lb2均grid到(0,0)位置
lb1.grid(row = 0,column = 0)
lb2.grid(row = 0,column = 0)

def forgetLabel():
    # grid_slaves返回grid中(0,0)位置的所有组件
    # grid_forget将这个组件从grid中移除（并未删除，可以使用grid再将它显示出来)
    print (root.grid_slaves(0,0)[0].grid_forget())

# 我测试时grid_salves返回的第一个值为lb2，最后grid的那一个
Button(root,text = 'forget last',command = forgetLabel).grid(row = 1)

root.mainloop()
# 这段代码是用来证明，多个组件同时放置到同一个位置上会产生覆盖的问题。对于grid_slaves返回的组件list如何排序，我没有去查想着资料，在这个例子中使用索引0，返回的正好是lb2,然后再使用grid_forget将这个删除从grid中移除，可以看到lb1显示出来了。
'''6.改变列（行）的属性值'''
# -*- coding: cp936 -*-
# 设置column的属性(columnconfigure)
from Tkinter import *
root = Tk()
# 创建两个Label
lb1 = Label(root,text = '1',bg = 'red')
lb2 = Label(root,text = '2',bg = 'blue')

# 将lb1和lb2分别放置到第1行的1,2列位置上
lb1.grid(row = 0,column = 0)
lb2.grid(row = 0,column = 1)

# 指定列的最小宽度为100
root.columnconfigure(0,minsize = 100)
root.mainloop()
# 1与2的距离变的远一些了。
# 但如果这个位置没有组件存在的话这个值是不起作用的.
# 设置列或行(rowconfigure)的属性时使用父容器的方法,不是自己调用。
'''7.组件使用多列（多行）'''
# -*- coding: cp936 -*-
# 使用多行（多列)
from Tkinter import *
root = Tk()
# 创建如下布局（一个字符占用一个grid位置）
# A  E
# B C
# D
# A占用(0,0)(0,1),B占用(1,0),C占用(1,1),D占用(2,0),E占用(0,2)
# 创建5个Label，分别以背景色区别
lbA = Label(root,text = 'A',bg = 'red')
lbB = Label(root,text = 'B',bg = 'blue')
lbC = Label(root,text = 'C',bg = 'red')
lbD = Label(root,text = 'D',bg = 'blue')
lbE = Label(root,text = 'E',bg = 'blue')
# 以下为布局参数设置
lbA.grid(row = 0,column = 0,columnspan = 2)
lbB.grid(row = 1,column = 0)
lbC.grid(row = 1,column = 1)
lbD.grid(row = 2)
lbE.grid(row = 0,column = 2)

root.mainloop()
# A与B、D的区别，它左边已改变，由于使用了两个表格；
# C与E的区别：C的右边与E的左边对齐，也就是说E被放置到第2列的下一个位置了，原因由于A已使用了第2列。
'''8.设置表格中组件的对齐属性'''
# -*- coding: cp936 -*-
# 使用sticky设置对齐方式
from Tkinter import *
root = Tk()
# 创建两个Label
Label(root,text = 'hello sticky').grid()
Label(root,text = 'Tkinter').grid()
# 创建两个Label，并指定sticky属性
Label(root,text = 'hello sticky').grid(sticky = W)
Label(root,text = 'Tkinter').grid(sticky = W)

root.mainloop()
# 默认属性下，组件的对齐方式为居中，设置sticky属性可以控制对齐方式，可用的值（N,S,E,W)及其组合值
