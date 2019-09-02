from tkinter import *
from configparser import ConfigParser
from tkinter import scrolledtext,Canvas,PhotoImage,Label,StringVar,Entry, Button,END, DISABLED, Toplevel  # 导入滚动文本框的模块
from os.path import exists as os_path_exists
import xlrd
import datetime
from sqlite3 import connect as sqlite3connect
from openpyxl import load_workbook
import os
import logging
from logging.handlers import RotatingFileHandler
from openpyxl.styles import Border, Side #设置字体和边框需要的模块

xl_border = Border(left=Side(style='thin',color='FF000000'),right=Side(style='thin',color='FF000000'),top=Side(style='thin',color='FF000000'),bottom=Side(style='thin',color='FF000000'),diagonal=Side(style='thin',color='FF000000'),diagonal_direction=0,outline=Side(style='thin',color='FF000000'),vertical=Side(style='thin',color='FF000000'),horizontal=Side(style='thin',color='FF000000'))

def set_logging():
    global logger
    logger = logging.getLogger('balance_logger')
    handler = RotatingFileHandler('日志记录.log', maxBytes=5000000, backupCount=6)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    formatter = logging.Formatter('%(asctime)-12s %(filename)s %(lineno)d %(message)s')
    handler.setFormatter(formatter)


class App():
    def __init__(self, master):

        self.svar_proc_time1 = StringVar()
        self.svar_cangku_filename = StringVar()
        self.svar_kehumingcheng = StringVar()
        self.svar_proc_time2 = StringVar()
        self.svar_youjiqingdan_filename = StringVar()
        self.svar_jichu_filename = StringVar()
        self.svar_label_prompt = StringVar()

        self.master = master
        self.customer_sname = ''
        self.sqlconn = sqlite3connect("db_dz.db3")
        self.sqlconn.isolation_level = None  # 这个就是事务隔离级别，默认是需要自己commit才能修改数据库，置为None则自动每次修改都提交,否则为""
        self.Holiday = []
        self.data_dir = ''
        self.file_from_cangkujxc = ''
        self.file_from_youjiqingdan = ''
        self.file_from_jichu = ''
        self.curr_month = ''
        self.initWidgets(master)

    def proc_folder(self, customer, work_dir):

        str_sql = "delete from hztj"
        self.sqlconn.execute(str_sql)
        self.sqlconn.commit()
        print("清空原有汇总统计数据（hztj）数据...")

        for parent, dirnames, filenames in os.walk(work_dir, followlinks=True):
            for filename in filenames:
                file_path = os.path.join(parent, filename)
                if '汇总统计' in filename:
                    print('文件名：%s' % filename)
                    print('文件完整路径：%s\n' % file_path)
                    self.xls_db('gsnx', file_path)

    def pricexls_db(self, customer, xlsfilename):

        if not os_path_exists(xlsfilename):
            print("文件不存在：", xlsfilename)
            return_message = messagebox.askquestion(title='提示',
                                                    message='无找到文件' + xlsfilename + '，继续？')  # return yes/no
            return (return_message)

        int_first_row = 2
        # day_column_start = 7  # 日数据开始位置

        str_sql = "delete from price"
        self.sqlconn.execute(str_sql)
        self.sqlconn.commit()
        print("清空原有对账价格基础表（price）数据...")
        print(xlsfilename)
        self.scr.insert(1.0, "清空原有对账价格基础表（price）数据...\n")
        self.master.update()

        workbook = xlrd.open_workbook(xlsfilename)
        sheetsname = workbook.sheet_names()  # 获取excel里的工作表sheet名称数组

        # sheetsname.sort(reverse=True)
        ##            for str_curr_sheet_name in sheetsname:
        ##

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
                    str_sql = "insert into price(id,kamiandaima,kapianbanbenhao,wuliao,mingcheng,grhpingrijiage1,grhjierijiage1,\
kongbaikajiage1,hetong2qiyongriqi,grhpingrijiage2,grhjierijiage2,kongbaikajiage2,gerenhuafuwu,fuwumingcheng,\
fuwuleixinbiaoshi,xinpianka,gongyiqueren)"
                    str_sql = str_sql + "values(" + str(
                        priceid) + ",'" + kamiandaima + "','" + kapianbanbenhao + "','" + wuliao + "','" + \
                              kapianmingcheng + "'," + str(grhpingrijiage1) + "," + str(grhjierijiage1) + "," + str(
                        kongbaikajiage1) + ",'" + str(hetong2qiyongriqi) + "'," + \
                              str(grhpingrijiage2) + "," + str(grhjierijiage2) + "," + str(
                        kongbaikajiage2) + ",'" + gerenhuafuwu + "','" + fuwumingcheng + "','" + \
                              fuwuleixingbiaoshi + "','" + xinpianka + "','" + gongjiqueren + "')"
                    print(kapianmingcheng)
                    self.scr.insert(1.0, "基础数据表（price）数据导入: " + str(kapianmingcheng) + ".\n")
                    self.master.update()

                    self.sqlconn.execute(str_sql)
                    # 如果隔离级别不是自动提交就需要手动执行commit
                    self.sqlconn.commit()
        print('=' * 40)
        print('共导入了 ', i - int_first_row + 1, '行数据.')
        self.scr.insert(1.0, "基础数据表（price）数据导入.." + str(i - int_first_row + 1) + "行数据..\n")
        self.master.update()

    def find_filename(self, curr_path, curr_filename_path):
        list_files = []
        for parent, dirnames, filenames in os.walk(curr_path, followlinks=True):
            for filename in filenames:
                file_path = os.path.join(parent, filename)
                if curr_filename_path in filename:
                    print('文件名：%s' % file_path)
                    list_files.append(file_path)
        if len(list_files) > 0:
            return (list_files[0])
        else:
            return (None)

    def price_list_from_db(self, customer):
        sqlselect = self.sqlconn.cursor()

        str_sql = "SELECT kamiandaima,kapianbanbenhao,wuliao,mingcheng,grhpingrijiage1,grhjierijiage1,kongbaikajiage1,hetong2qiyongriqi,grhpingrijiage2,grhjierijiage2,kongbaikajiage2 from price "
        # print(str_sql)
        sqlcursor = sqlselect.execute(str_sql)
        curr_price_list = []
        for row in sqlcursor:
            # print("wuliao,name = ", row[0],row[1])
            curr_price_list.append([row[0], row[1], row[2], row[3], row[4], row[5],row[6],row[7],row[8],row[9],row[10], 0])  # 最后一个0，为预留用于存节假日发卡数
        # self.sqlconn.close()
        # 不通过人工关闭SQL
        return (curr_price_list)

    def db_xls(self, customer, xlsfilename):

        time1_proc = str(self.svar_proc_time1.get())
        time2_proc = str(self.svar_proc_time2.get())

        self.scr.insert(1.0, "准备生成客户对账文件: " + customer + "对账周期: " + str(time1_proc) +' - ' +str(time2_proc)+ "\n")
        self.master.update()

        int_first_row = 3
        list_price = self.price_list_from_db(customer)

        list_price_onlycode  = []       # 现此变量暂时无用，只用于记录日志。
        for temp in list_price:
            list_price_onlycode.append(temp[0])
        logger.info ('代码列表： '+str(list_price_onlycode))

        # 获取明细表数据
        sqlselect = self.sqlconn.cursor()
        str_sql = "SELECT chanpinbianma,chanpinmingcheng,jigoudaima,danweimingcheng,shuliang,youjiriqi from hztj where kehu='" + customer + "'"
        # print(str_sql)
        sqlcursor = sqlselect.execute(str_sql)

#导出明细表begin
        xlsfilename = self.data_dir + 'gsnxxykdz.xlsx'
        workbook = load_workbook(xlsfilename)  # 打开excel文件
        worksheel = workbook['明细表']  # 根据Sheet1这个sheet名字来获取该sheet
        i = 0
        for row in sqlcursor:
            row_chanpinbianma = row[0]
            #print(row)
            rowprice = 0
            for temp_bianma in list_price:
                if row_chanpinbianma == temp_bianma[0]:
                    rowprice = temp_bianma[4]
                    #break


            if not (row_chanpinbianma in list_price_onlycode):
                logger.info('在价格基础表内查找不到对应的 ' + '产品编码 ' + str(row_chanpinbianma))
            #worksheel = workbook.worksheets[0]
            worksheel.cell(int_first_row + i, 1).value = i + 1
            worksheel.cell(int_first_row + i, 1).border = xl_border
            worksheel.cell(int_first_row + i, 2).value = row[0]  # 产品编码
            worksheel.cell(int_first_row + i, 2).border = xl_border
            worksheel.cell(int_first_row + i, 3).value = row[1]  # 产品名称
            worksheel.cell(int_first_row + i, 3).border = xl_border
            worksheel.cell(int_first_row + i, 4).value = row[2]  # 数量
            worksheel.cell(int_first_row + i, 4).border = xl_border
            worksheel.cell(int_first_row + i, 5).value = row[3]  # 单位名称
            worksheel.cell(int_first_row + i, 5).border = xl_border
            worksheel.cell(int_first_row + i, 6).value = row[4]  # 产品名称
            worksheel.cell(int_first_row + i, 6).border = xl_border
            worksheel.cell(int_first_row + i, 7).value = row[5]  # 邮寄日期
            worksheel.cell(int_first_row + i, 7).border = xl_border
            worksheel.cell(int_first_row + i, 8).value = rowprice  # 价格
            worksheel.cell(int_first_row + i, 8).border = xl_border
            worksheel.cell(int_first_row + i, 9).value = rowprice * row[4] # 价格
            worksheel.cell(int_first_row + i, 9).border = xl_border
            i = i + 1 #下一行

        # worksheel.cell(1,1).value = curr_month+'空白卡结算（东信和平）'
        #worksheel.cell(1, 1).value = curr_month + '空白卡结算（东信和平）'
        worksheel.delete_rows(int_first_row + i + 1, 100 - i - 1)
        worksheel.cell(int_first_row + i , 6).value = '=SUM(F3:F' + str(int_first_row + i-1) + ')'
        worksheel.cell(int_first_row + i , 9).value = '=SUM(I3:I' + str(int_first_row + i-1) + ')'
        workbook.save(self.data_dir + '..\\输出文件\\甘肃农信制卡清单对账明细表' + str(time2_proc) + '.xlsx')  # 保存修改后的excel
        # 空白卡数据文件保存
        self.scr.insert(1.0, "空白卡对账明细文件已保存：\\输出文件\\甘肃农信制卡清单对账明细表" + str(time2_proc) + ".xlsx" + "\n")
        self.master.update()
# 导出明细表end



        # print(curr_wuliao_list)
        list_return_from_db = []


# 保存个人化对账单excel文件

    def xls_db(self, customer, xlsfilename):
        # if not (customer in self.customers):
        #     print('不存在该客户格式资料')
        #     return ('不存在该客户格式资料')
#        self.scr = scrolledtext.ScrolledText(fm1)
#        self.scr.place(x=20, y=100)
        if customer == 'gsnx':
            int_first_row = 2

            workbook = xlrd.open_workbook(xlsfilename)
            sheetsname = workbook.sheet_names()  # 获取excel里的工作表sheet名称数组

            sheetsname.sort(reverse=True)

            str_curr_sheet_name = sheetsname[0]

            sheet_curr = workbook.sheet_by_name(str_curr_sheet_name)
            ##            sheet = excel.sheet_by_index(0) #根据下标获取对应的sheet表

            int_sheet_nrows = sheet_curr.nrows

            print('lines: ', int_first_row, int_sheet_nrows)
            if sheet_curr.cell(1, 0).value != '序号':
                print('单元格位置有误，A2应为文字“序号” ', sheet_curr.cell(1, 0).value)
            else:
                for i in range(int_first_row, int_sheet_nrows):
                    xuhao = sheet_curr.cell(i, 0).value
                    chanpinbianma = sheet_curr.cell(i, 1).value
                    chanpinmingcheng = sheet_curr.cell(i, 2).value
                    jigoudaima = sheet_curr.cell(i, 3).value
                    danweimingcheng = sheet_curr.cell(i, 4).value
                    shuliang = sheet_curr.cell(i, 5).value
                    youjiriqi = sheet_curr.cell(i, 6).value

                    # 写入表格前部主要数据
                    # 插入数据
                    str_sql = "insert into hztj(id,customer,chanpinbianma,chanpinmingcheng,jigoudaima,danweimingcheng,shuliang,youjiriqi) \
values('" + xuhao + "','" +customer +"','"+ chanpinbianma + "','" + chanpinmingcheng + "','" + jigoudaima + "','" + danweimingcheng + "'," + str(
                        shuliang) + ",'" + youjiriqi + "')"
                    print('test',danweimingcheng)
                    self.scr.insert(1.0,  danweimingcheng+': compare ok\n')
                    self.master.update()
                    # print(str_sql)
                    self.sqlconn.execute(str_sql)
                    # 如果隔离级别不是自动提交就需要手动执行commit
                    self.sqlconn.commit()

    def initWidgets(self, fm1):

        cp = ConfigParser()
        cp.read('配置文件.ini', encoding='gbk')
        str_kehu_name = cp.get('客户', '客户名称')
        self.customer_sname = cp.get('客户', 'sname')
        kehu_conf_jxc = cp.get(str_kehu_name, '仓库进销存')
        self.Holiday = cp.get(str_kehu_name, '节假日')
        self.file_from_cangkujxc = cp.get(str_kehu_name, '仓库进销存')
        self.file_from_youjiqingdan = cp.get(str_kehu_name, '邮寄清单')
        self.file_from_jichu = cp.get(str_kehu_name, '基础数据文件')
        # except Exception as err_message:
        #     print(err_message)

        print('host: ', str_kehu_name)
        print(self.file_from_youjiqingdan)

        # 创建第一个容器
        #        fm1 = Frame(self.master,width=1024,height=1700)
        # 该容器放在左边排列
        #        fm1.pack(side=LEFT )
        # fm1.place(x=5, y=55)
        # 向fm1中添加3个按钮
        # 设置按钮从顶部开始排列，且按钮只能在垂直（X）方向填充

        label_kehumingcheng = Label(fm1, text='客户名称：', font=('Arial', 12))
        label_kehumingcheng.place(x=20, y=30)
        self.svar_kehumingcheng.set(str_kehu_name)
        entry_kehumingcheng = Entry(fm1, textvariable=self.svar_kehumingcheng, width=30, font=('Arial', 12))
        entry_kehumingcheng.place(x=20, y=55)

        label_proc_time = Label(fm1, text='对账时间：', font=('Arial', 12))
        label_proc_time.place(x=300, y=30)

        temp_last_datetime = datetime.date.today() - datetime.timedelta(days=10)
        self.svar_proc_time1.set(temp_last_datetime.strftime('%Y%m'))

        entry_proc_time1 = Entry(fm1, textvariable=self.svar_proc_time1, width=12, font=('Arial', 12))
        entry_proc_time1.place(x=300, y=55)

        label_proc_time = Label(fm1, text='-', font=('Arial', 12))
        label_proc_time.place(x=420, y=55)

        self.svar_proc_time2.set('20190630')
        entry_proc_time2 = Entry(fm1, textvariable=self.svar_proc_time2, width=12, font=('Arial', 12))
        entry_proc_time2.place(x=440, y=55)

        label_cangku_filename = Label(fm1, text='仓库进销存文件名：', font=('Arial', 12))
        label_cangku_filename.place(x=620, y=30)

        self.svar_cangku_filename.set(self.file_from_cangkujxc)
        entry_cangku_filename = Entry(fm1, textvariable=self.svar_cangku_filename, width=40, font=('Arial', 12))
        entry_cangku_filename.place(x=620, y=55)

#        label_youjiqingdan_filename = Label(fm1, text='邮寄清单文件名：', font=('Arial', 12))
#        label_youjiqingdan_filename.place(x=620, y=80)
#        svar_youjiqingdan_filename = StringVar()
#        svar_youjiqingdan_filename.set(self.file_from_youjiqingdan)
#        entry_youjiqingdan_filename = Entry(fm1, textvariable=svar_youjiqingdan_filename, width=40, font=('Arial', 12))
#        entry_youjiqingdan_filename.place(x=620, y=105)

        label_jichu_filename = Label(fm1, text='价格等基础数据文件名：', font=('Arial', 12))
        label_jichu_filename.place(x=620, y=130)
        self.svar_jichu_filename.set(self.file_from_jichu)
        entry_jichu_filename = Entry(fm1, textvariable=self.svar_jichu_filename, width=40, font=('Arial', 12))
        entry_jichu_filename.place(x=620, y=155)

        svar_label_prompt = StringVar()
        svar_label_prompt.set('客户名称：')

        label_author = Label(fm1, text='by流程与信息化部ITjc. August,2019', font=('Arial', 9))
        label_author.place(x=820, y=770)

        self.scr = scrolledtext.ScrolledText(fm1, width=80, height=48)
        self.scr.place(x=20, y=100)

        #        btn_barcode_check = Button(fm1, text='导入仓库数据', command=self.barcode_check)
        #        btn_barcode_check.place(x=650, y=160)
        btn_barcode_init = Button(fm1, text='导入数据&输出对账单', command=self.command_btn_run)
        btn_barcode_init.place(x=620, y=200)

    def command_btn_run(self):

        self.curr_month = self.svar_proc_time1.get()
        self.file_from_cangkujxc = self.svar_cangku_filename.get()
        print('curr_month', self.curr_month)
        print('file_from_cangkujxc', self.file_from_cangkujxc)
        print('customer_sname', self.customer_sname)

#        if self.pricexls_db(self.customer_sname, self.file_from_jichu) == 'no':
#            return (1)

        work_dir = '..\\仓库文件\\'
#        self.proc_folder(self.customer_sname, work_dir)
        #甘肃农信有多个文件夹、多个文件excel需导入到数据库，使用处理文件夹方式导入明细数据

        self.db_xls(self.customer_sname, 'gsnxxykdz.xlsx')
        return 0


if __name__ == '__main__':

    set_logging()

    main_window = Tk()
    main_window.title('对账单生成工具 v.19090209')

    # 设定窗口的大小(长 * 宽)，显示窗体居中，winfo_xxx获取系统屏幕分辨率。
    sw = main_window.winfo_screenwidth()
    sh = main_window.winfo_screenheight()
    ww = 1024
    wh = 800
    x = (sw - ww) / 2
    y = (sh - wh) / 2
    main_window.geometry("%dx%d+%d+%d" % (ww, wh, x, y))  # 这里的乘是小x
    display = App(main_window)
    main_window.mainloop()
