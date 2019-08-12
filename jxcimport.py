import xlrd
from sys import argv

def is_number(s):
    try:  # 如果能运行float(s)语句，返回True（字符串s是浮点数）
        float(s)
        return True
    except ValueError:  # ValueError为Python的一种标准异常，表示"传入无效的参数"
        pass  # 如果引发了ValueError这种异常，不做任何事情（pass：不做任何事情，一般用做占位语句）
    try:
        import unicodedata  # 处理ASCii码的包
        for i in s:
            unicodedata.numeric(i)  # 把一个表示数字的字符串转换为浮点数返回的函数
            #return True
        return True
    except (TypeError, ValueError):
        pass
    return False


class JXCimportor:

    def __init__(self):
        self.customers = ['jtyh','gsnx']

    def xls_db(self, customer, xlsfilename):
        
        if not (customer in self.customers):
            print('不存在该客户格式资料')
            return ('不存在该客户格式资料')
            

        if customer == 'jtyh':
            int_first_row = 3
            workbook = xlrd.open_workbook(xlsfilename)
            sheetsname = workbook.sheet_names() # 获取excel里的工作表sheet名称数组

            sheetsname.sort(reverse=True)
            print(sheetsname)

##            for str_curr_sheet_name in sheetsname:
##                

            str_curr_sheet_name = sheetsname[0]

            sheet_curr = workbook.sheet_by_name(str_curr_sheet_name)
##            sheet = excel.sheet_by_index(0) #根据下标获取对应的sheet表

            int_sheet_nrows = sheet_curr.nrows
            for i in range(int_first_row,int_sheet_nrows):
                cell_curr_value = sheet_curr.cell(i,0).value
                
                if is_number(cell_curr_value):
                    for j in range(0,6):
                        cell_curr_value = sheet_curr.cell(i,j).value
                        #2.encode('utf-8')
                        print(i,j,cell_curr_value)

##            sheet.row_values(0) #获取第一行的数据
##            sheet.col_values(0) #获取第一列的数据
##            sheet.nrows #获取总共的行数
##            sheet.ncols #获取总共的列数

##            for i in range(1, sheet.nrows):
##                row_list = sheet.row_values(i) # 每一行的数据在row_list 数组里
##
##            print(row_list)




if __name__ == '__main__':
    argvs = argv
    #d:\python37\python .\jxcimport.py jtyh f:\\dev\\kefu\\jtyhwuliao.xlsx
    if len(argvs) < 3:
        print ('Usage:script parameter1 parameter2')
        exit(0)
    print('parameter: ',argvs[1],argvs[2])
    importer = JXCimportor()
    importer.xls_db(argvs[1],argvs[2])    
