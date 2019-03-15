#访问www.ip138.com获取本机外部公网IP地址
#author jasonchan 2019-03-15

import urllib.request
from html.parser import HTMLParser
import logging
import datetime

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='fetch_localhost_inet_ip.log',
                    filemode='a')
#################################################################################################
# 定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
#################################################################################################

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []

    def handle_starttag(self, tag, attrs):
        # print "Encountered the beginning of a %s tag" % tag
        if tag == "div":
            if len(attrs) == 0:
                pass
            else:
                #print(attrs)                       输出全部匹配tag的内容。
                for (variable, value) in attrs:
                    if variable == "fk":
                        #print(variable, value)
                        self.links.append(value)

def fetch_localhost_inet_ip():
    urls = ['http://www.baidu.com/s?ie=utf-8&f=3&rsv_bp=0&rsv_idx=1&tn=baidu&wd=ip%E5%9C%B0%E5%9D%80%E6%9F%A5%E8%AF%A2']
    try:
        for url in urls:
            #print ("下载目标地址：",url)
            #logging.info("下载目标地址："+url)
            with urllib.request.urlopen(url) as f:
                bhtmlFile = f.read()
            htmlFile = bhtmlFile.decode('utf-8')
            hp = MyHTMLParser()
            hp.feed(htmlFile)
            hp.close()
            return (hp.links[0])
    except:
        return ("fetch ip address FAILD.")

if __name__ == "__main__":
    inet_ip = fetch_localhost_inet_ip()
    logging.info("fetch_localhost_inet_ip: "+inet_ip)
    print(inet_ip)