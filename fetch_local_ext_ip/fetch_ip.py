#访问www.ip138.com获取本机外部公网IP地址
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
        with open(workdir + 'md5-hash.txt','wb') as code:
            code.write(f.read())
        rlines = []
        with open(workdir + 'md5-hash.txt','r') as f:
            for rline in f:
                rlines.append(rline)
        return rlines
    except:
        logging.warning('无法下载md5文件'+url)
        exit()

def getjdbfile(url):
    try:
        f = urllib.request.urlopen(url)
        pos1=url.rfind('/')
        fname = url[pos1+1:]
        with open(workdir+fname,'wb') as code:
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

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []

    def handle_starttag(self, tag, attrs):
        # print "Encountered the beginning of a %s tag" % tag
        if tag == "result-op c-container":
            print(attrs)
            if len(attrs) == 0:
                pass
            else:
                for (variable, value) in attrs:
                    if variable == "href" and "jdb" in value:
#                        print(attrs)
                        self.links.append(value)

def search_string(codestring):
    codelines = codestring.split("\r")
    for int in range(len(codelines)):
#        print (codelines[int])
        if "219.131.196.237" in codelines[int]:
            print(int,end="")
            print(codelines[int])
    print(int)

if __name__ == "__main__":
    urls = ['http://www.baidu.com/s?ie=utf-8&f=3&rsv_bp=0&rsv_idx=1&tn=baidu&wd=ip%E5%9C%B0%E5%9D%80%E6%9F%A5%E8%AF%A2']

    for url in urls:
#        print ("下载目标地址：",url)
        logging.info("下载目标地址："+url)
        with urllib.request.urlopen(url) as f:
            bhtmlFile = f.read()
    #        print('.',end='')

        htmlFile = bhtmlFile.decode('utf-8')
        #print(htmlFile)
#        print(type(htmlFile))
        search_string(htmlFile)
        exit(0)
#         for link in hp.links:
# #            if ('http' in link) and (not('core' in link)):
#             if ('http' in link):
#     #               print('正在下载文件 : ',link)
#                 logging.info('正在下载文件 : ' + link)
#                 retry = 0
#                 while retry < 3 :
#                     md5 = getjdbfile(link)
#     #               print ('MD5值 : ',md5)
#                     logging.info('MD5值 : ' + md5)
#                     md5check = False
#                     for md5search in md5file:
#                         if md5 in md5search:
#                             md5check = True
#     #                        print("Md5 Check...匹配成功...OK")
#                             logging.info("Md5 Check...匹配成功...OK")
#                             retry = 3
#                             break
#                     if md5check == False:
#      #                   print("Md5 Check...匹配失败...Fail.Fail.Fail.Fail.Fail.Fail.Fail.Fail.Fail")
#                         logging.info("Md5 Check...匹配失败...Fail.Fail.Fail.Fail.Fail.Fail.Fail.Fail....Retry times:"+str(retry+1))
#                         retry = retry + 1

                        
