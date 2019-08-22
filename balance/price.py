import xlrd
from sys import argv
from sqlite3 import connect as sqlite3connect
from calendar import monthrange

#j价格表（基础表）数据导入
class JGimportor:

    def __init__(self):
        self.customers = ['jtyh','gsnx']
        self.sqlconn = sqlite3connect("balance_jtyh.db3")
        self.sqlconn.isolation_level = None  # 这个就是事务隔离级别，默认是需要自己commit才能修改数据库，置为None则自动每次修改都提交,否则为""

    def xls_db(self, customer, xlsfilename):
        if not (customer in self.customers):
            print('不存在该客户格式资料')
            return ('不存在该客户格式资料')

        if customer == 'jtyh':
            int_first_row = 2
            #day_column_start = 7  # 日数据开始位置
            workbook = xlrd.open_workbook(xlsfilename)
            sheetsname = workbook.sheet_names() # 获取excel里的工作表sheet名称数组

            #sheetsname.sort(reverse=True)

##            for str_curr_sheet_name in sheetsname:
##                

            str_curr_sheet_name = sheetsname[0]

            sheet_curr = workbook.sheet_by_name(str_curr_sheet_name)
            int_sheet_nrows = sheet_curr.nrows
            print('sheetname & lines:', str_curr_sheet_name,int_sheet_nrows)

            for i in range(int_first_row,int_sheet_nrows):
                cell_curr_value = sheet_curr.cell(i,0).value
                #print('i: ',i)
                if True:#not isinstance(cell_curr_value,str):         #判断数据是否最后一行
                    priceid = sheet_curr.cell(i, 0).value
                    kamiandaima = sheet_curr.cell(i, 1).value
                    kapianbanbenhao = sheet_curr.cell(i, 2).value
                    wuliao = sheet_curr.cell(i, 3).value
                    kapianmingcheng = sheet_curr.cell(i, 4).value
                    gerenhuafuwu = sheet_curr.cell(i, 5).value
                    fuwumingcheng = sheet_curr.cell(i, 6).value
                    fuwuleixingbiaoshi = sheet_curr.cell(i, 7).value
                    cell_curr_value = sheet_curr.cell(i, 8).value
                    if isinstance(cell_curr_value, str):
                        gerenhuajiage = 0
                    else:
                        gerenhuajiage = cell_curr_value
                    xinpianka = sheet_curr.cell(i, 9).value
                    gongjiqueren = sheet_curr.cell(i, 10).value
                    cell_curr_value = sheet_curr.cell(i, 11).value
                    if isinstance(cell_curr_value, str):
                        kongbaikajiage = 0
                    else:
                        kongbaikajiage = cell_curr_value

                    if int(priceid) > 0: # testing
                        # 插入数据
                        str_sql = "insert into price(id,kamiandaima,kapianbanbenhao,wuliao,mingcheng,gerenhuafuwu,fuwumingcheng,\
fuwuleixinbiaoshi,gerenhuajiage,xinpianka,gongyiqueren,kongbaikajiage)"
                        str_sql= str_sql + "values("+str(priceid)+",'"+kamiandaima+"','"+kapianbanbenhao+"','"+wuliao+ "','"+ \
kapianmingcheng+"','"+gerenhuafuwu+"','"+fuwumingcheng+"','"+fuwuleixingbiaoshi+"',"+str(gerenhuajiage)+",'"+xinpianka+"','"+gongjiqueren+"',"+ \
str(kongbaikajiage)+ ")"
                        print (kapianmingcheng)
                        self.sqlconn.execute(str_sql)
                        # 如果隔离级别不是自动提交就需要手动执行commit
                        self.sqlconn.commit()
            print('='*40)
            print('共导入了 ',i - int_first_row +1,'行数据.')


if __name__ == '__main__':
    argvs = argv
    #d:\python37\python .\jxcimport.py jtyh f:\\dev\\kefu\\jtyhwuliao.xlsx
    if len(argvs) < 3:
        print ('Sample:c:>d:\python37\python .\price.py jtyh f:\\dev\\kefu\\jtyhjgqrb.xlsx')
        exit(0)
    print('parameter: ',argvs[1],argvs[2])
    importer = JGimportor()
    importer.xls_db(argvs[1],argvs[2])    
