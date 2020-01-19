#!/bin/python3
'''
功能：光大制卡业务库存反馈文件自动生成工具。
'''
from tkinter import *
from configparser import ConfigParser
from tkinter import messagebox,scrolledtext,Canvas,PhotoImage,Label,StringVar,Entry, Button,END, DISABLED, Toplevel  # 导入滚动文本框的模块
from os.path import exists as os_path_exists
import xlrd
import datetime,time
import os
import logging
from logging.handlers import RotatingFileHandler
from xlrd import xldate_as_tuple

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
        self.svar_dingdanggenzong_filename = StringVar()
        self.svar_kehumingcheng = StringVar()
        self.svar_proc_time2 = StringVar()
        self.svar_youjiqingdan_filename = StringVar()
        self.svar_fuliaokucun_filename = StringVar()
        self.svar_label_prompt = StringVar()
        self.master = master
        self.customer_sname = ''
        self.Holiday = []
        self.data_dir = ''
        self.file_from_dingdangenzong = ''
        self.file_from_youjiqingdan = ''
        self.file_from_fuliaokucun = ''
        self.curr_month = ''
        self.initWidgets(master)
        self.work_dir = ''
        self.savefile_dir = ''
        #程序是修改的，有部分变量没有用上

# 按文件夹统计符合条件文件列表，逐个文件导入数据库
    def proc_folder(self, customer, work_dir):

        print("清空原有汇总统计数据（hztj）数据...")

        for parent, dirnames, filenames in os.walk(work_dir, followlinks=True):
            for filename in filenames:
                file_path = os.path.join(parent, filename)
                if '汇总统计' in filename:
                    print('文件名：%s' % filename)
                    print('文件完整路径：%s\n' % file_path)
                    self.xls_db('gsnx', file_path)

        # 从数据库导入价格（基础表），返回含价格信息列表
        def pricexls_db(self, customer, xlsfilename):

            if not os_path_exists(xlsfilename):
                print("文件不存在：", xlsfilename)
                return_message = messagebox.askquestion(title='提示',
                                                        message='无找到文件' + xlsfilename + '，继续？')  # return yes/no
                return (return_message)

            int_first_row = 2
            # day_column_start = 7  # 日数据开始位置

            print("清空原有对账价格基础表（price）数据...")
            print(xlsfilename)
            self.scr.insert(END, "清空原有对账价格基础表（price）数据...\n")
            self.master.update()

            workbook = xlrd.open_workbook(xlsfilename)
            sheetsname = workbook.sheet_names()  # 获取excel里的工作表sheet名称数组

            str_curr_sheet_name = sheetsname[0]

            sheet_curr = workbook.sheet_by_name(str_curr_sheet_name)
            int_sheet_nrows = sheet_curr.nrows
            print('sheetname & lines:', str_curr_sheet_name, int_sheet_nrows)

            for i in range(int_first_row, int_sheet_nrows):
                cell_curr_value = sheet_curr.cell(i, 0).value
                # print('i: ',i)
                if True:  # not isinstance(cell_curr_value,str):         #判断数据是否最后一行
                    priceid = sheet_curr.cell(i, 0).value
                    kamiandaima = sheet_curr.cell(i, 1).value
                    kapianbanbenhao = sheet_curr.cell(i, 2).value
                    wuliao = sheet_curr.cell(i, 3).value
                    kapianmingcheng = sheet_curr.cell(i, 4).value

                    cell_curr_value = sheet_curr.cell(i, 5).value
                    if isinstance(cell_curr_value, str):
                        grhpingrijiage1 = 0
                    else:
                        grhpingrijiage1 = cell_curr_value
                    cell_curr_value = sheet_curr.cell(i, 6).value
                    if isinstance(cell_curr_value, str):
                        grhjierijiage1 = 0
                    else:
                        grhjierijiage1 = cell_curr_value
                    cell_curr_value = sheet_curr.cell(i, 7).value
                    if isinstance(cell_curr_value, str):
                        kongbaikajiage1 = 0
                    else:
                        kongbaikajiage1 = cell_curr_value

                    hetong2qiyongriqi = sheet_curr.cell(i, 8).value

                    cell_curr_value = sheet_curr.cell(i, 9).value
                    if isinstance(cell_curr_value, str):
                        grhpingrijiage2 = 0
                    else:
                        grhpingrijiage2 = cell_curr_value
                    cell_curr_value = sheet_curr.cell(i, 10).value
                    if isinstance(cell_curr_value, str):
                        grhjierijiage2 = 0
                    else:
                        grhjierijiage2 = cell_curr_value
                    cell_curr_value = sheet_curr.cell(i, 11).value
                    if isinstance(cell_curr_value, str):
                        kongbaikajiage2 = 0
                    else:
                        kongbaikajiage2 = cell_curr_value

                    gerenhuafuwu = sheet_curr.cell(i, 12).value
                    fuwumingcheng = sheet_curr.cell(i, 13).value
                    fuwuleixingbiaoshi = sheet_curr.cell(i, 14).value
                    xinpianka = sheet_curr.cell(i, 15).value
                    gongjiqueren = sheet_curr.cell(i, 16).value

                    if int(priceid) > 0:  # testing
                        # 插入数据
                        print(kapianmingcheng)
                        self.scr.insert(END, "基础数据表（price）数据导入: " + str(kapianmingcheng) + ".\n")
                        self.master.update()

            print('=' * 40)
            print('共导入了 ', i - int_first_row + 1, '行数据.')
            self.scr.insert(END, "基础数据表（price）数据导入.." + str(i - int_first_row + 1) + "行数据..\n")
            self.master.update()


    # 辅料入库反馈文件处理
    def fuliaoruku_file_proc(self, txtfilename, xlsfilename):
        if not os_path_exists(xlsfilename):
            print("文件不存在：", xlsfilename)
            logger.info("文件不存在："+ xlsfilename)
            return_message = messagebox.askquestion(title='提示',
                                                    message='无找到文件' + xlsfilename + '，继续？')  # return yes/no
            return (return_message)

        txtfilename = os.path.join(self.savefile_dir,txtfilename)
        #txt_open_file = open(txtfilename,'w+')

        int_first_row = 2
        # day_column_start = 7  # 日数据开始位置

        print("打开数据文件...")
        print(xlsfilename)
        logger.info(xlsfilename)
        self.scr.insert(END, "打开Excel表格数据...\n")
        self.master.update()

        workbook = xlrd.open_workbook(xlsfilename)
        sheet_curr = workbook.sheet_by_name('辅料')
        logger.info('sheet 辅料')
        int_sheet_nrows = sheet_curr.nrows
        int_sheet_ncols = sheet_curr.ncols
        print('sheetname & lines:', sheet_curr, int_sheet_nrows)
        str_split_string = '|&|'
        data_line_count  = 0


        # 首行日期查找
        date_position = 0
        for j in range(12, int_sheet_ncols ):
            cell_value_rukuriqi = sheet_curr.cell(0, j).value
            xls_date = xldate_as_tuple(cell_value_rukuriqi, 0)
            date_str = str(xls_date[0])
            if xls_date[1] < 10:
                date_str = date_str + '0' + str(xls_date[1])
            else:
                date_str = date_str + str(xls_date[1])
            if xls_date[2] < 10:
                date_str = date_str + '0' + str(xls_date[2])
            else:
                date_str = date_str + str(xls_date[2])
            compare_data_str = self.svar_proc_time1.get()
            if date_str == compare_data_str:
                date_position = j

        if date_position == 0 :
            self.scr.insert(END, "EXCEL表格无法查找到对应日期" + self.svar_proc_time1.get() + ".\n")
            self.master.update()
            return ('no')

        txt_open_file = open(txtfilename,'w+')

        for i in range(int_first_row, int_sheet_nrows):
            cell_curr_value = sheet_curr.cell(i, 0).value
            # print('i: ',i)
            if True:  # not isinstance(cell_curr_value,str):         #判断数据是否最后一行
                order_id = sheet_curr.cell(i, 0).value
                waibaoshangkucunbianhao = sheet_curr.cell(i, 2).value

                int_rukushuliang = 0
                rukushuliang = '0.0'

                cell_value_rukushuliang = sheet_curr.cell(i, date_position).value
                rukushuliang = cell_value_rukushuliang
                if isinstance(rukushuliang,float):
                    if round(rukushuliang*100) == round(rukushuliang) * 100 :
                        int_rukushuliang = round(rukushuliang)
                    else:
                        self.scr.insert(END, '包含小数，请注意。。。' + "\n")
                if isinstance(rukushuliang,str):
                    if rukushuliang.isdigit():
                        int_rukushuliang = int(rukushuliang)
                    else:
                        int_rukushuliang = 0

                str_merge = 'DATA' + str_split_string + order_id + str_split_string + str(int_rukushuliang) + str_split_string + waibaoshangkucunbianhao + str_split_string
                if int_rukushuliang >0:
                    txt_open_file.writelines(str_merge)
                    txt_open_file.writelines('\n')
                    data_line_count = data_line_count + 1

                    self.scr.insert(END, str(str_merge) + "\n")
                    self.master.update()
                    logger.info(str_merge)

        str_merge = 'TLRL' + str_split_string + str(data_line_count) + str_split_string
        txt_open_file.writelines(str_merge)
        txt_open_file.writelines('\n')
        logger.info(str_merge)

        txt_open_file.close()
        print('=' * 40)
        self.scr.insert(END, "文件输出..\n" )
        self.scr.insert(END, txtfilename + '\n' )
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
        self.scr.insert(END, "开始读取数据...   "+xlsfilename+"\n")
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
            self.scr.insert(END, ('打开表格sheet : ' + str_proc_date_month) + "\n")
        except:
            logger.info('无法打开表格sheet: ' + str_proc_date_month)
            self.scr.insert(END, ('无法打开表格sheet : ' + str_proc_date_month) + "\n")
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
        for j in range(15, int_sheet_ncols,3): #步长为3
            cell_value_rukuriqi = sheet_curr.cell(0, j).value
            xls_date = xldate_as_tuple(cell_value_rukuriqi, 0)
            date_str = str(xls_date[0])
            if xls_date[1] < 10:
                date_str = date_str + '0' + str(xls_date[1])
            else:
                date_str = date_str + str(xls_date[1])
            if xls_date[2] < 10:
                date_str = date_str + '0' + str(xls_date[2])
            else:
                date_str = date_str + str(xls_date[2])
            compare_data_str = self.svar_proc_time1.get()
            if date_str == compare_data_str:
                date_position = j

        if date_position == 0 :
            self.scr.insert(END, "EXCEL表格无法查找到对应日期" + self.svar_proc_time1.get() + ".\n")
            self.master.update()
            return ('no')

        txt_open_file = open(txtfilename,'w+')

        for i in range(int_first_row, int_sheet_nrows):
            cell_curr_value = sheet_curr.cell(i, 0).value
            logger.info(cell_curr_value)
            #int_chejianmeirichukuliang = 0
            #if True:  # not isinstance(cell_curr_value,str):         #判断数据是否最后一行
            if len(str(cell_curr_value)) > 0:  # not isinstance(cell_curr_value,str):         #判断数据是否最后一行
                yinhang_fuliaobianhao = sheet_curr.cell(i, 2).value #'银行辅料编号'
                fuliaobianhao = sheet_curr.cell(i, 1).value
                dangqiankucun = sheet_curr.cell(i, 14).value #现库存量（仓库+车间库存数）

                if isinstance(dangqiankucun,float):
                    int_dangqiankucun = round(dangqiankucun)

                chejianmeirichukuliang = sheet_curr.cell(i, date_position+2).value #数值在右移 2 位
                chejianmeirichukuliang = chejianmeirichukuliang
                if isinstance(chejianmeirichukuliang,float):
                    int_chejianmeirichukuliang = round(chejianmeirichukuliang)
                else:
                    int_chejianmeirichukuliang = 0
                str_merge = 'DATA' + str_split_string + yinhang_fuliaobianhao + str_split_string + fuliaobianhao + str_split_string + str(int_chejianmeirichukuliang) +str_split_string
                str_merge = str_merge + str(int_dangqiankucun) + str_split_string
                #if int_chejianmeirichukuliang >0 and len(fuliaobianhao) > 0:
                if int_chejianmeirichukuliang >0:
                    txt_open_file.writelines(str_merge)
                    txt_open_file.writelines('\n')

                    data_line_count = data_line_count +1
                    self.scr.insert(END, str(str_merge) + "\n")
                    logger.info(str_merge)
                    self.master.update()

        if data_line_count <1 :
            self.scr.insert(END, "\n注意： 0 条数据数据写入文件...\n" )
            self.scr.insert(END, txtfilename + '\n' )
            self.master.update()
        else:
            str_merge = 'TLRL' + str_split_string + str(data_line_count) + str_split_string
            logger.info(str_merge)
            txt_open_file.writelines(str_merge)
            txt_open_file.writelines('\n')
            self.scr.insert(END, str_merge)

        txt_open_file.close()
        self.scr.insert(END, "\n数据已写入文件...\n" )
        self.scr.insert(END, txtfilename + '\n' )
        self.scr.update()

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
        cp.read('配置文件.ini', encoding='gbk')
        str_kehu_name = cp.get('客户', '客户名称')

        try:
            self.customer_sname = cp.get('客户', 'sname')
            self.file_from_fuliaokucun = cp.get(str_kehu_name, '辅料库存表')
            #self.Holiday = cp.get(str_kehu_name, '节假日')
            self.file_from_dingdangenzong = cp.get(str_kehu_name, '订单跟踪表')
            self.work_dir = cp.get(str_kehu_name, '工作目录')
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
        label_dingdangenzong_filename.place(x=620, y=30)

        str_temp_find_filename = self.find_filename(self.work_dir,self.file_from_dingdangenzong)
        if str_temp_find_filename == None:
            self.svar_dingdanggenzong_filename.set('没有找到文件'+self.file_from_dingdangenzong)
        else:
            self.svar_dingdanggenzong_filename.set(str_temp_find_filename)

        entry_dingdangenzong_filename = Entry(fm1, textvariable=self.svar_dingdanggenzong_filename, width=40, font=('Arial', 12))
        entry_dingdangenzong_filename.place(x=620, y=55)


        label_fuliaokucun_filename = Label(fm1, text='辅料库存表：', font=('Arial', 12))
        label_fuliaokucun_filename.place(x=620, y=100)

        str_temp_find_filename = self.find_filename(self.work_dir,self.file_from_fuliaokucun)
        if str_temp_find_filename == None:
            self.svar_fuliaokucun_filename.set('没有找到文件'+self.file_from_dingdangenzong)
        else:
            self.svar_fuliaokucun_filename.set(str_temp_find_filename)

        entry_fuliaokucun_filename = Entry(fm1, textvariable=self.svar_fuliaokucun_filename, width=40, font=('Arial', 12))
        entry_fuliaokucun_filename.place(x=620, y=125)

        svar_label_prompt = StringVar()
        svar_label_prompt.set('客户名称：')

        label_author = Label(fm1, text='by流程与信息化部IT. Dec,2019', font=('Arial', 9))
        label_author.place(x=820, y=740)

        self.scr = scrolledtext.ScrolledText(fm1, width=80, height=48)
        self.scr.place(x=20, y=100)

        btn_barcode_init = Button(fm1, text='入库反馈文件', command=self.command_btn_run_ruku)
        btn_barcode_init.place(x=620, y=240)

        btn_barcode_init = Button(fm1, text='出库反馈文件', command=self.command_btn_run_chuku)
        btn_barcode_init.place(x=620, y=300)


        btn_barcode_init = Button(fm1, text=' 退  出 ', command=self.command_btn_exit)
        btn_barcode_init.place(x=620, y=420)

    # 退出键
    def command_btn_exit(self):
        self.master.destroy()

    # 主功能键
    def command_btn_run_ruku(self):

        self.scr.delete(1.0,END)

        label_tips1_filename = Label(self.master, text='读取订单跟踪表... ', font=('Arial', 12))
        label_tips1_filename.place(x=620, y=530)

        self.file_from_dingdangenzong = self.svar_dingdanggenzong_filename.get()
        self.file_from_fuliaokucun = self.svar_fuliaokucun_filename.get()

        str_timestamp = self.svar_proc_time1.get()

        str_temp_last_datetime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        str_ru_filename = '02_'+str_temp_last_datetime + '_frrsp.txt'

        try:
            if self.fuliaoruku_file_proc(str_ru_filename, self.file_from_dingdangenzong) == 'no':
                return (1)
        except Exception as err_message:
            print(err_message)
            self.scr.insert(END, err_message )
            self.scr.update()
            logger.error(err_message.__str__())
            logger.exception(sys.exc_info())

        label_tips1_filename = Label(self.master, text='完成...                     ', font=('Arial', 12))
        label_tips1_filename.place(x=620, y=530)

        return 0

    def command_btn_run_chuku(self):

        self.scr.delete(1.0,END)
        label_tips1_filename = Label(self.master, text='读取辅料库存表... ', font=('Arial', 12))
        label_tips1_filename.place(x=620, y=530)
        self.file_from_dingdangenzong = self.svar_dingdanggenzong_filename.get()
        self.file_from_fuliaokucun = self.svar_fuliaokucun_filename.get()
        str_timestamp = self.svar_proc_time1.get()

        str_temp_last_datetime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        str_chu_filename = '02_' + str_temp_last_datetime + '_fs.txt'

        try:
            if self.fuliao_chuku_file_proc(str_chu_filename, self.file_from_fuliaokucun) == 'no':
                return (1)
        except Exception as err_message:
            print(err_message)
            self.scr.insert(END, err_message)
            self.scr.update()
            logger.error(err_message.__str__())
            logger.exception(sys.exc_info())

        label_tips1_filename = Label(self.master, text='完成...                     ', font=('Arial', 12))
        label_tips1_filename.place(x=620, y=530)
        return 0

if __name__ == '__main__':

    set_logging()

    main_window = Tk()
    main_window.title('光大制卡业务库存反馈文件生成工具 v.2001191026')

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
