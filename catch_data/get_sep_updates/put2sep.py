# -*- coding: utf-8 -*-
#程序功能：检测cdrom上有无jdb定义库，有则ftp到sep服务器手动更新文件夹
#author：jasonchan
#2017-11-30

import ftplib
import os
import socket
import logging
import ctypes

#获取本机IP地址，用于记录日志
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("10.66.7.2", 80))
    print("active ip:%s" %s.getsockname()[0])
    Local_IP = s.getsockname()[0]
except:
    print("can not get ip addr.")
    Local_IP = 'None'

#日志记录文件格式配置
logging.basicConfig(level=logging.INFO,
                    format=Local_IP + ' %(asctime)s %(message)s',
                    datefmt='%Y%m%d %H:%M:%S',
                    filename='aupd_log.txt',
                    filemode='a')
logging.info('自动更新程序启动 local_ip:%s' %Local_IP)
#HOST是远程FTP地址
HOST = ''
USER = 'test'
USERPWD = 'test'
host_dir = ''


def UlFtpFile(f, downloadlist):
    localdir = os.getcwd()
    pathname = os.path.dirname(downloadlist)
    rawfilename = os.path.basename(downloadlist)
    localfilepath = localdir + pathname
    print('getfile:', pathname, ' l:', localfilepath, ' r:', rawfilename)
    logging.info('路径:'+pathname+ '本地:'+ localfilepath+ '文件名:'+ rawfilename)
    # ftp 转到指定工作目录
    try:
        f.cwd(pathname)
    except:
        print('无效路径:',pathname)
        logging.info('无效路径:'+pathname)
        f.quit()
        return 1
    # print('RETR %s' % rawfilename)
    try:
        f.storbinary('APPE %s' % rawfilename, open(rawfilename, 'rb'))
    except:
        print('无法上传',rawfilename)
        logging.info('无法上传'+rawfilename)
        os.unlink(getfile)
        return 2
    print('文件"%s"上传成功' % rawfilename)
    logging.info ('文件上传成功:'+rawfilename)
    return 0


def DlFtpFile(f, downloadlist):
    localdir = os.getcwd()
    pathname = os.path.dirname(downloadlist)
    rawfilename = os.path.basename(downloadlist)
    localfilepath = localdir + pathname
    #        localfilepath = localfilepath.replace('/','\\')
    #        localfilepath = localfilepath.replace('\\','\\\\')
    print('getfile:', pathname, ' l:', localfilepath, ' r:', rawfilename)
    logging.info('路径:'+pathname+ '本地:'+ localfilepath+ '文件名:'+ rawfilename)
    # ftp 转到指定工作目录
    try:
        f.cwd(pathname)
    except:
        print('无效路径:',pathname)
        logging.info('无效路径:'+pathname)
        f.quit()
        return 1

    # print('RETR %s' % rawfilename)
    try:
        f.retrbinary('RETR %s' % rawfilename, open(rawfilename, 'wb').write)
    except:
        print('无法下载',rawfilename)
        logging.info('无法下载'+rawfilename)
        os.unlink(getfile)
        return 2
    print('文件"%s"下载成功' % rawfilename)
    logging.info ('文件下载成功:'+rawfilename)
    return 0

def get_remote_ver_file(f, dir):
#读取指定ftp服务器dir下目录的文件
#参数f：已打开的ftp服务器连接，dir：指定需遍历的路径。
    try:
        f.cwd(dir)
    except ftplib.error_perm:
        print('列出当前目录失败:',dir)
        logging.info('列出当前目录失败:' + dir)
        return
    #创建列表，用于保存遍历的文件（含路径）
    downloadlist = f.mlsd()
    for i in downloadlist:
        rawfilename = i[0]
        if rawfilename[:3] == 'ver' and rawfilename[3:11].isdigit():
            return rawfilename
    logging.info('服务器无版本信息文件.')
    return

def get_local_version():
    try:
        with open('version.txt','r') as fp:
            l_ver = fp.readline()
            global host_ip
            global host_dir
            host_ip = fp.readline()
            host_dir = fp.readline()

        l_ver =  l_ver.strip()
        if l_ver[:3] == 'ver' and l_ver[3:11].isdigit():
            return l_ver
        else:
            logging.info('本机版本文件版本信息格式有误:%s',l_ver)
            return
    except:
#        logging.info('读取版本文件信息失败。')
        return



def ftpmain():
    try:
        f = ftplib.FTP(HOST)
        f.encode = 'utf-8'
    except:
        print('无法连接到"%s"' % HOST)
        logging.info('无法连接到"%s"' % HOST)
        return
    print('连接到: %s' % HOST)
    logging.info('连接到%s .' % HOST)
    try:
        # user是FTP用户名，pwd就是密码了
        f.login(USER, USERPWD)
    except ftplib.error_perm:
        print('登录失败')
        logging.info('登录失败')
        f.quit()
        return
#    print('登陆成功')
    retfl = get_remote_ver_file(f, DIRN)
    if not retfl:
        print("无发现服务器版本文件.")
        logging.info("无发现服务器版本文件.")
    else:
        remote_ver = str(retfl).strip()
        remote_ver = remote_ver[:11]
        if get_local_version():
            l_ver = get_local_version()
        else:
            logging.info('无法获取本机程序版本信息。')
            l_ver = 'None'
        if remote_ver == l_ver:
            logging.info('此版本无需更新.')
        else:
#            print(retfl)
            upd_file = '\\epit\\upd' + retfl[3:11]+'.exe'
            print(upd_file)
            logging.info('准备下载升级文件:%s ',upd_file)
            try:
                if DlFtpFile(f, upd_file) == 0 :
                    logging.info('执行自解压程序:'+ os.path.basename(upd_file))
                    os.system(os.path.basename(upd_file))
            except:
                logging.info('下载或执行命令失败:' + upd_file)

            upd_file = '\\epit\\aupd_log.txt'
            try:
                if UlFtpFile(f, upd_file) == 0:
                    logging.info('上传日志文件:' + os.path.basename(upd_file))
            except:
                logging.info('上传日志执行失败:' + upd_file)
    f.quit()

#获取本机ip地址，为记录日志，已将代码移动到程序开始部分，本函数
#无需重复执行
def getLocalIpa():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.66.7.2", 80))
        print("active ip:",s.getsockname()[0])
        return s.getsockname()[0]
    except:
        print("can not get ip addr.")
        logging.info("can not get ip addr.")

        return

def cdrom_eject():
	ctypes.windll.WINMM.mciSendStringW(u"set cdaudio door open", None, 0, None)
    return 0

if __name__== '__main__':

    ftpmain()
#    os.popen('notepad.exe')

