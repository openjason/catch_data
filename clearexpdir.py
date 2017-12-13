# -*- coding: utf-8 -*-
# 2017-7-26

import os
import datetime,time
import os.path

rootdir = "E:\\日志同步"  # 指定被遍历的文件夹
logname = open(r"E:\\日志同步\\log.txt","a+")
this_day = time.strftime('%Y%m%d-%H%M%S', time.localtime(time.time()))


def getDirList(p):
#遍历指定文件夹内的文件夹名称，不含文件名及子文件夹名
    p = str(p)
    if p == "":
        return []
    p = p.replace("/", "\\")
    if p[-1] != "\\":
        p = p + "\\"
    a = os.listdir(p)
    b = [x for x in a if os.path.isdir(p + x)]
    return b


def is_valid_date(str):
    '''判断是否是一个有效的日期字符串'''
    tString = str
    if len(tString) < 8:
        return False
    tString = str[:8]
    try:
        datetime.datetime.strptime(tString, "%Y%m%d")
        return True
    except:
        return False


def is_expire(str):
    '''判断是否是 过期'''
    #    currdate = time.strftime('%Y%m%d',time.localtime(time.time()))
    currdate = datetime.date.today()
    checkdate = datetime.date(int(str[:4]), int(str[4:6]), int(str[6:8]))
    interval = currdate - checkdate
    rint = interval.days
    return rint


def removed(str):
    # 删除符合条件的文件夹（含文件夹内的子文件夹和文件）
    # 没有对文件及文件夹锁定情况进行判断。

    rootdir = str

    for parent, dirnames, filenames in os.walk(rootdir, False):
        for name in filenames:
            print(this_day, ":","删除文件", '文件名为：'+parent + '\\'+ name,file=logname)
            try:
                os.remove(os.path.join(parent, name))
            except:
                print(this_day, ":", "删除文件失败", '文件名为：' + parent + '\\' + name, file=logname)
        for name in dirnames:
            print(this_day, ":","删除文件夹", '文件夹名为：'+parent + '\\'+ name,file=logname)
            try:
                os.rmdir(os.path.join(parent, name))
            except:
                print(this_day, ":", "删除文件夹失败", '文件夹名为：' + parent + '\\' + name, file=logname)
    os.rmdir(str)


def clear_expired_dir():
    dirlists = getDirList(rootdir)  # 遍历指定文件夹内的文件夹，没有递归
    for str in dirlists:
        print(str)
        if is_valid_date(str):  # 判断是否符合日期型的文件夹'YYYYMMDD'
            if int(is_expire(str)) < 3:  # 文件夹名字 是否 与当前日期相差3天以上
                print('is 3days floder')
                print(this_day, ":", "保留文件夹", '文件夹名为：'+rootdir + '\\'+ str, file=logname)
            else:
                #                print(is_expire(str))
                removed(rootdir + '\\' + str)  # 删除符合条件的文件夹（含文件夹内的子文件夹和文件）
        else:
            print('not_valid_date')  # 非日期型的文件夹不做处理
            print(this_day, ":", "保留文件夹", '文件夹名为：'+rootdir + '\\'+ str, file=logname)

if __name__ == '__main__':
    clear_expired_dir()
#    logname.close()
