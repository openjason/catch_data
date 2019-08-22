import xlrd
from sys import argv
from sqlite3 import connect as sqlite3connect
from calendar import monthrange

#邮寄清单列表导入数据库
class MLimportor:
    def __init__(self):
        self.customers = ['jtyh','gsnx']
        self.sqlconn = sqlite3connect("balance_jtyh.db3")
        self.sqlconn.isolation_level = None  # 这个就是事务隔离级别，默认是需要自己commit才能修改数据库，置为None则自动每次修改都提交,否则为""

    def xls_db(self, customer, xlsfilename):
        if not (customer in self.customers):
            print('不存在该客户格式资料')
            return ('不存在该客户格式资料')

        if customer == 'jtyh':
            int_first_row = 1
            day_column_start = 7  # 日数据开始位置
            workbook = xlrd.open_workbook(xlsfilename)
            sheetsname = workbook.sheet_names() # 获取excel里的工作表sheet名称数组

            #sheetsname.sort(reverse=True)

##            for str_curr_sheet_name in sheetsname:
##                

            str_curr_sheet_name = sheetsname[0]
            #list_curr_sheet_name_year_month = str_curr_sheet_name.split('.')
            #print('sheetsname: ',list_curr_sheet_name_year_month[0],list_curr_sheet_name_year_month[1])
            #monthdaysrange = monthrange(int(list_curr_sheet_name_year_month[0]),int(list_curr_sheet_name_year_month[1]))
            #int_curr_month_days = monthdaysrange[1]
            #if int(list_curr_sheet_name_year_month[1]) > 9:
            #    str_date_y_m = str(list_curr_sheet_name_year_month[0]) + '-' + str(list_curr_sheet_name_year_month[1])
            #else:
            #    str_date_y_m = str(list_curr_sheet_name_year_month[0]) + '-0' + str(list_curr_sheet_name_year_month[1])
            #Returns weekday of first day of the month and number of days in month, for the specified year and month.

            sheet_curr = workbook.sheet_by_name(str_curr_sheet_name)
##            sheet = excel.sheet_by_index(0) #根据下标获取对应的sheet表
            int_sheet_nrows = sheet_curr.nrows
            print('sheetname & lines:', str_curr_sheet_name,int_sheet_nrows, '行')

            #cell_curr_value = sheet_curr.cell(2, 2).value
            #print(cell_curr_value,int_sheet_nrows)

            for i in range(int_first_row,int_sheet_nrows):
                cell_curr_value = sheet_curr.cell(i,0).value
                if i % 100 == 0 :
                    print ('processing: ',i)
                if True:#not isinstance(cell_curr_value,str):         #判断数据是否最后一行
                    maillistid = sheet_curr.cell(i, 0).value
                    picihao = sheet_curr.cell(i, 1).value
                    shenqinbianhao = sheet_curr.cell(i, 2).value
                    youjifangshi = sheet_curr.cell(i, 3).value
                    #print(youjifangshi)
                    youjidanghao = sheet_curr.cell(i, 4).value
                    jichudi = sheet_curr.cell(i, 5).value
                    zhikafangshi = sheet_curr.cell(i, 6).value
                    chikarenxingmin = sheet_curr.cell(i, 7).value
                    zhukaxingmin = sheet_curr.cell(i, 8).value
                    kamiandaima = sheet_curr.cell(i, 9).value
                    fakayuanyin = sheet_curr.cell(i, 10).value
                    kahao = sheet_curr.cell(i, 11).value
                    youjidizhi = sheet_curr.cell(i, 12).value
                    youbian = sheet_curr.cell(i, 13).value
                    chikarenshouji = sheet_curr.cell(i, 14).value
                    youjiriqi = sheet_curr.cell(i, 15).value
                    shengchengriqi = sheet_curr.cell(i, 16).value
                    zhufukabiaoji = sheet_curr.cell(i, 17).value
                    emsliushuihao = sheet_curr.cell(i, 18).value
                    pid = sheet_curr.cell(i, 19).value
                    quyu = sheet_curr.cell(i, 20).value

                    if int(maillistid) > 0: # testing
                        # 插入数据
                        str_sql = "insert into maillist(id,kehu,picihao,shenqinbianhao,youjifangshi,youjidanghao,jichudi,zhikafangshi,\
chikarenxingmin,kazhuxingmin,kamiandaima,fakayuanyin,kahao,youjidizhi,youbian,chikarenshouji,youjiriqi,shengchengriqi,zhufukabiaoji,\
emsliushuihao,pid,quyu)"
                        str_sql= str_sql + "values("+str(maillistid)+",'"+customer+"','"+picihao+"','"+shenqinbianhao+ "',"+ \
youjifangshi+",'"+youjidanghao+"','"+jichudi+"','"+zhikafangshi+"','"+chikarenxingmin+"','"+zhukaxingmin+"','"+kamiandaima+"','"+fakayuanyin+"','"+ \
kahao+"','"+youjidizhi+"','"+youbian+"','"+chikarenshouji+"','"+youjiriqi+"','"+shengchengriqi+"','"+zhufukabiaoji+"','"+emsliushuihao+"','"+ pid+"','"+ quyu+ "')"
                        #print (str_sql)
                        self.sqlconn.execute(str_sql)
                        # 如果隔离级别不是自动提交就需要手动执行commit
                        self.sqlconn.commit()


if __name__ == '__main__':
    argvs = argv
    #d:\python37\python .\jxcimport.py jtyh f:\\dev\\kefu\\jtyhwuliao.xlsx
    if len(argvs) < 3:
        print ('Sample:c:>d:\python37\python .\maillist.py jtyh f:\\dev\\kefu\\jtyhyjqd.xls')
        exit(0)
    print('parameter: ',argvs[1],argvs[2])
    importer = MLimportor()
    importer.xls_db(argvs[1],argvs[2])    
