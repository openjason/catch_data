'''
功能：2020年1月考勤数据转换脚本。
'''
from tkinter import *
from tkinter import messagebox,scrolledtext,Canvas,PhotoImage,Label,StringVar,Entry, Button,END, DISABLED, Toplevel  # 导入滚动文本框的模块
from os.path import exists as os_path_exists
import xlrd
import datetime
import os
import logging
from logging.handlers import RotatingFileHandler

#设置日志文件配置参数
def set_logging():
    global logger
    logger = logging.getLogger('balance_logger')
    handler = RotatingFileHandler('日志记录.log', maxBytes=5000000, backupCount=9)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    formatter = logging.Formatter('%(asctime)-12s %(filename)s %(lineno)d %(message)s')
    handler.setFormatter(formatter)

#定义类，脚本主要更能
class App():
    def __init__(self, master):

        self.svar_proc_time1 = StringVar()
        self.svar_cangku_filename = StringVar()
        self.svar_kehumingcheng = StringVar()
        self.svar_proc_time2 = StringVar()
        self.svar_youjiqingdan_filename = StringVar()
        self.svar_jichu_filename = StringVar()
        self.svar_label_prompt = StringVar()
    # 脚本指定数据库名称sqlite3("db_dz.db3")
        self.master = master
        self.customer_sname = ''
        self.userid_list = []
        self.data_dir = ''
        self.file_from_cangkujxc = ''
        self.file_from_youjiqingdan = ''
        self.file_from_jichu = ''
        self.curr_month = ''
        self.initWidgets(master)

# 按文件夹统计符合条件文件列表，逐个文件导入数据库
    def fix_recorder_proc(self, work_dir):
        if len(self.userid_list) < 1 :
            self.scr.insert(1.0, "error请先运行更新员工信息 ...\n")
            self.master.update()
            return(2)

        buqian_txt_file = open('buqian.txt','w')
        for parent, dirnames, filenames in os.walk(work_dir, followlinks=True):
            for filename in filenames:
                file_path = os.path.join(parent, filename)
                if '#' in filename:
                    logger.info('文件名: '+ file_path)
                    print('文件名: '+ filename)
                    temp = filename.split('#')
                    username=temp[0]
                    userid=temp[1]
                    if userid[-4:] == '.txt':
                        userid = userid[:-4]
                    else:
                        logger.info("error文件名格式错： "+filename)
                        self.scr.insert(1.0, "error文件名格式错： "+filename+"...\n")
                        self.master.update()

                    self.scr.insert(1.0, "处理： "+filename+"...\n")
                    self.master.update()

                    #检查 工号 存在 begin
                    testid = '00'
                    for temp_userid in self.userid_list:
                        temp_id =temp_userid[0]
                        if userid == temp_id :
                            testid = userid
                            break
                    if testid== '00':
                            self.scr.insert(1.0, "无匹配工号，姓名： " + str(username)+"\n")
                            self.master.update()   
                    #检查 工号 存在 end


                    with open(file_path, 'r', encoding='utf-8') as f:
                        for txtfile_line in f.readlines():
                            txtfile_line = txtfile_line.strip()
                            txtfile_line = txtfile_line.replace('：',':')
                            #打卡文件 行 处理
                            logger.info(txtfile_line)
                            print(txtfile_line)
                            line_proc_list = txtfile_line.split('#')
                            if len(line_proc_list)>3:
                                logger.info('error line format error: '+txtfile_line)
                            #检查日期格式正确 begin
                            try:
                                daka_date = line_proc_list[0]
                                daka_date_format = datetime.datetime.strptime(daka_date, "%Y-%m-%d").date()
                                if daka_date_format < datetime.datetime.strptime('2020-02-01', "%Y-%m-%d").date() \
                                    or daka_date_format > datetime.datetime.strptime('2020-02-29', "%Y-%m-%d").date():
                                    self.scr.insert(1.0, 'error日期超出范围： '+str(daka_date)+'\n' )
                                    self.scr.update()
                                daka_date = daka_date_format.strftime('%Y-%m-%d')
                            except Exception as err_message:
                                print(err_message)
                                self.scr.insert(1.0, err_message)
                                self.scr.update()
                                logger.error(err_message.__str__())
                                logger.exception(sys.exc_info())
                                continue
                            #检查日期格式正确 end

                            if len(line_proc_list)>2:
                                daka_morning = line_proc_list[1]
                                daka_afternoon = line_proc_list[2]
                            else:
                                daka_morning = line_proc_list[1]
                                
                            #检查 上班 时间格式正确 begin
                            try:
                                daka_date_format = datetime.datetime.strptime('2020-01-01 '+daka_morning, "%Y-%m-%d %H:%M")
                                daka_morning = daka_date_format.strftime('%H:%M')
                            except Exception as err_message:
                                print(err_message)
                                self.scr.insert(1.0, err_message)
                                self.scr.update()
                                logger.error(err_message.__str__())
                                logger.exception(sys.exc_info())
                                continue
                           #检查 上班 时间格式正确 end

                            #检查 下班 时间格式正确 begin
                            try:
                                daka_date_format = datetime.datetime.strptime('2020-01-01 '+daka_afternoon, "%Y-%m-%d %H:%M")
                                daka_afternoon = daka_date_format.strftime('%H:%M')
                            except Exception as err_message:
                                print(err_message)
                                self.scr.insert(1.0, err_message)
                                self.scr.update()
                                logger.error(err_message.__str__())
                                logger.exception(sys.exc_info())
                                continue
                           #检查 下班 时间格式正确 end

                            buqian_txt_file.write(userid+' '+daka_date+' '+daka_morning+':00')
                            buqian_txt_file.write('\n')
                            if len(line_proc_list)>2:
                                buqian_txt_file.write(userid+' '+daka_date+' '+daka_afternoon+':00')
                                buqian_txt_file.write('\n')

                            
        buqian_txt_file.close()

    def dingding_data_ech(self, xlsfilename):
        if len(self.userid_list) < 1 :
            self.scr.insert(1.0, "error请先运行更新员工信息 ...\n")
            self.master.update()
            return (2)        
        if not os_path_exists(xlsfilename):
            print("文件不存在：", xlsfilename)
            return_message = messagebox.askquestion(title='提示',
                                                    message='无找到文件' + xlsfilename + '，继续？')  # return yes/no
            return (return_message)
        int_first_row = 3
        # 日数据开始位置
        print(xlsfilename)
        self.scr.insert(1.0, "钉钉数据"+xlsfilename+"...\n")
        self.master.update()
        workbook = xlrd.open_workbook(xlsfilename)
        sheetsname = workbook.sheet_names()  # 获取excel里的工作表sheet名称数组

        str_curr_sheet_name = sheetsname[0]

        sheet_curr = workbook.sheet_by_name(str_curr_sheet_name)
        int_sheet_nrows = sheet_curr.nrows
        int_sheet_ncols = sheet_curr.ncols
        
        logger.info('sheet size:')
        logger.info(int_sheet_nrows)
        logger.info(int_sheet_ncols)

        print('sheetname & lines:', str_curr_sheet_name, int_sheet_nrows)

        int_first_col = 6
        file_txt_kaoqin = open('nc.txt','w')
        curr_year_month = '2020-02-'
        match_list=[]
        for i in range(int_first_row, int_sheet_nrows):
            cell_curr_value = sheet_curr.cell(i, 0).value
            # print('i: ',i)
            #userid = sheet_curr.cell(i, 0).value
            username = sheet_curr.cell(i, 0).value
            logger.info(username)
            
            #匹配工号
            userid = '00'
            for temp_userid in self.userid_list:
                temp_j =temp_userid[1]
                if username == temp_j :
                    userid = temp_userid[0]
                    break
            if userid== '00':
                    self.scr.insert(1.0, "无匹配工号，姓名： " + str(username)+"\n")
                    self.master.update()   

            #self.scr.insert(1.0, "检查重名：\n")
            if username not in match_list:
                match_list.append(username)
            else:
                self.scr.insert(1.0, "重名.." + str(username)+"\n")
                self.master.update()   


            daka_line = ''
            for j in range(int_first_col, int_sheet_ncols):

                # 插入数据
                cell_value = sheet_curr.cell(i, j).value
                cell_value = cell_value.replace('\n','*')
                cell_value_cut = cell_value.replace('\n','*')
                cell_value = cell_value_cut.replace(' ','')
                #logger.info(cell_value)
                if len(cell_value)>0:
                    daka_line = daka_line+ str(cell_value)+'@'+str(j-5) +'#'
                    click_one_times = cell_value.split('*')
                    for click_one_time in click_one_times:                    
                        if (j-5) > 9:
                            curr_day = str(j-5)
                        else:
                            curr_day = '0' + str(j-5)
                        #file_txt_kaoqin.write(username+ userid+" "+curr_year_month+curr_day+' '+click_one_time+':00')
                        file_txt_kaoqin.write(userid+" "+curr_year_month+curr_day+' '+click_one_time+':00')
                        file_txt_kaoqin.write("\n")
                #self.scr.insert(1.0, "基础数据表（price）数据导入: " + str(username) + ".\n")
                #self.master.update()
            logger.info(daka_line)

        file_txt_kaoqin.close()
        print('=' * 40)
        print('共导入了 ', i - int_first_row + 1, '行数据.')
        self.scr.insert(1.0, "共导入了 .." + str(i - int_first_row + 1) + "行数据..\n")
        self.master.update()


# 从数据库导入价格（基础表），返回含价格信息列表
    def user_id_export_list(self, xlsfilename):

        if not os_path_exists(xlsfilename):
            print("文件不存在：", xlsfilename)
            return_message = messagebox.askquestion(title='提示',
                                                    message='无找到文件' + xlsfilename + '，继续？')  # return yes/no
            return (return_message)

        int_first_row = 1
        # day_column_start = 7  # 日数据开始位置
        self.userid_list = []

        print("清空原有staff 数据...")
        print(xlsfilename)
        self.scr.insert(1.0, "清空列表（staff）数据...\n")
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
                userid = sheet_curr.cell(i, 0).value
                username = sheet_curr.cell(i, 1).value

            
                if int(len(userid)) > 0:  # testing
                    # 插入数据
                    str_sql = "insert into staff(userid,username) values('" +str(userid) + "','" + str(username) + "')" 
                    #print(str_sql)
                    #self.scr.insert(1.0, "基础数据表（price）数据导入: " + str(username) + ".\n")
                    #self.master.update()

                    self.userid_list.append([userid,username])
                else:
                    self.scr.insert(1.0, "ERROR基础数据表（price）数据导入: " + str(username) + ".\n")
                    self.master.update()
        logger.info(self.userid_list)
        print('=' * 40)
        logger.info('共导入了 '+str(i - int_first_row + 1)+ '行数据.')
        print('共导入了 ', i - int_first_row + 1, '行数据.')
        self.scr.insert(1.0, "共导入了.." + str(i - int_first_row + 1) + "行数据..\n")
        self.master.update()

        match_list=[]
        self.scr.insert(1.0, "检查重名：\n")
      
        for temp_userid in self.userid_list:
            temp_j =temp_userid[1]
            if temp_j not in match_list:
                match_list.append(temp_j)
            else:
                self.scr.insert(1.0, "重名.." + str(temp_j)+"\n")
                self.master.update()   


# 程序主gui界面。
    def initWidgets(self, fm1):

        str_kehu_name = 'ep'
        
        self.customer_sname = 'ep'
        kehu_conf_jxc = '仓库进销存'
        self.Holiday = '节假日'
        self.file_from_cangkujxc = '仓库进销存'
        self.file_from_youjiqingdan = '邮寄清单'
        self.file_from_jichu = '基础数据文件'

        print('host: ', str_kehu_name)
        print(self.file_from_youjiqingdan)

        #label_kehumingcheng = Label(fm1, text='客户名称：', font=('Arial', 12))
        #label_kehumingcheng.place(x=20, y=30)
        #self.svar_kehumingcheng.set(str_kehu_name)
        #entry_kehumingcheng = Entry(fm1, textvariable=self.svar_kehumingcheng, width=30, font=('Arial', 12))
        #entry_kehumingcheng.place(x=20, y=55)

        #label_proc_time = Label(fm1, text='对账时间：', font=('Arial', 12))
        #label_proc_time.place(x=300, y=30)

        temp_last_datetime = datetime.date.today() - datetime.timedelta(days=10)

        #self.svar_proc_time1.set('20180201')
        #entry_proc_time1 = Entry(fm1, textvariable=self.svar_proc_time1, width=12, font=('Arial', 12))
        #entry_proc_time1.place(x=300, y=55)

        #label_proc_time = Label(fm1, text='-', font=('Arial', 12))
        #label_proc_time.place(x=420, y=55)


        #self.svar_proc_time2.set('20190630')
        #entry_proc_time2 = Entry(fm1, textvariable=self.svar_proc_time2, width=12, font=('Arial', 12))
        #entry_proc_time2.place(x=440, y=55)

        #label_cangku_filename = Label(fm1, text='仓库进销存文件名：', font=('Arial', 12))
        #label_cangku_filename.place(x=620, y=30)

        #self.svar_cangku_filename.set(self.file_from_cangkujxc)
        #entry_cangku_filename = Entry(fm1, textvariable=self.svar_cangku_filename, width=40, font=('Arial', 12))
        #entry_cangku_filename.place(x=620, y=55)


        #label_jichu_filename = Label(fm1, text='价格等基础数据文件名：', font=('Arial', 12))
        #label_jichu_filename.place(x=620, y=130)
        #self.svar_jichu_filename.set(self.file_from_jichu)
        #entry_jichu_filename = Entry(fm1, textvariable=self.svar_jichu_filename, width=40, font=('Arial', 12))
        #entry_jichu_filename.place(x=620, y=155)

        #svar_label_prompt = StringVar()
        #svar_label_prompt.set('客户名称：')

        label_author = Label(fm1, text='by流程与信息化部IT. Feb,2020', font=('Arial', 9))
        label_author.place(x=820, y=770)

        self.scr = scrolledtext.ScrolledText(fm1, width=80, height=54)
        self.scr.place(x=20, y=30)

        btn_id_import_init = Button(fm1, text='更新员工信息', command=self.command_id_import_run)
        btn_id_import_init.place(x=620, y=200)

        btn_dingding_exchage_run = Button(fm1, text='钉钉数据转换', command=self.command_dingding_ech_run)
        btn_dingding_exchage_run.place(x=620, y=270)

        btn_fix_rec_run = Button(fm1, text='补 签 卡', command=self.command_fix_recorder_run)
        btn_fix_rec_run.place(x=620, y=340)



        btn_barcode_init = Button(fm1, text=' 退  出 ', command=self.command_btn_exit)
        btn_barcode_init.place(x=620, y=500)




    # 退出键
    def command_btn_exit(self):
        self.master.destroy()

    # 导入员工工号
    def command_id_import_run(self):
        label_tips1_filename = Label(self.master, text='正在导入员工工号数据... ', font=('Arial', 12))
        label_tips1_filename.place(x=620, y=430)

        userid_filename = '在职人员信息表.xls'
        self.user_id_export_list(userid_filename)

    # 补签卡
    def command_fix_recorder_run(self):
        label_tips1_filename = Label(self.master, text='正在导入补签卡数据... ', font=('Arial', 12))
        label_tips1_filename.place(x=620, y=430)

        work_dir = '补签卡\\'
        self.fix_recorder_proc(work_dir)

    # 主功能键
    def command_dingding_ech_run(self):

        label_tips1_filename = Label(self.master, text='正在处理钉钉数据... ', font=('Arial', 12))
        label_tips1_filename.place(x=620, y=430)

        file_from_dingding = '东信和平科技股份有限公司_打卡时间表.xlsx'

        self.dingding_data_ech(file_from_dingding)

        label_tips1_filename = Label(self.master, text='完成...                     ', font=('Arial', 12))
        label_tips1_filename.place(x=620, y=430)

        return 0


if __name__ == '__main__':

    set_logging()

    main_window = Tk()
    main_window.title('临时考勤数据处理工具 v.02292315')

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
