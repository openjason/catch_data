# 打开指定文件夹，文件列表，是否有*.jdb文件，无则退出，无其他操作和写日志
# 发现制定文件，copy到d盘jdb文件夹，copy文件到该文件夹,记录日志
# 满足条件下，md5校验，记录日志
# ftp 指定目录，是否有残余文件，有，记录日志。
# ftp put 到服务器指定文件夹，文件大小确认，记录日志
# 弹出cd rom，记录日志。
# author openjc
# 2017-12-12

import logging
from ftplib import FTP  # 引入ftp模块
import os
import ctypes
import configparser
import hashlib
import time

cf = configparser.ConfigParser()
cf.read("jdb2s.conf")
secs = cf.sections()

CDROMjdbDir = cf.get("jdb", "CDROMjdbDir")
HDjdbDir = cf.get("jdb", "HDjdbDir")
SepServer = cf.get("jdb", "SepServer")
SepSerDir = cf.get("jdb", "SepSerDir")
ftpuser = cf.get("jdb", "ftpuser")
ftppass = cf.get("jdb", "ftppass")

SepServer2 = cf.get("jdb", "SepServer2")
SepSerDir2 = cf.get("jdb", "SepSerDir2")
ftpuser2 = cf.get("jdb", "ftpuser2")
ftppass2 = cf.get("jdb", "ftppass2")


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='jdb2slog.log',
                    filemode='a')
#################################################################################################
# 定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

#################################################################################################

def cdrom_eject():
    val = ctypes.windll.WINMM.mciSendStringW(u"set cdaudio door open", None, 0, None)
    return val

def jdb_file_ready():
    global CDROMjdbDir
    FileList = []
    source_dir = CDROMjdbDir
    if not os.path.exists(source_dir):
        print('无法打开'+source_dir)
        CDROMjdbDir = 'none'

    source_dir = 'E:\jdb'
    if not os.path.exists(source_dir):
        print('无法打开' + source_dir)
    else:
        CDROMjdbDir = source_dir

    source_dir = 'F:\jdb'
    if not os.path.exists(source_dir):
        print('无法打开' + source_dir)
    else:
        CDROMjdbDir = source_dir

    source_dir = 'G:\jdb'
    if not os.path.exists(source_dir):
        print('无法打开' + source_dir)
    else:
        CDROMjdbDir = source_dir

    if CDROMjdbDir == 'none':
        print("无法打开CDROM SEP 文件夹。\n程序退出。")
        exit()
    print("JDB file is Ready."+CDROMjdbDir)
    have_jdb_file = False
    for i in os.listdir(CDROMjdbDir):
        if i.find(".jdb") > 0 :
            have_jdb_file = True
            FileList.append(i)

    if not have_jdb_file :
        print("CDROM SEP文件夹没有发现*.jdb升级文件。\n程序退出。")
        exit()
    return FileList


def getmd5file(url):
    try:
        rlines = []
        with open(os.path.join(CDROMjdbDir,'md5-hash.txt'), 'r') as f:
            for rline in f:
                rlines.append(rline)
        return rlines
    except:
        logging.warning('无法下载md5文件' + url)
        return rlines

def GetFileMd5(filepath):
    if not os.path.isfile(filepath):
        print('no file open.')
        return
    myhash = hashlib.md5()
    with open(filepath,'rb') as f:
        myhash.update(f.read())
    MD5 = myhash.hexdigest()
    MD5 = MD5.upper()
    return  MD5

def CopyFiles(sourceList,  targetDir):
    md5file = getmd5file('')
    for file in sourceList:

        sourceFile = os.path.join(CDROMjdbDir,  file)
        targetFile = os.path.join(targetDir,  file)
        try:
           open(targetFile, "wb").write(open(sourceFile, "rb").read())
           logging.info ("复制文件:"+sourceFile+ " to " + targetDir)

        except:
           logging.info('copy file error.')

        md5 = GetFileMd5(targetFile)
        md5check = False
        for md5search in md5file:
            if md5 in md5search:
                md5check = True
        if md5check:
             logging.info("Md5 Check...匹配成功...OK:"+md5)
        else:
             logging.warning("Md5 Check...匹配失败:"+md5)

def FtpFiles(sourceList, inftpserver,inftpuser,inftppass):
    try:
        ftp = FTP(inftpserver)  # 设置ftp服务器地址
        ftp.login(inftpuser, inftppass)  # 设置登录账户和密码
        ftp.cwd(SepSerDir)  # 选择操作目录
    except:
        logging.warning('can not connect to ftp server...'+inftpserver+'请检查ftp服务器可用，用户密码正确')
        exit(1)
    logging.info(ftp.retrlines('LIST'))
    for filename in sourceList:
       sourceFile = os.path.join(HDjdbDir,  filename)
#       targetFile = os.path.join(FtpServer,  filename)
       try:
           f = open(sourceFile, 'rb')  # 打开文件
           logging.info('发送文件到'+inftpserver+'ftp:'+sourceFile)
           ftp.storbinary('STOR %s' % os.path.basename(filename), f)  #上传文件
           f.close()
       except:
           logging.warning('ftp'+inftpserver+'发送错误...'+sourceFile)
    ftp.close()
       #文件上传后，sep立即进行解压处理，上传后大小比对，出错

def cleardir(str):
    # 删除符合条件的文件夹（含文件夹内的子文件夹和文件）
    # 没有对文件及文件夹锁定情况进行判断。
    rootdir = str
    for parent, dirnames, filenames in os.walk(rootdir, False):
        for name in filenames:
            print("清理文件", '文件名为：'+parent + '\\'+ name)
            try:
                os.remove(os.path.join(parent, name))
            except:
                print("清理文件失败", '文件名为：' + parent + '\\' + name)
        for name in dirnames:
            print("清理文件夹", '文件夹名为：'+parent + '\\'+ name)
            try:
                os.rmdir(os.path.join(parent, name))
            except:
                print("清理文件夹失败", '文件夹名为：' + parent + '\\' + name)



if __name__ == "__main__":
    jdbFileList = jdb_file_ready()
    print(jdbFileList)
    cleardir(HDjdbDir)
    CopyFiles(jdbFileList,HDjdbDir)
    FtpFiles(jdbFileList,SepServer,ftpuser,ftppass)
    FtpFiles(jdbFileList, SepServer2,ftpuser2,ftppass2)

    cleardir(CDROMjdbDir[:len(CDROMjdbDir)-1]+'old')

    if os.path.exists(CDROMjdbDir[:len(CDROMjdbDir)-1]+'old'):
        os.rmdir(CDROMjdbDir[:len(CDROMjdbDir)-1]+'old')
        time.sleep(5)
    os.rename(CDROMjdbDir,CDROMjdbDir[:len(CDROMjdbDir)-1]+'old')

    logging.info('CD Eject Return value:'+str(cdrom_eject()))
    time.sleep(20)
