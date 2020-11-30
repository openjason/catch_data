#！usr/bin/python3
# -*- coding: utf-8 -*-
#==========================
import xml.etree.ElementTree as ET
from openpyxl import Workbook
option_dict = {'FileRead': 'FR', 'FileWrite': 'FW', 'FileDelete': 'FD', 'FileAppend': 'FA', \
               'DirCreate': 'DC', 'DirDelete': 'DD', 'DirList': 'DL', 'DirSubdirs': 'DS', \
               'IsHome': 'IH', 'AutoCreate': 'AC'}
value_dic = {'1': '+', '0':'-'}
def Optionformat(optionname,value):
    rt = option_dict[optionname] + value_dic[value]
    return (rt)
wb = Workbook()
ws = wb.create_sheet("User Sheet",0)
xuhao = 1
ws.cell(row=1, column=1).value = '序号'
ws.column_dimensions['A'].width=5
ws.cell(row=1, column=2).value ='户名'
ws.column_dimensions['B'].width=10
ws.cell(row=1, column=3).value = '所属组名称'
ws.column_dimensions['C'].width=30
ws.cell(row=1, column=4).value = '文件夹(组成员请查看对应组权限)'
ws.column_dimensions['D'].width=30
ws.cell(row=1, column=5).value = '权限：FileRead,FileWrite，FileDelete，FileAppend，DirCreate，DirDelete，DirList，DirSubdirs,IsHome,AutoCreate'
ws.column_dimensions['E'].width=55


#ws = wb.active
cell_row=1
tree = ET.parse('FileZillaServer.xml')
root = tree.getroot()
print('root-tag:',root.tag,',root-attrib:',root.attrib,',root-text:',root.text)
for child in root:
    print('child-tag是：',child.tag,',child.attrib：',child.attrib,',child.text：',child.text)
    if child.tag != 'Users':
        continue
    for sub in child:
        print('sub-tag是：',sub.tag,',sub.attrib：',sub.attrib,',sub.text：',sub.text)
        if sub.tag == 'User':
            cell_row = cell_row + 1
            ws.cell(row=cell_row, column=2).value = str(sub.attrib['Name'])
            ws.cell(row=cell_row, column=1).value = str(xuhao)
            xuhao = xuhao + 1
        for sub2 in sub:
            print('sub-tag2是：',sub2.tag,',sub2.attrib：',sub2.attrib,',sub2.text：',sub2.text)
            #ws.cell(row=cell_row, column=3).value = str(sub2.text)
            try:
                #if sub2.attrib['Name'] = {}:
                if sub2.attrib['Name'] == 'Group':
                    ws.cell(row=cell_row, column=3).value = str(sub2.text)
                    if str(sub2.text) != 'None':
                        break
            except:
                pass
            row_next = 0
            for sub3 in sub2:
                print('sub-tag3是：',sub3.tag,',sub3.attrib：',sub3.attrib,',sub3.text：',sub3.text)
                row_next = 0
                if sub3.tag == 'Permission':
                    try:
                        ws.cell(row=cell_row, column=4).value = str(sub3.attrib['Dir'])
                        row_next = 1
                    except:
                        pass
                for sub4 in sub3:
                    print('sub-tag4是：',sub4.tag,',sub4.attrib：',sub4.attrib,',sub4.text：',sub4.text)
                    if sub4.tag == 'Option':
                        try:
                            #ws.cell(row=cell_row, column=5).value = str(ws.cell(row=cell_row, column=5).value) + str(sub4.attrib['Name']) + str(sub4.text)
                            if ws.cell(row=cell_row, column=5).value == None:
                                ws.cell(row=cell_row, column=5).value = Optionformat(sub4.attrib['Name'] , str(sub4.text))
                            else:
                                ws.cell(row=cell_row, column=5).value = str(ws.cell(row=cell_row, column=5).value) + Optionformat(sub4.attrib['Name'] , str(sub4.text))
                        except:
                            pass
                if row_next == 1:
                    cell_row = cell_row +1
            if row_next == 1:
                cell_row = cell_row -1

ws = wb.create_sheet("Group sheet",0)
cell_row=1
tree = ET.parse('FileZillaServer.xml')
root = tree.getroot()
print('root-tag:',root.tag,',root-attrib:',root.attrib,',root-text:',root.text)
xuhao = 1
ws.cell(row=1, column=1).value = '序号'
ws.column_dimensions['A'].width=5
ws.cell(row=1, column=2).value ='组名称'
ws.column_dimensions['B'].width=15
ws.cell(row=1, column=3).value = '文件夹'
ws.column_dimensions['C'].width=50
ws.cell(row=1, column=4).value = '权限：FileRead,FileWrite，FileDelete，FileAppend，DirCreate，DirDelete，DirList，DirSubdirs,IsHome,AutoCreate'
ws.column_dimensions['D'].width=55
for child in root:
    print('child-tag是：',child.tag,',child.attrib：',child.attrib,',child.text：',child.text)
    if child.tag != 'Groups':
        continue
    for sub in child:
        print('sub-tag是：',sub.tag,',sub.attrib：',sub.attrib,',sub.text：',sub.text)
        if sub.tag == 'Group':
            cell_row = cell_row + 1
            ws.cell(row=cell_row, column=2).value = str(sub.attrib['Name'])
            ws.cell(row=cell_row, column=1).value = str(xuhao)
            xuhao = xuhao +1
        for sub2 in sub:
            print('sub-tag2是：',sub2.tag,',sub2.attrib：',sub2.attrib,',sub2.text：',sub2.text)
            #ws.cell(row=cell_row, column=3).value = str(sub2.text)
            try:
                #if sub2.attrib['Name'] = {}:
                if sub2.attrib['Name'] == 'Group':
                    ws.cell(row=cell_row, column=3).value = str(sub2.text)
            except:
                pass

            for sub3 in sub2:
                print('sub-tag3是：',sub3.tag,',sub3.attrib：',sub3.attrib,',sub3.text：',sub3.text)
                row_next = 0
                if sub3.tag == 'Permission':
                    try:
                        ws.cell(row=cell_row, column=3).value = str(sub3.attrib['Dir'])
                        row_next = 1
                    except:
                        pass

                for sub4 in sub3:
                    print('sub-tag4是：',sub4.tag,',sub4.attrib：',sub4.attrib,',sub4.text：',sub4.text)
                    if sub4.tag == 'Option':
                        try:
                            #ws.cell(row=cell_row, column=5).value = str(ws.cell(row=cell_row, column=5).value) + str(sub4.attrib['Name']) + str(sub4.text)
                            if ws.cell(row=cell_row, column=4).value == None:
                                ws.cell(row=cell_row, column=4).value = Optionformat(sub4.attrib['Name'] , str(sub4.text))
                            else:
                                ws.cell(row=cell_row, column=4).value = str(ws.cell(row=cell_row, column=4).value) + Optionformat(sub4.attrib['Name'] , str(sub4.text))
                        except:
                            pass
                if row_next == 1:
                    cell_row = cell_row +1
            if row_next == 1:
                cell_row = cell_row -1

wb.save('FTP用户表.xlsx')
