# 对指定文件夹内文件进行清理，文件创建日期超指定时间的文件将删除，并记录日志
# author jc
# 2017-12-25
# 编写时间：20171226
# 用途：
# 用户交通银行FCC报表接收电脑，清理备份文件夹文件
# 功能：
# 脚本用于清理指定文件夹内超过指定时间（文件创建时间）的文件。
# 配置文件：
# time2clean.conf
# 参数说明：
# 参数workdir：待清理文件夹
# 参数dtime：（单位：分钟）超过以上时间的文件将删除
#
# 脚本不适用：
# 1、对只读文件、已打开或其他原因锁定文件无法执行删除。
# 2、对文件夹内的文件夹无法执行删除。
#
# 备注：需在系统计划任务添加相应任务，自动定时调用本脚本程序。

import logging
import os
import configparser
import time

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='time2clean.log',
                    filemode='a')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

def check_dir(work_dir,dtime):
    source_dir = work_dir
    FileList = []
    if not os.path.exists(source_dir):
        print('无法打开文件夹：' + source_dir)
    else:
        have_jdb_file = False
        for i in os.listdir(source_dir):
            fullname = os.path.join(source_dir,i)
            statinfo = os.stat(fullname)
            howlong  = statinfo.st_ctime - time.time()
            file_ctime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(statinfo.st_ctime))
            print(fullname + ' 文件创建时间:' + file_ctime)
            if abs(howlong/60) > dtime :
                try:
                    os.remove(fullname)
                    logging.info('删除文件' + fullname + ' 文件创建时间:' + file_ctime)
                except:
                    logging.info(fullname + ' 文件删除失败')
        return FileList

if __name__ == '__main__':
    cf = configparser.ConfigParser()
    try:
        cf.read("time2clean.conf")
        work_dir = cf.get("setting", "workdir")
        dtimestr = cf.get("setting", "dtime")
        dtime = int(dtimestr)
    except:
        print('missing file time2clean.conf or parser error.')
        exit(2)
    check_dir(work_dir,dtime)
