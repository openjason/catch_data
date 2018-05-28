#-*- coding: utf-8 -*-
#Author: JasonChan
VERSION = "Ver: 20180528 "

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders
from email.header import Header
import logging
import os
import configparser
import time
import datetime
from filecmp import dircmp
import socket
from ctypes import *
import ssl

from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import http.cookiejar

SMTP_SERVER = ""
WORK_DIR = ""
SMTP_USER = ""
SMTP_PWD = ""
SMTP_SENDER = ""

long_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
folder_prefix = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
log_prefix = time.strftime('%m%d', time.localtime(time.time()))

cf = configparser.ConfigParser()
cf_file = 'fang.ini'

cf.read(cf_file, encoding="utf-8")
target_total = int (cf.get("Common", "total"))
from_email_addr = cf.get("Common", "from_email_addr")
SMTP_SERVER = cf.get("Common", "SMTP_SERVER")
WORK_DIR = cf.get("Common", "WORK_DIR")
SMTP_USER = cf.get("Common", "SMTP_USER")
SMTP_PWD = cf.get("Common", "SMTP_PWD")

target_name = []
target_httpa = []
target_httpb = []
target_httpc = []
target_id = []
target_dk_flag =[]
target_dk_value = []
target_dk_amount = []
target_emailaddr = []

target_volatility = []
target_timerange = []
target_onduty = []
last_first_price = []
last_secondary_price = []
exchage_done = []


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(message)s',
                    datefmt='%a, %d %b %H:%M:%S',
                    filename = os.path.join(WORK_DIR,log_prefix+'.log'),
                    filemode='a')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)





def check_smtp_server(ipaddr,port):
    try:
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((ipaddr,port))
        sock.close()
        return True
    except socket.error as e:
        sock.close()
        return False

def send_email(toaddr,c_subject):
    logging.info("Subject:"+c_subject)
    toaddr = SMTP_USER
    try:
        msg = MIMEMultipart()
        msg['To'] = ";".join(toaddr)
        msg['From'] = SMTP_SENDER+"<" + SMTP_USER + ">"
        msg['Subject'] = c_subject[:30]
        html = c_subject
        html = html.replace("YYYY-MM-DD",long_date)
        body = MIMEText(html, 'plain')
        #    body = MIMEText(text_body, 'plain')
        msg.attach(body)  # add message body (text or html)

        server = smtplib.SMTP(SMTP_SERVER, 25)
        server.login(SMTP_USER, SMTP_PWD)
        mailbody = msg.as_string()

        server.sendmail(SMTP_USER, toaddr, mailbody) #send mail to & cc email address
#        logging.info("send email OK："+"to:"+c_subject)
        logging.info("send email OK.")
        server.quit()
    except:
        logging.info("error in send mail :"+"to:"+c_subject)

def check_server_auth():
    try:
        server = smtplib.SMTP(SMTP_SERVER, 25)
        server.login(SMTP_USER, SMTP_PWD)
        server.quit()
        return True
    except:
        return False

def clear_files(dir):
    rootdir = dir
    for parent, dirnames, filenames in os.walk(rootdir, False):
        for name in filenames:
            logging.info("移动文件, 文件名为："+parent + '\\'+ name)
            try:
                os.remove(os.path.join(parent, name))
            except:
                logging.warning("移动文件失败文件名为：" + parent + '\\' + name)
                return False
    return True

def getHtml_0756(url):
    try:
        context = ssl._create_unverified_context()
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-Agent','Mozilla/5.0')]
        urllib.request.install_opener(opener)
        html_bytes = urllib.request.urlopen(url,context=context).read()
        html_string = html_bytes.decode('utf-8')
        print("get html..")
        return html_string
    except:
        logging.info("error in getHtml_0756(url).")
        return "error in getHtml_0756(url)."

def get_curr_0756(html_doc,listfilename):
    soup = BeautifulSoup(html_doc, 'html.parser')
    stock_info1 = soup.find_all(class_ = "house-text")
    stock_info2 = soup.find_all(class_ = "house-text2")
    get_text = ""
#    for stock_info in stock_info1:
    housestr = ''
    house_info1_list = []
    house_info2_list = []
#    for i in range(len(stock_info1)):
    listcount = 5
    if len(stock_info1) < 5:
        listcount = len(stock_info1)
    for i in range(listcount):
        housestr = stock_info1[i].get_text()
        housestr = housestr.replace('\r','\n')
        housestr = housestr.replace('丨','')
        housestr = housestr.replace(' ', '')
        houseinfo1 = housestr.split('\n')
        while '' in houseinfo1:
            houseinfo1.remove('')
        housestr = stock_info2[i].get_text()
        housestr = housestr.replace('\r','\n')
        housestr = housestr.replace('丨','')
        housestr = housestr.replace(' ', '')
        houseinfo2 = housestr.split('\n')
        while '' in houseinfo2:
            houseinfo2.remove('')

#        print(houseinfo1)
#        print(houseinfo2)
        house_info1_list.append(houseinfo1)
        house_info2_list.append(houseinfo2)

    houseinfo1 = house_info1_list[0]
    houseinfo2 = house_info2_list[0]
    with open(listfilename + '.txt','r',encoding='utf-8') as fp_hl:
        hl1 = fp_hl.readline()
        hl1 = hl1.replace('\n','')
        hl2 = fp_hl.readline()
        hl2 = hl2.replace('\n', '')
        lasthouselist1 = hl1.split('|')
        lasthouselist2 = hl2.split('|')

        # print(lasthouselist1)
        # print(houseinfo1)
        #
        # print(lasthouselist2)
        # print(houseinfo2)

        if lasthouselist1 != houseinfo1 or lasthouselist2 != houseinfo2 :
            houselist_xm_update = True
            print (listfilename+' anything was changed.')
        else:
            houselist_xm_update = False
            print(listfilename + ' nothing changed.')


    if houselist_xm_update :
        os.rename(listfilename+ '.txt',listfilename + folder_prefix + '.txt')
        with open(listfilename+ '.txt','w',encoding='utf-8') as fp_hl:
            for i in range(len(house_info1_list)):
                templist = house_info1_list [i]
                print(templist)
                for j in range(len(templist)):
                    if j > 0:
                        writestr = writestr + '|' + templist[j]
                    else:
                        writestr  = templist[j]
                fp_hl.writelines(writestr)
                fp_hl.writelines('\n')

                templist = house_info2_list [i]
                for j in range(len(templist)):
                    if j > 0:
                        writestr = writestr + '|' + templist[j]
                    else:
                        writestr  = templist[j]
#                print(writestr)
                fp_hl.writelines(writestr)
                fp_hl.writelines('\n')

        with open(listfilename + '.txt', 'r') as fp_hl:
            hl1 = fp_hl.readline()
            hl1 = hl1.replace('\n', '')
            hl2 = fp_hl.readline()
            hl2 = hl2.replace('\n', '')
        send_email(SMTP_USER, "Fang变动:" + hl1 + hl2)
        for i in range(70):
            print("sleep..." + str(i))
            time.sleep(60)
            str_time = time.strftime('%Y%m%d %H%M%S', time.localtime(time.time()))
            logging.info(str_time)


def get_from_site(httpa,httpb,httpc):
    current_price_str = '2.31 1% 0.02'
    current_price_str = get_current(httpa)
    if 'error' in current_price_str:
        current_price_str = get_current(httpb)
        if 'error' in current_price_str:
            current_price_str = get_current(httpc)
            if 'error' in current_price_str:
                return "error in get_from_site(httpa,httpb,httpc)"
    return current_price_str

def get_current(http):
    f0756_html = getHtml_0756(http)
    new_price_str = get_curr_0756(f0756_html)
    return (new_price_str)
    if 'sinajs' in http:
        sianjs_html = getHtml_sinajs(http)
        new_price_str = get_curr_sinajs(sianjs_html)
        return (new_price_str)
    return "error in get_current(http)."


#对目标进行轮询,检测当前价格与设定dk价格进行比较,如最新价及上两次价格都满足条件,则进行交易操作.
#对目标dk值设置采用相反的比较,符合条件(差为正)则执行操作.否则记录更新上两次价格.

def show_setting():
    for i in range(target_total):
    #标号 数字 显示 从 1 开始，与配置文件一致，读取配置文件标号已做处理 。
        httpa = target_httpa[i]
        httpb = target_httpb[i]
        httpc = target_httpc[i]
        dk_flag = target_dk_flag[i]
        dk_value = float(target_dk_value[i])
        dk_amount = int(target_dk_amount[i])
        id = target_id [i]

        print(str(i + 1) + ":" + str(id) + "|" + " " + "|" + dk_flag + "_" + str(dk_amount) + " value:"
              + str(dk_value) + "|" + str(httpa) + "|" + str(httpb))

def is_exchage_time(i):
    str_time = time.strftime('%Y%m%d %H%M%S', time.localtime(time.time()))
    if (int(str_time[9:16]) in range(92700, 113800) or int(str_time[9:16]) in range(125700, 150800)):
        return True
    else:
        logging.info(str_time + " error, out of exchange time.")
        return False

if __name__ == "__main__":
    logging.info(VERSION)
    icount = 0
    while(True):
        html = getHtml_0756('http://www.0756fang.com/Fang_1_0_0_0_0_0_0_15_0_0_0_0_%E5%A4%8F%E7%BE%8E.html')
        curr = get_curr_0756(html,'houselist_xm')

        time.sleep(2)

        html = getHtml_0756('http://www.0756fang.com/Fang_1_0_0_0_0_0_0_15_0_0_0_0_%E4%B8%B0%E6%B3%BD%E5%9B%AD.html')
        curr = get_curr_0756(html,'houselist_fzy')
        str_time = time.strftime('%Y%m%d %H%M%S', time.localtime(time.time()))
        logging.info(str_time+" count:" + str(icount))

        time.sleep(240)
