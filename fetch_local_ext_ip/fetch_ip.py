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
