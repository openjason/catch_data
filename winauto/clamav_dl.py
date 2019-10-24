#自动在clamav官网上下载病毒更新定义库（3个文件）
#自动下载并保存在工作目录（变量：workdir）
#urls定义clamav官网上病毒定义等下载的指定页面。
#author jasonchan


import urllib.request
from html.parser import HTMLParser

import logging
import hashlib
import os
import datetime,time

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
    md5 = 'x'
    md52= ''
    while(True):
        try:
            logging.info(url)
            f = urllib.request.urlopen(url,timeout=60)
            pos1=url.rfind('/')
            fname = url[pos1+1:]+'chk'
            with open( fname,'wb') as code:
                code.write(f.read())
            f.close()
            time.sleep(10)
            md5 = GetFileMd5(fname)
            logging.info('save file: '+fname+' md5: '+md5)
            f.close()
            logging.info(url)
            f = urllib.request.urlopen(url,timeout=60)
            pos1=url.rfind('/')
            fname = url[pos1+1:]
            with open( fname,'wb') as code:
                code.write(f.read())
            f.close()
            time.sleep(1)
            md52 = GetFileMd5(fname)
            logging.info('save file: '+fname+' md5: '+md52)
            
        except:
            logging.warning("下载cvd文件exception，retry.get " + url)
        if md52 == md5:
            md5 = md5.upper()
            break
    return md5

if __name__ == "__main__":
    urls = ['http://database.clamav.net/bytecode.cvd',\
            'http://database.clamav.net/daily.cvd',\
            'http://database.clamav.net/main.cvd']

    for link in urls:
        if ('cvd' in link) :
            logging.info('正在下载文件 : ' + link)
            retry = 0
            md5 = getjdbfile(link)
            logging.info('MD5值 : ' + md5)
