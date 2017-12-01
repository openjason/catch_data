# -*- coding: UTF-8 -*-
'''
根据防火墙配置文件配置内容，提取分类内容，保存到excel文件不同的sheet相应栏目中
author:jason chan
2017-11-29
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

def save_xls_file(blocked_list, block_child_list):
    workbook = openpyxl.load_workbook(xlsfile)
    print(xlsfile)
    wb = workbook
    writecell = []
    cellrow = 2

#Edit sheet "interface" begin
#    sheet = wb.get_active_sheet()
#    sheet = wb.set_active_sheet('interface')
    sheet = wb.get_sheet_by_name('interface')
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
            if interface_alias != '-' :                 #if have ip address
                tempList2 = tempList1[1].split()            #ip / netmask
                if len(tempList2) == 4:
                    interface_ip = tempList2[1].strip()
                    interface_netmask = tempList2[3].strip()
            else:
                interface_ip = '-'
                interface_netmask = '-'
            for i in range(1,len(tempList1)):
                tempStr1 = tempList1[i].strip()
                if len(tempStr1) > 7 :
                    if tempStr1[:7] == 'comment':
                        interface_comment = tempStr1[8:len(tempStr1)]
                        break
                else:
                    interface_comment = ' '
            cellcolumn = 1
            sheet.cell(row=cellrow, column=cellcolumn).value = interface_name
            cellcolumn += 1
            sheet.cell(row=cellrow, column=cellcolumn).value = interface_alias
            cellcolumn += 1
            cellcolumn += 1
            sheet.cell(row=cellrow, column=cellcolumn).value = interface_ip
            cellcolumn += 1
            sheet.cell(row=cellrow, column=cellcolumn).value = interface_netmask
            cellcolumn += 1
            cellcolumn += 1
            cellcolumn += 1
            sheet.cell(row=cellrow, column=cellcolumn).value = interface_comment
            cellrow += 1
# Edit sheet "interface" end

# Edit sheet "route" begin
    sheet = wb.get_sheet_by_name('route')

    for i in range(len(blocked_list)):
        if 'ipv6' in blocked_list[i]:  # remove include "ipv6" string
            continue

        tempStr1 = blocked_list[i]
        if 'routing' == tempStr1[:7]:
            child_List = block_child_list[i]
            for j in range(len(child_List)):
                tempStr2 = child_List[j].strip()
                if len(tempStr2) > 16 :
                    if  'policy interface' == tempStr2[:16] :
                        tempStr3 = child_List[j+1].strip()
                        tempList3 = tempStr3.split()
                        route_id = tempList3[1]

                        tempStr3 = child_List[j+2].strip()
                        tempList3 = tempStr3.split()
                        route_interface = tempList3[1]

                        tempStr3 = child_List[j+3].strip()
                        tempList3 = tempStr3.split()
                        route_metric = tempList3[1]

                        tempStr3 = child_List[j+4].strip()
                        tempList3 = tempStr3.split()
                        route_source = tempList3[1]

                        tempStr3 = child_List[j+5].strip()
                        tempList3 = tempStr3.split()
                        route_distination = tempList3[1] + tempList3[2]

                        tempStr3 = child_List[j+6].strip()
                        tempList3 = tempStr3.split()
                        route_service = tempList3[1]

                        tempStr3 = child_List[j+7].strip()
                        tempList3 = tempStr3.split()
                        if len(tempList3) > 2:
                            route_gateway = tempList3[1] +tempList3[2]
                        else:
                            route_gateway = tempList3[1]

                        tempStr3 = child_List[j+8].strip()
                        tempList3 = tempStr3.split()
                        route_comment = tempList3[1]

                        print(route_id,route_interface,route_metric,route_source,route_distination,route_service,route_gateway,route_comment)

                    continue


            if len(tempList2) == 3:
                tempStr2 = tempList2[1].strip()
            else:
                tempStr2 = '-'
            interface_alias = tempStr2
            if interface_alias != '-':  # if have ip address
                tempList2 = tempList1[1].split()  # ip / netmask
                if len(tempList2) == 4:
                    interface_ip = tempList2[1].strip()
                    interface_netmask = tempList2[3].strip()
            else:
                interface_ip = '-'
                interface_netmask = '-'
            for i in range(1, len(tempList1)):
                tempStr1 = tempList1[i].strip()
                if len(tempStr1) > 7:
                    if tempStr1[:7] == 'comment':
                        interface_comment = tempStr1[8:len(tempStr1)]
                        break
                else:
                    interface_comment = ' '
            cellcolumn = 1
            sheet.cell(row=cellrow, column=cellcolumn).value = interface_name
            cellcolumn += 1
            sheet.cell(row=cellrow, column=cellcolumn).value = interface_alias
            cellcolumn += 1
            cellcolumn += 1
            sheet.cell(row=cellrow, column=cellcolumn).value = interface_ip
            cellcolumn += 1
            sheet.cell(row=cellrow, column=cellcolumn).value = interface_netmask
            cellcolumn += 1
            cellcolumn += 1
            cellcolumn += 1
            sheet.cell(row=cellrow, column=cellcolumn).value = interface_comment
            cellrow += 1
# Edit sheet "route" end

#        print(str(cellrow) + interface_name+':'+interface_alias + interface_ip+';'+ interface_netmask + interface_comment)

    workbook.save(WorkDir+'cfg_new.xlsx')
    workbook.close()




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
    save_xls_file(confile_blocked, confile_block)


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


if __name__ == '__main__':
    WorkDir = 'F:\\test\\'
    xlsfile = WorkDir + 'sonicwall.xlsx'
    filename = 'hw254.cfg'
    wfilename = 'hwblock.txt'
    keyslist = []

    confile_blocked = []
    confile_block = []
    swcfgfile = WorkDir + 'sw.log'
    get_block(swcfgfile, confile_blocked, sn_block_key_str, WorkDir+'sn_block.txt')
