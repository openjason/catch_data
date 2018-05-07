#-*- coding: utf-8 -*-
#Author: JasonChan

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

from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import http.cookiejar
from anjian import stock_sale
from anjian import stock_buy

VERSION = "Ver: 20180506 "
SMTP_SERVER = ""
WORK_DIR = ""
SMTP_USER = ""
SMTP_PWD = ""
SMTP_SENDER = ""

long_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
folder_prefix = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))

cf = configparser.ConfigParser()
cf_file = 'c:\\dk\\dk_curr.ini'
if not os.path.isfile(cf_file):
    cf_file = 'd:\\dk\\dk_curr.ini'
    if not os.path.isfile(cf_file):
        cf_file = 'e:\\dk\\dk_curr.ini'
        if not os.path.isfile(cf_file):
            logging.critical('无法打开配置文件：dk_curr.ini ')
            exit(2)
try:
    cf.read(cf_file, encoding="utf-8-sig")
    target_total = int (cf.get("Common", "total"))
    from_email_addr = cf.get("Common", "from_email_addr")
    SMTP_SERVER = cf.get("Common", "SMTP_SERVER")
    WORK_DIR = cf.get("Common", "WORK_DIR")
    SMTP_USER = cf.get("Common", "SMTP_USER")
    SMTP_PWD = cf.get("Common", "SMTP_PWD")
except:
    logging.warning('无法打开文件 dk_curr.ini 或设置错误.')
    exit(2)

target_name = []
target_http = []
target_id = []
target_dk_flag =[]
target_dk_value = []
target_dk_amount = []
target_emailaddr = []
target_ccaddr = []
target_sourcedir = []
target_destdir = []

last_first_price = []
last_secondary_price = []
exchage_ready = []


for i in range(1,target_total+1):
    try:
        cfstr = 'Target' + str(i)
        target_name.append(cf.get(cfstr,'name'))
        target_http.append(cf.get(cfstr,'http_addr'))
        target_id.append(cf.get(cfstr, 'stock_id'))
        target_dk_flag.append(cf.get(cfstr, 'dk_flag'))
        target_dk_value.append(cf.get(cfstr, 'dk_value'))
        target_dk_amount.append(cf.get(cfstr, 'dk_amount'))
        target_emailaddr.append(cf.get(cfstr,'to_email_addr'))
        if cf.get(cfstr, 'dk_flag') == 'buy':
            last_first_price.append(0)
            last_secondary_price.append(0)
        else:
            last_first_price.append(888888)
            last_secondary_price.append(888888)

        exchage_ready.append(True)

    except:
        logging.warning("conf.ini 配置有误，参数:"+cfstr)


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename = os.path.join(WORK_DIR,'dk_curr.log'),
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

def getHtml(url):
    try:
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-Agent',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36'),
        ('Cookie', '4564563564564564565646544')]

        urllib.request.install_opener(opener)
        html_bytes = urllib.request.urlopen(url).read()
        html_string = html_bytes.decode('utf-8')
        return html_string
    except:
        print("can not get html file.")
        return "can not get html file."

def get_curr(html_doc):
    soup = BeautifulSoup(html_doc, 'html.parser')
    stock_info = soup.find_all(class_ = "price s-up ") #price s-down
    get_text = ""
    if len(stock_info)>0:
        i = stock_info[0]
        get_text = i.get_text()
        if len(get_text)>0:
            get_text = get_text.split()
    else:
        stock_info = soup.find_all(class_="price s-down ")  # price s-down
        if len(stock_info) > 0:
            i = stock_info[0]
            get_text = i.get_text()
            if len(get_text) > 0:
                get_text = get_text.split()
        else:
            print("no data.")
    return (get_text)

#对目标进行轮询,检测当前价格与设定dk价格进行比较,如最新价及上两次价格都满足条件,则进行交易操作.
#对目标dk值设置采用相反的比较,符合条件(差为正)则执行操作.否则记录更新上两次价格.
def dk_detect():
    global exchage_ready
    global target_total
    global target_dk_value
    global target_dk_amount
    global target_dk_flag
    global target_http
    global target_id
    global last_first_price
    global last_secondary_price

    for i in range(target_total):
        http_addr = target_http[i]
        dk_flag = target_dk_flag[i]
        dk_value = float(target_dk_value[i])
        dk_amount = int(target_dk_amount[i])
        id = target_id [i]
        last_one_value = last_first_price[i]
        last_two_value = last_secondary_price[i]

        html_doc = getHtml(http_addr)
        new_price_str = get_curr(html_doc)

        dk_gap = -888888
        try:
            new_price = round(float(new_price_str[0]), 3)
        except:
            logging.info("gap get error.")
            continue
        if dk_flag == 'buy':
            #计划买入,之前价格检测２次均符合条件，执行交易
            dk_gap = round(new_price - dk_value,3)
            if (dk_gap >0) and (last_one_value - dk_value) > 0 and (last_two_value - dk_value) >0:
                if exchage_ready[i]:
                    #excute
                    stock_buy(id,str(dk_amount))
                    exchage_ready[i] = False
                    logging.info ("excute exchage......" + id + "buy:" +str(dk_amount))
            else:
                last_secondary_price[i] = last_first_price[i]
                last_first_price[i] = new_price
        else:
            #计划卖出，之前价格检测２次均符合条件，执行交易
            dk_gap = round(dk_value - new_price, 3)
            if (dk_gap >0) and (dk_value - last_one_value ) > 0 and (dk_value - last_two_value ) >0:
                if exchage_ready[i]:
                    #excute
                    stock_sale(id,str(dk_amount))
                    logging.info ("excute exchage......" + id + "sale:" +str(dk_amount))
                    exchage_ready[i] = False
            else:
                last_secondary_price[i] = last_first_price[i]
                last_first_price[i] = new_price
        logging.info(str(id) + str(new_price_str)+dk_flag+" gap:"+str(dk_gap) + "|"+str(last_one_value) + "|"+str(last_two_value))
        continue
    return 0



if __name__ == "__main__":
    while (True):
        str_time = time.strftime('%Y%m%d %H%M%S', time.localtime(time.time()))
        print (str_time,flush=True)
        if (int(str_time[9:16]) in range(93000, 113500)) or (int(str_time[9:16]) in range(125500, 150500)):
#        if (True):
#            print("test")
            dk_detect()
            time.sleep(2)
        else:
            print("out of exchange time.")
            time.sleep(6)
