import openpyxl
import os

work_dir = "."
for parent, dirnames, filenames in os.walk(work_dir,followlinks=True):
    for filename in filenames:
        file_path = os.path.join(parent, filename)
        if 'xlsx' in filename:
            print('文件名：%s' % filename)
            print('文件完整路径：%s\n' % file_path)

            wb=openpyxl.load_workbook(filename)
            #wb.create_sheet(title='Sheet2',index=0)
            wb.save(filename[:-2]+'0')
