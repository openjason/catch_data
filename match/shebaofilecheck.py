# -*- coding: utf-8 -*-  
''' 
处理广州三代社保数据文件检查校验工作
功能：三代社保卡处理文件：任务单、ep文件、打印清单、mdb文件、数据单等文件分拣，校验文件内容匹配情况，如字符串长度、样式名称、字段内容等。
需求提交时间：20210611
测试版本首次提交时间：20210720 
配置文件.ini sample

[JC配置]
customer = 广州三代社保|!|珠海社保
dxhppwd = qxd|!|xxxxxx631
[广州三代社保]
working = 1|!|11|!|13
#原始文件夹
sourcedir = D:\dev\py\match\脚本测试\测试5
#分拣文件夹
sortingdir = D:\testddd\
#临时文件夹
tempdir = D:\dev\py\match\temp
#taskorder文件所含的关键字
rawverify1 = 数据单|!|数据单
rawverify2 = 错误输出文件|!|Error
rawverify3 = 印刷数据|!|.mdb
rawverify4 = 订单表|!|订单
rawverify5 = 生产报告|!|生产报告
rawverify6 = ZIP打印清单|!|打印清单
rawverify7 = 客服提供分单|!|广州三代社保卡金融蓝卡
rawverify8 = 个人化数据离线平台ep|!|离线平台.ep
rawverify9 = 社保原始数据|!|.txt
rawverify10 =生产任务单|!|生产任务单
rawverify11 =文件log|!|log
#参数数字为对应文件
checkpoint1 = ErrorFile|!|2
#检查Error文件是否为0
checkpoint2 = TaskOrderProReport|!|10|!|5
#对比生产任务单需求文档编号 = 生产报告产品规格编号
#对比生产任务单 应用要求 = 生产报告产 产品名称
checkpoint3 = TaskOrderOrderProReport|!|10|!|4|!|5
#生产任务单*工单号 - 订单表*工单号*报告编号 - 生产报告*生产报告编号
checkpoint4 = SMCLenPrintItem|!|5
#提取生产报告文件 SMCLen值 和打印项要素
checkpoint5 = DataForm|!|1
#提取数据单各要素，匹配客户名，订单数量（未匹配），下单数量，提取ep(mdb xls)文件列表，前提：SMCLenPrintItem
checkpoint6 = SMCLenEPs|!|8
#核对ep文件smc/endsmc之间字符长度是否与报告一致，只检查第一行/最后一行,前提：DataForm
checkpoint7 = PersonalizationPrintItem|!|10|!|0
#任务单个人化需求与打印清单格式核对，前提：获取ep文件列表DataForm
checkpoint8 = PrintItemEP|!|5|!|8
#核对ep文件与生产报告中打印标签项（列表）内容长度是否一致，只检查第一行/最后一行
checkpoint9 = PrintListEP|!|0|!|8
#核对ep文件中各项内容与打印列表中内容是否一致，
checkpoint10 = PrintListMdb|!|0
#核对打印列表中各项内容与mdb中printdata内容是否一致
checkpoint11 = SuccessFailurelogCheck|!|11
#核查订单目录log文件是否匹配
checkpoint12 = ZipPwdCheck|!|6
#核对打印清单zip密码是否正确
checkpoint13 = SortedPackageCheck|!|7
#分发文件夹文件检查分拣文件序号7
[珠海社保]
working = 0|!|10|!|10
#原始文件夹
sourcedir = D:\dev\py\match\
#分拣文件夹
sortingdir = D:\testddd\
#临时文件夹
tempdir = D:\dev\py\match\temp
#taskorder文件所含的关键字
rawverify1 = 原始数据|!|ZKSJ
rawverify2 = 个人化数据|!|.ep
rawverify3 = 印刷数据|!|.mdb
rawverify4 = 打印清单|!|总EP
rawverify5 = 生产报告|!|ICSB
rawverify6 = 生产任务单|!|生产任务单
rawverify7 = 客服提供分单|!|广州三代社保卡金融蓝卡
rawverify8 = 
rawverify9 = 
rawverify10 =生产任务单|!|生产任务单
checkpoint1 = 
checkpoint2 = 
checkpoint3 = 
checkpoint4 = 
checkpoint5 = 
checkpoint6 = 
checkpoint7 = 
checkpoint8 = 
checkpoint9 = 
checkpoint10 = 
'''
from ntpath import realpath
from tkinter import Tk
from tkinter import ttk
from tkinter.ttk import Treeview,Style
from configparser import ConfigParser
from tkinter import HORIZONTAL,VERTICAL,MULTIPLE,Message,Listbox,messagebox,Label,StringVar,Scrollbar, Button,END, DISABLED, Toplevel,SUNKEN,LEFT,Y  # 导入滚动文本框的模块
import os,sys
from logging import getLogger,INFO,Formatter
from logging.handlers import RotatingFileHandler
import datetime,time  
import shutil, zipfile
from types import SimpleNamespace

from xml.dom.minidom import parse as xml_parse
#import xml.dom.minidom

import pdfplumber
from xlrd import open_workbook as openworkbook
import pyodbc
import subprocess

def convert_pdf_to_txt_scbg(pdffilename,txtfilename):
    #pdf文件另存为text文件 生产报告
    #按表格保存
    try:
        temp_dir = os.path.dirname(txtfilename)
        if not os.path.exists(temp_dir):
            os.mkdir(temp_dir)
        txt_file_table = open(txtfilename,mode='w',encoding='gbk')
        with pdfplumber.open(pdffilename) as pdf:
            icount =0 
            for page01 in pdf.pages:
                page_text = page01.extract_text()
                txt_file_table.write(page_text)
                txt_file_table.write('\n')
                # tables = page01.extract_tables()
                # for table in tables:
                #     for rows in table:
                #         for row in rows:
                #             if row:
                #                 txt_file_table.write(row)
                #             txt_file_table.write('\n')
                #         icount = icount+1
        return('正常返回，转换PDF文件正常。')
    except Exception as err_message:
        print(err_message)
        logger.error(err_message.__str__())
        logger.exception(sys.exc_info())
        return('Error，程序异常，转换PDF文件出错！')

def convert_pdf_to_txt(pdffilename,txtfilename):
    #pdf文件另存为text文件
    #按表格保存
    try:
        temp_dir = os.path.dirname(txtfilename)
        if not os.path.exists(temp_dir):
            os.mkdir(temp_dir)
        txt_file_table = open(txtfilename,mode='w',encoding='gbk')
        with pdfplumber.open(pdffilename) as pdf:
            icount =0 
            for page01 in pdf.pages:
                tables = page01.extract_tables()
                for table in tables:
                    for rows in table:
                        for row in rows:
                            if row:
                                txt_file_table.write(row)
                            txt_file_table.write('\n')
                        icount = icount+1
        return('正常返回，转换PDF文件正常。')
    except Exception as err_message:
        print(err_message)
        logger.error(err_message.__str__())
        logger.exception(sys.exc_info())
        return('Error，程序异常，转换PDF文件出错！')

def brackets_catchcontent(sourcestr):
    #读取括号内内容
    temp_pos1 = sourcestr.find('(')
    temp_pos2 = sourcestr.find('（')
    temp_pos3 = max(temp_pos1,temp_pos2)
    temp_pos1 = sourcestr.find(')')
    temp_pos2 = sourcestr.find('）')
    temp_pos1 = max(temp_pos1,temp_pos2)
    if temp_pos1 > temp_pos3:
        temp_str = sourcestr[temp_pos3+1:temp_pos1]
        temp_str = temp_str.strip()
        return(temp_str)
    return -1

def catchfilefullname(path,shortname):
    for relpath, dirs, files in os.walk(path):  # path 为根目录
        for filename in files:
            if shortname in filename:
                #flag = 1      #判断是否找到文件
                return os.path.join(path, relpath,filename)
    return -1

def catchfilefullnameindir(path,shortname,includedir):
    for relpath, dirs, files in os.walk(path):  # path 为根目录
        for filename in files:
            if (shortname in filename) and (includedir in relpath):
                print('relpath',relpath)
                return os.path.join(path, relpath,filename)
    return -1

def get_xlsfile_nrow(sourcedir,xlsfilename_match):
    #查找异常反馈表，返回数据行数量
    for relpath, dirs, files in os.walk(sourcedir):  # path 为根目录
        for filename in files:
            if os.path.splitext(filename)[1]=='.xls' or os.path.splitext(filename)[1]=='.xlsx':
                if xlsfilename_match in filename:
                    xlsfullfilename = os.path.join(sourcedir, relpath,filename)
                    logger.info(xlsfullfilename)
                    wb = openworkbook(xlsfullfilename)
                    ws1 = wb.sheet_by_index(0)
                    return_nrows = ws1.nrows
                    return('正常返回:'+str(return_nrows))
    return('Error:没有找到异常反馈表'+str(xlsfilename_match))

def getSortedNumberFromxls(sourcedir,xlsfilename_match,strProductOrderNo):
    for relpath, dirs, files in os.walk(sourcedir):  # path 为根目录
        for filename in files:
            if os.path.splitext(filename)[1]=='.xls':
                if xlsfilename_match in filename:
                    xlsfullfilename = os.path.join(sourcedir, relpath,filename)

                    logger.info(xlsfullfilename)
                    wb = openworkbook(xlsfullfilename)
                    ws1 = wb.sheet_by_index(0)
                    strFenDanHao = ''
                    for worksheetdatarow in range(1,ws1.nrows):
                        strZongDanHao = str(ws1.cell(worksheetdatarow,0).value )
                        #print(strZongDanHao)
                        if strZongDanHao == strProductOrderNo:
                            strFenDanHao = str(ws1.cell(worksheetdatarow,2).value )
                            return('正常返回:'+str(strFenDanHao))
    return('Error:没有找到ProductOrderNo')
        
def Success_Failure_log_filecheck(path):
    success_log_filename = ''
    failure_log_filename = ''
    shortname = '.log'
    for relpath, dirs, files in os.walk(path):  # path 为根目录
        for filename in files:
            if shortname in filename:
                if 'Success' in filename:
                    success_log_filename = os.path.join(path, relpath,filename)
                if 'Failure' in filename:
                    failure_log_filename = os.path.join(path, relpath,filename)
    if success_log_filename == '' or failure_log_filename == '':
        return 'Error: 无Success.log/Failure.log文件。'
    openf = open(failure_log_filename,'r',encoding='gbk')
    while openf : 
        oneline = openf.readline()
        if not('一共有0个ATR' in oneline):
            oneline = oneline.strip()
            return 'Error: 文件Failure.log 异常：' + oneline
        else:
            openf = open(success_log_filename,'r',encoding='gbk')
            while openf : 
                oneline = openf.readline()
                oneline = openf.readline()  #读第二行
                if not(('一共成功导入' in oneline) and ('条数据'in oneline)) :
                    oneline = oneline.strip()
                    return 'Error: 文件Success.log 异常：' + oneline
                else:
                    str_pos1 = oneline.index('一共成功导入')
                    str_pos2 = oneline.index('条数据')
                    result_str = oneline[str_pos1+6:str_pos2]
                    return '正常返回: ' + result_str

def catchepmdbxls_filelist_form_ep(path,shortname,one_ep_file_shuliang):
    if shortname[-3:] == '.ep':
        match_file_str = shortname[:-3]     #去.ep后缀，用名字匹配
    else:
        match_file_str = shortname
    logger.info(path)
    logger.info(match_file_str)
    epfilelist = []
    mdbfilelist = []
    xlsfilelist = []
    for relpath, dirs, files in os.walk(path):  # path 为根目录
        for filename in files:
            if shortname in filename:
                #ep文件匹配-全名
                if not ('离线平台' in filename):
                    epfilelist.append(os.path.join(path, relpath,filename))
            if match_file_str in filename:
                if filename[-4:] == '.mdb':
                    mdbfilelist.append(os.path.join(path, relpath,filename))
                elif filename[-4:] == '.xls':
                    xlsfilelist.append(os.path.join(path, relpath,filename))                
    if epfilelist==[] :
        return -1
    else:
        for one_ep_file in epfilelist:        
            logger.info('处理ep，mdb不同名情况：')
            logger.info(one_ep_file)
            one_ep_file_dirname = os.path.dirname(one_ep_file)
            one_ep_file_basename = os.path.basename(one_ep_file)
            if mdbfilelist==[]:
                xlsfilelist = []
                #if mdbfilelist==[] or xlsfilelist== []: 修改为只判断是否找到对应mdb 文件
                temp_list = one_ep_file_basename.split('_')
                match_file_str = temp_list[0]+'_'+temp_list[1]+'_'+temp_list[2]+'_'+temp_list[3]+'_'+temp_list[4]+'_'+temp_list[5]+'_'+temp_list[6]+'_'
                logger.info(one_ep_file_dirname)
                logger.info(match_file_str)
                #for relpath, dirs, files in os.walk(one_ep_file_dirname):  # path 为根目录
                for files in os.listdir(one_ep_file_dirname):  # path 为根目录
                    #for filename in files:
                        filename = files
                        if match_file_str in filename:
                            #print('filename',filename)
                            if filename[-4:] == '.xls':
                                xlsfilelist.append(os.path.join(one_ep_file_dirname, filename))
                            elif filename[-4:] == '.mdb':
                                mdbfilelist.append(os.path.join(one_ep_file_dirname, filename))
                if mdbfilelist==[] or xlsfilelist== []:
                    return -1
                else:    
                    return ([epfilelist,mdbfilelist,xlsfilelist,one_ep_file_shuliang])
            else:
                return ([epfilelist,mdbfilelist,xlsfilelist,one_ep_file_shuliang])

def catch_ep_cutting_form_ep(path,shortname,one_ep_file_shuliang):
    if shortname[-3:] == '.ep':
        match_file_str = shortname[:-3]     #去.ep后缀，用名字匹配
    else:
        match_file_str = shortname
    epfilelist = []
    mdbfilelist = []
    xlsfilelist = []
    for relpath, dirs, files in os.walk(path):  # path 为根目录
        for filename in files:
            if shortname in filename:
                #ep文件匹配-全名, 含扩展名.ep
                epfilelist.append(os.path.join(path, relpath,filename))
    if epfilelist==[] :
        return -1
    else:
        for one_ep_file in epfilelist:        
            print(one_ep_file)
            one_ep_file_dirname = os.path.dirname(one_ep_file)
            cutting_files_str = ''
            for files in os.listdir(one_ep_file_dirname):  # path 为根目录
                #for filename in files:
                filename = files
                print(filename)
                if filename[-3:] == '.ep':
                    if match_file_str in filename:
                        if (shortname in filename) or ('离线平台' in filename):
                            continue
                        cutting_files_str = cutting_files_str + filename[len(match_file_str):-3]
        if cutting_files_str=='':
            return -1
        else:    
            return cutting_files_str

def catch_pdf_string_val_shengchanbaogao(pdffilename,getstring):
    #pdf文件提取字符串值
    openf = open(pdffilename,'r',encoding='gbk')
    is_get_string = False
    oneline = 'tempstr'
    while oneline: 
        before_oneline = oneline
        oneline = openf.readline()
        if getstring in oneline:
            is_get_string = True
            break
    if is_get_string:
        logger.info('从文件行中找到字符串: '+oneline)
        oneline = oneline.replace(':',' ')
        oneline = oneline.replace('：',' ')
        temp_list = oneline.split()
        i_indx = temp_list.index(getstring)
        print(i_indx,len(temp_list))
        if i_indx +1 == len(temp_list):
            #判断找到的字符串是否在行尾
            logger.info('字符串在行尾')
            oneline = openf.readline()
            temp_list = oneline.split()
            i_indx=0
        else:
            i_indx += 1         #将返回找到字符串的后一个串
        logger.info(i_indx)
        logger.info(temp_list)
        result_str = temp_list[i_indx]
        if '编号' in getstring:
            if is_Chinese(result_str[0]):
                temp_list = before_oneline.split()
                result_str = temp_list[0]
        result_str = double_character_proc(result_str)
        return result_str
    else:
        return 'Error, 没有找到字符串: ' + getstring

def is_Chinese(ch):
    if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

def double_character_proc(chars):
    chars_len = len(chars)
    if chars_len < 10:
            return chars
    else:
        if chars_len % 2 == 0:
            r_chars = ''
            for tint in range(0,chars_len//2):
                if chars[tint*2] == chars[tint*2+1]:
                    r_chars = r_chars + chars[tint*2]
                else:
                    return chars
            return r_chars
    return chars

def catch_pdf_string_val(pdffilename,getstring):
    #pdf文件提取字符串值
    print(pdffilename,getstring)
    openf = open(pdffilename,'r',encoding='gbk')
    is_get_string = False
    oneline = openf.readline()
    while oneline: 
        if getstring in oneline:
            is_get_string = True
            break
        oneline = openf.readline()
    if is_get_string:
        logger.info('从文件行中找到字符串: '+oneline)
        oneline = oneline.replace(':',' ')
        oneline = oneline.replace('：',' ')
        temp_list = oneline.split()
        i_indx = temp_list.index(getstring)
        print(i_indx,len(temp_list))
        if i_indx +1 == len(temp_list):
            #判断找到的字符串是否在行尾
            logger.info('字符串在行尾')
            oneline = openf.readline()
            temp_list = oneline.split()
            i_indx=0
        else:
            i_indx += 1         #将返回找到字符串的后一个串
        logger.info(i_indx)
        logger.info(temp_list)
        ret_str = temp_list[i_indx]
        #若不是最后一个 判断是不是v开头，是的加上
        if i_indx +1 + 1 <= len(temp_list):
            tempstr = temp_list[i_indx+1]
            #首符号是v，末符号是数字
            if tempstr[0]=='v' or tempstr[0] == 'V':
                if tempstr[-1].isdigit():
                    ret_str = ret_str +temp_list[i_indx+1] 
        ret_str = double_character_proc(ret_str)
        return ret_str
    else:
        return 'Error, 没有找到字符串: ' + getstring

def check_sortingfile_yinshua_zip_content(zipfilename,xiafashuliang,tempdir,zippwd,mdb_wurenxiang_count):
    #检查分拣文件印刷.zip压缩包文件数量内容等
    cmdstr = '7za e -p'+zippwd+' ' +zipfilename +' photo.zip -o'+tempdir
    return_code = subprocess.call(cmdstr, shell=True)
    photozipfile = os.path.join(tempdir,'photo.zip')
    if not os.path.exists(photozipfile):
        return 'Error, 文件photo.zip没有正常压缩，错误，请检查'
    zfobj = zipfile.ZipFile(zipfilename)
    mdbfile_count = 0
    mdbfilelist = []
    wurenxiang = 0
    filelist = zfobj.namelist()
    for name in filelist:
        if '.mdb' in name.lower():
            mdbfile_count = mdbfile_count +1
            mdbfilelist.append(name)
            if '无人像' in name:
                wurenxiang = 1
    zfobj = zipfile.ZipFile(photozipfile)
    jpgfile_count = 0
    filelist = zfobj.namelist()
    for name in filelist:
        if '.jpg' in name.lower():
            jpgfile_count = jpgfile_count +1
    jpgfile_and_wurenxiang_count = jpgfile_count + mdb_wurenxiang_count
    #加上无人像数量
    if jpgfile_and_wurenxiang_count != xiafashuliang:
        return 'Error, 文件jpg数量与下发数量不符合，错误，请检查:' + str(jpgfile_count) + '≠' + str(xiafashuliang) +' 无人像='+str(mdb_wurenxiang_count)
    mdb_suffix_count =0 
    try:
        for mdbfilename in mdbfilelist:
            templist = mdbfilename.split('_')
            tempstr = templist[-1]
            tempstr = tempstr[:-5]
            temp_pos = tempstr.index('-')
            tempstr = tempstr[temp_pos+1:]
            mdb_suffix_count =mdb_suffix_count + int(tempstr)
    except:
            return 'Error, mdb文件名称尾数量转换数字错误，请检查'
    if wurenxiang > 0 :
        mdb_suffix_count = mdb_suffix_count/2
    if mdb_suffix_count != xiafashuliang:
        return 'Error, 文件mdb后缀标记数量与下单数据不符合，错误，请检查'
    return '正常返回, mdb文件数量'+str(mdbfile_count)+' jpg文件数量' + str(jpgfile_count)+' 无人像文件'+str(wurenxiang)+' 无人像='+str(mdb_wurenxiang_count)

def check_sortingfile_gerenhua_zip_content(zipfilename,dingdanshuliang):
    #检查分拣文件个人化.zip压缩包文件数量内容等
    temp_dir = os.path.dirname(zipfilename)
    temp_dir = temp_dir.replace('分发','原始')
    #files in os.walk(temp_dir):  # 只计算当前目录文件
    yuanshi_txtfile_count =0
    filelist = os.listdir(temp_dir)
    for filename in filelist:
        if '.txt' in filename:
            yuanshi_txtfile_count = yuanshi_txtfile_count +1
    zfobj = zipfile.ZipFile(zipfilename)
    epfile_count = 0
    cutting_file_count = 0
    txtfile_count = 0
    jinrongfloder = 1
    filelist = zfobj.namelist()
    for name in filelist:
        if '.ep' in name:
            epfile_count = epfile_count +1
            if '_01.ep' in name:
                cutting_file_count = cutting_file_count + 1
        if '.txt' in name and (not ('/' in name)):
            txtfile_count = txtfile_count +1
        if '金融' in name:
            jinrongfloder = 1
    logger.info('yuanshi_txtfile_count,epfile_count,cutting_file_count,txtfile_count,jinrongfloder')
    logger.info(yuanshi_txtfile_count)
    logger.info(epfile_count)
    logger.info(cutting_file_count)
    logger.info(txtfile_count)
    logger.info(jinrongfloder)
    if yuanshi_txtfile_count != txtfile_count:
        return 'Error, 原始文件夹txt数量不等于分发-个人化.txt文件数量'
    if dingdanshuliang > 240:
        if cutting_file_count == 0:
            return 'Error, 订单数量大于240，没有分割EP文件'
    return '正常返回, txt文件数量'+str(yuanshi_txtfile_count)+' ep文件数量' + str(epfile_count)+' 分割文件数量'+str(cutting_file_count)+' 含金融文件夹.'
    
def catch_pdf_string_multilines(pdffilename,getstring):
    #pdf文件提取字符串值
    openf = open(pdffilename,'r',encoding='gbk')
    is_get_string = False
    while openf : 
        oneline = openf.readline()
        if getstring in oneline:
            is_get_string = True
            break
    if is_get_string:
        #logger.info('从文件行中找到字符串: '+oneline)
        oneline = oneline.replace(':',' ')
        oneline = oneline.replace('：',' ')
        temp_list = oneline.split()
        i_indx = temp_list.index(getstring)
        print(i_indx,len(temp_list))
        multistring = ''
        while openf : 
            oneline = oneline.strip()
            multistring = multistring + oneline 
            oneline = openf.readline()
            print(oneline)
            if len(oneline) < 2 :
                break
        return multistring
    else:
        return 'Error, 没有找到字符串: ' + getstring

def convert_epbasename_fullname(txtfilename,startstring,endstring):
    #查找一行字符中，开始符号和中间符号的字符数
    #不对中文处理，含中文字可能有误
    if not (os.path.exists(txtfilename)):
        return('Error: pdftxtfile 文件不存在.')
    try:
        epfilesize = os.path.getsize(txtfilename)
    except:
        return('Error pdf文件提取字符串值 程序出错#@#')

def catch_txtfile_string_len(txtfilename,startstring,endstring):
    #查找一行字符中，开始符号和中间符号的字符数
    #不对中文处理，含中文字可能有误
    if not (os.path.exists(txtfilename)):
        return('Error: pdftxtfile 文件不存在.')
    epfilesize = os.path.getsize(txtfilename)
    logger.info('catch_txtfile_string_len filesize')
    logger.info(txtfilename)
    logger.info(epfilesize)
    if epfilesize > 1024*1024:
        with open(txtfilename,'r',encoding='gbk') as f:  #打开文件
            for i in range(6):
                onelinefirst = f.readline()  #读第5行
            onelinefirst = f.readline()       #读第六行
        print(onelinefirst[:20])
        filesize = epfilesize
        blocksize = 1024 * 50
        dat_file = open(txtfilename, 'r',encoding='gbk')
        lines = []
        if filesize > blocksize:
            maxseekpoint = (filesize // blocksize)#" / "就表示 浮点数除法，返回浮点结果;" // "表示整数除法
            maxseekpoint -= 1 
            dat_file.seek(maxseekpoint * blocksize)
            lines = dat_file.readlines()
            while((len(lines)<2)) | ((len(lines)>=2)&(lines[1]==b'\r\n')):
                #因为在Windows下，所以是b'\r\n'
                #如果列表长度小于2，或者虽然长度大于等于2，但第二个元素却还是空行
                #如果跳出循环，那么lines长度大于等于2，且第二个元素肯定是完整的行
                maxseekpoint -= 1 
                dat_file.seek(maxseekpoint * blocksize)
                lines  = dat_file.readlines()  
            onelinelast = lines[-1]
    else:
        #小文件，打开文件#读取所有行
        with open(txtfilename,'r',encoding='gbk') as f:  
            lines = f.readlines()                        
        onelinefirst=lines[6]    
        onelinelast=lines[-1]    
    #获取第一条匹配行
    startpos = onelinefirst.find(startstring)
    endpos = onelinefirst.find(endstring)
    if (startpos < 0) or (endpos < 0):
        return -1
    print(startpos,endpos)
    templen1 = endpos-startpos -len(startstring)
    tempstr1 = str(templen1)
    #和最后一行匹配行
    startpos = onelinelast.find(startstring)
    endpos = onelinelast.find(endstring)
    if (startpos < 0) or (endpos < 0):
        return -1
    print(startpos,endpos)
    templen2 = endpos-startpos -len(startstring)
    tempstr2 = str(templen2)

    if tempstr1==tempstr2:
        return tempstr1
    else:
        return -1

def check_PrintList_mdb_val(pitemlist,xlsfilename,mdbfilename):
    #核对打印列表各项数据，检查EP文件，对应项，打印列表内容添加pitem尖括号
    #比对具体字符，可处理中文字符
    if not (os.path.exists(mdbfilename)):
        return('Error: mdbfilemissing.')
    if not (os.path.exists(xlsfilename)):
        return('Error: xlsfilemissing.')
    wb = openworkbook(xlsfilename)
    worksheetdatarow = 1
    ws1 = wb.sheet_by_index(0)
    DBfile = mdbfilename # 数据库文件需要带路径
    print(DBfile)
    try:
        for driverstr in pyodbc.drivers():
            if driverstr.startswith('Microsoft Access Driver'):
                conn = pyodbc.connect(r"DRIVER={"+driverstr+"};DBQ="+ DBfile +";Uid=;Pwd=;")
    except:
        return('Error Microsoft Access Driver 驱动有误，程序出错。')
    cursor = conn.cursor() 
    SQL = "SELECT * from printdata;"
    for row in cursor.execute(SQL): 
        col = 0
        for fieldwalue  in row:
            mdbvalue = fieldwalue
            xlsvalue = ws1.cell(worksheetdatarow,col).value
            if type(xlsvalue) == float:
                xlsvalue = int(xlsvalue)
            col +=1
            if mdbvalue != xlsvalue:
                return('Error: mdb文件与Excel文件数据不等，行='+str(worksheetdatarow)+',列='+str(col))
        worksheetdatarow +=1
    cursor.close() 
    conn.close()
    return('匹配正确:核对打印清单与mdb数量相同, 行=' +str(worksheetdatarow-1))

def get_Data_Form_listval(xlsfilename):
    #提取数据单值，返回列表
    if not (os.path.exists(xlsfilename)):
        return('Error: xlsfilemissing.')
    wb = openworkbook(xlsfilename)
    ws1 = wb.sheet_by_index(0)
    #ws1.cell(worksheetdatarow,col).vlaue
    xlsnrows = ws1.nrows
    col = 0
    worksheetdatarow = 1
    kehu = ws1.cell(worksheetdatarow,1).value
    kaleibie = ws1.cell(worksheetdatarow,5).value
    dingdanshuliang = ws1.cell(worksheetdatarow,8).value
    xiafashuliang = ws1.cell(worksheetdatarow,10).value
    shujugeshi = ws1.cell(3,2).value
    zhidanren = ws1.cell(5,2).value
    zhidanriqi = ws1.cell(5,6).value
    neibudingdanhao = ws1.cell(5,9).value
    epfilelist = []
    for row  in range(9,xlsnrows):
        if ws1.cell(row,1).value == None:
            break
        onerec = []
        for j in [0,1,4,8,9,10]:
            onerec.append(ws1.cell(row,j).value)
        epfilelist.append(onerec)
    dataformlist=[kehu,kaleibie,dingdanshuliang,xiafashuliang,shujugeshi,zhidanren,zhidanriqi,neibudingdanhao,epfilelist]
    #print(dataformlist)
    return(dataformlist)

def catch_xls_onecell_value(xlsfilename,target_title):
    # 读取excel表格第一行信息（标题），返回字符串，空格分隔
    print('catch_xls_onecell_value(xlsfilename,data_row,data_col)')
    print(xlsfilename)
    if not (os.path.exists(xlsfilename)):
        return('Error: xlsfilemissing.')
    wb = openworkbook(xlsfilename)
    ws1 = wb.sheet_by_index(0)
    title_row = 0
    xlscols = ws1.ncols
    for col  in range(0,xlscols):   #忽略第一列，‘序号’
        if ws1.cell(title_row,col).value == target_title:
            result_value = ws1.cell(title_row+1,col).value
            return result_value
    return 'Error: 没有找到对应的值：' + str(target_title)

def catch_xls_oneline(xlsfilename,data_firstrow):
    # 读取excel表格第一行信息（标题），返回字符串，空格分隔
    print('catch_xls_firstline')
    print(xlsfilename)
    if not (os.path.exists(xlsfilename)):
        return('Error: xlsfilemissing.')
    wb = openworkbook(xlsfilename)
    ws1 = wb.sheet_by_index(0)
    #ws1.cell(worksheetdatarow,col).vlaue
    xlscols = ws1.ncols
    result_str = ''
    #data_firstrow = 0
    for col  in range(1,xlscols):   #忽略第一列，‘序号’
        if ws1.cell(data_firstrow,col).value != None:
            result_str = result_str + ws1.cell(data_firstrow,col).value
            result_str = result_str + ' '
    result_str = result_str[:-1]
    return(result_str)

def catch_xls_order_report_no(xlsfilename,ordernumber):
    # 订单表*工单号*报告编号 ，返回字符串
    print('catch_xls_order_report_no')
    print(xlsfilename)
    print(ordernumber)
    if not (os.path.exists(xlsfilename)):
        return('Error: xlsfilemissing.')
    wb = openworkbook(xlsfilename)
    ws1 = wb.sheet_by_index(0)
    #ws1.cell(worksheetdatarow,col).vlaue
    xlsnrows = ws1.nrows
    sourcecol = 1
    catch_str_col = 3
    data_firstrow = 2
    print('data_firstrow,xlsnrows',data_firstrow,xlsnrows)
    for row  in range(data_firstrow,xlsnrows):
        if ws1.cell(row,sourcecol).value == None:
            continue
        print(ws1.cell(row,sourcecol).value)
        if ws1.cell(row,sourcecol).value == ordernumber:
            result_str = ws1.cell(row,catch_str_col).value
            result_str = result_str.strip()
            return(result_str)
    return('Error: 没有查找到工单号：'+ordernumber)

def get_ProductReport_PrintItem_listval(txtfilename):
    #提取生产报告打印项列表，返回列表
    if not (os.path.exists(txtfilename)):
        return('Error: txtfilename file missing.')
    with open(txtfilename,'r',encoding='gbk') as f:  
        lines = f.readlines()
        save_infomation_step1_enabled = False
        save_infomation_step2_enabled_count = 0
        save_infomation_step3_skiplast = 0
        print_intem_desc_list = []
        for i in range(len(lines)):
            oneline = lines[i]
            if '打印及写磁数据格式描述' in oneline:
                save_infomation_step1_enabled = True
                #print(oneline)
            if save_infomation_step1_enabled:
                #print(oneline)
                if '></' in oneline:
                    save_infomation_step2_enabled_count = 1
            if save_infomation_step2_enabled_count >0:
                if '></' in oneline:
                    onelinelist = oneline.split()
                    print_intem_desc_list.append(onelinelist)
                    save_infomation_step2_enabled_count = 1
                else:
                    save_infomation_step1_enabled =False
                    save_infomation_step2_enabled_count = save_infomation_step2_enabled_count+1
                if save_infomation_step2_enabled_count > 3:
                    #当出现两个非 xml 格式行就跳出循环。
                    break
    return(print_intem_desc_list)

def check_printitem_ep_str_match(pitemlist,epfilename):
    #查找一行字符中，开始符号和中间符号的字符数
    #不对中文处理，含中文字可能有误
    txtfilename = epfilename
    if not (os.path.exists(txtfilename)):
        return('Error: pdftxtfile 文件不存在.')
    printitem_match_list = []
    for printitem_onefull in pitemlist:
        printitem_length = printitem_onefull[3]
        if printitem_length.isdigit():
            temp_item = printitem_onefull[2]
            temp_pos = temp_item.find('><')
            item_first = temp_item[:temp_pos+1]
            item_end = temp_item[temp_pos+1:]
            printitem_match_list.append([item_first,item_end,int(printitem_length)])
    epfilesize = os.path.getsize(txtfilename)
    print(epfilesize)
    if epfilesize > 1024*1024:
        with open(txtfilename,'r',encoding='gbk') as f:  #打开文件
            for i in range(5):
                onelinefirst = f.readline()  #读第5行
            onelinefirst = f.readline()       #读第六行
        print(onelinefirst[:20])
        filesize = epfilesize
        blocksize = 1024 * 50
        dat_file = open(txtfilename, 'r',encoding='gbk')
        lines = []
        if filesize > blocksize:
            maxseekpoint = (filesize // blocksize)#" / "就表示 浮点数除法，返回浮点结果;" // "表示整数除法
            maxseekpoint -= 1 
            dat_file.seek(maxseekpoint * blocksize)
            lines = dat_file.readlines()
            while((len(lines)<3)) | ((len(lines)>=3)&(lines[1]==b'\r\n')):
                #因为在Windows下，所以是b'\r\n'
                #如果列表长度小于2，或者虽然长度大于等于2，但第二个元素却还是空行
                #如果跳出循环，那么lines长度大于等于2，且第二个元素肯定是完整的行
                maxseekpoint -= 1 
                dat_file.seek(maxseekpoint * blocksize)
                lines  = dat_file.readlines()  
            onelinelast = lines[-2]
    else:
        #小文件，打开文件#读取所有行
        with open(txtfilename,'r',encoding='gbk') as f:  
            lines = f.readlines()                        
        onelinefirst=lines[5]    
        onelinelast=lines[-2]
    
    #获取匹配行首行
    matchContent = ''
    for match_printitem_one in printitem_match_list:
        startstring = match_printitem_one[0]
        endstring = match_printitem_one[1]
        pistringlen = match_printitem_one[2]
        startpos = onelinefirst.find(startstring)
        endpos = onelinefirst.find(endstring)
        print(startstring,endstring)
        if (startpos < 0) or (endpos < 0):
            return -1
        templen1 = endpos-startpos -len(startstring)
        if templen1 != pistringlen:
            return('Error 字符串长度检查不匹配 '+startstring+' 出错.')
        else:
            print('Match:' + startstring)
            matchContent = matchContent + startstring
    #获取匹配行末行
    for match_printitem_one in printitem_match_list:
        startstring = match_printitem_one[0]
        endstring = match_printitem_one[1]
        pistringlen = match_printitem_one[2]
        startpos = onelinelast.find(startstring)
        endpos = onelinelast.find(endstring)
        print(startstring,endstring)
        if (startpos < 0) or (endpos < 0):
            return -1
        templen1 = endpos-startpos -len(startstring)
        if templen1 != pistringlen:
            return('Error 字符串长度检查不匹配 '+startstring+' 出错.')
        else:
            print('Match:' + startstring)
           
    return ('匹配正确，'+matchContent+'字符串长度相符。')

def check_printList_EP_match(pitemlist,epfilename,xlsfilename):
    #核对打印列表各项数据，检查EP文件，对应项，打印列表内容添加pitem尖括号
    #比对具体字符，可处理中文字符
    txtfilename = epfilename
    if not (os.path.exists(txtfilename)):
        return('Error: pdftxtfile 文件不存在.' + txtfilename)
    if not (os.path.exists(xlsfilename)):
        return('Error: xlsfile 文件不存在.' + xlsfilename)
    printitem_match_list = []
    for printitem_onefull in pitemlist:
        #获取<XM></XM>类的字符串以便套入相应值，不排除 ’不定长‘ 项。
        printitem_length = printitem_onefull[3]
        temp_item = printitem_onefull[2]
        temp_pos = temp_item.find('><')
        item_first = temp_item[:temp_pos+1]
        item_end = temp_item[temp_pos+1:]
        printitem_match_list.append([item_first,item_end,printitem_length])
    print(printitem_match_list)
    #获取最前一行 最后一行数据 字符串
    epfilesize = os.path.getsize(txtfilename)
    print(epfilesize)
    if epfilesize > 1024*1024:
        with open(txtfilename,'r',encoding='gbk') as f:  #打开文件
            for i in range(5):
                onelinefirst = f.readline()  #读第5行
            onelinefirst = f.readline()       #读第六行
        print(onelinefirst[:20])
        filesize = epfilesize
        blocksize = 1024 * 50
        dat_file = open(txtfilename, 'r',encoding='gbk')
        lines = []
        if filesize > blocksize:
            maxseekpoint = (filesize // blocksize)#" / "就表示 浮点数除法，返回浮点结果;" // "表示整数除法
            maxseekpoint -= 1 
            dat_file.seek(maxseekpoint * blocksize)
            lines = dat_file.readlines()
            while((len(lines)<3)) | ((len(lines)>=3)&(lines[1]==b'\r\n')):
                #因为在Windows下，所以是b'\r\n'
                #如果列表长度小于2，或者虽然长度大于等于2，但第二个元素却还是空行
                #如果跳出循环，那么lines长度大于等于2，且第二个元素肯定是完整的行
                maxseekpoint -= 1 
                dat_file.seek(maxseekpoint * blocksize)
                lines  = dat_file.readlines()  
            onelinelast = lines[-2]
    else:
        #小文件，打开文件#读取所有行
        with open(txtfilename,'r',encoding='gbk') as f:  
            lines = f.readlines()                        
        onelinefirst=lines[5]    
        onelinelast=lines[-2]
    #获取匹配行首行
    wb = openworkbook(xlsfilename)
    ws1 = wb.sheet_by_index(0)
    xlsnrows = ws1.nrows
    xlsncols = ws1.ncols
    xlsfirstrow = 1
    for i in range(1,xlsncols-1):
        temp_str1 = ws1.cell(xlsfirstrow,i).value
        print(printitem_match_list,'xlsncols',xlsncols)
        temp_list = printitem_match_list[i - 1]
        if temp_list[0]== '<BankCardNo>':
            temp_str1 = temp_str1.replace(' ','')
        if temp_list[0]== '<SHBZHM>':
            SHBZHM = temp_str1

        search_str1 = temp_list[0]+temp_str1+temp_list[1]
        print(search_str1)
        startpos = onelinefirst.find(search_str1)
        if startpos>0 :
            print('catched pos:',startpos)
            #print(search_str1)
        else:
            return('Error 查找不到 '+search_str1+' 出错.')
    #检查jpg照片项
    temp_str1 = ws1.cell(xlsfirstrow,xlsncols-1).value
    #temp_list = printitem_match_list[xlsncols - 1]         #照片无需添加<>尖括号
    search_str1 = temp_str1
    print('照片',search_str1)
    startpos = onelinefirst.find(search_str1)
    if startpos>0 :
        print('catched pos:',startpos)
        print(search_str1)
    else:
        return('Error 查找不到 '+search_str1+' 出错.')
    #获取匹配行末行
    print('xlsnrows',xlsnrows)
    for i in range(1,xlsncols-1):
        temp_str1 = ws1.cell(xlsnrows-1,i).value
        temp_list = printitem_match_list[i - 1]
        if temp_list[0]== '<BankCardNo>':
            temp_str1 = temp_str1.replace(' ','')
        if temp_list[0]== '<SHBZHM>':
            SHBZHM = temp_str1
        search_str1 = temp_list[0]+temp_str1+temp_list[1]
        print(search_str1)
        startpos = onelinelast.find(search_str1)
        if startpos>0 :
            print('catched pos:',startpos)
            #print(search_str1)
        else:
            return('Error 查找不到 '+search_str1+' 出错.')
    #检查jpg照片项
    temp_str1 = ws1.cell(xlsnrows-1,xlsncols-1).value
    search_str1 = temp_str1
    startpos = onelinelast.find(search_str1)
    if startpos>0 :
        print('catched pos:',startpos)
        print(search_str1)
    else:
        return('Error 查找不到 '+search_str1+' 出错.')
    return ('匹配正确，社会保障号码'+SHBZHM+' 各项内容相符。')

def check_zip_pwd(zipfilename, checkpwd):
    #验证zip加压缩密码
    if not (os.path.exists(zipfilename)):
        return('Error: pdftxtfile 文件不存在.' + zipfilename)
    print('zipfile:',zipfilename)
    cmdstr = '7za t -p' + checkpwd + ' '+zipfilename
    return_code = subprocess.call(cmdstr, shell=True)
    print('return_code',return_code)
    return (return_code)

def ech_printlist_title_xls2xml(xlsfilename,tempdir):
    #获取打印列表printlist excel 文件 打印页眉
    if not (os.path.exists(xlsfilename)):
        return('Error: xls2xlsxzip 文件不存在.' + xlsfilename)
    shutil.copy(xlsfilename,tempdir)
    print('xls2xlsxzip:',xlsfilename)
    convertfilename = os.path.join(tempdir,os.path.basename(xlsfilename))
    xlsxfilename = os.path.join(tempdir,os.path.basename(xlsfilename)+'x')
    cmdstr = 'xls2xlsxzip ' + convertfilename
    return_code = subprocess.call(cmdstr, shell=True)
    if not (os.path.exists(xlsxfilename)):
        return('Error: xls2xlsx Excel文件转换失败.' + xlsfilename)
    zipfilename = xlsxfilename.replace('.xlsx','.zip')
    os.rename(xlsxfilename,zipfilename)
    cmdstr = '7za e -y '+ zipfilename +' xl\worksheets\sheet1.xml -o'+tempdir
    return_code = subprocess.call(cmdstr, shell=True)
    return ('正常返回: return_code: '+str(return_code))

def get_xmlfile_sheet_title_value(tempdir):
    #从xml文件提取页眉
    xmlfilename = os.path.join(tempdir,'sheet1.xml')
    if not (os.path.exists(xmlfilename)):
        return('Error: xmlfilename 文件不存在.' + xmlfilename)
    print('xmlfilename:',xmlfilename)
    # 使用minidom解析器打开 XML 文档
    xmlparse = xml_parse(xmlfilename)
    collection = xmlparse.documentElement
    # 在集合中获取所有电影
    movies = collection.getElementsByTagName("oddHeader")
    movie = movies[0]
    movie_value = movie.childNodes[0].data
    return (movie_value)


def set_logging(base_dir):
    ##设置日志文件配置参数
    ##设置全局logger
    global logger
    logger = getLogger('balance_logger')
    args=datetime.datetime.now().strftime('%Y%m%d_%H%M%S.log')
    handler = RotatingFileHandler('日志记录'+args, maxBytes=5*1024*1024, backupCount=6)
    handler.suffix = "%Y-%m-%d %H-%M-%S.log"
    logger.setLevel(INFO)
    logger.addHandler(handler)
    formatter = Formatter('%(asctime)-12s %(filename)s %(lineno)d %(message)s')
    handler.setFormatter(formatter)

#定义类，脚本主要更能
class App():
    def __init__(self, master):

        self.master = master
        self.svar_tips = StringVar()
        self.svar_file_detail_tips = StringVar() 
        self.customerlist = []
        self.sourcedir = ''
        self.sortingdir = ''
        self.tempdir = ''
        self.product_report = ''
        self.customer_sname = ''
        self.targetdir = ''
        self.label_tips = Label()
        self.label_author = ''
        self.filesymbol = ''
        self.savefilename = ''
        self.btn_download_init = None #Button()
        self.btn_app_exit_init = None
        self.file_detail_tips = []
        self.scr_history_have_clean = False
        self.initWidgets(master)
        self.master.bind( '<Configure>', self.onFormEvent )

    # 程序主gui界面。
    def initWidgets(self, fm1):

        base_dir=os.path.dirname(__file__)
        cp = ConfigParser()
        cp.read('配置文件.ini', encoding='gbk')
        #cp.read(base_dir+'\\配置文件.ini', encoding='gbk')
        #try:
        #self.ftpremotedir  = cp.get('F配置', 'ftpremotedir')
        temp_str = cp.get('JC配置', 'customer')
        temp_customer_list = temp_str.split('|!|')
        temp_str = cp.get('JC配置', 'dxhppwd')
        self.dxhppwd_list = temp_str.split('|!|')

        for i in range(0,len(temp_customer_list)):
            one_customer_list = [temp_customer_list[i]]
            temp_curtomer = temp_customer_list[i]
            temp_str = cp.get(temp_curtomer, 'working')
            temp_verify =  temp_str.split('|!|')
            one_customer_list.append(temp_verify)
            temp_str = cp.get(temp_curtomer, 'sourcedir')
            one_customer_list.append(temp_str)
            temp_str = cp.get(temp_curtomer, 'sortingdir')
            one_customer_list.append(temp_str)
            temp_str = cp.get(temp_curtomer, 'tempdir')
            one_customer_list.append(temp_str)
            
            for j in range(1,int(one_customer_list[1][1])+1):
                cfstr = 'rawverify' + str(j)
                temp_str = cp.get(temp_curtomer, cfstr)
                temp_verify =  temp_str.split('|!|')
                one_customer_list.append(temp_verify)

            for j in range(1,int(one_customer_list[1][2])+1):
                cfstr = 'checkpoint' + str(j)
                temp_str = cp.get(temp_curtomer, cfstr)
                temp_verify =  temp_str.split('|!|')
                one_customer_list.append(temp_verify)
            self.customerlist.append(one_customer_list)
        logger.info('配置读取结果:')
        logger.info(self.customerlist)
                
        self.label_author = Label(fm1, text='it•流程与信息化部•东信和平 June,2021', font=('宋体', 9))
        #label_author.place(x=814, y=877)

        self.btn_download_init = Button(fm1, text='  检  测  ', command=self.command_download_btn_run)
        #self.btn_download_init.place(x=929, y=100)

        self.btn_app_exit_init = Button(fm1, text='  退  出  ', command=self.command_btn_exit)
        #btn_app_exit_init.place(x=929, y=270)

        self.sbar_lr = Scrollbar(fm1,width=20)

        self.var_combobox = StringVar()
        self.combobox = ttk.Combobox(fm1, textvariable=self.var_combobox)
        self.combobox['value'] = temp_customer_list  #('python', 'java', 'C', 'C++')
        self.combobox.current(0)
        self.combobox.update
        #self.combobox.pack(padx=15, pady=10)
        self.combobox.place(x=870, y=10)

        self.style = Style()
        aktualTheme = self.style.theme_use()
        self.style.theme_create("dummy", parent=aktualTheme)
        self.style.theme_use("dummy")

        self.list_treeview = Treeview(fm1, columns=('F1', 'F2','F3'), show='headings',height=41)
        
        self.list_treeview.heading('F1', text='序号')
        self.list_treeview.heading('F2', text='内容')
        self.list_treeview.heading('F3', text='状态')
        self.list_treeview.column(0, width=40, stretch=True)
        self.list_treeview.column(1, width=930, stretch=True)
        self.list_treeview.column(2, width=40, stretch=True)

        self.y_scollbar = Scrollbar(fm1, orient=VERTICAL)
        self.x_scollbar = Scrollbar(fm1, orient=HORIZONTAL)

        self.list_treeview['yscroll'] = self.y_scollbar.set 
        self.list_treeview['xscroll'] = self.x_scollbar.set 
        #self.list_treeview.grid(row = 0, column = 0, sticky = NSEW) 
        #self.list_treeview.winfo_screenwidth()
        #self.list_treeview.pack()

        self.list_treeview.tag_configure('odd', background='#E6B3FF')
        self.list_treeview.tag_configure('even', background='yellow', foreground='red')
        self.list_treeview.tag_configure('R', background='yellow', foreground='red', font='Arial 11')
        self.list_treeview.tag_configure('G', background='white', font=('Arial', 9))

        #selectmode list多选模式multiple
        self.list_treeview.place(x=30, y=33)

        self.list_treeview.insert('', END, values=(str(1),'待检测',"Pass"), tags = ('even', 'A10'))


        self.sbar_lr.config(command=self.list_treeview.yview)                
        self.sbar_lr.pack(side=LEFT, fill=Y)                     
        self.sbar_lr.pack(padx=10,pady=10)

        sourcedir = self.customerlist[0][2]
        str_tips = '待检文件夹:' + sourcedir
        self.label_tips = Label(textvariable=self.svar_tips, font=('Arial', 11))
        
        self.label_tips.place(x=30, y=7)
        self.label_tips.config(fg='green')
        self.svar_tips.set(str_tips)
        
    def command_btn_exit(self):
        # 退出键
        try:
            for i in range(0,1): #len(self.customerlist)):
                tempj = self.customerlist[i]
                verifyfiles = []
                working_items = tempj[1]
                sourcedir = tempj[2]
                sortingdir = tempj[3]
                tempdir = tempj[4]
                logger.info(tempdir)
                if os.path.exists(tempdir):
                    shutil.rmtree(tempdir)
                os.makedirs(tempdir)
        except:
            self.master.destroy()    
        self.master.destroy()

    def run_main_fresh(self):
        run_main_fresh_begin_time = datetime.datetime.now()
        str_tips = str(run_main_fresh_begin_time.strftime('%Y-%m-%d %H:%M:%S'))
        str_tips = '检测开始：' + str_tips +'...'
        self.svar_tips.set(str_tips)

        dir_list = []
        file_list  =[]
        self.file_detail_tips = []
        obj = self.list_treeview.get_children()  # 获取所有对象
        for o in obj:
            self.list_treeview.delete(o)  # 删除对象

        try:
            #从配置文件提取待校验文件名和类型
            for i in range(0,1): #len(self.customerlist)):
                tempj = self.customerlist[i]
                verifyfiles = []
                working_items = tempj[1]
                sourcedir = tempj[2]
                sortingdir = tempj[3]
                tempdir = tempj[4]
                logger.info(tempdir)
                if os.path.exists(tempdir):
                    shutil.rmtree(tempdir)
                os.makedirs(tempdir)

                for j in range(5,5+int(working_items[1])):   #verify file pos 5 to 14
                    tempk = tempj[j]
                    print('tempk:',tempk)
                    tempm = tempk[0]
                    #print('tempm:',tempm)
                    if not tempm == '':
                        tempn = tempk[1]
                        product_report_fullname =  catchfilefullname(sourcedir,tempn)
                        logger.info('查找文件:' + tempm)
                        logger.info(product_report_fullname)
                        if product_report_fullname == -1:
                            self.list_treeview.insert('', END, values=('0',tempm +' 查找无此文件.','错误'), tags = ('R'))
                            product_report_fullname = ''
                        else:
                            temp_str = '查找：' + tempm + ' = ' + os.path.basename(product_report_fullname)
                            logger.info(temp_str)
                            #self.list_treeview.insert('', END, values=('0',temp_str,'ready'), tags = ('G'))
                        
                        if len(product_report_fullname) > 4:
                            if product_report_fullname[-4:] == '.pdf':
                                temp_filename = os.path.join(tempdir,os.path.basename(product_report_fullname))
                                temp_filename = temp_filename[:-4] + '.txt'
                                logger.info('convert_pdf_to_txt')
                                logger.info(product_report_fullname)
                                if '生产报告' in product_report_fullname:
                                    result_str =  convert_pdf_to_txt_scbg(product_report_fullname,temp_filename)
                                else:
                                    result_str =  convert_pdf_to_txt(product_report_fullname,temp_filename)
                                if '正常返回' in result_str:
                                    self.list_treeview.insert('', END, values=('-','解析PDF文件: ' + os.path.basename(product_report_fullname),'Pass'), tags = ('G'))

                                else:
                                    self.list_treeview.insert('', END, values=('-','无法解析PDF文件: ' + os.path.basename(product_report_fullname),'错误'), tags = ('R'))
                                product_report_fullname = temp_filename
                        verifyfiles.append([tempm,tempn,product_report_fullname])
                        #若为pdf文件，用转换后的txt替代

                logger.info('待校验文件清单verifyfiles')
                logger.info(verifyfiles)

                logger.info(tempj)
                for j in range(5+int(working_items[1]),5+int(working_items[1])+int(working_items[2])):   #check point pos 15 to 25
                    tempk = tempj[j]
                    logger.info('tempk:')
                    logger.info(tempk)
                    cpstr = tempk[0]
                    if cpstr == '':
                        break
                    else:
                        if cpstr == 'ErrorFile':
                            temp_str = tempk[1]
                            temp_int = int(temp_str) -1
                            temp_list = verifyfiles[temp_int]
                            comparefile1 = temp_list[2]
                            if os.path.exists(comparefile1):
                                tempErrorFileSize = os.path.getsize(comparefile1)
                                if tempErrorFileSize == 0:
                                    self.list_treeview.insert('', END, values=('1','Error.txt 文件大小为 0.','Pass'), tags = ('G'))
                                else:
                                    temp_str = os.path.basename(comparefile1)
                                    self.list_treeview.insert('', END, values=('1',temp_str + ' 文件大小为' + str(tempErrorFileSize),'错误'), tags = ('R'))
                                    logger.info(comparefile1 + ' 文件大小为' + str(tempErrorFileSize))
                            else:
                                self.list_treeview.insert('', END, values=('1','查找Error.txt文件，无此文件','错误'), tags = ('R'))
                                logger.info('查找Error文件，无此文件')
                            self.list_treeview.update()

                        elif cpstr == 'DataForm':
                            temp_str = tempk[1]
                            temp_int = int(temp_str) -1
                            temp_list = verifyfiles[temp_int]
                            comparefile1 = temp_list[2]
                            logger.info('读取数据单DataForm')
                            #因有两个同名‘数据单’，需筛选出在分发文件夹的‘数据单’
                            comparefile1 = catchfilefullnameindir(sourcedir,'数据单','分发')
                            logger.info(comparefile1)
                            data_form_list =  get_Data_Form_listval(comparefile1)
                            logger.info('读取数据单,获订单下单数量，描述，ep文件列表等内容')
                            logger.info(data_form_list)
                            kehu = data_form_list[0]
                            logger.info('匹配客户名称')
                            logger.info(kehu)
                            if kehu in comparefile1:
                                self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'数据单客户:'+kehu+' 名称匹配.','Pass'), tags = ('G'))
                            else:
                                self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'数据单客户:'+kehu+' 名称不匹配.','错误'), tags = ('R'))
                            try:
                                dingdanshuliang = data_form_list[2]
                                logger.info('匹配订单数量')
                                logger.info(dingdanshuliang)
                                dingdanshuliang_str = dingdanshuliang[:-1]#订单数量 去 ’万‘ 字
                                dingdanshuliang = int(float(dingdanshuliang_str)*10000)
                                logger.info(dingdanshuliang)

                                xiafashuliang = data_form_list[3]
                                logger.info('匹配下发数量')
                                logger.info(dingdanshuliang)
                                xiafashuliang_str = xiafashuliang[:-1]#下单数量 去 ’万‘ 字
                                xiafashuliang = int(float(xiafashuliang_str)*10000)
                                logger.info(xiafashuliang)
                            except:
                                self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'Error.订单下单数值有误.程序出错','错误'), tags = ('R'))
                            if dingdanshuliang != xiafashuliang:
                                yi_chang_return_str = get_xlsfile_nrow(sourcedir,'异常反馈表')
                                if '正常返回' in yi_chang_return_str:
                                    yi_chang_fan_kui_biao_nrows_str = yi_chang_return_str[5:]
                                    yi_chang_fan_kui_biao_nrows = int(yi_chang_fan_kui_biao_nrows_str) -1
                                    if yi_chang_fan_kui_biao_nrows == dingdanshuliang - xiafashuliang:
                                        self.list_treeview.insert('', END, values=('-','订单数量:'+str(dingdanshuliang)+' 与下单数量:'+str(xiafashuliang)+\
                                            '不相同.异常反馈表:'+str(yi_chang_fan_kui_biao_nrows),'Pass'), tags = ('G'))
                                    else:
                                        self.list_treeview.insert('', END, values=('-','订单数量:'+str(dingdanshuliang)+' 与下单数量:'+str(xiafashuliang)+\
                                            '不相同.异常反馈表:'+str(yi_chang_fan_kui_biao_nrows),'Pass'), tags = ('R'))
                                else:
                                    self.list_treeview.insert('', END, values=('-','订单数量:'+str(dingdanshuliang)+' 与下单数量:'+str(xiafashuliang)+'不相同.'+yi_chang_return_str,'Pass'), tags = ('R'))

                            #数据表中EPmdbxls文件列表下单数量合计 与 表头下单数据 核对
                            ep_wenjian_liebiao = data_form_list[8]  #8,第9，ep文件列表
                            ep_mdb_xls_liebiao_fullname = []
                            sum_xiadan = 0
                            ep_mdb_xls_filelist = []
                            for ep_wenjian_i in ep_wenjian_liebiao:
                                sum_xiadan = sum_xiadan  + ep_wenjian_i[3]
                                #将ep列表中的文件转为 含路径的 文件名
                                ep_wenjian_basename = ep_wenjian_i[1]
                                ep_wenjian_onefile_shuliang = ep_wenjian_i[3]
                                logger.info('ep_mdb_xls_filelist:\n ep_wenjian_basename')
                                logger.info(ep_wenjian_basename)
                                ep_mdb_xls_filelist =  catchepmdbxls_filelist_form_ep(sourcedir,ep_wenjian_basename,ep_wenjian_onefile_shuliang)
                                logger.info(ep_mdb_xls_filelist)
                                if ep_mdb_xls_filelist == -1:
                                    self.list_treeview.insert('', END, values=('-','数据单EPmdbxls文件列表对应mdb*xls:'+str(ep_wenjian_basename)+' 找无此文件.','错误'), tags = ('R'))
                                else:
                                    ep_mdb_xls_liebiao_fullname.append(ep_mdb_xls_filelist)
                                    if ep_wenjian_onefile_shuliang > 240:
                                        str_fendan_filename_digest = catch_ep_cutting_form_ep(sourcedir,ep_wenjian_basename,ep_wenjian_onefile_shuliang)
                                        logger.info(str_fendan_filename_digest)
                                        if int(ep_wenjian_onefile_shuliang//240)+1 == str_fendan_filename_digest.count('_'):
                                            self.list_treeview.insert('', END, values=('-','EP文件:'+str(ep_wenjian_basename)+' 分单文件：' + str(str_fendan_filename_digest)+ ' 数量:' + str(int(ep_wenjian_onefile_shuliang//240)+1),'Pass'), tags = ('G'))
                                        else:
                                            self.list_treeview.insert('', END, values=('-','EP文件:'+str(ep_wenjian_basename)+' 分单文件：' + str(str_fendan_filename_digest)+ ' 数量:' + str(int(ep_wenjian_onefile_shuliang//240)+1),'错误'), tags = ('R'))
                            if sum_xiadan == xiafashuliang:
                                self.list_treeview.insert('', END, values=('-','下发数量:'+str(xiafashuliang)+' ep文件数据数量匹配.','Pass'), tags = ('G'))
                            else:
                                self.list_treeview.insert('', END, values=('-','下发数据:'+str(xiafashuliang)+' ep文件数据数量不匹配.','错误'), tags = ('R'))
                            #在数据格式栏中查找是否有相应数据长度值
                            shuju_geshi_shuju_changdu = data_form_list[4]
                            logger.info('在数据格式栏中查找是否有相应数据长度值SMC_Len_value_str/shuju_geshi_shuju_changdu')
                            logger.info(SMC_Len_value_str)
                            logger.info(shuju_geshi_shuju_changdu)

                            if SMC_Len_value_str in shuju_geshi_shuju_changdu:
                                self.list_treeview.insert('', END, values=('','数据表数据格式数据长度:'+SMC_Len_value_str+' 数值匹配.','Pass'), tags = ('G'))
                            else:
                                self.list_treeview.insert('', END, values=('','数据表数据格式数据长度:'+' 数值不匹配.','错误'), tags = ('R'))
                            self.list_treeview.update()
                            

                        elif cpstr == 'TaskOrderProReport':
                            logger.info('TaskOrderProReport')
                            temp_str = tempk[1]
                            temp_int = int(temp_str) -1
                            temp_list = verifyfiles[temp_int]
                            comparefile1 = temp_list[2]
                            logger.info(temp_list)
                            temp_str = tempk[2]
                            temp_int = int(temp_str) -1
                            temp_list = verifyfiles[temp_int]
                            comparefile2 = temp_list[2]
                            logger.info(temp_list)
                            #对比生产任务单需求文档编号 = 生产报告产品规格编号
                            comparevalue1 =  catch_pdf_string_val(comparefile1,'ProjectCode')
                            comparevalue2 =  catch_pdf_string_val(comparefile2,'产品规格编号')
                            logger.info('comparevalue 1, 2')
                            logger.info(comparevalue1)
                            logger.info(comparevalue2)
                            if comparevalue1 == comparevalue2:
                                self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'生产任务单*ProjectCode 与 生产报告*产品规格编号 相同: ' + str(comparevalue1),'Pass'), tags = ('G'))
                            else:
                                self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'生产任务单*ProjectCode 与 生产报告*产品规格编号 不同: ' + str(comparevalue1),'错误'), tags = ('R'))
                            #对比生产任务单 应用要求 = 生产报告产 产品名称
                            comparevalue1 =  catch_pdf_string_val(comparefile1,'ApplicantDemand')
                            comparevalue2 =  catch_pdf_string_val(comparefile2,'产品名称')
                            logger.info('comparevalue 1, 2')
                            logger.info(comparevalue1)
                            logger.info(comparevalue2)
                            if comparevalue1 == comparevalue2:
                                self.list_treeview.insert('', END, values=('-','生产任务单*ApplicantDemand 与 生产报告*产品名称 相同: ' + str(comparevalue1),'Pass'), tags = ('G'))
                            else:
                                self.list_treeview.insert('', END, values=('-','生产任务单*ApplicantDemand 与 生产报告*产品名称 不同: ' + str(comparevalue1),'错误'), tags = ('R'))


                        elif cpstr == 'TaskOrderOrderProReport':
                            logger.info('TaskOrderOrderProReport')
                            temp_str = tempk[1]                 #文件1
                            temp_int = int(temp_str) -1
                            temp_list = verifyfiles[temp_int]
                            comparefile1 = temp_list[2]
                            logger.info(comparefile1)
                            temp_str = tempk[2]                 #文件2
                            temp_int = int(temp_str) -1
                            temp_list = verifyfiles[temp_int]
                            comparefile2 = temp_list[2]
                            logger.info(comparefile2)
                            temp_str = tempk[3]                 #文件3
                            temp_int = int(temp_str) -1
                            temp_list = verifyfiles[temp_int]
                            comparefile3 = temp_list[2]
                            logger.info(comparefile3)

                            comparevalue1 =  catch_pdf_string_val(comparefile1,'ProductOrderNo')
                            ProductOrderNo_value = comparevalue1
                            logger.info('comparevalue1, 2, 3')
                            logger.info(comparevalue1)
                            if 'Error' in comparevalue1:
                                self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'生产任务单*工单号*查找失败: ' + str(comparevalue1),'错误'), tags = ('R'))
                            else:
                                comparevalue2 = catch_xls_order_report_no(comparefile2,comparevalue1)
                                logger.info(comparevalue2)
                                if 'Error' in comparevalue2:
                                    self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'订单表*工单号*报告编号*查找失败: ' + str(comparevalue1),'错误'), tags = ('R'))
                                else:
                                    comparevalue3 =  catch_pdf_string_val_shengchanbaogao(comparefile3,'生产报告编号')
                                    #特殊处理 查找pdf 转txt 错位问题
                                    logger.info(comparevalue3)
                                    if 'Error' in comparevalue3:
                                        self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'生产报告*生产报告编号*查找失败: ' + str(comparevalue1),'错误'), tags = ('R'))
                                    else:
                                        if comparevalue2 == comparevalue3:
                                            self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'生产任务单*工单号 - 订单表*工单号*报告编号 - 生产报告*生产报告编号 相同: ' + str(comparevalue3),'Pass'), tags = ('G'))
                                        else:
                                            self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'生产任务单*工单号 - 订单表*工单号*报告编号 - 生产报告*生产报告编号 不同: ' + str(comparevalue3),'错误'), tags = ('R'))
                            self.list_treeview.update()

                        elif cpstr == 'PersonalizationPrintItem':
                            logger.info('PersonalizationPrintItem')
                            temp_str = tempk[1]                 #生产任务单
                            temp_int = int(temp_str) -1
                            temp_list = verifyfiles[temp_int]
                            comparefile1 = temp_list[2]
                            logger.info(comparefile1)

                            comparevalue1 =  catch_pdf_string_multilines(comparefile1,'PersonalizationDemand1')
                            logger.info('PersonalizationPrintItem comparevalue 1, 2')
                            logger.info(comparevalue1)
                            temp_str = comparevalue1
                            try:
                                temp_pos1 = temp_str.index('（')
                                temp_pos2 = temp_str.index('）')
                                temp_pos3 = temp_str.index('分隔方式')
                            except:
                                comparevalue1 = 'Error: 个人化要求没有找到括号（）.'
                            temp_str_personal = temp_str[temp_pos1+1:temp_pos2]
                            logger.info(temp_str_personal)
                            temp_str_personal= temp_str_personal.replace('和','、')
                            temp_str_personal= temp_str_personal.replace('相片','照片')
                            temp_str_personal= temp_str_personal.replace('、',' ')
                            comparevalue1path1 = temp_str_personal
                            logger.info(comparevalue1path1)
                            separate_mathod = ''
                            for temp_i in range(temp_pos3+4,temp_pos3+16):    #分隔方式
                                if temp_str[temp_i].isdigit() or temp_str[temp_i]=='/':
                                    separate_mathod = separate_mathod + temp_str[temp_i]
                                else:
                                    break
                            logger.info('separate_mathod')
                            logger.info(separate_mathod)
                            for temp_ep_level_list in ep_mdb_xls_liebiao_fullname:      #可能有多个ep文件及对应mdb xls
                                temp_list = temp_ep_level_list[1]                       #对应mdb
                                logger.info('mdb file list')
                                logger.info(temp_list)
                                if len(temp_list) > 2:
                                    self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'ep文件对应多于2个mdb文件。' ,'错误'), tags = ('R'))
                                    logger.info('ep文件对应多于2个mdb文件。')
                                elif len(temp_list) == 2:
                                    wu_ren_xiang = False
                                    for temp_str in temp_list:
                                        if '无人像' in temp_str:
                                            wu_ren_xiang = True
                                        else:
                                            mdb_normal_file = temp_str
                                    if not wu_ren_xiang :
                                        self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'ep文件对应2个mdb文件，缺无人像文件。' ,'错误'), tags = ('R'))
                                        logger.info('ep文件对应2个mdb文件，缺无人像文件。')
                                else:
                                    mdb_normal_file = temp_list[0]
                                temp_list = temp_ep_level_list[2]                       #对应xls
                                logger.info('xls file list')
                                logger.info(temp_list)
                                mdb_basename = os.path.basename(mdb_normal_file)
                                xls_basename = mdb_basename.replace('mdb','xls')
                                xls_normal_file = ''
                                for temp_str in temp_list:
                                    if xls_basename in temp_str:
                                        xls_normal_file = temp_str
                                if xls_basename == '':
                                    self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'ep文件对应mdb文件，缺xls文件。' ,'错误'), tags = ('R'))
                                    logger.info('ep文件对应mdb文件，缺xls文件。')
                                else:
                                    self.list_treeview.insert('', END, values=('-','文件ep,mdb,xls对应 正常: ' + str(mdb_normal_file),'Pass'), tags = ('G'))
                                comparevalue2 = catch_xls_oneline (xls_normal_file,0)      #读第0行数据
                                logger.info(comparevalue2)
                                if 'Error' in comparevalue2:
                                    self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'xls文件*失败: ' + str(xls_basename),'错误'), tags = ('R'))
                                    logger.info('xls文件*失败: ')
                                else:
                                    if comparevalue2 == comparevalue1path1:
                                        self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'印刷个人信息与xls对应相同: ' + str(comparevalue2),'Pass'), tags = ('G'))
                                        logger.info('印刷个人信息与xls对应相同: ' + str(comparevalue2))
                                    else:
                                        self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'印刷个人信息与xls对应不同: ' + str(comparevalue2),'错误'), tags = ('R'))
                                        logger.info('印刷个人信息与xls对应不同:')

                                comparevalue3 =  catch_xls_onecell_value(xls_normal_file,'银行卡号')
                                logger.info(comparevalue3)
                                if 'Error' in comparevalue3:
                                    self.list_treeview.insert('', END, values=('-','卡号分隔方式读取打印列表出错: ' + str(comparevalue3),'错误'), tags = ('R'))
                                else:
                                    separate_mathod_list1 = separate_mathod.split('/')
                                    separate_mathod_list2 = comparevalue3.split(' ')
                                    logger.info(separate_mathod_list1)
                                    logger.info(separate_mathod_list2)
                                    for i in range(0,len(separate_mathod_list1)):
                                        if int(separate_mathod_list1[i]) == len(separate_mathod_list2[i]):
                                            separate_isok = 'OK'
                                        else:
                                            separate_isok = 'Error'
                                    if separate_isok == 'OK':
                                        self.list_treeview.insert('', END, values=('-','卡号分隔方式 相符: ' + str(comparevalue3) + '==' +separate_mathod,'Pass'), tags = ('G'))
                                    else:
                                        self.list_treeview.insert('', END, values=('-','卡号分隔方式 不相符: ' + str(comparevalue3),'错误'), tags = ('R'))
                                        
                                    self.list_treeview.update()
                                    printlist_title_ech = ech_printlist_title_xls2xml(xls_normal_file, tempdir)
                                    logger.info(printlist_title_ech)
                                    if 'Error' in printlist_title_ech:
                                        self.list_treeview.insert('', END, values=('-',printlist_title_ech,'错误'), tags = ('R'))
                                    
                                    if not os.path.exists(os.path.join(tempdir,'sheet1.xml')):
                                        self.list_treeview.insert('', END, values=('-','打印列表sheet1.xml不存在. ' + str(comparevalue3),'错误'), tags = ('R'))
                                    else:
                                        printlist_title_string = get_xmlfile_sheet_title_value(tempdir)
                                        temp_pos1 = printlist_title_string.index('&C')
                                        temp_pos2 = printlist_title_string.index('&R')
                                        printlist_title_projectname = printlist_title_string[2:temp_pos1]
                                        printlist_title_order_count = printlist_title_string[temp_pos2+2:]
                                        logger.info(printlist_title_string)
                                        if 'Error' in printlist_title_string:
                                            self.list_treeview.insert('', END, values=('-','打印列表xml get title执行错误' + str(comparevalue3),'错误'), tags = ('R'))
                                        else:
                                            if str(dingdanshuliang) in printlist_title_order_count:
                                                self.list_treeview.insert('', END, values=('-','打印列表页眉: ' + printlist_title_projectname+'-'+printlist_title_order_count,'Pass'), tags = ('G'))
                                            else:
                                                self.list_treeview.insert('', END, values=('-','打印列表页眉有误，订单量不符: ' + printlist_title_projectname+'-'+printlist_title_order_count,'错误'), tags = ('R'))
                                    self.list_treeview.update()

                        elif cpstr == 'SMCLenPrintItem':
                            temp_str = tempk[1]
                            temp_int = int(temp_str) -1
                            temp_list = verifyfiles[temp_int]
                            comparefile1 = temp_list[2]

                            comparevalue1 =  catch_pdf_string_val(comparefile1,'SMCLen')
                            if comparevalue1 == 'Error, 没有找到字符串: SMCLen':
                                comparevalue1 =  catch_pdf_string_val(comparefile1,'SMC长度')
                            logger.info('comparevalue1')
                            logger.info(comparevalue1)
                            if 'Error' in comparevalue1:
                                self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'生产报告，提取SMCLen: ' + comparevalue1,'错误'), tags = ('R'))
                            self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'生产报告,提取SMCLen:' + str(comparevalue1),'Pass'), tags = ('G'))
                            #self.catch_,comparefile2)
                            SMC_Len_value_str = str(comparevalue1)   #用户匹配数据单中数据格式的相应值
                            
                            logger.info('提取生产报告打印项列表，返回列表')
                            get_PrintItem_list =  get_ProductReport_PrintItem_listval(comparefile1)
                            logger.info(get_PrintItem_list)
                            self.list_treeview.insert('', END, values=('-','提取生产报告 打印数据项描述:' + str(len(get_PrintItem_list))+'条','Pass'), tags = ('G'))
                            self.list_treeview.update()

                        elif cpstr == 'SMCLenEPs':
                            logger.info('EPmdbxls文件列表ep_mdb_xls_liebiao_fullname')
                            logger.info(ep_mdb_xls_liebiao_fullname )
                            logger.info('SMC_Len_value_str')
                            logger.info(SMC_Len_value_str)
                            for ep_wenjian_batch_epmdbxls  in ep_mdb_xls_liebiao_fullname:
                                ep_wenjian_multi_file = ep_wenjian_batch_epmdbxls[0]    #只提取 ep 文件列表，mdb，xls 文件列表不处理
                                for ep_wenjian_onefile  in ep_wenjian_multi_file:
                                    #logger.info(ep_wenjian_onefile)
                                    ep_wenjian_smcstrlen =  catch_txtfile_string_len(ep_wenjian_onefile,'[SMC]','[ENDSMC]')
                                    ep_wenjian_onefile_basename = os.path.basename(ep_wenjian_onefile)
                                    if ep_wenjian_smcstrlen == SMC_Len_value_str :                        
                                        self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'核对SMCLen: ' + str(ep_wenjian_onefile_basename)+'='+ep_wenjian_smcstrlen,'Pass'), tags = ('G'))
                                        #用户匹配数据单中数据格式的相应值
                                    else:
                                        self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'核对SMCLen: ' + str(ep_wenjian_onefile_basename)+'='+ep_wenjian_smcstrlen,'错误'), tags = ('R'))
                            self.list_treeview.update()

                        elif cpstr == 'PrintItemEP':
                            #生产报告打印标签和长度描述和ep内容是否一致，只检查 第一条 和最后一条
                            logger.info('生产报告打印标签长度描述 与 ep内容是否一致')
                            logger.info(get_PrintItem_list)
                            logger.info(ep_mdb_xls_liebiao_fullname)
                            for ep_wenjian_batch_epmdbxls  in ep_mdb_xls_liebiao_fullname:
                                ep_wenjian_multi_file = ep_wenjian_batch_epmdbxls[0]    #只提取 ep 文件列表，mdb，xls 文件列表不处理
                                for ep_wenjian_onefile  in ep_wenjian_multi_file:
                                    #logger.info(ep_wenjian_onefile)
                                    ep_wenjian_printitem_match =  check_printitem_ep_str_match(get_PrintItem_list,ep_wenjian_onefile)
                                    ep_wenjian_onefile_basename = os.path.basename(ep_wenjian_onefile)
                                    if '匹配正确' in ep_wenjian_printitem_match:                        
                                        self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'核对打印标签项长度: ' + str(ep_wenjian_onefile_basename),'Pass'), tags = ('G'))
                                        self.list_treeview.insert('', END, values=('-',ep_wenjian_printitem_match[5:],'Pass'), tags = ('G'))
                                    else:
                                        self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'核对打印标签项长度: ' + str(ep_wenjian_onefile_basename),'错误'), tags = ('R'))
                            self.list_treeview.update()

                        elif cpstr == 'PrintListEP':
                            #生产报告打印清单内容与ep文件是否一致，只检查 第一条 和最后一条
                            logger.info('生产报告打印清单内容与ep文件是否一致')
                            logger.info(get_PrintItem_list)
                            logger.info(ep_mdb_xls_liebiao_fullname)

                            for ep_wenjian_batch_epmdbxls  in ep_mdb_xls_liebiao_fullname:
                                ep_wenjian_multi_file = ep_wenjian_batch_epmdbxls[0]    #只提取 ep 文件列表，mdb，xls 文件列表不处理
                                xls_wenjian_multi_file = ep_wenjian_batch_epmdbxls[2]   #xls文件组
                                for ep_wenjian_onefile  in ep_wenjian_multi_file:
                                    xls_wenjian_onefile = xls_wenjian_multi_file[0]
                                    #现只处理一个ep文件对应一个xls文件
                                    ep_wenjian_printitem_match =  check_printList_EP_match(get_PrintItem_list,ep_wenjian_onefile,xls_wenjian_onefile)
                                    logger.info(ep_wenjian_printitem_match)
                                    ep_wenjian_onefile_basename = os.path.basename(ep_wenjian_onefile)
                                    logger.info(ep_wenjian_onefile_basename)
                                    if '匹配正确' in ep_wenjian_printitem_match:                        
                                        self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'核对打印标签项内容: ' + str(ep_wenjian_onefile_basename),'Pass'), tags = ('G'))
                                        self.list_treeview.insert('', END, values=('-',ep_wenjian_printitem_match[5:],'Pass'), tags = ('G'))
                                    else:
                                        self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'核对打印标签项内容: ' + str(ep_wenjian_onefile_basename),'错误'), tags = ('R'))
                                        self.list_treeview.insert('', END, values=('-',ep_wenjian_printitem_match,'错误'), tags = ('R'))
                            self.list_treeview.update()

                        elif cpstr == 'PrintListMdb':
                            #核对打印清单内容与mdb文件是否一致，只检查 第一条 和最后一条
                            logger.info('生产报告打印清单内容与mdb文件是否一致')
                            logger.info(get_PrintItem_list)
                            logger.info(ep_mdb_xls_liebiao_fullname)

                            for ep_wenjian_batch_epmdbxls  in ep_mdb_xls_liebiao_fullname:
                                ep_wenjian_multi_file = ep_wenjian_batch_epmdbxls[0]    #ep 文件
                                mdb_wenjian_multi_file = ep_wenjian_batch_epmdbxls[1]   #mdb文件组
                                xls_wenjian_multi_file = ep_wenjian_batch_epmdbxls[2]   #xls文件组
                                value_float_temp = ep_wenjian_batch_epmdbxls[3]   #当个ep文件数据量
                                count_ep_onefile_shuliang_str = str(int(value_float_temp))
                                logger.info('count_ep_onefile_shuliang_str')
                                logger.info(count_ep_onefile_shuliang_str)
                                
                                #for ep_wenjian_onefile  in ep_wenjian_multi_file: 只有一个ep文件
                                ep_wenjian_onefile  = ep_wenjian_multi_file[0]
                                is_wurenxiang_mdb = False
                                if len(mdb_wenjian_multi_file) >1:
                                    is_wurenxiang_mdb =True
                                if is_wurenxiang_mdb:
                                    if '无人像' in mdb_wenjian_multi_file[0]:
                                        mdb_wurenxiang_file = mdb_wenjian_multi_file[0]
                                        mdb_wenjian_onefile = mdb_wenjian_multi_file[1]
                                    else:
                                        mdb_wenjian_onefile = mdb_wenjian_multi_file[0]
                                        mdb_wurenxiang_file = mdb_wenjian_multi_file[1]
                                    temp_str = brackets_catchcontent(mdb_wurenxiang_file)
                                    temp_list = temp_str.split('-')
                                    mdb_wurenxiang_count = int(temp_list[1])
                                    logger.info('mdb_wurenxiang_count')
                                    logger.info(mdb_wurenxiang_count)
                                else:           #无 无人像 文件
                                    mdb_wenjian_onefile = mdb_wenjian_multi_file[0]
                                    mdb_wurenxiang_count = 0

                                xls_wenjian_onefile = mdb_wenjian_onefile.replace('.mdb','.xls')

                                ep_wenjian_printitem_match =  check_PrintList_mdb_val(get_PrintItem_list,xls_wenjian_onefile,mdb_wenjian_onefile)
                                ep_wenjian_onefile_basename = os.path.basename(ep_wenjian_onefile)
                                mdb_check_result_str =ep_wenjian_printitem_match[0-len(count_ep_onefile_shuliang_str):]
                                logger.info('ep_wenjian_printitem_match')
                                logger.info(ep_wenjian_printitem_match)
                                logger.info(mdb_check_result_str)
                                mdb_check_result_str = str(int(mdb_check_result_str)+mdb_wurenxiang_count)
                                logger.info(mdb_check_result_str)
                                if '匹配正确' in ep_wenjian_printitem_match:                        
                                    if mdb_check_result_str == count_ep_onefile_shuliang_str:
                                        self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'核对打印清单内容与mdb文件:相符 无人像='+str(mdb_wurenxiang_count) ,'Pass'), tags = ('G'))
                                        self.list_treeview.insert('', END, values=('-',ep_wenjian_printitem_match[5:],'Pass'), tags = ('G'))
                                    else:
                                        self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'核对打印清单内容与mdb文件:不符'+str(count_ep_onefile_shuliang_str)+'无人像='+str(mdb_wurenxiang_count),'错误'), tags = ('R'))
                                        self.list_treeview.insert('', END, values=('-',ep_wenjian_printitem_match[5:],'错误'), tags = ('R'))
                                else:
                                    self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'核对打印清单内容与mdb文件:不符' + str(ep_wenjian_onefile_basename[:-3])+'无人像='+str(mdb_wurenxiang_count),'错误'), tags = ('R'))
                                    self.list_treeview.insert('', END, values=('-',ep_wenjian_printitem_match,'错误'), tags = ('R'))
                            self.list_treeview.update()

                        elif cpstr == 'SuccessFailurelogCheck':
                            #核查订单目录log文件是否匹配
                            logger.info('success_failure_filecheck')
                            success_failure_filecheck =  Success_Failure_log_filecheck(sourcedir)
                            logger.info(success_failure_filecheck)
                            if '正常返回' in success_failure_filecheck:                        
                                self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'核查订单目录log文件success 错误0，总数量：' + str(success_failure_filecheck[5:]),'Pass'), tags = ('G'))
                                success_count = int(success_failure_filecheck[5:])
                                if xiafashuliang == success_count:
                                    self.list_treeview.insert('', END, values=('-','成功导入数量相同：' + str(success_count),'Pass'), tags = ('G'))
                                else:
                                    self.list_treeview.insert('', END, values=('-','成功导入数量不相同：' + str(success_count),'错误'), tags = ('R'))
                            else:
                                self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'核查订单目录log文件匹配 异常：' + str(success_failure_filecheck),'错误'), tags = ('R'))
                            self.list_treeview.update()

                        elif cpstr == 'ZipPwdCheck':
                            #核对zip压缩文件密码是否正确
                            temp_str = tempk[1]
                            temp_int = int(temp_str) -1
                            temp_list = verifyfiles[temp_int]
                            comparefile1 = temp_list[2]
                            checkzippwd =  check_zip_pwd(comparefile1,self.dxhppwd_list[0])
                            if checkzippwd == 0:                        
                                self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'核对打印清单zip压缩文件密码是否正确: 正确','Pass'), tags = ('G'))
                            else:
                                self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),'核对打印清单zip压缩文件密码是否正确: 错误' ,'错误'), tags = ('R'))
                            self.list_treeview.update()

                        elif cpstr == 'SortedPackageCheck': #分发文件夹文件检查
                            logger.info('SortedPackageCheck')
                            #提取客户分拣文件文件名
                            temp_str = tempk[1]
                            temp_int = int(temp_str) -1
                            temp_list = verifyfiles[temp_int]
                            comparefile_match = temp_list[1]
                            logger.info(comparefile_match)
                            strSortedNumber = getSortedNumberFromxls(sourcedir,comparefile_match,ProductOrderNo_value)
                            logger.info('strSortedNumber')
                            strSortedNumber = strSortedNumber[5:]
                            logger.info(strSortedNumber)
                            zipfile_gerenhua = catchfilefullname(sourcedir,'个人化.zip')
                            logger.info('文件名检查（单号，分单号）个人化.zip')
                            logger.info(zipfile_gerenhua)
                            zipfile_gerenhuabasename = os.path.basename(zipfile_gerenhua)
                            #文件名检查（单号，分单号）
                            if ProductOrderNo_value in zipfile_gerenhuabasename:
                                temp_pos1 = zipfile_gerenhuabasename.find('(')
                                temp_pos2 = zipfile_gerenhuabasename.find('（')
                                temp_pos3 = max(temp_pos1,temp_pos2)
                                temp_pos1 = zipfile_gerenhuabasename.find(')')
                                temp_pos2 = zipfile_gerenhuabasename.find('）')
                                temp_pos1 = max(temp_pos1,temp_pos2)
                                if temp_pos1 > temp_pos3:
                                    temp_str = zipfile_gerenhuabasename[temp_pos3+1:temp_pos1]
                                    logger.info(temp_str)
                                    temp_str = temp_str.strip()
                                    if strSortedNumber == temp_str:
                                        self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),os.path.basename(zipfile_gerenhua)+' 打包文件名与分单单号相符','Pass'), tags = ('G'))
                                    else:
                                        self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),os.path.basename(zipfile_gerenhua)+' 打包文件名与分单单号不相符: 错误' ,'错误'), tags = ('R'))
                                else:
                                    self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),os.path.basename(zipfile_gerenhua)+' 打包文件名与分单单号不相符: 错误' ,'错误'), tags = ('R'))
                            else:
                                self.list_treeview.insert('', END, values=(str(j-4-int(working_items[1])),os.path.basename(zipfile_gerenhua)+' 打包文件名与分单单号不相符: 错误' ,'错误'), tags = ('R'))
                            self.list_treeview.update()

                            checkzippwd =  check_zip_pwd(zipfile_gerenhua,self.dxhppwd_list[1])
                            #密码检查
                            if checkzippwd == 0:                        
                                self.list_treeview.insert('', END, values=('-',os.path.basename(zipfile_gerenhua)+' 核对个人化文件密码是否正确: 正确','Pass'), tags = ('G'))
                            else:
                                self.list_treeview.insert('', END, values=('-',os.path.basename(zipfile_gerenhua)+' 核对个人化文件密码是否正确: 错误' ,'错误'), tags = ('R'))
                            self.list_treeview.update()

                            comparevalue1 =  check_sortingfile_gerenhua_zip_content(zipfile_gerenhua,dingdanshuliang)
                            #压缩包内容检查
                            logger.info(comparevalue1)
                            if '正常返回' in comparevalue1:                        
                                self.list_treeview.insert('', END, values=('-',comparevalue1,'Pass'), tags = ('G'))
                            else:
                                self.list_treeview.insert('', END, values=('-','个人化zip压缩包检查异常：' + str(comparevalue1),'错误'), tags = ('R'))
                            self.list_treeview.update()
                            #检查印刷文件 印刷.zip
                            zipfile_gerenhua = catchfilefullname(sourcedir,'印刷.zip')
                            logger.info('检查印刷文件 印刷.zip')
                            logger.info(zipfile_gerenhua)
                            zipfile_gerenhuabasename = os.path.basename(zipfile_gerenhua)
                            if ProductOrderNo_value in zipfile_gerenhuabasename:
                                temp_pos1 = zipfile_gerenhuabasename.find('(')
                                temp_pos2 = zipfile_gerenhuabasename.find('（')
                                temp_pos3 = max(temp_pos1,temp_pos2)
                                temp_pos1 = zipfile_gerenhuabasename.find(')')
                                temp_pos2 = zipfile_gerenhuabasename.find('）')
                                temp_pos1 = max(temp_pos1,temp_pos2)
                                if temp_pos1 > temp_pos3:
                                    temp_str = zipfile_gerenhuabasename[temp_pos3+1:temp_pos1]
                                    temp_str = temp_str.strip()
                                    logger.info(temp_str)
                                    logger.info(strSortedNumber)
                                    if strSortedNumber == temp_str:
                                        self.list_treeview.insert('', END, values=('-',os.path.basename(zipfile_gerenhua)+' 打包文件名与分单单号相符','Pass'), tags = ('G'))
                                    else:
                                        self.list_treeview.insert('', END, values=('-',os.path.basename(zipfile_gerenhua)+' 打包文件名与分单单号不相符: 错误' ,'错误'), tags = ('R'))
                                else:
                                    self.list_treeview.insert('', END, values=('-',os.path.basename(zipfile_gerenhua)+' 打包文件名与分单单号不相符: 错误' ,'错误'), tags = ('R'))
                            else:
                                self.list_treeview.insert('', END, values=('-',os.path.basename(zipfile_gerenhua)+' 打包文件名与分单单号不相符: 错误' ,'错误'), tags = ('R'))
                            self.list_treeview.update()

                            checkzippwd =  check_zip_pwd(zipfile_gerenhua,self.dxhppwd_list[1])
                            if checkzippwd == 0:                        
                                self.list_treeview.insert('', END, values=('-',os.path.basename(zipfile_gerenhua)+' 核对印刷文件密码是否正确: 正确','Pass'), tags = ('G'))
                            else:
                                self.list_treeview.insert('', END, values=('-',os.path.basename(zipfile_gerenhua)+' 核对印刷文件密码是否正确: 错误' ,'错误'), tags = ('R'))
                            self.list_treeview.update()

                            comparevalue1 =  check_sortingfile_yinshua_zip_content(zipfile_gerenhua,xiafashuliang,tempdir,self.dxhppwd_list[1],mdb_wurenxiang_count)
                            logger.info(comparevalue1)
                            if '正常返回' in comparevalue1:                        
                                self.list_treeview.insert('', END, values=('-',comparevalue1,'Pass'), tags = ('G'))
                            else:
                                self.list_treeview.insert('', END, values=('-','印刷zip压缩包检查异常：' + str(comparevalue1),'错误'), tags = ('R'))
                            self.list_treeview.update()

                            #检查 数据单文件名 与 单号 是否相符
                            checkfilename = catchfilefullnameindir(sourcedir,'数据单','分发')
                            logger.info('检查 数据单文件名 与 单号 是否相符')
                            logger.info(checkfilename)
                            geted_checkfilename = os.path.basename(checkfilename)
                            if ProductOrderNo_value in geted_checkfilename:
                                temp_pos1 = geted_checkfilename.find('(')
                                temp_pos2 = geted_checkfilename.find('（')
                                temp_pos3 = max(temp_pos1,temp_pos2)
                                temp_pos1 = geted_checkfilename.find(')')
                                temp_pos2 = geted_checkfilename.find('）')
                                temp_pos1 = max(temp_pos1,temp_pos2)
                                if temp_pos1 > temp_pos3:
                                    temp_str = geted_checkfilename[temp_pos3+1:temp_pos1]
                                    temp_str = temp_str.strip()
                                    logger.info(temp_str)
                                    logger.info(strSortedNumber)
                                    if strSortedNumber == temp_str:
                                        self.list_treeview.insert('', END, values=('-',os.path.basename(geted_checkfilename)+' 文件名与分单单号相符','Pass'), tags = ('G'))
                                    else:
                                        self.list_treeview.insert('', END, values=('-',os.path.basename(geted_checkfilename)+' 文件名与分单单号不相符: 错误' ,'错误'), tags = ('R'))
                                else:
                                    self.list_treeview.insert('', END, values=('-',os.path.basename(geted_checkfilename)+' 文件名与分单单号不相符: 错误' ,'错误'), tags = ('R'))
                            else:
                                self.list_treeview.insert('', END, values=('-',os.path.basename(geted_checkfilename)+' 文件名与分单单号不相符: 错误' ,'错误'), tags = ('R'))

                            #检查 打印清单 文件名 与 单号 是否相符
                            checkfilename = catchfilefullnameindir(sourcedir,'打印清单','分发')
                            logger.info('检查 打印清单 文件名 与 单号 是否相符')
                            logger.info(checkfilename)
                            geted_checkfilename = os.path.basename(checkfilename)
                            if ProductOrderNo_value in geted_checkfilename:
                                temp_pos1 = geted_checkfilename.find('(')
                                temp_pos2 = geted_checkfilename.find('（')
                                temp_pos3 = max(temp_pos1,temp_pos2)
                                temp_pos1 = geted_checkfilename.find(')')
                                temp_pos2 = geted_checkfilename.find('）')
                                temp_pos1 = max(temp_pos1,temp_pos2)
                                if temp_pos1 > temp_pos3:
                                    temp_str = geted_checkfilename[temp_pos3+1:temp_pos1]
                                    temp_str = temp_str.strip()
                                    logger.info(temp_str)
                                    logger.info(strSortedNumber)
                                    if strSortedNumber == temp_str:
                                        self.list_treeview.insert('', END, values=('-',os.path.basename(geted_checkfilename)+' 文件名与分单单号相符','Pass'), tags = ('G'))
                                    else:
                                        self.list_treeview.insert('', END, values=('-',os.path.basename(geted_checkfilename)+' 文件名与分单单号不相符: 错误' ,'错误'), tags = ('R'))
                                else:
                                    self.list_treeview.insert('', END, values=('-',os.path.basename(geted_checkfilename)+' 文件名与分单单号不相符: 错误' ,'错误'), tags = ('R'))
                            else:
                                self.list_treeview.insert('', END, values=('-',os.path.basename(geted_checkfilename)+' 文件名与分单单号不相符: 错误' ,'错误'), tags = ('R'))

                            
                            logger.info('检查 data_form_list[7] 数据单内部订单号是否相符')
                            checkfilename = data_form_list[7]
                            logger.info(checkfilename)
                            geted_checkfilename = os.path.basename(checkfilename)
                            if ProductOrderNo_value in geted_checkfilename:
                                temp_pos1 = geted_checkfilename.find('(')
                                temp_pos2 = geted_checkfilename.find('（')
                                temp_pos3 = max(temp_pos1,temp_pos2)
                                temp_pos1 = geted_checkfilename.find(')')
                                temp_pos2 = geted_checkfilename.find('）')
                                temp_pos1 = max(temp_pos1,temp_pos2)
                                if temp_pos1 > temp_pos3:
                                    temp_str = geted_checkfilename[temp_pos3+1:temp_pos1]
                                    temp_str = temp_str.strip()
                                    logger.info(temp_str)
                                    logger.info(strSortedNumber)
                                    if strSortedNumber == temp_str:
                                        self.list_treeview.insert('', END, values=('-',os.path.basename(geted_checkfilename)+' 数据单内部订单号相符','Pass'), tags = ('G'))
                                    else:
                                        self.list_treeview.insert('', END, values=('-',os.path.basename(geted_checkfilename)+' 数据单内部订单号不相符: 错误' ,'错误'), tags = ('R'))
                                else:
                                    self.list_treeview.insert('', END, values=('-',os.path.basename(geted_checkfilename)+' 数据单内部订单号不相符: 错误' ,'错误'), tags = ('R'))
                            else:
                                self.list_treeview.insert('', END, values=('-',os.path.basename(geted_checkfilename)+' 数据单内部订单号不相符: 错误' ,'错误'), tags = ('R'))

                        else:
                            self.list_treeview.insert('', END, values=('0','无此命令: ','Pass'), tags = ('G'))

            run_main_fresh_finish_time = datetime.datetime.now()
            run_time = run_main_fresh_finish_time - run_main_fresh_begin_time
            str_tips = str(run_main_fresh_finish_time.strftime('%Y-%m-%d %H:%M:%S'))
            str_tips = '开检时间：' + str_tips + ' 完成！耗时 ' + str(run_time.seconds)+'秒'
            self.svar_tips.set(str_tips)


        except Exception as err_message:
            print(err_message)
            self.list_treeview.insert('', END, values=('E',err_message,"Error"), tags = ('R'))
            self.list_treeview.update
            logger.error(err_message.__str__())
            logger.exception(sys.exc_info())
        # 主功能键end

    def command_download_btn_run(self):
        
        logger.info("Run file list refresh...")
        self.run_main_fresh()
        #self.list_treeview.insert('', 0, values=('##','检查结束','END'), tags = ('G'))
        self.list_treeview.insert('', END, values=('##','检查结束','END'), tags = ('G'))

    def onFormEvent(self,event):
        #self.master.bind( '<Configure>', self.onFormEvent )
        #绑定主窗口大小位置事件。 #事件包含子控件的大小位置等信息
        #event.type等类型是tk.tkinter类
        #主窗口widget是.    #子控件widget是.!Button（类似），通过查找只有一个点的widget判断是主窗口属性
        #读取主窗口的长宽，再重赋值给各个控件。

        if (len(str(event.widget))) == 1:
            #print('%s=%s' % ( event.width,event.height))

            self.btn_app_exit_init.place(x=event.width-80 ,y= event.height-470)
            self.btn_download_init.place(x=event.width-80, y= event.height-640)
    
            self.label_author.place(x=event.width-234, y=event.height-22)
            # self.list_treeview.column(0, width=40, stretch=True)
            # self.list_treeview.column(1, width=event.width-270, stretch=True)
            # self.list_treeview.column(2, width=40, stretch=True)
            #self.list_treeview.parent.   # = Treeview(fm1, columns=('F1', 'F2','F3'), show='headings',height=41)
            #self.list_treeview.winfo_height = 660
            #self.list_treeview.winfo_screenwidth = 270
            #if getattr( event, key ) == '.':
            #print('event.type=  ',event.type)

if __name__ == '__main__':
    base_dir=os.path.dirname(__file__)
    print(base_dir)  #临时修改环境变量    
    #os.environ['TZ'] = 'Asia/Shanghai'
    set_logging(base_dir)
    main_window = Tk()
    jver = '三代社保数据文件检验工具 - Eastcompeace Ver.20210922'
    main_window.title(jver)

    # 设定窗口的大小(长 * 宽)，显示窗体居中，winfo_xxx获取系统屏幕分辨率。
    sw = main_window.winfo_screenwidth()
    sh = main_window.winfo_screenheight()
    ww = 1140
    wh = 900
    x = (sw - ww) / 2
    y = (sh - wh) / 2-40    #窗口位置上移少许
    main_window.geometry("%dx%d+%d+%d" % (ww, wh, x, y))  # 这里的乘是小x
    logger.info('program restart...'+jver)
    display = App(main_window)
    main_window.mainloop()
    #SW_SHOWMAXIMIZED\SW_MINIMIZE\WM_DELETE_WINDOW
