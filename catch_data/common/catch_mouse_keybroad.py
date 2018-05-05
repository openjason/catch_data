'''
Python:监控键盘输入、鼠标操作，并将捕获到的信息记录到文件中
标签： pythoninternetwindowskeyboardhook图形
2012-03-01 23:36 23090人阅读 评论(15) 收藏 举报
分类：
Python（65） 脚本语言（42）

版权声明：本文为博主原创文章，未经博主允许不得转载。

目录(?)[+]
  使用pyhook模块可以很快地完成键盘及鼠标事件捕获，此模块可从http://sourceforge.net/projects/pyhook/files/pyhook/1.5.1/下载，API手册：http://pyhook.sourceforge.net/doc_1.5.0/，网站上提供了个使用的例子，改写了下，将信息记录到文件中，本来想使用python的logging模块，但测试时发现，因为鼠标事件频率太高，导致写时报I/O错误的异常，所以使用了自己写文件记录日志的方式。

代码：

[python] view plain copy
print?
'''
#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pythoncom
import pyHook
import time


def onMouseEvent(event):
    "处理鼠标事件"
    fobj.writelines('-' * 20 + 'MouseEvent Begin' + '-' * 20 + '\n')
    fobj.writelines("Current Time:%s\n" % time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime()))
    fobj.writelines("MessageName:%s\n" % str(event.MessageName))
    fobj.writelines("Message:%d\n" % event.Message)
    fobj.writelines("Time_sec:%d\n" % event.Time)
    fobj.writelines("Window:%s\n" % str(event.Window))
    fobj.writelines("WindowName:%s\n" % str(event.WindowName))
    fobj.writelines("Position:%s\n" % str(event.Position))
    fobj.writelines('-' * 20 + 'MouseEvent End' + '-' * 20 + '\n')
    return True


def onKeyboardEvent(event):
    "处理键盘事件"
    fobj.writelines('-' * 20 + 'Keyboard Begin' + '-' * 20 + '\n')
    fobj.writelines("Current Time:%s\n" % time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime()))
    fobj.writelines("MessageName:%s\n" % str(event.MessageName))
    fobj.writelines("Message:%d\n" % event.Message)
    fobj.writelines("Time:%d\n" % event.Time)
    fobj.writelines("Window:%s\n" % str(event.Window))
    fobj.writelines("WindowName:%s\n" % str(event.WindowName))
    fobj.writelines("Ascii_code: %d\n" % event.Ascii)
    fobj.writelines("Ascii_char:%s\n" % chr(event.Ascii))
    fobj.writelines("Key:%s\n" % str(event.Key))
    fobj.writelines('-' * 20 + 'Keyboard End' + '-' * 20 + '\n')
    return True




if __name__ == "__main__":
    ''''' 
    Function:操作SQLITE3数据库函数 
    Input：NONE 
    Output: NONE 
    author: socrates 
    blog:http://blog.csdn.net/dyx1024 
    date:2012-03-1 
    '''

    #打开日志文件
    file_name = "F:\\test\\hook_log.txt"
    fobj = open(file_name,  'w')


    #创建hook句柄
    hm = pyHook.HookManager()


    #监控键盘
    hm.KeyDown = onKeyboardEvent
    hm.HookKeyboard()


    #监控鼠标
    hm.MouseAll = onMouseEvent
    hm.HookMouse()

    #循环获取消息
    pythoncom.PumpMessages()

    #关闭日志文件
    fobj.close()
