#! -*- coding utf-8 -*-
#! Python Version 3.7

import openpyxl   
from openpyxl.styles import Font,Alignment


def main():
    sSourceFile="f:\\dev\\kefu\\jtyhkbkdzd_mb.xlsx"
    sTargetFile="f:\\dev\\kefu\\test.xlsx"
    wb = openpyxl.load_workbook(sSourceFile)
     
    copy_sheet1=wb.copy_worksheet(wb['201904'])
    #copy_sheet2=wb.copy_worksheet(wb.worksheets[0])
    #copy_sheet3=wb.copy_worksheet(wb.worksheets[0])

    wb.save(sTargetFile)
    
    print("It is over")
    
if __name__=="__main__":
    main()
