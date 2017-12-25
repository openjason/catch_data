# 对指定文件夹内文件进行清理，文件创建日期超指定时间的文件将删除，并记录日志
# author openjc
# 2017-12-25


import logging
import os
import ctypes
import time

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='time2clean.log',
                    filemode='a')
#################################################################################################
# 定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)


def check_dir(work_dir):
    source_dir = work_dir
    FileList = []
    if not os.path.exists(source_dir):
        print('无法打开' + source_dir)
    else:
        have_jdb_file = False
        for i in os.listdir(source_dir):
            fullname = os.path.join(source_dir,i)
            statinfo = os.stat(fullname)
            howlong  = statinfo.st_ctime - time.time()
            file_ctime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(statinfo.st_ctime))
            print (fullname + ':' + file_ctime)
            if abs(howlong/60) > 15 :
                print(abs(howlong/60))
                os.remove(fullname)
                logging.info(fullname)

        return FileList

if __name__ == '__main__':
    work_dir = 'E:\\upload.succ\\'
    check_dir(work_dir)
