# -*- coding: UTF-8 -*-
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

VERSION = "Ver: 20180409 "
SMTP_SERVER = ""
WORK_DIR = ""
SMTP_USER = ""
SMTP_PWD = ""
SMTP_SENDER = ""

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
    SMTP_SENDER = cf.get("Common", "SMTP_SENDER")

except:
    logging.warning('无法打开文件 automail.ini 或设置错误.')
    exit(2)
customer_name = []
customer_folder = []
customer_wildcard = []
customer_toaddr = []
customer_ccaddr = []
customer_subject = []
customer_sourcedir = []
customer_destdir = []

for i in range(1,customer_total+1):
    try:
        cfstr = 'Customer' + str(i)
        customer_name.append(cf.get(cfstr,'name'))
        customer_folder.append(cf.get(cfstr,'folder'))
        customer_wildcard.append(cf.get(cfstr,'wildcard'))
        customer_toaddr.append(cf.get(cfstr,'to_email_addr'))
        customer_ccaddr.append(cf.get(cfstr,'cc_email_addr'))
        customer_subject.append(cf.get(cfstr,'subject'))
        customer_sourcedir.append(cf.get(cfstr,'sourcedir'))
        customer_destdir.append(cf.get(cfstr, 'destdir'))
    except:
        logging.warning("conf.ini 配置有误，参数:"+cfstr)


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
                j = j + (tem_str1[i].decode('utf-8', 'ignore'))
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
    logging.info(VERSION + str(p_count))
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
    msg['From'] = SMTP_SENDER+"<" + SMTP_USER + ">"
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
        fullname = os.path.join(dir_path, f)
        with open(fullname, 'rb') as o_f:
            msg_attach = MIMEBase('application', 'octet-stream')
            msg_attach.set_payload(o_f.read())
            encoders.encode_base64(msg_attach)
            msg_attach.add_header('Content-Disposition', 'attachment',
                                  filename=(Header(f, 'utf-8').encode()))
            msg.attach(msg_attach)

    logging.info ("附件共" + str(len(files)) + "个，其中有："+ fullname)

#    return 2
#if enable return, then program will not send email...

    server = smtplib.SMTP(SMTP_SERVER, 25)
    server.login(SMTP_USER, SMTP_PWD)
    mailbody = msg.as_string()

    server.sendmail(SMTP_USER, toaddr + ccaddr, mailbody) #send mail to & cc email address
    logging.info(c_name + ":发送邮件："+"to:"+";".join(toaddr)+" ;附件："+";".join(files))
    server.quit()

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

def get_customer_file_list(folder,wildard):
    _filelist = []
    source_dir = folder
    have_file = False
    _wildcard = wildard.split('|')
    if not os.path.exists(folder):
        logging.warning("文件夹不存在："+ folder)
        return _filelist
#    if dir_compare_diff(dir_com1,dir_com2,folder):
    if True:
        for i in range(len(_wildcard)):
            _wcard = _wildcard[i]
            _wcard = _wcard.replace('*','')
            for j in os.listdir(source_dir):
                if j.find(_wcard) != -1 :
                    have_file = True
                    if not(j in _filelist):
                        _filelist.append(j)
        if not have_file :
#            logging.info("无更新:"+source_dir+" "+wildard)
            print("无更新:" + source_dir + " " + wildard)
    return _filelist


def get_customer_mail_list(toaddr):
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


if __name__ == '__main__':
    if EnumProcesses('automail.exe'):
        logging.warning('automail.exe is running ,请不要重复运行. Exit().')
        exit(4)
    clear_expire_folder()
    for i in range(customer_total):
        folder_list = customer_folder[i]
        if not os.path.exists(folder_list):
            logging.info("无法打开文件夹："+folder_list)
            continue
        c_name = customer_name[i]
        source_dir = customer_sourcedir[i]
        dest_dir = customer_destdir[i]

        if compare_clear_right_side(dest_dir,source_dir) != 0:
            logging.info("无法比较文件夹，请查看配置是否正确.")
            continue
        if main_compare_sync(source_dir,dest_dir,folder_list) != 0:
            logging.info("无法比较文件夹，请查看配置是否正确.")
            continue

        file_list = get_customer_file_list(folder_list, customer_wildcard[i])

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

