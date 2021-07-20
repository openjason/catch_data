import win32com.client as win32
from configparser import ConfigParser
import sys,os

def main():
    cp = ConfigParser()
    cp.read('配置文件.ini', encoding='gbk')
    temp_str = cp.get('JC配置', 'customer')
    temp_customer_list = temp_str.split('|!|')
    temp_curtomer = temp_customer_list[0]

    one_customer_list = [temp_customer_list[0]]
    tempdir = cp.get(temp_curtomer, 'tempdir')


    if len(sys.argv) !=2:
        print('Error: Usage: xls2xlsxzip filename.xls')
        return 'Error: Usage: xls2xlsxzip filename.xls'

    fname = sys.argv[1]
    print(fname)
    if os.path.splitext(fname)[1] != '.xls':
        print("Error: only convert .xls file")
        return("Error: only convert .xls file")

    if not os.path.exists(fname):
        print("Error: file not exist")
        return("Error: file not exist")

        

    #fname = "D:\\temp\\95580.xls"
    excel = win32.gencache.EnsureDispatch('Excel.Application')

    excel.DisplayAlerts = False
    #告警提示停用
    wb = excel.Workbooks.Open(fname)

    wb.SaveAs(fname+"x", FileFormat = 51)    #FileFormat = 51 is for .xlsx extension
    wb.Close()                               #FileFormat = 56 is for .xls extension
    print('Success: SaveAs ',fname+'x')
    #告警提示启用
    excel.DisplayAlerts = True
    excel.Application.Quit()
    return('Success: SaveAs ',fname+'x')

main()
