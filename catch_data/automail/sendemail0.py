# -*- coding: UTF-8 -*-
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import logging
import os
import configparser
import re
import time

SMTP_SERVER = "smtp.163.com"
SMTP_SERVER = "mail.eastcompeace.com"
WORK_DIR = "e:\\test\\"
SMTP_USER = "sdd@eastcompeace.com"
SMTP_PWD = "asd19"

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='automail.log',
                    filemode='a')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)


def files_ready():
    global CDROMjdbDir
    FileList = []
    source_dir = CDROMjdbDir
    if not os.path.exists(source_dir):
        print('无法打开'+source_dir)
        CDROMjdbDir = 'none'

    source_dir = 'E:\jdb'
    if not os.path.exists(source_dir):
        print('无法打开' + source_dir)
    else:
        CDROMjdbDir = source_dir

    source_dir = 'F:\jdb'
    if not os.path.exists(source_dir):
        print('无法打开' + source_dir)
    else:
        CDROMjdbDir = source_dir

    source_dir = 'G:\jdb'
    if not os.path.exists(source_dir):
        print('无法打开' + source_dir)
    else:
        CDROMjdbDir = source_dir

    if CDROMjdbDir == 'none':
        print("无法打开CDROM SEP 文件夹。\n程序退出。")
        exit()
    print("JDB file is Ready."+CDROMjdbDir)
    have_jdb_file = False
    for i in os.listdir(CDROMjdbDir):
        if i.find(".jdb") > 0 :
            _fullname_s = os.path.join(CDROMjdbDir,i)
            _fullname_t = os.path.join(HDjdbDir, i)
            print(_fullname_s)
            if os.path.exists(_fullname_t):
                print(_fullname_t)
                md5_s = GetFileMd5(_fullname_s)
                md5_t = GetFileMd5(_fullname_t)
                if md5_s == md5_t:
                    print('File:'+i + '已存在，MD5：'+md5_s)
                    continue
            have_jdb_file = True
            FileList.append(i)

    if not have_jdb_file :
        print("CDROM SEP文件夹没有发现新的*.jdb升级文件。\n程序退出。")
        exit()
    return FileList





def send_email(dir_path,files,toaddr,ccaddr,c_name):

    msg = MIMEMultipart()
    msg['To'] = ";".join(toaddr)
    msg['CC'] = ";".join(ccaddr)
    msg['From'] = SMTP_USER
    msg['Subject'] = "test for python send email to customer:" + c_name

    html = """\
    xxx,
        你好，这是一个测试邮件，
        附件："""
    html = html + ";".join(files)
    html = html +"""
    请不要拦截我的邮件。MIMEText(content,_subtype='html',_charset='gb2312') 
    """
    body = MIMEText(html, 'plain')
#    body = MIMEText(text_body, 'plain')
    msg.attach(body)  # add message body (text or html)

    for f in files:  # add files to the message
        file_path = os.path.join(dir_path, f)
        attachment = MIMEApplication(open(file_path, "rb").read())
        attachment.add_header('Content-Disposition','attachment', filename=f)
        msg.attach(attachment)

    server = smtplib.SMTP(SMTP_SERVER, 25)
#    server.starttls()
    server.login(SMTP_USER, SMTP_PWD)
    mailbody = msg.as_string()

    server.sendmail(SMTP_USER, toaddr + ccaddr, mailbody) #send mail to & cc email address
    logging.info(SMTP_USER + "发送邮件："+"to:"+";".join(toaddr))
    server.quit()

def get_customer_file_list(folder,wildard):
    _filelist = []
    source_dir = folder
    have_file = False
    _wildcard = wildard.split('|')
    if not os.path.exists(folder):
        logging.warning("文件夹不存在："+ folder)
        return _filelist
    for i in range(len(_wildcard)):
        _wcard = _wildcard[i]
        _wcard = _wcard.replace('*','')
        for j in os.listdir(source_dir):
            if j.find(_wcard) > 0 :
                have_file = True
                if not(j in _filelist):
                    _filelist.append(j)
    if not have_file :
        logging.info("没有匹配文件_folder:"+source_dir+"  "+wildard)
    return _filelist

def get_customer_mail_list(toaddr):
    _mail_list =[]
    _to_addr = toaddr.split("|")
    for i in range(len(_to_addr)):
        if len(_to_addr[i]) > 7:
            if re.match('^[\w\d]+[\d\w\_\.]+@([\d\w]+)\.([\d\w]+)(?:\.[\d\w]+)?$|^(?:\+86)?(\d{3})\d{8}$|^(?:\+86)?(0\d{2,3})\d{7,8}$', _to_addr[i]) != None:
                _mail_list.append(_to_addr[i])
            else:
                logging.info("邮件地址有误："+_to_addr[i])
    return _mail_list

if __name__ == '__main__':

    cf = configparser.ConfigParser()
    try:
        cf.read('conf.ini', encoding="utf-8-sig")
        customer_total = int (cf.get("Customer", "total"))
        from_email_addr = cf.get("Customer", "from_email_addr")
        from_email_addr_mm = cf.get("Customer", "mm")
    except:
        logging.warning('无法打开文件 file d:\\automail\\conf.ini 或设置错误.')
        exit(2)
    customer_name = []
    customer_folder = []
    customer_wildcard = []
    customer_toaddr = []
    customer_ccaddr = []
    for i in range(1,customer_total+1):
        try:
            cfstr = 'Customer' + str(i)
            customer_name.append(cf.get(cfstr,'name'))
            customer_folder.append(cf.get(cfstr,'folder'))
            customer_wildcard.append(cf.get(cfstr,'wildcard'))
            customer_toaddr.append(cf.get(cfstr,'to_email_addr'))
            customer_ccaddr.append(cf.get(cfstr,'cc_email_addr'))
        except:
            logging.warning("conf.ini 配置有误，位置:"+cfstr)
#    print (customer_name)
#    print (customer_toaddr)

    for i in range(customer_total):
        folder_list = customer_folder[i]
        if files_ready(folder_list):
            c_name = customer_name[i]
            file_list = get_customer_file_list(customer_folder[i],customer_wildcard[i])
            print((file_list))
            if len(file_list) > 0:
                tomail_list = get_customer_mail_list(customer_toaddr[i])
                ccmail_list = get_customer_mail_list(customer_ccaddr[i])
                print(tomail_list,ccmail_list)
                print (folder_list)
                send_email(folder_list,file_list,tomail_list,ccmail_list,c_name)
                logging.info("sending mail....."+c_name)
                time.sleep(5)
