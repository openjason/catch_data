# -*- coding: UTF-8 -*-
# 版本：2018-02-02
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import logging
import os
import configparser
import re
import time,datetime
from filecmp import dircmp
import socket
from ctypes import *

SMTP_SERVER = ""
WORK_DIR = ""
SMTP_USER = ""
SMTP_PWD = "none"

long_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
folder_prefix = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))

cf = configparser.ConfigParser()
cf_file = 'c:\\automail\\automail.ini'
if not os.path.isfile(cf_file):
    cf_file = 'd:\\automail\\automail.ini'
    if not os.path.isfile(cf_file):
        cf_file = 'e:\\automail\\automail.ini'
        if not os.path.isfile(cf_file):
            logging.critical('无法打开配置文件：automail.ini ')
            exit(2)
try:
    cf.read(cf_file, encoding="utf-8-sig")
    customer_total = int (cf.get("Common", "total"))
    from_email_addr = cf.get("Common", "from_email_addr")
    SMTP_SERVER = cf.get("Common", "SMTP_SERVER")
    WORK_DIR = cf.get("Common", "WORK_DIR")
    SMTP_USER = cf.get("Common", "SMTP_USER")
    SMTP_PWD = cf.get("Common", "SMTP_PWD")

except:
    logging.warning('无法打开文件 automail.ini 或设置错误.')
    exit(2)
customer_name = []
customer_folder = []
customer_wildcard = []
customer_toaddr = []
customer_ccaddr = []
customer_subject = []
for i in range(1,customer_total+1):
    try:
        cfstr = 'Customer' + str(i)
        customer_name.append(cf.get(cfstr,'name'))
        customer_folder.append(cf.get(cfstr,'folder'))
        customer_wildcard.append(cf.get(cfstr,'wildcard'))
        customer_toaddr.append(cf.get(cfstr,'to_email_addr'))
        customer_ccaddr.append(cf.get(cfstr,'cc_email_addr'))
        customer_subject.append(cf.get(cfstr,'subject'))
    except:
        logging.warning("conf.ini 配置有误，位置:"+cfstr)
#    print (customer_name)
#    print (customer_toaddr)


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename = os.path.join(WORK_DIR,'automail.log'),
                    filemode='a')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

psapi = windll.psapi
kernel = windll.kernel32

def EnumProcesses(process_name):
    arr = c_ulong * 256
    lpidProcess = arr()
    cb = sizeof(lpidProcess)
    cbNeeded = c_ulong()
    hModule = c_ulong()
    count = c_ulong()
    modname = c_buffer(30)
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_VM_READ = 0x0010
    process_list = []
    # Call Enumprocesses to get hold of process id's
    psapi.EnumProcesses(byref(lpidProcess),
                        cb,
                        byref(cbNeeded))

    # Number of processes returned
    nReturned = int(cbNeeded.value / sizeof(c_ulong()))

    pidProcess = [i for i in lpidProcess][:nReturned]

    for pid in pidProcess:

        # Get handle to the process based on PID
        hProcess = kernel.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
                                      False, pid)
        if hProcess:
            psapi.EnumProcessModules(hProcess, byref(hModule), sizeof(hModule), byref(count))
            psapi.GetModuleBaseNameA(hProcess, hModule.value, modname, sizeof(modname))
            tem_str1 = [i for i in modname if i != b'\x00']
            j=''
            for i in range(len(tem_str1)):
                j = j + (tem_str1[i].decode())
#            print (j)
            process_list.append(j)

            # -- Clean up
            for i in range(modname._length_):
                modname[i] = b'\x00'

            kernel.CloseHandle(hProcess)
    p_count = 0
    for i in range(len(process_list)):
        if process_name == process_list[i]:
            p_count += 1
#            logging.info(str(process_name)+str(i))
    logging.info("Version: 20180202 "+str(p_count))
    if p_count > 2 :
        return True
    else:
        return False

def send_email(dir_path,files,toaddr,ccaddr,c_name,c_subject):
    c_subject = c_subject.replace("YYYY-MM-DD",long_date)
    logging.info("Subject:"+c_subject)
    msg = MIMEMultipart()
    msg['To'] = ";".join(toaddr)
    msg['CC'] = ";".join(ccaddr)
    msg['From'] = SMTP_USER
    msg['Subject'] = c_subject
    html = ""
    template_file_name = WORK_DIR+"template\\"+c_name+".template"
    try:
        with open(template_file_name,"r",encoding="utf-8") as t_f:
            for temp_line in t_f:
                html = html + temp_line
    except:
        html = '无正文内容'

    html = html.replace("YYYY-MM-DD",long_date)
    html = html.replace("ATTACHMENT","、".join(files))

    print(html)
    body = MIMEText(html, 'plain')
    #    body = MIMEText(text_body, 'plain')
    msg.attach(body)  # add message body (text or html)

    for f in files:  # add files to the message
        file_path = os.path.join(dir_path, f)
        attachment = MIMEApplication(open(file_path, "rb").read())
        attachment.add_header('Content-Disposition','attachment', filename=f)
        msg.attach(attachment)
    logging.info ("附件共" + str(len(files)) + "个，其中有文件名："+ file_path)

#    return 2
#if enable return, then program will not send email...

    server = smtplib.SMTP(SMTP_SERVER, 25)
    #    server.starttls()
    server.login(SMTP_USER, SMTP_PWD)
    mailbody = msg.as_string()

    server.sendmail(SMTP_USER, toaddr + ccaddr, mailbody) #send mail to & cc email address
    logging.info(c_name + ":发送邮件："+"to:"+";".join(toaddr)+" ;附件："+";".join(files))
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

if __name__ == '__main__':
    if EnumProcesses('automail.exe') :
        logging.warning('automail.exe is running ,请不要重复运行. Exit().')
        exit(4)
    clear_expire_folder()
    for i in range(customer_total):
        folder_list = customer_folder[i]
        c_name = customer_name[i]
        file_list = get_customer_file_list(folder_list,customer_wildcard[i])

        if len(file_list) > 0:
            mail_server_ok()        #检查网络是否可用
            limit_times = 0
            while limit_times < 5:
                limit_times += 1
                folder_prefix = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                prepare_folder = WORK_DIR+"sent\\" + folder_prefix+customer_name[i]
                os.mkdir(prepare_folder)
                if prepare_files(customer_folder[i],prepare_folder) == False:
                    logging.warning("拷贝文件夹出错...")
                    time.sleep(limit_times * 10)
                else:
                    if check_diff_n_leftonly_files(customer_folder[i],prepare_folder) == False:
                        logging.info("拷贝文件夹与原文件夹一致.")
                        if clear_files(customer_folder[i]):
                            break
                        else:
                            logging.warning("清空文件夹失败，重试次数:" + str(limit_times))
                    else:
                        logging.warning("拷贝文件夹与原文件夹不一致次数:" + str(limit_times))
                        time.sleep(limit_times * 10)
            if limit_times == 5 :
                logging.warning("文件夹复制或文件比对重试多次后失败，此客户邮件发送暂停，重试次数:" + str(limit_times))
                continue
            file_list = get_customer_file_list(prepare_folder,customer_wildcard[i])

            tomail_list = get_customer_mail_list(customer_toaddr[i])
            ccmail_list = get_customer_mail_list(customer_ccaddr[i])
            c_subject = customer_subject[i]
            print(tomail_list,ccmail_list)
            print (prepare_folder,file_list,tomail_list,ccmail_list,c_name,c_subject)

            send_email(prepare_folder,file_list,tomail_list,ccmail_list,c_name,c_subject)
            logging.info("sending mail....."+c_name)
            time.sleep(3)
