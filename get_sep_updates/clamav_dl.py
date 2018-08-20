#自动在symantec官网上下载SEP更新定义库（3个文件）
#自动下载并保存在工作目录（变量：workdir）
#自动对所下载的定义文件（jdb）与官网上md5文件对应的md5值进行校验，并显示结果。
#urls定义SEP官网上病毒定义等下载的指定页面。
#author jasonchan


import urllib.request
from html.parser import HTMLParser

import logging
import hashlib
import os
import datetime

def GetFileMd5(filepath):
    if not os.path.isfile(filepath):
        print('no file open.')
        return
    myhash = hashlib.md5()
    with open(filepath,'rb') as f:
        myhash.update(f.read())
    return  myhash.hexdigest()

workdir = 'f:\\test\\'

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='clamav_dl.log',
                    filemode='a')
#################################################################################################
# 定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
#################################################################################################

def getjdbfile(url):
    try:
        f = urllib.request.urlopen(url)
        pos1=url.rfind('/')
        fname = url[pos1+1:]
        with open( fname,'wb') as code:
            code.write(f.read())
    except:
        logging.warning("无法下载cvd文件" + url)
        exit()
    try:
#        md5 = GetFileMd5(workdir + fname)
        md5 = GetFileMd5(fname)
        md5 = md5.upper()
        return md5
    except:
       logging.warning("MD5 失败：" + fname)
       exit()


if __name__ == "__main__":
    urls = ['http://database.clamav.net/main.cvd',\
            'http://database.clamav.net/daily.cvd',\
            'http://database.clamav.net/bytecode.cvd']

    for link in urls:
        if ('cvd' in link) :
            logging.info('正在下载文件 : ' + link)
            retry = 0
            md5 = getjdbfile(link)
            logging.info('MD5值 : ' + md5)
