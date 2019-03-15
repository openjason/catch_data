# -*- coding: UTF-8 -*-
#访问www.baidu.com获取本机外部公网IP地址
#author jasonchan 2019-03-15

import urllib.request
from html.parser import HTMLParser
import logging
import datetime

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders
from email.header import Header
import os
import configparser
import re
import time

SMTP_SERVER = ""
SMTP_USER = ""
SMTP_PWD = ""
SMTP_to_email_addr = ""
long_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
folder_prefix = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))

cf = configparser.ConfigParser()
try:
    cf.read("smtpmsg.ini", encoding="utf-8-sig")
    customer_total = int (cf.get("Common", "total"))
    SMTP_from_email_addr = cf.get("Common", "SMTP_from_email_addr")
    SMTP_SERVER = cf.get("Common", "SMTP_SERVER")
    SMTP_USER = cf.get("Common", "SMTP_USER")
    SMTP_PWD = cf.get("Common", "SMTP_PWD")
    SMTP_to_email_addr = cf.get("Common", "SMTP_to_email_addr")
except:
    logging.warning('无法打开文件 file conf.ini 或设置错误.')
    exit(2)

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

#coding:utf-8
'''
f_name为所读xx.txt文件
输出为：文件最后一行
'''
def get_old_ip_from_txt():
    fname = 'lastip.log'
    with open(fname, 'r') as f:  #打开文件
        first_line = f.readline()  #读第一行
        off = -50      #设置偏移量
        while True:
            f.seek(off, 2) #seek(off, 2)表示文件指针：从文件末尾(2)开始向前50个字符(-50)
            lines = f.readlines() #读取文件指针范围内所有行
            if len(lines)>=2: #判断是否最后至少有两行，这样保证了最后一行是完整的
                last_line = lines[-1] #取最后一行
                break
            #如果off为50时得到的readlines只有一行内容，那么不能保证最后一行是完整的
            #所以off翻倍重新运行，直到readlines不止一行
            off *= 2
        print('文件' + fname + '第一行为：' + first_line)
        print('文件' + fname + '最后一行为：'+ last_line)
    return (last_line)

def send_email(dir_path,files,toaddr,ccaddr,c_name,c_subject):
    logging.info("Subject:"+c_subject)
    msg = MIMEMultipart()
    msg['To'] = ";".join(toaddr)
    msg['CC'] = ";".join(ccaddr)
    msg['From'] = SMTP_USER
    msg['Subject'] = "IP地址:"+ c_subject
    html = ""
    html = '正文内容: '+c_subject
    print(html)

    body = MIMEText(html, 'plain')
    #    body = MIMEText(text_body, 'plain')
    msg.attach(body)  # add message body (text or html)

    for f in files:  # add files to the message
        fullname = os.path.join(dir_path, f)
        with open(fullname, 'rb') as o_f:
            msg_attach = MIMEBase('application', 'octet-stream')
            msg_attach.set_payload(o_f.read())
            encoders.encode_base64(msg_attach)
            msg_attach.add_header('Content-Disposition', 'attachment',
                                  filename=(Header(f, 'utf-8').encode()))
            msg.attach(msg_attach)

    server = smtplib.SMTP(SMTP_SERVER, 25)
    server.login(SMTP_USER, SMTP_PWD)
    mailbody = msg.as_string()

    server.sendmail(SMTP_USER, toaddr + ccaddr, mailbody) #send mail to & cc email address
    logging.info(c_name + ":发送邮件："+"to:"+";"+toaddr)
    server.quit()

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
    last_ip_from_txt = get_old_ip_from_txt()
    inet_ip = fetch_localhost_inet_ip()
    logging.info("fetch_localhost_inet_ip: "+inet_ip)
    print(inet_ip)

    folder_list = ""
    c_name = "JC"
    file_list = ""
    ccaddr = ""
    ccmail_list = ''
    c_subject = inet_ip
    print (folder_list,file_list,SMTP_to_email_addr,ccaddr,c_name,c_subject)

    send_email(folder_list,file_list,SMTP_to_email_addr,ccaddr,SMTP_USER,c_subject)
    logging.info("正在发送邮件..."+c_name)
    time.sleep(1)
