# -*- coding: UTF-8 -*-
'''
根据关键字读取配置文件中相关内容，截取并存放在excel文件相应栏目中
author:jason chan
修改对应文件名，增加收集的路由器信息
'''
# import os
import openpyxl

hw_block_key_str = ['#', 'ip address-set', 'nat server', 'interface', 'ip route-static',
                    'rule name', 'nat address-group', 'ip service-set']

sn_block_key_str = ['zone', 'address-object', 'address-group', 'service-object', 'service-group',
                    'interface', 'policy', 'access-rule', 'log category']


def save_block_file(blocked_list, block_child_list, fn):
    with open(fn, 'w') as fopen:
        for i in range(len(blocked_list)):
            if 'ipv6' in blocked_list[i]:
                continue
            fopen.write('\n===========\n')
            fopen.writelines(blocked_list[i])
#            if block_list[i] != 'null':
            fopen.writelines(block_child_list[i])

def save_xls_file(blocked_list, block_child_list, xlsfile):
    workbook = openpyxl.load_workbook(xlsfile)

    for i in range(len(blocked_list)):
        if 'ipv6' in blocked_list[i]:   #remove include "ipv6" string
            continue

        tempStr1 = blocked_list[i]
        if 'interface' == tempStr1[:9] :
            interface_name = tempStr1[10:len(tempStr1)]
            tempList1 = interface_name.split()
            if len(tempList1) == 3:                     #interface name like 'X3 vlan 2',fix it
                interface_name = tempList1[0]+':V'+tempList1[2]
            tempList1 = block_child_list[i]
            tempList2 = tempList1[0].split()            #catch alias name
            if len(tempList2) == 3:
                tempStr2 = tempList2[1].strip()
            else:
                tempStr2 = '-'
            interface_alias = tempStr2

            if interface_alias != '-' :
                tempList2 = tempList1[1].split()            #ip / netmask
                if len(tempList2) == 4:
                    tempStr1 = tempList2[1].strip()
                    tempStr2 = tempList2[3].strip()
            else:
                tempStr1 = '-'
                tempStr2 = '-'
            interface_ip = tempStr1
            interface_netmask = tempStr2

            print(interface_name+':'+interface_alias+interface_ip+';'+ interface_netmask)
#            tempList1 = tempStr2.split()
            if tempList1[0] =='ip-assignment':
                interface_name = tempList1[4]
                print(interface_name)

    # workbook.save(WorkDir+'cfg_new.xlsx')
    # workbook.close()




def get_first_word(str):
    tstr1 = str.lstrip(' ')
    tlist = tstr1.split(' ')
    return tlist[0]


def list_to_string(rawlist):
    tstr = ''
    for tlist1 in rawlist:
        tlist2 = "\n".join(str(elm) for elm in tlist1)
        tstr =tstr + tlist2 + '\n'
    return tstr


def get_block(filename, confile_blocked, block_key_str, wfilename):
    confile_raw = []
    confile_temp = []
    fpline = ''
    with open(filename, 'r', encoding='gbk') as fp:
        for fpline in fp:
            #print(len(fpline),fpline)
            #        if len(fpline) > 3 and fpline[0] != '#': 井号也是标志，不可清理
            if len(fpline) > 1:
                fpline = fpline.rstrip('\n')
                if len(fpline.strip(" ")) < 1:
                    continue
                confile_raw.append(fpline)
    for line_num in range(len(confile_raw) - 1):
        # = confile_raw.index(fpline)
        lineStr = confile_raw[line_num]
        space1 = len(confile_raw[line_num]) - len(confile_raw[line_num].lstrip(' '))
        space2 = len(confile_raw[line_num + 1]) - len(confile_raw[line_num + 1].lstrip(' '))
        step1 = 0
 #       step2 = 1
        if space1 == 0 and space2 == 0 :
            confile_blocked.append (lineStr)
            confile_block.append ("null")
        if space1 == 0 and space2 > 0:
            confile_blocked.append(lineStr)

        if space1 > 0 and space2 > 0:
            confile_temp.append('\n'+ lineStr)
#            confile_temp.append('\n')
        if space1 > 0 and space2 == 0:
            confile_temp.append(lineStr)
            confile_block.append(confile_temp)
            confile_temp = []
    save_block_file(confile_blocked, confile_block, wfilename)
    save_xls_file(confile_blocked, confile_block, xlsfile)


def get_xls_keys(workbook, keyslist):
    wb = workbook
    sheet = wb.get_sheet_by_name('route')
    cellrow = 1
    cellcolumn = 1
    sheetcell = sheet.cell(row=cellrow, column=cellcolumn).value
    while sheetcell != None:
        celllist = sheetcell.split()
        keyslist.append(celllist)
        cellrow += 1
        #    print (sheetcell)
        sheetcell = sheet.cell(row=cellrow, column=cellcolumn).value
    wb.close()


def compare(keyslist, confile_blocked, workbook, cellcolumn):
    wb = workbook
    writecell = []
    sheet = wb.get_active_sheet()
    cellrow = 1
    for ci in keyslist:
        #    print(ci,keyslist.index(ci),len(ci))
        cellrow = keyslist.index(ci) + 1
        for tint1 in range(len(ci)):
            #        keys = keyslist[tint1]
            print('>', end='')
            for confile_block in confile_blocked:
                for tint2 in range(len(confile_block)):
                    if ci[tint1] in confile_block[tint2]:
                        writecell.append(confile_block)
                        break

        if writecell:# print(writecell)
            sheet.cell(row=cellrow, column=cellcolumn).value = list_to_string(writecell)
        writecell = []


if __name__ == '__main__':
    WorkDir = 'F:\\test\\'
    xlsfile = WorkDir + 'sonicwall.xlsx'
    workbook = openpyxl.load_workbook(xlsfile)
    filename = 'hw254.cfg'
    wfilename = 'hwblock.txt'
    keyslist = []

    # confile_blocked = []
    # get_xls_keys(workbook, keyslist)
    # get_block('hw254.cfg', confile_blocked, hw_block_key_str, 'hwblock.txt')
    # compare(keyslist, confile_blocked, workbook, 7)

    confile_blocked = []
    confile_block = []
#    get_xls_keys(workbook, keyslist)
    swcfgfile = WorkDir + 'sw.log'
    get_block(swcfgfile, confile_blocked, sn_block_key_str, WorkDir+'sn_block.txt')
    compare(keyslist, confile_blocked, workbook, 8)

    workbook.save(WorkDir+'cfg_new.xlsx')
    workbook.close()
