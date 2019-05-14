# 对指定文件夹内文件进行清理，文件创建日期超指定时间的文件将删除，并记录日志
# author jc
# 编写时间：2019-05-14
# 用途：
# 清理指定文件夹特定文件
# 功能：
# 脚本用于清理指定文件夹内超过指定时间（文件创建时间）的文件。
# 配置文件：
# folderclean.conf
# 参数说明：
# 参数folder：待清理文件夹
# 参数dtime：（单位：分钟）超过以上时间的文件将删除
# 参数filepatten：文件名匹配
# 脚本不适用：
# 1、对只读文件、已打开或其他原因锁定文件无法执行删除。
# 2、对文件夹内的文件夹无法执行删除。
#
# 备注：需在系统计划任务添加相应任务，自动定时调用本脚本程序。

import logging
import os
import sys
import configparser
import time

def set_logging(logfile_path):
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename = logfile_path + '\\foderclean.log',
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
    os.path.abspath(sys.argv[0])
    dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
    realpathname, realfilename = os.path.split(os.path.realpath(sys.argv[0]))

    set_logging(realpathname)

    cf = configparser.ConfigParser()
    try:
        cf.read(dirname + "foderclean.conf")
        work_dir = cf.get("setting", "folder")
        dtimestr = cf.get("setting", "dtime")
        dtimestr = cf.get("setting", "filepatten")
        dtime = int(dtimestr)
    except:
        print('missing file folderclean.conf or parser error.')
        exit(2)
    check_dir(work_dir,dtime)