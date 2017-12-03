# 打开指定文件夹，文件列表，是否有*.jdb文件，无则退出，无其他操作和写日志
# 发现制定文件，copy到d盘jdb文件夹，新建MMDD文件夹，copy文件到该文件夹,记录日志
# 满足条件下，md5校验，记录日志
# ftp 指定目录，是否有残余文件，有，记录日志。
# ftp put 到服务器指定文件夹，文件大小确认，记录日志
# 弹出cd rom，记录日志。
# author openjc

import logging
from md5 import GetFileMd5
from ftplib import FTP  # 引入ftp模块
import os

CDROMjdbDir = 'E:\\temp\\'
HDjdbDir = 'D:\\temp\\'
SepServer = '10.66.1.11'

def jdb_file_ready():
    FileList = []
    if not os.path.exists(CDROMjdbDir):
        print("无法打开CDROM SEP 文件夹。\n程序退出。")
        exit()
    print("CDROM is Ready.")
    have_jdb_file = False
    for i in os.listdir(CDROMjdbDir):
        if i.find(".jdb") > 0 :
            if have_jdb_file == False:
                print("升级文件列表：")
            print(i)
            have_jdb_file = True
            FileList.append(i)
    if not have_jdb_file :
        print("CDROM SEP文件夹没有发现*.jdb升级文件。\n程序退出。")
        exit()
    return FileList

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='sep_update.log',
                    filemode='a')
#################################################################################################
# 定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


#################################################################################################

def getmd5file(url):
    try:
        url = 'https://www.symantec.com/avcenter/download/md5-hash.txt'
        f = urllib.request.urlopen(url)
        with open(workdir + 'md5-hash.txt', 'wb') as code:
            code.write(f.read())
        rlines = []
        with open(workdir + 'md5-hash.txt', 'r') as f:
            for rline in f:
                rlines.append(rline)
        return rlines
    except:
        logging.warning('无法下载md5文件' + url)
        exit()


def getjdbfile(url):
    try:
        f = urllib.request.urlopen(url)
        pos1 = url.rfind('/')
        fname = url[pos1 + 1:]
        with open(workdir + fname, 'wb') as code:
            code.write(f.read())
    except:
        logging.warning("无法下载jdb文件" + url)
        exit()
    try:
        md5 = GetFileMd5(workdir + fname)
        md5 = md5.upper()
        return md5
    except:
        logging.warning("MD5 失败：" + workdir + fname)
        exit()

def CopyFiles(sourceList,  targetDir):
   for file in sourceList:
       sourceFile = os.path.join(CDROMjdbDir,  file)
       targetFile = os.path.join(targetDir,  file)
       try:
           open(targetFile, "wb").write(open(sourceFile, "rb").read())
           logging.warning("复制文件:"+sourceFile)
       except:
           logging.warning('copy file error.')

       if (os.path.getsize(targetFile) != os.path.getsize(sourceFile)):
           logging.warning("比对文件大小一致。")
       else:
           logging.warning("文件大小错误！！！")

def FtpFiles(sourceDir, FtpServer):
   for file in sourceList:
       sourceFile = os.path.join(CDROMjdbDir,  file)
       targetFile = os.path.join(targetDir,  file)
       try:

           ftp = FTP(FtpServer)  # 设置ftp服务器地址
           ftp.login('Administrator', 'Admin@007')  # 设置登录账户和密码
           ftp.retrlines('LIST')  # 列出文件目录
           ftp.cwd('a')  # 选择操作目录
           ftp.retrlines('LIST')  # 列出目录文件
           localfile = 'sourceFile'  # 设定文件位置
           f = open(localfile, 'rb')  # 打开文件
           ftp.storbinary('STOR %s' % os.path.basename(localfile), f)  #上传文件
        except:
           logging.warning('ftp file error.'+localfile)

       # if (os.path.getsize(targetFile) != os.path.getsize(sourceFile)):
       #     logging.warning("比对文件大小一致。")
       # else:
       #     logging.warning("文件大小错误！！！")


if __name__ == "__main__":

    jdbFileList = jdb_file_ready()
    print(jdbFileList)

    CopyFiles(jdbFileList,HDjdbDir)
    FtpFiles(HDjdbDir,SepServer)

    exit()
    md5file = getmd5file('')
    for url in urls:
        #        print ("下载目标地址：",url)
        logging.info("下载目标地址：" + url)
        with urllib.request.urlopen(url) as f:
            bhtmlFile = f.read()
            #        print('.',end='')

        htmlFile = bhtmlFile.decode('utf-8')
        hp = MyHTMLParser()
        hp.feed(htmlFile)
        hp.close()
        for link in hp.links:
            if ('http' in link) and (not ('core' in link)):
                #               print('正在下载文件 : ',link)
                logging.info('正在下载文件 : ' + link)
                retry = 0
                while retry < 3:
                    md5 = getjdbfile(link)
                    #               print ('MD5值 : ',md5)
                    logging.info('MD5值 : ' + md5)
                    md5check = False
                    for md5search in md5file:
                        if md5 in md5search:
                            md5check = True
                            #                        print("Md5 Check...匹配成功...OK")
                            logging.info("Md5 Check...匹配成功...OK")
                            retry = 3
                            break
                    if md5check == False:
                        #                   print("Md5 Check...匹配失败...Fail.Fail.Fail.Fail.Fail.Fail.Fail.Fail.Fail")
                        logging.info("Md5 Check...匹配失败...Fail.Fail.Fail.Fail.Fail.Fail.Fail.Fail....Retry times:" + str(
                            retry + 1))
                        retry = retry + 1


