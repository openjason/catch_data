#-*- coding:utf-8 -*-
#date: V200723
#auth: openjc

from configparser import ConfigParser
import sys,os
from shutil import copyfile
import time
import xlrd, xlwt
import logging
from logging.handlers import RotatingFileHandler

from tkinter import Tk,filedialog
from tkinter import MULTIPLE,Message,Listbox,messagebox,Label,StringVar,Scrollbar, Button,END, DISABLED, Toplevel,SUNKEN,LEFT,Y  # 导入滚动文本框的模块

#xl_border = Border(left=Side(style='thin',color='FF000000'),right=Side(style='thin',color='FF000000'),top=Side(style='thin',color='FF000000'),bottom=Side(style='thin',color='FF000000'),diagonal=Side(style='thin',color='FF000000'),diagonal_direction=0,outline=Side(style='thin',color='FF000000'),vertical=Side(style='thin',color='FF000000'),horizontal=Side(style='thin',color='FF000000'))

dlevel = 1

#设置日志文件配置参数
def set_logging():
    global logger
    logger = logging.getLogger('balance_logger')
    handler = RotatingFileHandler('日志记录.log', maxBytes=5000000, backupCount=3)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    formatter = logging.Formatter('%(asctime)-12s %(filename)s %(lineno)d %(message)s')
    handler.setFormatter(formatter)

#定义类，脚本主要更能
class App():
    def __init__(self, master):

    # 脚本指定数据库名称sqlite3("db_dz.db3")
        self.master = master

        self.md5filename = 'filelist.md5'
        self.svar_tips = StringVar()
        self.svar_file_detail_tips = StringVar() 
        self.list_conf_customer_lists = []
        self.list_conf_match_lists = []
        #self.history_opendir = ''
        #self.history_saveas = ''
        self.label_tips = Label()
        self.list_message = Listbox()
        self.filesymbol = ''
        self.pendingdir = ''
        self.savefilename = ''
        self.btn_download_init = None #Button()
        self.file_md5_list = []
        self.file_detail_tips = []
        self.scr_history_have_clean = False
        self.customer_zone_list = []

        self.customer_name = ''
        #self.kehu_pos_datail = []
        self.data_dir = ''
        self.file_from_cangkujxc = ''
        self.file_from_youjiqingdan = ''
        self.file_from_jichu = ''
        self.curr_month = ''
        self.initWidgets(master)

    #按字符查找符合条件文件名，返回文件列表
    def find_filename(self, curr_path, curr_filename_path):
        list_files = []
        for parent, dirnames, filenames in os.walk(curr_path, followlinks=True):
            for filename in filenames:
                file_path = os.path.join(parent, filename)
                if curr_filename_path in filename:
                    self.list_message.insert(END,'文件名：%s' % file_path)
                    list_files.append(file_path)
        if len(list_files) > 0:
            return (list_files[0])
        else:
            return (None)

    # 从数据库导出价格（基础表），返回含价格信息列表

#从数据库处理数据，导出对账文件excel

    def excel_cell_rowcell_to_position(self,int_row,int_column):
        if int_row < 26:
            str_excel_cell_pos = chr(64+int_row)
            str_excel_cell_pos = str_excel_cell_pos + str(int_column)
        return str_excel_cell_pos
# 整合数据，导出生成excel文件

    def new_csvdata_list(self, customer, xlsfilename):

        self.list_message.insert(END,'【导入文件】')
        self.list_message.insert(END,'文件名：' + xlsfilename)
        int_first_row = 3
        self.customer_zone_list  = []

        # 获取明细表数据
        xlsfilename = self.data_dir + xlsfilename
        #workbook = load_workbook(xlsfilename)  # 打开excel文件
        logger.info('导入 ~开票平台中客户及区域~ 表' )

        i = 0

        # 获取明细表数据
        try:
            workbook_source = xlrd.open_workbook(xlsfilename) # 打开excel文件
        except Exception as err_message:
            print('ERR:',err_message)
            err_message_str = err_message.__str__()
            logger.error(err_message_str)
            logger.exception(sys.exc_info())
            self.list_message.insert(END,'【数据结果】')
            if 'Unsupported format, or corrupt file: Expected BOF record' in err_message_str:
                self.list_message.insert(END,'错误代码：-10\n')
                self.list_message.insert(END,'异常：文件加密\n')
                self.list_message.insert(END,'描述：读取文件异常，请检查《'+str(xlsfilename)+'》是否已解密。')
                return(-10)
            elif 'Workbook is encrypted' in err_message_str or "Can't find workbook in OLE2" in err_message_str:
                self.list_message.insert(END,'错误代码：-11\n')
                self.list_message.insert(END,'异常：密码保护\n')
                self.list_message.insert(END,'描述：读取文件异常，请检查《'+str(xlsfilename)+'》是否已撤销工作簿保护。')
                return(-11)
            else:
                self.list_message.insert(END,'错误代码：-20\n')
                self.list_message.insert(END,'异常：文件打开失败\n')
                self.list_message.insert(END,'描述：文件异常，请检查《'+str(xlsfilename)+'》是否正常。')
                return(-20)

        str_temp_last_datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.list_message.insert(END,'【数据处理】')
        self.list_message.insert(END,'处理时间： ' + str_temp_last_datetime)

        worksheet_source= workbook_source.sheets()[0]

        worksheet_source_maxrow = worksheet_source.nrows

        # 创建一个workbook 设置编码
        workbook_target = xlwt.Workbook(encoding = 'utf-8')
        # 创建一个worksheet
        worksheet = workbook_target.add_sheet('Sheet1')
        for idx_one_customer_conf in range(len(self.list_conf_customer_lists)):
            list_one_customer_conf = self.list_conf_customer_lists[idx_one_customer_conf]
            #fxl = form excel
            fxl_sheetname = list_one_customer_conf [0]
            fxl_title_row = int(list_one_customer_conf [1])
            self.list_message.insert(END,'开始匹配模板标题信息... ...'+str(fxl_sheetname))
            self.list_message.update()

            worksheet_source= workbook_source.sheets()[0]

            fxl_tile_maxcol = worksheet_source.ncols

            #读 excel 表格 标题 行 内容
            list_excel_title = []
            for i in range(0,fxl_tile_maxcol):
                list_excel_title.append([i,worksheet_source.cell(fxl_title_row,i).value])
            logger.info(list_excel_title)
            self.list_conf_match_lists = []

            #打印‘*’ 行
            asterisks = 0
            #查找excel的标题 是否在模板标题，不存在，提示，在标记所在位置
            for i in range(0,len(list_excel_title)):
                excel_titile_cell = list_excel_title[i][1]
                bool_match_title_cell = False
                conf_title_cell_first = 2
                #配置文件标题 位置 首个元素
                for idx_one_cell_in_conf_line in range(conf_title_cell_first,conf_title_cell_first+36):               #T1 - T36 
                    if excel_titile_cell == list_one_customer_conf[idx_one_cell_in_conf_line]:
                        self.list_conf_match_lists.append(excel_titile_cell+'@'+str(idx_one_cell_in_conf_line-conf_title_cell_first))
                        bool_match_title_cell = True
                if not bool_match_title_cell:
                    if asterisks ==0:
                        self.list_message.insert(END,'*'*66)
                        asterisks = 1
                    self.list_conf_match_lists.append(excel_titile_cell+'@'+'9999')
                    logger.info('在EBS模板中没有找到对应的标题：' + '  '+str(excel_titile_cell))
                    self.list_message.insert(END,'在EBS模板中没有找到对应的标题：' + '  '+ str(excel_titile_cell))
                    self.list_message.update()
            if asterisks == 1:
                self.list_message.insert(END,'*'*66)
            logger.info(self.list_conf_match_lists)        

        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet1')

        standard_title_begin = 2 #list_conf_customer_lists 输出标题首个位置
        for i in range(standard_title_begin,len(list_one_customer_conf)):
            worksheet.write(0,i-standard_title_begin,list_one_customer_conf[i])


        #读取excel文件内容，按格式写入ebs模板
        excel_data_lines_first = 1 
        lines_target_count = 1
        for data_line in range(excel_data_lines_first,worksheet_source_maxrow):
            #判断是否为数据行
            test_count = 0
            for i in range(0,16):
                if worksheet_source.cell(data_line,i).value:
                    test_count = test_count + 1
            logger.info('value_count: ' + str(data_line) +','+ str(test_count))
            if test_count < 4:
                break   #若前五列有数据的单元小于3个，则认为到数据末行，跳出循环

            for i in range(0,len(self.list_conf_match_lists)):
                excel_titile_cell_str = self.list_conf_match_lists[i]
                excel_titile_cell_list = excel_titile_cell_str.split('@')
                excel_titile_cell_pos = excel_titile_cell_list[1]

                if not excel_titile_cell_pos =='9999':
                    value_temp = worksheet_source.cell(data_line,i).value
                    #有值，写excel，无则不写
                    if value_temp:
                        worksheet.write(lines_target_count,int(excel_titile_cell_pos),value_temp)

                if i == 0:  #处理单据号码单元格为合并单元格情况，用上一个有效数据替代
                    if worksheet_source.cell(data_line,i).value:
                        last_dan_ju_hao_ma = worksheet_source.cell(data_line,i).value
                    else:
                        worksheet.write(lines_target_count,0,last_dan_ju_hao_ma)
            #写入行 计数
            lines_target_count = lines_target_count + 1

        logger.info('转存EBS报表数据行： ' + str(lines_target_count-excel_data_lines_first) +' 行.')
        self.list_message.insert(END,'转存EBS报表数据行： ' + str(lines_target_count - excel_data_lines_first) +' 行.')
        self.list_message.update()


        # 设置单元格宽度
        #worksheet.col(0).width = 3333
        #xls_save_filename = '开票明细信息EBS模板.xls'

        str_temp_date = time.strftime('%Y%m%d', time.localtime(time.time()))

        xls_save_filename = os.path.basename(xlsfilename)
        xls_save_filename_list = os.path.splitext(xls_save_filename)
        xls_save_filename = xls_save_filename_list[0]
        xls_save_filename = xls_save_filename+'(导出'+str_temp_date+').xls'

        sys_path0 = os.path.split(os.path.realpath(__file__))[0]#sys.path[0]
        xls_save_filename = os.path.join(sys_path0,xls_save_filename)

        try:
            workbook.save(xls_save_filename)
        except Exception as err_message:
            print('ERR:',err_message)
            self.list_message.insert(END,'ERROR：' + str(err_message))
            logger.error(err_message.__str__())
            logger.exception(sys.exc_info())
            return(2)
            
        # savefile_path = filedialog.asksaveasfilename(title=u'保存文件')
        # if savefile_path is not None:
        #     logger.info('保存文件：' + savefile_path)
        #     copyfile(xls_save_filename, savefile_path)

        #self.list_conf_match_lists.append('格式化文件另存为： ' + xls_save_filename)

        logger.info('格式化文件保存： ' + xls_save_filename)
        self.list_message.insert(END,'【处理结果】')
        self.list_message.insert(END,'处理完成')
        #self.list_message.insert(END,'#'*60)
        self.list_message.insert(END,'格式化文件另存为：' + xls_save_filename)
        self.list_message.update()

# 程序主gui界面。
    def initWidgets(self,fm1):
        logger.info('读取配置信息:')
        self.list_conf_customer_lists = [['EBS模板', '0', '单据号码', '购方名称', '购方税号', '购方地址电话', '购方银行账号', '备注', '复核人', '收款人', '清单行商品名称', '单据日期', '销方银行账号', '货物名称', '计量单位', '规格', '数量', '金额', '税率', '商品税目', '折扣金额', '税额', '折扣税额', '折扣率', '单价', '发票类型', '区域', '客户编号', '销售人员', '收单方', '摘要', '行-项目', '行-税分类', '分配-收入科目', '分配-税科目', '发票事物类型', '开票规则', '行-会计规则']]
        logger.info(self.list_conf_customer_lists)

        label_author = Label(fm1, text='by流程与信息化部IT. July,2020', font=('Arial', 9))
        label_author.place(x=814, y=717)

        self.btn_download_init = Button(fm1, text='打开文件', command=self.command_refresh_btn_run)
        self.btn_download_init.place(x=929, y=170)

        btn_app_exit_init = Button(fm1, text='  退  出  ', command=self.command_btn_exit)
        btn_app_exit_init.place(x=929, y=270)

        self.sbar_lr = Scrollbar(fm1,width=20)
        self.list_message = Listbox(relief=SUNKEN,width =127,height=39,yscrollcommand=self.sbar_lr.set,font=('Arial', 10))
        #selectmode list多选模式multiple  selectmode = MULTIPLE,
        self.list_message.place(x=30, y=33)
        self.list_message.bind('<Double-Button-1>',self.click_left_printList) #双击 <Double-Button-1>
        
        self.sbar_lr.config(command=self.list_message.yview)                
        self.sbar_lr.pack(side=LEFT, fill=Y)                     
        self.sbar_lr.pack(padx=10,pady=40)

        str_tips = '刷新，请先点选要发送的文件       '
        str_tips = '      '
        self.label_tips = Label(textvariable=self.svar_tips, font=('Arial', 11))
        self.label_tips.place(x=30, y=7)
        self.svar_tips.set(str_tips)
        
        str_file_detail_tips = '双击, 查看文件大小和时间'
        str_file_detail_tips = ' '
        self.label_file_detail_tips = Label(textvariable=self.svar_file_detail_tips, font=('Arial', 10))
        self.label_file_detail_tips.place(x=30, y=704)
        self.svar_file_detail_tips.set(str_file_detail_tips)


    # 退出键
    def command_btn_exit(self):
        self.master.destroy()

    def command_refresh_btn_run(self):
        init_dir = ''
        
        openfname_select = filedialog.askopenfilename(title='打开Excel文件',filetypes=[('Excel文件', '*.xls;*.xlsx')],initialdir=init_dir )
        if openfname_select:
            self.new_csvdata_list(self.customer_name, openfname_select)
            #self.history_opendir = openfname_select
        else:
            messagebox.showinfo(title='提示',message='请先选择待处理的EXCEL文件!' )

    def command_saveas_btn_run(self):
        return
    def click_left_printList(self,event):
        pass
    def get_md5file(self):
        pass
    # 主功能键
    #def command_btn_run(self):

if __name__ == '__main__':
    set_logging()
    main_window = Tk()
    main_window.title('开票明细信息EBS格式化工具 V200722')

    # 设定窗口的大小(长 * 宽)，显示窗体居中，winfo_xxx获取系统屏 幕分辨率。
    sw = main_window.winfo_screenwidth()
  
    sh = main_window.winfo_screenheight()
    ww = 1000
    wh = 740
    x = (sw - ww) / 2
    y = (sh - wh) / 2
    main_window.geometry("%dx%d+%d+%d" % (ww, wh, x, y))  # 这里的乘是小x
    logger.info('程序启动，program restart...')
    display = App(main_window)
    main_window.mainloop()
