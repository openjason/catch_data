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
import re
import time
import datetime
from filecmp import dircmp
import socket
from ctypes import *
import shutil

from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import http.cookiejar

VERSION = "Ver: 20180504 "
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
    logging.warning('无法打开文件 automail.ini 或设置错误.')
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





def dir_compare_diff(dir_com1,dir_com2,folder):
    dcmp = dircmp(dir_com1, dir_com2)
    is_diff = False
    if len(dcmp.diff_files)>0:
        is_diff = True
        logging.info ("diff_file:" + ";".join(dcmp.diff_files))
    if len(dcmp.left_only)>0:
        is_diff = True
        logging.info ("source_only:" + ";".join(dcmp.left_only))
    return is_diff
    return True



def get_target_mail_list(toaddr):
    _mail_list =[]
    _to_addr = toaddr.split("|")
    for i in range(len(_to_addr)):
        if len(_to_addr[i]) > 7:
            if re.match('^[\w\d]+[\d\w\-\.]+@([\d\w-]+)\.([\d\w-]+)(?:\.[\d\w-]+)?$|^(?:\+86)?(\d{3})\d{8}$|^(?:\+86)?(0\d{2,3})\d{7,8}$', _to_addr[i]) != None:
                _mail_list.append(_to_addr[i])
            else:
                logging.info("邮件地址有误："+_to_addr[i])
    return _mail_list

def prepare_files(source_dir,  target_dir):
    copy_ok = True
    for file in os.listdir(source_dir):
        sourceFile = os.path.join(source_dir,  file)
        targetFile = os.path.join(target_dir,  file)
        try:
            open(targetFile, "wb").write(open(sourceFile, "rb").read())
            logging.info("复制文件:"+str(sourceFile) + " to " + str(targetFile))
        except:
            logging.info('copy file error.')
            copy_ok = False
    return copy_ok
def check_diff_n_leftonly_files(dir1,dir2):
    dcmp = dircmp(dir1, dir2)
    is_diff = False
    if len(dcmp.diff_files)>0:
        is_diff = True
        logging.info ("diff_file:" + ";".join(dcmp.diff_files))
    if len(dcmp.left_only)>0:
        is_diff = True
        logging.info ("source_only:" + ";".join(dcmp.left_only))
    return is_diff

def check_diff_files(dir1,dir2):
#check directory diff, only check files diffenect exist in both side.
    dcmp = dircmp(dir1, dir2)
    is_diff = False
    if len(dcmp.diff_files)>0:
        is_diff = True
        logging.info ("diff_file:" + ";".join(dcmp.diff_files))
    return is_diff


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

def mail_server_ok():
    delay_time = 1
    while not check_server_auth():
        logging.critical("无法连上邮件服务器 或 用户认证失败：" + SMTP_SERVER+"... ... "+str(delay_time * 10)+" 秒后重试")
        time.sleep(delay_time * 10)
        if delay_time < 4:
            delay_time += 1
        else:
            logging.critical("无法连上 SMTP 服务器 或 用户认证失败：程序退出...")
            exit(3)
    else:
        logging.info("连接SMTP服务器OK: " + SMTP_SERVER)

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

def erase_dir(dir):
    # 删除符合条件的文件夹
    rootdir = dir
    logging.info("删除文件夹："+rootdir )
    for parent, dirnames, filenames in os.walk(rootdir, False):
        for name in filenames:
            try:
                os.remove(os.path.join(parent, name))
            except:
                logging.warning("删除文件失败文件名：" + parent + '\\' + name)
        for name in dirnames:
            erase_dir(os.path.join(parent, name))
    try:
        os.rmdir(rootdir)
    except:
        logging.warning("删除文件出错："+ rootdir)


def clear_expire_folder():
    rootdir = WORK_DIR + "sent"
    def is_expire(str):
        try:
            currdate = datetime.date.today()
            checkdate = datetime.date(int(str[:4]), int(str[4:6]), int(str[6:8]))
        except:
            return False
        interval = (currdate - checkdate).days
        if interval > 14:
            return True
        else:
            return False
    dirlists = os.listdir(rootdir)
    for cef_foldername in dirlists:
        if is_expire(cef_foldername):
            erase_dir(rootdir + '\\' + cef_foldername)

def compare_clear_right_side(dir1,dir2):
    holderlist = []
    if dir1 == '' or dir2 == '':
        return 2
    if not(os.path.exists(dir1) or os.path.exists(dir2)):
        logging.warning("无法打开文件夹：" + dir1 + "|" + dir2)
        return 2
    def compareme(dir1, dir2):  # 递归获取更新项函数
        dircomp = dircmp(dir1, dir2)
        only_in_one = dircomp.left_only  # 源目录新文件或目录
        diff_in_one = dircomp.diff_files  # 不匹配文件，源目录文件已发生变化
        dirpath = os.path.abspath(dir1)  # 定义源目录绝对路径

        # 将更新文件或目录追加到holderlist
        [holderlist.append(os.path.abspath(os.path.join(dir1, x))) for x in only_in_one]
#        [holderlist.append(os.path.abspath(os.path.join(dir1, x))) for x in diff_in_one]
        if len(dircomp.common_dirs) > 0:  # 判断是否存在相同子目录，以便递归
            for item in dircomp.common_dirs:  # 递归子目录
                compareme(os.path.abspath(os.path.join(dir1, item)), os.path.abspath(os.path.join(dir2, item)))
        return holderlist

    source_files = compareme(dir1, dir2)  # 对比源目录与备份目录
    dir1 = os.path.abspath(dir1)  # 取绝对路径后，后面不会自动加上'/'

    if not dir2.endswith('/'):
        dir2 = dir2 + '/'  # 备份目录路径加'/'

    dir2 = os.path.abspath(dir2)
    destination_files = []
    createdir_bool = False

    for item in source_files:  # 遍历返回的差异文件或目录清单
#        destination_dir = re.sub(dir1, dir2, item)  # 将源目录差异路径清单对应替换成备份目录,即需要在dir2中创建的差异目录和文件
        destination_dir = item.replace(dir1,dir2)
        destination_files.append(destination_dir)
        if os.path.isdir(item):  # 如果差异路径为目录且不存在，则在备份目录中创建
            if not os.path.exists(destination_dir):
                destination_dir = item.replace(dir2, dir1)
                logging.info("dist文件夹删除：" + destination_dir)
                shutil.rmtree(destination_dir)

                createdir_bool = True  # 再次调用copareme函数标记
    if createdir_bool:  # 重新调用compareme函数，重新遍历新创建目录的内容
        destination_files = []
        source_files = []
        source_files = compareme(dir1, dir2)  # 调用compareme函数
        for item in source_files:  # 获取源目录差异路径清单，对应替换成备份目录
#            destination_dir = re.sub(dir1, dir2, item)
            destination_dir = item.replace(dir1, dir2)
            destination_files.append(destination_dir)
    print('update item:',end="")
    print(source_files)  # 输出更新项列表清单
    copy_pair = zip(source_files, destination_files)  # 将源目录与备份目录文件清单拆分成元组
    for item in copy_pair:
        if os.path.isfile(item[0]):  # 判断是否为文件，是则进行复制操作
            logging.info("dist文件删除："+ item[0])
            os.remove(item[0])
    return 0


def main_compare_sync(dir1,dir2,dir2_diff):
    holderlist = []
    if dir1 == '' or dir2 == '':
        return 2
    if not(os.path.exists(dir1) or os.path.exists(dir2)):
        logging.warning("无法打开文件夹："+dir1+"|"+dir2)
        return 2
    def compareme(dir1, dir2):  # 递归获取更新项函数
        dircomp = dircmp(dir1, dir2)
        only_in_one = dircomp.left_only  # 源目录新文件或目录
#        only_in_right = dircomp.right_only
        diff_in_one = dircomp.diff_files  # 不匹配文件，源目录文件已发生变化
        dirpath = os.path.abspath(dir1)  # 定义源目录绝对路径

        # 将更新文件或目录追加到holderlist
        [holderlist.append(os.path.abspath(os.path.join(dir1, x))) for x in only_in_one]
        [holderlist.append(os.path.abspath(os.path.join(dir1, x))) for x in diff_in_one]
        if len(dircomp.common_dirs) > 0:  # 判断是否存在相同子目录，以便递归
            for item in dircomp.common_dirs:  # 递归子目录
                compareme(os.path.abspath(os.path.join(dir1, item)), os.path.abspath(os.path.join(dir2, item)))
        return holderlist

    source_files = compareme(dir1, dir2)  # 对比源目录与备份目录
    dir1 = os.path.abspath(dir1)  # 取绝对路径后，后面不会自动加上'/'

    if not dir2.endswith('/'):
        dir2 = dir2 + '/'  # 备份目录路径加'/'

    dir2 = os.path.abspath(dir2)
    destination_files = []
    createdir_bool = False

    for item in source_files:  # 遍历返回的差异文件或目录清单
#        destination_dir = re.sub(dir1, dir2, item)  # 将源目录差异路径清单对应替换成备份目录,即需要在dir2中创建的差异目录和文件
        destination_dir = item.replace(dir1,dir2)
        destination_files.append(destination_dir)
        if os.path.isdir(item):  # 如果差异路径为目录且不存在，则在备份目录中创建
            if not os.path.exists(destination_dir):
                os.makedirs(destination_dir)
                createdir_bool = True  # 再次调用copareme函数标记
    if createdir_bool:  # 重新调用compareme函数，重新遍历新创建目录的内容
        destination_files = []
        source_files = []
        source_files = compareme(dir1, dir2)  # 调用compareme函数
        for item in source_files:  # 获取源目录差异路径清单，对应替换成备份目录
#            destination_dir = re.sub(dir1, dir2, item)
            destination_dir = item.replace(dir1, dir2)
            destination_files.append(destination_dir)
    print('update item:',end="")
    print(source_files)  # 输出更新项列表清单
    if len(source_files) > 0:
        time.sleep(2)
    copy_pair = zip(source_files, destination_files)  # 将源目录与备份目录文件清单拆分成元组
    for item in copy_pair:
        if os.path.isfile(item[0]):  # 判断是否为文件，是则进行复制操作
            shutil.copyfile(item[0], item[1])
            shutil.copyfile(item[0], os.path.join(dir2_diff,os.path.basename(item[0])))
    return 0




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






def dk_detect():
    for i in range(target_total):
        http_addr = target_http[i]
        dk_flag = target_dk_flag[i]
        dk_value = float(target_dk_value[i])
        dk_amount = int(target_dk_amount[i])
        id = target_id [i]
        html_doc = getHtml(http_addr)
        new_price_str = get_curr(html_doc)
        try:
            if dk_flag == 'buy':
                dk_gap = float(new_price_str[0])-dk_value
                dk_gap = round(dk_gap,2)
            else:
                dk_gap = dk_value - float(new_price_str[0])
                dk_gap = round(dk_gap,2)
        except:
            dk_gap = 999999

#        print(id, end="")
#        print (new_price_str,end=" ",flush=True)
        logging.info(str(id) + str(new_price_str)+dk_flag+" gap:"+str(dk_gap))

        continue
        dk_fit = False
        if dk_fit:
            mail_server_ok()        #检查网络是否可用
            limit_times = 0
            while limit_times < 5:
                limit_times += 1
                folder_prefix = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                prepare_folder = WORK_DIR+"sent\\" + folder_prefix+target_name[i]
                os.mkdir(prepare_folder)
                if prepare_files(target_http[i],prepare_folder) == False:
                    logging.warning("拷贝文件夹出错...")
                    time.sleep(limit_times * 10)
                else:
                    if check_diff_n_leftonly_files(target_http[i],prepare_folder) == False:
                        logging.info("拷贝文件夹与原文件夹一致.")
                        if clear_files(target_http[i]):
                            break
                        else:
                            logging.warning("清空文件夹失败，重试次数:" + str(limit_times))
                    else:
                        logging.warning("拷贝文件夹与原文件夹不一致次数:" + str(limit_times))
                        time.sleep(limit_times * 10)
            if limit_times == 5 :
                logging.warning("文件夹复制或文件比对重试多次后失败，此客户邮件发送暂停，重试次数:" + str(limit_times))
                continue

            tomail_list = get_target_mail_list(target_emailaddr[i])
            ccmail_list = get_target_mail_list(target_ccaddr[i])
            print(tomail_list,ccmail_list)
            logging.info("sending mail....."+c_name)
        return 1


if __name__ == "__main__":
    while (True):
        str_time = time.strftime('%Y%m%d %H%M%S', time.localtime(time.time()))
        print (str_time,flush=True)
        if (int(str_time[9:16]) in range(92500, 113500)) or (int(str_time[9:16]) in range(125500, 150500)):
        # if (True):
        #     print("test")
            dk_detect()
            time.sleep(2)
            

        else:
            print("out of exchange time.")
            time.sleep(6)