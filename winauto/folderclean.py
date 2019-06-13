# 对指定文件夹内文件进行清理，文件创建日期超指定时间的文件将删除，并记录日志
# author jc
# 编写时间：2019-06-12
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
from logging.handlers import RotatingFileHandler
import os
import sys
import configparser
import time
import string
import platform



def set_logging(logfile_path):
    global logger
    logger = logging.getLogger('my_logger')
    handler = RotatingFileHandler(logfile_path + '\\folderclean.log', maxBytes=2000000, backupCount=6)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    formatter = logging.Formatter('%(asctime)-12s  %(message)s')
    handler.setFormatter(formatter)

def GetDesktopPath():
    platform_string = platform.platform()
    logger.info(platform_string)
    if 'Windows-7' in platform_string:
        return os.path.join(os.path.expanduser("~"), 'Desktop')
    elif 'Windows-XP' in platform_string:
        return os.path.join(os.path.expanduser("~"), '桌面')
    else:
        return os.path.join(os.path.expanduser("~"), 'Desktop')


def check_dir(work_dir, dtime, filepatten_list):
    source_dir = work_dir
    FileList = []

    #若为空，则直接返回
    if len(work_dir) < 1:
        return FileList

    if not os.path.exists(source_dir):
        logger.info('无法打开文件夹：' + source_dir)
    else:
        have_jdb_file = False
        for i in os.listdir(source_dir):
            fullname = os.path.join(source_dir,i)
            statinfo = os.stat(fullname)
            howlong  = statinfo.st_ctime - time.time()
            file_ctime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(statinfo.st_ctime))
            #print(fullname + ' 文件创建时间:' + file_ctime)
            logger.info(fullname + ' 文件创建时间:' + file_ctime)
            if abs(howlong/60) > dtime :
                for j in range(len(filepatten_list)):
                    if filepatten_list[j] in os.path.basename(fullname):
                        print(fullname + ' match patten:' + filepatten_list[j])
                        try:
                            os.remove(fullname)
                            logger.info('删除文件' + fullname + ' 文件创建时间:' + file_ctime)
                        except:
                            logger.info(fullname + ' 文件删除失败')
        return FileList

if __name__ == '__main__':
    os.path.abspath(sys.argv[0])
    dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
    realpathname, realfilename = os.path.split(os.path.realpath(sys.argv[0]))

    set_logging(realpathname)

    cf = configparser.ConfigParser()
    cffile = os.path.join(realpathname,"folderclean.conf")
    try:
        cf.read(cffile,encoding='GBK')
        folder_str = cf.get("setting", "folder")
        dtimestr = cf.get("setting", "dtime")
        filepatten = cf.get("setting", "filepatten")
        dtime = int(dtimestr)
        filepatten = filepatten.replace('*','')
        filepatten_list = filepatten.split('|')
        folder_list = folder_str.split('|')
    except Exception as e:
        logger.info(e)
        exit(1)
    for im in range(len(folder_list)):
        work_dir = folder_list[im]
        check_dir(work_dir,dtime,filepatten_list)
    work_dir = GetDesktopPath()
    check_dir(work_dir, dtime, filepatten_list)
