#!/bin/python3
'''
功能：广发制卡业务库存反馈文件自动生成工具。
'''
from tkinter import *
#import tkinter
from configparser import ConfigParser
from tkinter import messagebox,scrolledtext,Canvas,PhotoImage,Label,StringVar,Entry, Button,END, DISABLED, Toplevel  # 导入滚动文本框的模块
from os.path import exists as os_path_exists
import xlrd
import datetime,time
import os
import logging
from openpyxl import load_workbook
from logging.handlers import RotatingFileHandler
from calendar import monthrange

#设置日志文件配置参数
def set_logging():
    global logger
    logger = logging.getLogger('balance_logger')
    handler = RotatingFileHandler('日志记录.log', maxBytes=5000000, backupCount=6)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    formatter = logging.Formatter('%(asctime)-12s %(filename)s %(lineno)d %(message)s')
    handler.setFormatter(formatter)

#定义类，脚本主要更能
class App():
    def __init__(self, master):
        self.svar_proc_time1 = StringVar()
        self.svar_proc_time2 = StringVar()
        self.svar_wuliaoshiyong_filename = StringVar()
        self.svar_kehumingcheng = StringVar()
        self.svar_youjiqingdan_filename = StringVar()
        self.svar_nnnnnnnnnnnnnnn_filename = StringVar()
        self.svar_label_prompt = StringVar()
        self.master = master
        self.customer_sname = ''
        self.Holiday = []
        self.data_dir = ''
        self.file_from_wuliaoshiyong = '广发银行物料使用情况记录表'
        self.file_from_youjiqingdan = ''
        self.file_from_fuliaokucun = ''
        self.curr_month = ''
        self.initWidgets(master)
        self.work_dir = ''
        self.savefile_dir = ''
        #程序是修改的，有部分变量没有用上



    # 辅料入库反馈文件处理
    def wuliaojxc_file_proc(self, export_xls_filename, xlsfilename):

        return_message = 'err'
        curr_proc_time_str = self.svar_proc_time1.get()
        try:
            date_p = datetime.datetime.strptime(curr_proc_time_str, '%Y%m%d').date()
            this_month_start = datetime.datetime(int(curr_proc_time_str[:4]), int(curr_proc_time_str[4:6]), 1)
            #today = datetime.datetime.today().date()
            last_month_end = this_month_start - datetime.timedelta(days=1)
            last_month_start = datetime.datetime(last_month_end.year, last_month_end.month, 1)
            last2_month_end = last_month_start - datetime.timedelta(days=1)
            last2_month_start = datetime.datetime(last2_month_end.year, last2_month_end.month, 1)
            last3_month_end = last2_month_start - datetime.timedelta(days=1)

            print(date_p, type(date_p))
        except:
            self.scr.insert(1.0, "无法查找到对应日期" + self.svar_proc_time1.get() + ".\n")
            self.master.update()
            return 0

        curr_proc_time_last_str = datetime.datetime.strftime(last_month_end,'%Y%m')
        curr_proc_time_last2_str = datetime.datetime.strftime(last2_month_end,'%Y%m')
        curr_proc_time_last3_str = datetime.datetime.strftime(last3_month_end, '%Y%m')
        logger.info('文件名前缀: '+self.file_from_wuliaoshiyong)
        wuliaoshiyongqingkjilubiao = self.file_from_wuliaoshiyong + curr_proc_time_str[:6] + '.xlsx'
        wuliaoshiyongqingkjilubiao_last = self.file_from_wuliaoshiyong + curr_proc_time_last_str+ '.xlsx'
        wuliaoshiyongqingkjilubiao_last2 = self.file_from_wuliaoshiyong + curr_proc_time_last2_str+ '.xlsx'
        wuliaoshiyongqingkjilubiao_last3 = self.file_from_wuliaoshiyong + curr_proc_time_last3_str+ '.xlsx'

        wuliaoshiyong_filelist = [wuliaoshiyongqingkjilubiao_last3,wuliaoshiyongqingkjilubiao_last2,wuliaoshiyongqingkjilubiao_last,wuliaoshiyongqingkjilubiao]
        self.scr.insert(1.0, wuliaoshiyongqingkjilubiao + ".\n")
        logger.info(wuliaoshiyongqingkjilubiao)
        self.scr.insert(1.0, wuliaoshiyongqingkjilubiao_last + ".\n")
        logger.info(wuliaoshiyongqingkjilubiao_last)
        self.scr.insert(1.0, wuliaoshiyongqingkjilubiao_last2 + ".\n")
        logger.info(wuliaoshiyongqingkjilubiao_last2)
        self.scr.insert(1.0, wuliaoshiyongqingkjilubiao_last3 + ".\n")
        logger.info(wuliaoshiyongqingkjilubiao_last3)
        self.master.update()

        #        to_xls_filename = os.path.join(self.savefile_dir,export_xls_filename)
        for wlsy_file in wuliaoshiyong_filelist:
            xlsfilename = wlsy_file
            if not os_path_exists(xlsfilename):
                print("文件不存在：", xlsfilename)
                logger.info("文件不存在："+ xlsfilename)
                self.scr.insert("文件不存在："+ xlsfilename)
                self.scr.update()
                return (return_message)

        xlsfilename = '物料出入库明细表.xlsx'
        if not os_path_exists(xlsfilename):
            print("文件不存在：", xlsfilename)
            logger.info("文件不存在："+ xlsfilename + '\n')
            self.scr.insert("文件不存在：" + xlsfilename)
            self.scr.update()
            return (return_message)

        workbook = xlrd.open_workbook(xlsfilename)
        sheet_curr = workbook.sheet_by_index(0)

        mxb_int_first_row = 3
        print("打开数据文件..." + xlsfilename)
        logger.info("打开数据文件..." + xlsfilename+'\n')
        self.scr.insert(1.0, "打开数据文件..." + xlsfilename+"\n")
        self.master.update()

        logger.info('sheet 广发')
        int_sheet_nrows = sheet_curr.nrows
        int_sheet_ncols = sheet_curr.ncols
        print('sheetname & lines:', sheet_curr, int_sheet_nrows)

        self.scr.insert(1.0,"\n")
        wuliaochurukumxb_list=[]
        #读取物料出入库明细表‘结存数量’
        for i in range(mxb_int_first_row,int_sheet_nrows):
            wuliaodaima_fromexcel = sheet_curr.cell(i,3).value
            wuliao_jiecunshulian = sheet_curr.cell(i,17).value
            self.scr.insert(1.0, str(wuliaodaima_fromexcel)+"\n")
            self.scr.insert(1.0, str(wuliao_jiecunshulian) + "\n")
            wuliaochurukumxb_list.append([wuliaodaima_fromexcel,wuliao_jiecunshulian])
        logger.info(wuliaochurukumxb_list)
        print(wuliaochurukumxb_list)

        wuliaoshiyong_grid = []
        logger.info('文件列表')
        logger.info(wuliaoshiyong_filelist)
        print(wuliaoshiyong_filelist)
        for wlsy_file in wuliaoshiyong_filelist:
            xlsfilename = wlsy_file
            workbook = xlrd.open_workbook(xlsfilename)
            sheet_curr = workbook.sheet_by_name('广发')

            #worksheetj = workbook['广发']
            int_first_row = 2
            print("打开数据文件..." + xlsfilename)
            logger.info("打开数据文件..." + xlsfilename)
            self.scr.insert(1.0, "打开数据文件..." + xlsfilename+"\n")
            self.master.update()

            # workbook = xlrd.open_workbook(xlsfilename)
            # sheet_curr = workbook.sheet_by_name('广发')
            logger.info('sheet 广发')
            int_sheet_nrows = sheet_curr.nrows
            int_sheet_ncols = sheet_curr.ncols
            print('sheetname & lines:', sheet_curr, int_sheet_nrows)

            shiyongqingkuang_int_first_row = 3
            for i in range(shiyongqingkuang_int_first_row,int_sheet_nrows):
                wuliaodaima_fromexcel = sheet_curr.cell(i,2).value
                if wuliaodaima_fromexcel == '':
                    break;
                if len(wuliaodaima_fromexcel) < 2:
                    break;
                print(wuliaodaima_fromexcel)
                data_date = sheet_curr.cell(1,7).value
                xls_date = xlrd.xldate_as_datetime(data_date, 0)
                month_range = monthrange(xls_date.year, xls_date.month)
                logger.info(str(month_range))
                for j in range(int(month_range[1])):
                    data_date = sheet_curr.cell(1,j*4+7).value
                    #print(data_date)
                    xls_date = xlrd.xldate_as_datetime(data_date,0)
                    if i == int_first_row:              #显示一行日期数据
                        print(xls_date)

                    try:
                        cell_value_temp = sheet_curr.cell(i, j * 4 + 7).value
                    except:
                        logging.info('明细数据格式错, excel位置：')
                        logging.info(i)
                        logging.info(j)
                    cell_value_ruku = cell_value_temp

                    try:
                        cell_value_temp = sheet_curr.cell(i, j * 4 + 7+1).value
                    except:
                        logging.info('明细数据格式错, excel位置：')
                        logging.info(i)
                        logging.info(j)
                    cell_value_dingdanshiyong = cell_value_temp

                    try:
                        cell_value_temp = sheet_curr.cell(i, j * 4 + 7+2).value
                    except:
                        logging.info('明细数据格式错, excel位置：')
                        logging.info(i)
                        logging.info(j)
                    cell_value_buhangengxinka = cell_value_temp

                    try:
                        cell_value_temp = sheet_curr.cell(i, j * 4 + 7+3).value
                    except:
                        logging.info('明细数据格式错, excel位置：')
                        logging.info(i)
                        logging.info(j)
                    cell_value_xiaohao = cell_value_temp
                    cell_value_comb = [cell_value_ruku,cell_value_dingdanshiyong,cell_value_buhangengxinka,cell_value_xiaohao]

                    wuliaoshiyong_grid.append([wuliaodaima_fromexcel,xls_date,cell_value_comb])
        logger.info(wuliaoshiyong_grid)

        xlsfilename = wuliaoshiyong_filelist[3]
        workbook_from = xlrd.open_workbook(xlsfilename)
        sheet_curr_from = workbook_from.sheet_by_name('广发')
        logger.info('当月excel情况表')
        logger.info(xlsfilename)

        xlsfilename = '配置\\模板-物料进销存日报表.xlsx'
        workbook = load_workbook(xlsfilename)  # 打开excel文件
        # 导出明细表begin
        logger.info('导出 ~明细表~ 表')
        self.scr.insert(1.0, "导出 ~明细表~ 表" + "\n")
        worksheetj = workbook['sheet1']  # 根据Sheet1这个sheet名字来获取该sheet
        #i = 0
        worksheetj.cell(1, 1).value = str(xls_date.year)+'2019年广发银行'+str(xls_date.month)+' 月物料收发进销存日报表'
        int_first_row = 3
        for i in range(int_first_row, int_sheet_nrows):
            wuliaodaima_fromexcel = sheet_curr_from.cell(i, 2).value
            if wuliaodaima_fromexcel == '':
                break;
            if len(wuliaodaima_fromexcel) < 2:
                break;
            print(wuliaodaima_fromexcel)
            data_date = sheet_curr_from.cell(1, 7).value
            xls_date = xlrd.xldate_as_datetime(data_date, 0)
            month_range = monthrange(xls_date.year, xls_date.month)
            logger.info(str(month_range))

            # a)取“物料使用情况记录表”中的A列到E列填充到“物料进销存日报”的A—E列。
            for j in range(0,5):
                logger.info('复制ABCDE：')
                logger.info(i)
                logger.info(j)
                logger.info(sheet_curr_from.cell(i, j).value)
                worksheetj.cell(i+2,j+1).value = sheet_curr_from.cell(i, j).value

            # b)“上月仓库结存”=同一物料代码的使用情况记录表的“上月车间结存量”+物料出入库明细表的“结存数量”。
            # c)“上月余下订单数”、“本月订单数”、“未入库数量”无需处理，由客服填写。
            wuliaodaima_fromexcel = sheet_curr_from.cell(i, 2).value
            shangyuechejianjiecun = sheet_curr_from.cell(i, 6).value
            logger.info(wuliaodaima_fromexcel)
            for k in range(len(wuliaochurukumxb_list)):
                mxb_jiecunshuliang_match = 0
                #print(wuliaodaima_fromexcel)
                #print(wuliaochurukumxb_list[k][0])
                temp_compare = wuliaochurukumxb_list[k][0]
                if wuliaodaima_fromexcel == temp_compare:
                    mxb_jiecunshuliang_match = 1
                    mxb_jiecunshuliang = wuliaochurukumxb_list[k][1]
                else:
                    mxb_jiecunshuliang = 0
                if mxb_jiecunshuliang_match == 0 :
                    self.scr.insert(1.0,'物料明细表无法匹配 物料：')
                    self.scr.insert(1.0,wuliaodaima_fromexcel)
                    self.scr.update()
                else:
                    worksheetj.cell(i+2,6).value = shangyuechejianjiecun + mxb_jiecunshuliang


            # d)“上月发出总量”=T - 1月物料进销存日报的“本月发出总数”。
            xlsfilename = '广发银行物料进销存日报'+curr_proc_time_last_str+'.xlsx'
            if not os_path_exists(xlsfilename):
                print("文件不存在：", xlsfilename)
                logger.info("文件不存在："+ xlsfilename + '\n')
                self.scr.insert(1.0,"文件不存在：" + xlsfilename+'\n')
                self.scr.update()
                return (return_message)
            l
            workbook = xlrd.open_workbook(xlsfilename)
            sheet_curr = workbook.sheet_by_index(0)

            mxb_int_first_row = 3
            print("打开数据文件..." + xlsfilename)
            logger.info("打开数据文件..." + xlsfilename+'\n')
            self.scr.insert(1.0, "打开数据文件..." + xlsfilename+"\n")
            self.master.update()

            logger.info('sheet 广发')
            int_sheet_nrows = sheet_curr.nrows
            int_sheet_ncols = sheet_curr.ncols
            print('sheetname & lines:', sheet_curr, int_sheet_nrows)

            self.scr.insert(1.0,"\n")
            wuliaochurukumxb_list=[]
            #读取物料出入库明细表‘结存数量’
            for i in range(mxb_int_first_row,int_sheet_nrows):
                wuliaodaima_fromexcel = sheet_curr.cell(i,3).value
                wuliao_jiecunshulian = sheet_curr.cell(i,17).value
                self.scr.insert(1.0, str(wuliaodaima_fromexcel)+"\n")
                self.scr.insert(1.0, str(wuliao_jiecunshulian) + "\n")
                wuliaochurukumxb_list.append([wuliaodaima_fromexcel,wuliao_jiecunshulian])
            logger.info(wuliaochurukumxb_list)
            print(wuliaochurukumxb_list)






        # e)“前1周周用量”=T日所在星期的前1个自然周（7
        # 天）的用量之和。
        # f)“前2周周用量”=T日所在星期的前2个自然周（14
        # 天）的用量之和。
        # g)“前12周周用量”=T日所在星期的前12个自然周（84
        # 天）的用量之和。
        # h)“入库数量”=同一时间日期、同一物料代码的物料出入库明细表的“入库数量”。
        # i)“出库数量”=同一时间日期、同一物料代码的物料使用情况记录表的“订单使用”+“订单使用（不含更新卡）”+“消耗”。
        # 3、物料预警表各字段取值规则：
        # a)取“物料进销存日报”的A到E列填充到“物料预警表”的A - E列。
        # b)“使用状态”=同一物料代码的“物料使用情况记录表”的“使用状态”。
        # c)“YYYYMM - 2
        # 成品数（不含更新卡）”=同一物料代码T - 2
        # 月份“物料使用情况记录表”的“订单使用（不含更新卡）总量”
        # d)“YYYYMM - 1
        # 成品数（不含更新卡）”=同一物料代码T - 1
        # 月份“物料使用情况记录表”的“订单使用（不含更新卡）总量”
        # e)“YYYYMM成品数（不含更新卡）”=同一物料代码T月份“物料使用情况记录表”的“订单使用（不含更新卡）总量”
        # f)“14
        # 天日均用量”=同一物料代码“物料使用情况记录表”T日往前推算14天的“订单使用（不含更新卡）”之和除以14。
        # g)“7
        # 天日均用量”=同一物料代码“物料使用情况记录表”T日往前推算7天的“订单使用（不含更新卡）”之和除以7。
        # h)“截止T月MM日库存量”=同一物料代码“物料进销存日报”的“库存总数”。

        temp_proc_time1 = self.svar_proc_time1.get()
        workbook.save('物料进销存日报表'+temp_proc_time1[:6]+'.xlsx')

        print('=' * 40)
        self.scr.insert(1.0, "文件输出..\n" )
        self.scr.insert(1.0, 'txtfilename' + '\n' )
        self.master.update()

    # 辅料出库反馈文件处理：
    def fuliao_chuku_file_proc(self, txtfilename, xlsfilename):

        if not os_path_exists(xlsfilename):
            print("文件不存在：", xlsfilename)
            logger.info("文件不存在：" + xlsfilename)
            return_message = messagebox.askquestion(title='提示',
                                                    message='无找到文件' + xlsfilename + '，继续？')  # return yes/no
            return (return_message)

        txtfilename = os.path.join(self.savefile_dir,txtfilename)

        int_first_row = 2
        # day_column_start = 7  # 日数据开始位置

        print(xlsfilename)
        logger.info(xlsfilename)
        self.scr.insert(1.0, "开始读取数据...   "+xlsfilename+"\n")
        self.master.update()

        str_proc_date = self.svar_proc_time1.get()
        if str_proc_date[4] == '1':
            str_proc_date_month = str_proc_date[:4]+'.'+str_proc_date[4:6]
        else:
            str_proc_date_month = str_proc_date[:4] + '.' + str_proc_date[5:6]

        workbook = xlrd.open_workbook(xlsfilename)
        try:
            sheet_curr = workbook.sheet_by_name(str_proc_date_month)
            logger.info('打开表格sheet: ' + str_proc_date_month)
            self.scr.insert(1.0, ('打开表格sheet : ' + str_proc_date_month) + "\n")
        except:
            logger.info('无法打开表格sheet: ' + str_proc_date_month)
            self.scr.insert(1.0, ('无法打开表格sheet : ' + str_proc_date_month) + "\n")
            self.scr.update()
            return 'can not open sheet.'

        int_sheet_nrows = sheet_curr.nrows
        int_sheet_ncols = sheet_curr.ncols
        print('sheetname & lines:', sheet_curr, int_sheet_nrows)
        logger.info('sheetname & lines:')
        logger.info(str_proc_date_month)
        logger.info(int_sheet_nrows)
        str_split_string = '|&|'
        data_line_count  = 0

        # 首行日期查找
        date_position = 0
        # for j in range(15, int_sheet_ncols,3): #步长为3
        #     cell_value_rukuriqi = sheet_curr.cell(0, j).value
        #     xls_date = xldate_as_tuple(cell_value_rukuriqi, 0)
        #     date_str = str(xls_date[0])
        #     if xls_date[1] < 10:
        #         date_str = date_str + '0' + str(xls_date[1])
        #     else:
        #         date_str = date_str + str(xls_date[1])
        #     if xls_date[2] < 10:
        #         date_str = date_str + '0' + str(xls_date[2])
        #     else:
        #         date_str = date_str + str(xls_date[2])
        #     compare_data_str = self.svar_proc_time1.get()
        #     if date_str == compare_data_str:
        #         date_position = j

        if date_position == 0 :
            self.scr.insert(1.0, "EXCEL表格无法查找到对应日期" + self.svar_proc_time1.get() + ".\n")
            self.master.update()
            return ('no')

        txt_open_file = open(txtfilename,'w+')

        for i in range(int_first_row, int_sheet_nrows):
            cell_curr_value = sheet_curr.cell(i, 1).value
            if True:  # not isinstance(cell_curr_value,str):         #判断数据是否最后一行
                yinhang_fuliaobianhao = sheet_curr.cell(i, 2).value #'银行辅料编号'
                fuliaobianhao = sheet_curr.cell(i, 1).value
                dangqiankucun = sheet_curr.cell(i, 14).value #现库存量（仓库+车间库存数）

                if isinstance(dangqiankucun,float):
                    int_dangqiankucun = round(dangqiankucun)

                chejianmeirichukuliang = sheet_curr.cell(i, date_position+2).value #数值在右移 2 位
                chejianmeirichukuliang = chejianmeirichukuliang
                if isinstance(chejianmeirichukuliang,float):
                    int_chejianmeirichukuliang = round(chejianmeirichukuliang)

                str_merge = 'DATA' + str_split_string + yinhang_fuliaobianhao + str_split_string + fuliaobianhao + str_split_string + str(int_chejianmeirichukuliang) +str_split_string
                str_merge = str_merge + str(int_dangqiankucun) + str_split_string
                if int_chejianmeirichukuliang >0 and len(yinhang_fuliaobianhao) > 0:
                    txt_open_file.writelines(str_merge)
                    txt_open_file.writelines('\n')

                    data_line_count = data_line_count +1
                    self.scr.insert(1.0, str(str_merge) + "\n")
                    logger.info(str_merge)
                    self.master.update()

        str_merge = 'TLRL' + str_split_string + str(data_line_count) + str_split_string
        logger.info(str_merge)
        txt_open_file.writelines(str_merge)
        txt_open_file.writelines('\n')
        self.scr.insert(1.0, str_merge)

        txt_open_file.close()
        self.scr.insert(1.0, "\n数据已写入文件...\n" )
        self.scr.insert(1.0, txtfilename + '\n' )
        self.master.update()

    #按字符查找符合条件文件名，返回文件列表
    def find_filename(self, curr_path, curr_filename_path):
        list_files = []
        curr_filename_path = curr_filename_path.replace('*','')
        FileNames = os.listdir(curr_path)
        for file_name in FileNames:
            if file_name[0] == '~':
                continue
            fullfilename = os.path.join(os.path.abspath(os.path.dirname(curr_path)),file_name)
            if curr_filename_path in fullfilename:
                print('文件名：%s' % fullfilename)
                list_files.append(fullfilename)

        if len(list_files) > 0:
            return (list_files[0])
        else:
            return (None)

    # 从数据库导出价格（基础表），返回含价格信息列表
    def excel_cell_rowcell_to_position(self,int_row,int_column):
        if int_row < 26:
            str_excel_cell_pos = chr(64+int_row)
            str_excel_cell_pos = str_excel_cell_pos + str(int_column)
        return str_excel_cell_pos

# 整合数据，导出生成excel文件

# 程序主gui界面。
    def initWidgets(self, fm1):

        cp = ConfigParser()
        cp.read('配置\\配置文件.ini', encoding='gbk')
        str_kehu_name = cp.get('客户', '客户名称')

        try:
            self.customer_sname = cp.get('客户', 'sname')
            self.file_from_fuliaokucun = cp.get(str_kehu_name, '物料预警表')
            #self.Holiday = cp.get(str_kehu_name, '节假日')
            self.file_from_wuliaoshiyong = cp.get(str_kehu_name, '物料使用情况')
            self.work_dir = ".//"#cp.get(str_kehu_name, '工作目录')
            #self.file_from_fuliaokucun = cp.get(str_kehu_name, '辅料库存表')
        except Exception as err_message:
            print(err_message)
            return_message = messagebox.showinfo(title='提示',message='无法打开配置文件.ini或配置有误!' )
            exit(2)

        print('host: ', str_kehu_name)
        print(self.file_from_youjiqingdan)

        label_kehumingcheng = Label(fm1, text='客户名称：', font=('Arial', 12))
        label_kehumingcheng.place(x=20, y=30)
        self.svar_kehumingcheng.set(str_kehu_name)
        entry_kehumingcheng = Entry(fm1, textvariable=self.svar_kehumingcheng, width=20, font=('Arial', 12))
        entry_kehumingcheng.place(x=20, y=55)

        label_proc_time = Label(fm1, text='数据处理时间：', font=('Arial', 12))
        label_proc_time.place(x=240, y=30)

        temp_last_datetime = datetime.date.today() - datetime.timedelta(days=10)

        str_temp_last_datetime = time.strftime('%Y%m%d', time.localtime(time.time()))
        self.svar_proc_time1.set(str_temp_last_datetime)
        entry_proc_time1 = Entry(fm1, textvariable=self.svar_proc_time1, width=20, font=('Arial', 12))
        entry_proc_time1.place(x=240, y=55)

        label_dingdangenzong_filename = Label(fm1, text='订单跟踪表：', font=('Arial', 12))
        label_dingdangenzong_filename.place(x=540, y=30)

        str_temp_find_filename = self.find_filename(self.work_dir,self.file_from_wuliaoshiyong)
        if str_temp_find_filename == None:
            self.svar_wuliaoshiyong_filename.set('没有找到文件'+self.file_from_wuliaoshiyong)
        else:
            self.svar_wuliaoshiyong_filename.set(str_temp_find_filename)

        entry_dingdangenzong_filename = Entry(fm1, textvariable=self.svar_wuliaoshiyong_filename, width=50, font=('Arial', 12))
        entry_dingdangenzong_filename.place(x=540, y=55)


        label_wuliaojxc_filename = Label(fm1, text='辅料库存表：', font=('Arial', 12))
        label_wuliaojxc_filename.place(x=540, y=100)

        str_temp_find_filename = self.find_filename(self.work_dir,self.file_from_fuliaokucun)
        if str_temp_find_filename == None:
            self.svar_nnnnnnnnnnnnnnn_filename.set('没有找到文件'+self.file_from_wuliaoshiyong)
        else:
            self.svar_nnnnnnnnnnnnnnn_filename.set(str_temp_find_filename)

        entry_wuliaojxc_filename = Entry(fm1, textvariable=self.svar_nnnnnnnnnnnnnnn_filename, width=50, font=('Arial', 12))
        entry_wuliaojxc_filename.place(x=540, y=125)

        svar_label_prompt = StringVar()
        svar_label_prompt.set('客户名称：')

        label_author = Label(fm1, text='by流程与信息化部IT. Dec,2019', font=('Arial', 9))
        label_author.place(x=820, y=740)

        self.scr = scrolledtext.ScrolledText(fm1, width=70, height=48)
        self.scr.place(x=20, y=100)

        btn_barcode_init = Button(fm1, text='广发银行物料进销存日报', command=self.command_btn_run_wuliaojxc)
        btn_barcode_init.place(x=540, y=240)

        btn_barcode_init = Button(fm1, text='出库反馈文件', command=self.command_btn_run_chuku)
        btn_barcode_init.place(x=540, y=300)


        btn_barcode_init = Button(fm1, text=' 退  出 ', command=self.command_btn_exit)
        btn_barcode_init.place(x=540, y=420)

    # 退出键
    def command_btn_exit(self):
        self.master.destroy()

    # 主功能键
    def command_btn_run_wuliaojxc(self):

        self.scr.delete(1.0,END)

        label_tips1_filename = Label(self.master, text='读取订单跟踪表... ', font=('Arial', 12))
        label_tips1_filename.place(x=540, y=530)

        #self.file_from_wuliaoshiyong = self.svar_wuliaoshiyong_filename.get()
        #self.file_from_fuliaokucun = self.svar_nnnnnnnnnnnnnnn_filename.get()

        str_timestamp = self.svar_proc_time1.get()

        str_temp_last_datetime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        str_wuliaojxc_filename = '广发银行物料进销存日报'+'.xlsx'

        self.wuliaojxc_file_proc(str_wuliaojxc_filename, self.file_from_wuliaoshiyong)
        # try:
        #     if self.wuliaojxc_file_proc(str_wuliaojxc_filename, self.file_from_wuliaoshiyong) == 'no':
        #         return (1)
        # except Exception as err_message:
        #     print(err_message)
        #     self.scr.insert(1.0, err_message )
        #     self.scr.update()
        #     logger.error(err_message.__str__())
        #     logger.exception(sys.exc_info())

        label_tips1_filename = Label(self.master, text='完成...                     ', font=('Arial', 12))
        label_tips1_filename.place(x=540, y=530)

        return 0

    def command_btn_run_chuku(self):

        self.scr.delete(1.0,END)
        label_tips1_filename = Label(self.master, text='读取辅料库存表... ', font=('Arial', 12))
        label_tips1_filename.place(x=540, y=530)
        self.file_from_wuliaoshiyong = self.svar_wuliaoshiyong_filename.get()
        self.file_from_fuliaokucun = self.svar_nnnnnnnnnnnnnnn_filename.get()
        str_timestamp = self.svar_proc_time1.get()

        str_temp_last_datetime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        str_chu_filename = '01_' + str_temp_last_datetime + '_fs.txt'

        try:
            if self.fuliao_chuku_file_proc(str_chu_filename, self.file_from_fuliaokucun) == 'no':
                return (1)
        except Exception as err_message:
            print(err_message)
            self.scr.insert(1.0, err_message)
            self.scr.update()
            logger.error(err_message.__str__())
            logger.exception(sys.exc_info())

        label_tips1_filename = Label(self.master, text='完成...                     ', font=('Arial', 12))
        label_tips1_filename.place(x=540, y=530)
        return 0

if __name__ == '__main__':

    set_logging()

    main_window = Tk()
    main_window.title('光大制卡业务库存反馈文件生成工具 v.2001031701')

    # 设定窗口的大小(长 * 宽)，显示窗体居中，winfo_xxx获取系统屏幕分辨率。
    sw = main_window.winfo_screenwidth()
    sh = main_window.winfo_screenheight()
    ww = 1024
    wh = 770
    x = (sw - ww) / 2
    y = (sh - wh) / 2
    main_window.geometry("%dx%d+%d+%d" % (ww, wh, x, y))  # 这里的乘是小x
    display = App(main_window)
    main_window.mainloop()
