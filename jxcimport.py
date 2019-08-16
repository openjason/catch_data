import xlrd
from sys import argv
from sqlite3 import connect as sqlite3connect
from calendar import monthrange

class JXCimportor:

    def __init__(self):
        self.customers = ['jtyh','gsnx']
        self.sqlconn = sqlite3connect("F:\\dev\\kefu\\jinxiaocun.db3")
        self.sqlconn.isolation_level = None  # 这个就是事务隔离级别，默认是需要自己commit才能修改数据库，置为None则自动每次修改都提交,否则为""

    def xls_db(self, customer, xlsfilename):
        if not (customer in self.customers):
            print('不存在该客户格式资料')
            return ('不存在该客户格式资料')

        if customer == 'jtyh':
            int_first_row = 3
            day_column_start = 7  # 日数据开始位置
            workbook = xlrd.open_workbook(xlsfilename)
            sheetsname = workbook.sheet_names() # 获取excel里的工作表sheet名称数组

            sheetsname.sort(reverse=True)

##            for str_curr_sheet_name in sheetsname:
##                

            str_curr_sheet_name = sheetsname[0]
            list_curr_sheet_name_year_month = str_curr_sheet_name.split('.')
            print('sheetsname: ',list_curr_sheet_name_year_month[0],list_curr_sheet_name_year_month[1])
            monthdaysrange = monthrange(int(list_curr_sheet_name_year_month[0]),int(list_curr_sheet_name_year_month[1]))
            int_curr_month_days = monthdaysrange[1]
            if int(list_curr_sheet_name_year_month[1]) > 9:
                str_date_y_m = str(list_curr_sheet_name_year_month[0]) + '-' + str(list_curr_sheet_name_year_month[1])
            else:
                str_date_y_m = str(list_curr_sheet_name_year_month[0]) + '-0' + str(list_curr_sheet_name_year_month[1])
            #Returns weekday of first day of the month and number of days in month, for the specified year and month.

            sheet_curr = workbook.sheet_by_name(str_curr_sheet_name)
##            sheet = excel.sheet_by_index(0) #根据下标获取对应的sheet表

            int_sheet_nrows = sheet_curr.nrows
            for i in range(int_first_row,int_sheet_nrows):
                cell_curr_value = sheet_curr.cell(i,0).value

                if not isinstance(cell_curr_value,str):         #判断数据是否最后一行
                    wuliao = sheet_curr.cell(i, 1).value
                    style = sheet_curr.cell(i, 2).value
                    name = sheet_curr.cell(i, 3).value
                    cell_curr_value = sheet_curr.cell(i, 4).value
                    if isinstance(cell_curr_value,str):
                        shangyuejiecun = 0
                    else:
                        shangyuejiecun = cell_curr_value

                    cell_curr_value = sheet_curr.cell(i, 5).value
                    if isinstance(cell_curr_value,str):
                        benyuerucang = 0
                    else:
                        benyuerucang = cell_curr_value

                    cell_curr_value = sheet_curr.cell(i, 6).value
                    if isinstance(cell_curr_value,str):
                        benyuejiecun = 0
                    else:
                        benyuejiecun = cell_curr_value
#表格后部分的内容
                    next_path_data_pos_start = day_column_start + int_curr_month_days * 4
                    cell_curr_value = sheet_curr.cell(i, next_path_data_pos_start).value
                    if isinstance(cell_curr_value,str):
                        benyuefachushu = 0
                    else:
                        benyuefachushu = cell_curr_value
                    cell_curr_value = sheet_curr.cell(i, next_path_data_pos_start+1).value
                    if isinstance(cell_curr_value,str):
                        benyuechengpinshu = 0
                    else:
                        benyuechengpinshu = cell_curr_value
                    cell_curr_value = sheet_curr.cell(i, next_path_data_pos_start+2).value
                    if isinstance(cell_curr_value,str):
                        benyuejiankashu = 0
                    else:
                        benyuejiankashu = cell_curr_value
                    cell_curr_value = sheet_curr.cell(i, next_path_data_pos_start+3).value
                    if isinstance(cell_curr_value,str):
                        benyuefeikashu = 0
                    else:
                        benyuefeikashu = cell_curr_value
                    cell_curr_value = sheet_curr.cell(i, next_path_data_pos_start+4).value
                    if isinstance(cell_curr_value,str):
                        benyuefeikaleijishu = 0
                    else:
                        benyuefeikaleijishu = cell_curr_value
                    cell_curr_value = sheet_curr.cell(i, next_path_data_pos_start+5).value
                    if isinstance(cell_curr_value,str):
                        shangyuejiankaleijishu = 0
                    else:
                        shangyuejiankaleijishu = cell_curr_value
                    cell_curr_value = sheet_curr.cell(i, next_path_data_pos_start+6).value
                    if isinstance(cell_curr_value,str):
                        shangyuefeikaleijishu = 0
                    else:
                        shangyuefeikaleijishu = cell_curr_value
                    cell_curr_value = sheet_curr.cell(i, next_path_data_pos_start+7).value
                    if isinstance(cell_curr_value,str):
                        benyuexiaohuikongbaikashu = 0
                    else:
                        benyuexiaohuikongbaikashu = cell_curr_value
                    cell_curr_value = sheet_curr.cell(i, next_path_data_pos_start+8).value
                    if isinstance(cell_curr_value,str):
                        benyuexiaohuifeikashu = 0
                    else:
                        benyuexiaohuifeikashu = cell_curr_value



                    if len(wuliao) > 3:         #物料字符长度大于 3 写数据
                        # 插入数据
                        str_sql = 'insert into wuliao(kehu,wuliao,style,name,suoshuyuefen,shangyuejiecun,benyuerucang,benyuejiecun,\
benyuefachushu,benyuechengpinshu,benyuejiankashu,benyuefeikashu,benyuefeikaleijishu,shangyuejiankaleijishu,shangyuefeikaleijishu,benyuexiaohuikongbaikashu,benyuexiaohuifeikashu) \
values("'+customer+'","'+ wuliao + '","' + style + '","'+ name + '","' + str_date_y_m+'",'+str(shangyuejiecun)+','+str(benyuerucang)+','+str(benyuejiecun)+','+\
str(benyuefachushu)+','+str(benyuechengpinshu)+','+str(benyuejiankashu)+','+str(benyuefeikashu)+','+str(benyuefeikaleijishu)+\
','+str(shangyuejiankaleijishu)+','+str(shangyuefeikaleijishu)+','+str(benyuexiaohuikongbaikashu)+','+str(benyuexiaohuifeikashu)+')'
                        print (str_sql)
                        self.sqlconn.execute(str_sql)
                        # 如果隔离级别不是自动提交就需要手动执行commit
                        self.sqlconn.commit()

                        for j in range(0,int_curr_month_days):
                            if j > 9:
                                str_date = str_date_y_m + '-' +str(j+1)
                            else:
                                str_date = str_date_y_m + '-0' + str(j + 1)
                            cell_curr_value = sheet_curr.cell(i, day_column_start+4*j+0).value
                            if isinstance(cell_curr_value, str):
                                fachu = 0
                            else:
                                fachu = cell_curr_value
                            cell_curr_value = sheet_curr.cell(i, day_column_start+4*j+1).value
                            if isinstance(cell_curr_value, str):
                                chengpin = 0
                            else:
                                chengpin = cell_curr_value
                            cell_curr_value = sheet_curr.cell(i, day_column_start+4*j+2).value
                            if isinstance(cell_curr_value, str):
                                jianka = 0
                            else:
                                jianka = cell_curr_value
                            cell_curr_value = sheet_curr.cell(i, day_column_start+4*j+3).value
                            if isinstance(cell_curr_value, str):
                                feika = 0
                            else:
                                feika = cell_curr_value

                            str_sql = 'insert into days(kehu,wuliao,date,fachu,chengpin,jianka,feika) \
values("' + customer +'","'+ wuliao + '","' + str_date + '","' + str(fachu) + '",' + str(chengpin) + ',' + str(jianka) + ',' + str(feika) + ')'
                            #print (str_sql)
                            print('.',end="")
                            self.sqlconn.execute(str_sql)
                            self.sqlconn.commit()

if __name__ == '__main__':
    argvs = argv
    #d:\python37\python .\jxcimport.py jtyh f:\\dev\\kefu\\jtyhwuliao.xlsx
    if len(argvs) < 3:
        print ('Sample:c:>d:\python37\python .\jxcimport.py jtyh f:\\dev\\kefu\\jtyhwuliao.xlsx')
        exit(0)
    print('parameter: ',argvs[1],argvs[2])
    importer = JXCimportor()
    importer.xls_db(argvs[1],argvs[2])    
