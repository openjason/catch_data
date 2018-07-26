# -*- coding: UTF-8 -*-
'''
根据华为防火墙配置文件配置内容，提取分类内容，保存到excel文件不同的sheet相应栏目中
author:jason chan
2018-04-08
'''
# import os
import openpyxl
import copy
import re

def judge_legal_ip(one_str):
    '''''
    正则匹配方法
    判断一个字符串是否是合法IP地址
    '''
    compile_ip = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if compile_ip.match(one_str):
        return True
    else:
        return False

def fix_address_string(add_str):
    #停用    return add_str
    fix_addr_str = "地址有误"
    if add_str[0]=='"':
        tmp_pos = add_str[1:].find('"')
        aname = add_str[0:tmp_pos+2]
        tmp_list = add_str[tmp_pos:].split()
    else:
        tmp_list = add_str.split()
        aname = tmp_list[0]
    if len(tmp_list)< 3:
        return add_str
    if 'host' == tmp_list[1]:
        fix_addr_str = tmp_list[2] + '/32'

    if 'range' == tmp_list[1]:
        fix_addr_str = tmp_list[2] + '-' + tmp_list[3]

    if 'network' == tmp_list[1]:
        if '255.255.255.0' == tmp_list [3]:
            netmaskstr = '/24'
        else:
            netmaskstr = tmp_list [3]
        fix_addr_str = tmp_list[2] + netmaskstr

#    return aname + ":" +fix_addr_str
    return fix_addr_str


def save_block_file(blocked_list, block_child_list, fn):
    #配置文件一块为单位，进行保存
    with open(fn, 'w') as fopen:
        for i in range(len(blocked_list)):
            if 'ipv6' in blocked_list[i]:
                continue
            fopen.write('\n===========\n')
            fopen.writelines(blocked_list[i])
#            if block_list[i] != 'null':
            fopen.writelines(block_child_list[i])

def getAddressGroupList(blocked_list, block_child_list,Aname,AddressGroupList):
    #对地址明细进行解释，解析address-group明细，获取具体地址列表
    address_g_list = []
    if '"' in Aname:
        Aname = Aname[1:len(Aname) - 1]

    for i in range(len(blocked_list)):
        if 'ipv6' in blocked_list[i]:  # remove include "ipv6" string
            continue
        tempStr1 = blocked_list[i]
        if 'address-group' == tempStr1[:13]:

            if '"' in tempStr1:
                tempList1 = tempStr1.split('"')
#                tempGname = '"'+tempList1[1]+'"'
                tempAname = tempList1[1]
            else:
                tempList1 = tempStr1.split()
#                print (tempList1)
                tempAname = tempList1[2]
            if Aname == tempAname:
                tempList2 = block_child_list[i]
                for j in range(len(tempList2)):
                    tempStr2 = tempList2[j].strip()
                    if 'address-object' == tempStr2[:14]:
                        tempGetSObject = tempStr2[15+5:len(tempStr2)]
                        AddressGroupList.append(getAddressList(blocked_list, block_child_list,tempGetSObject))
                    if 'address-group' == tempStr2[:13]:
                        tempGetSObject = tempStr2[14+5:len(tempStr2)]
                        tempGetSObject = tempGetSObject.strip()
                        tempList3 = getServiceGroupList(blocked_list, block_child_list,tempGetSObject,AddressGroupList)
#                        for tempInt1 in range(len(tempList3)):
#                            AddressGroupList.append(tempList3[tempInt1])
                break
    return AddressGroupList



def getServiceGroupList(blocked_list, block_child_list,Gname,ServicePortList):
    # 对服务（端口）明细进行解释，解析service-group明细，获取具体地址列表
    #    ServicePortList = []
    if Gname == 'ICMP':
        ServicePortList.append('ICMP')
        return ServicePortList
    if Gname == 'Ping':
        ServicePortList.append('Ping')
        return ServicePortList

    if Gname == '5000&ping':
        Gname = Gname

    for i in range(len(blocked_list)):
        if 'ipv6' in blocked_list[i]:  # remove include "ipv6" string
            continue
        tempStr1 = blocked_list[i]
        if 'service-group' == tempStr1[:13]:
            if '"' in Gname:
                Gname = Gname[1:len(Gname)-1]

            if '"' in tempStr1:
                tempList1 = tempStr1.split('"')
#                tempGname = '"'+tempList1[1]+'"'
                tempGname = tempList1[1]
            else:
                tempList1 = tempStr1.split()
#                print (tempList1)
                tempGname = tempList1[1]
            if Gname == tempGname:
                tempList2 = block_child_list[i]
                for j in range(len(tempList2)):
                    tempStr2 = tempList2[j].strip()
                    if 'service-object' == tempStr2[:14]:
                        tempGetSObject = tempStr2[15:len(tempStr2)]
                        ServicePortList.append(getServiceList(blocked_list, block_child_list,tempGetSObject))
                    if 'service-group' == tempStr2[:13]:
                        tempGetSObject = tempStr2[14:len(tempStr2)]
                        tempGetSObject = tempGetSObject.strip()

                        tempList3 = getServiceGroupList(blocked_list, block_child_list,tempGetSObject,ServicePortList)
#                        ServicePortList = ServicePortList + tempList3

    return ServicePortList

def getServiceList(blocked_list, block_child_list,sname):
    #获取具体服务对应的服务名和端口号
    ServicePort = ''
    for i in range(len(blocked_list)):
        if 'ipv6' in blocked_list[i]:  # remove include "ipv6" string
            continue
        tempStr1 = blocked_list[i]
        if 'service-object' == tempStr1[:14]:
            if sname == tempStr1[15:15+len(sname)] and tempStr1[15+len(sname):15+len(sname)+1]== ' ':
                ServicePort = tempStr1[15 + len(sname)+1:len(tempStr1)]
                break
    return ServicePort

def getAddressList(blocked_list, block_child_list,aname):
    #获取具体地址对应的地址名和地址
    address_detail = ''
    if aname =='any':
        return '0.0.0.0'

    for i in range(len(blocked_list)):
        if 'ipv6' in blocked_list[i]:  # remove include "ipv6" string
            continue
        tempStr_raw = blocked_list[i]
        # temp_str_zone_pos = tempStr_raw.find('zone')
        # if temp_str_zone_pos > 0:
        #     tempStr1 = tempStr_raw[:temp_str_zone_pos]
        # else:
        tempStr1 = tempStr_raw
        if 'address-object' == tempStr1[:14]:
            if aname == tempStr1[20:20+len(aname)] and tempStr1[20+len(aname):21+len(aname)]== ' ':
                # try:
                #     first_space = tempStr1[21 + len(aname):len(tempStr1)].index(' ')
                # except:
                #     first_space = 0
                #address_detail = tempStr1[21+1 + len(aname)+first_space:len(tempStr1)]
                address_detail = tempStr_raw[len("address-object ipv4 ") :len(tempStr_raw)]
                address_detail = fix_address_string(address_detail)
                break
    #    return aname +":"+ address_detail
    return address_detail


def save_xls_file(blocked_list, block_child_list):
    #保存配置文件，保存配置文件文件名
    xlsfile = 'sonicwall.xlsx'

    workbook = openpyxl.load_workbook(xlsfile)
    vaild_counter = 1
    print(xlsfile)
    wb = workbook
    writecell = []

#Edit sheet "interface" begin
    sheet = wb.get_sheet_by_name('interface')
    cellrow = 2
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
                ipassignment = tempList2[2].strip()
            else:
                tempStr2 = '-'
                ipassignment = '-'
            interface_alias = tempStr2
            if interface_alias != '-' :                 #if have ip address
                tempList2 = tempList1[1].split()            #ip / netmask
                if len(tempList2) == 4:
                    interface_ip = tempList2[1].strip()
                    interface_netmask = tempList2[3].strip()
                if len(tempList2) == 2 and tempList2[0]=='ip':
                    interface_ip = tempList2[1].strip()
                    tempList2 = tempList1[2].split()
                    interface_netmask = tempList2[1].strip()
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
            sheet.cell(row=cellrow, column=cellcolumn).value = ipassignment
            cellcolumn += 1
            cellcolumn += 1
#            sheet.cell(row=cellrow, column=cellcolumn).value = interface_comment
            cellrow += 1
# Edit sheet "interface" end

# Edit sheet "route" begin
    sheet = wb.get_sheet_by_name('route')
    cellrow = 2
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
                        if len(tempList3) > 2:
#                            route_distination = tempList3[1] + tempList3[2]
                            route_distination =  tempList3[2]
                        else:
                            route_distination = tempList3[1]

                        tempStr3 = child_List[j+6].strip()
                        tempList3 = tempStr3.split()
                        route_service = tempList3[1]

                        tempStr3 = child_List[j+7].strip()
                        tempList3 = tempStr3.split()
                        if len(tempList3) > 2:
                            route_gateway = tempList3[2]
                            if route_gateway[0] == '"':
                                tempList3 = tempStr3.split('"')
                                route_gateway = '"'+tempList3[1]+'"'
                        else:
                            route_gateway = tempList3[1]

                        tempStr3 = child_List[j+8].strip()
                        tempList3 = tempStr3.split()
                        route_comment = tempList3[1]

#                        print(route_id,route_interface,route_metric,route_source,route_distination,route_service,route_gateway,route_comment)
                        cellcolumn = 1
                        sheet.cell(row=cellrow, column=cellcolumn).value = route_id
                        cellcolumn += 1
                        sheet.cell(row=cellrow, column=cellcolumn).value = route_source
                        cellcolumn += 1
                        sheet.cell(row=cellrow, column=cellcolumn).value = route_distination
                        cellcolumn += 1
                        sheet.cell(row=cellrow, column=cellcolumn).value = route_service
                        cellcolumn += 1
                        sheet.cell(row=cellrow, column=cellcolumn).value = route_gateway
                        cellcolumn += 1
                        sheet.cell(row=cellrow, column=cellcolumn).value = route_interface
                        cellcolumn += 1
                        sheet.cell(row=cellrow, column=cellcolumn).value = route_metric
                        cellcolumn += 1
#配置文件没找到优先级                        sheet.cell(row=cellrow, column=cellcolumn).value = route_priority
                        cellrow += 1
# Edit sheet "route" end

#        print(str(cellrow) + interface_name+':'+interface_alias + interface_ip+';'+ interface_netmask + interface_comment)

# Edit sheet "rule" begin

    rule_source_zone = ''
    rule_destination_zone = ''
    rule_source_address = ''
    rule_destination_address = ''
    rule_service = ''
    rule_action = ''


    sheet = wb.get_sheet_by_name('rule')
    cellrow = 2
    for i in range(len(blocked_list)):
        if 'security-policy' in blocked_list[i]:   #remove include "ipv6" string
            i = i + 1
            in_security_polich = True
            tempStr1 = blocked_list[i]
            while in_security_polich:
            if ' rule name' == tempStr1[:10] :
                rule_name = tempStr1[10:]
                rule_name = rule_name.strip

                cellcolumn = 1
                sheet.cell(row=cellrow, column=cellcolumn).value = rule_destination_address
                cellcolumn += 1

                row_diaplay = rule_destination_detail.split('\n')
                rule_destination_address_row = len(row_diaplay)
                # if len(row_diaplay) > 1:
                #     for i in range(len(row_diaplay)):
                #         sheet.cell(row=cellrow + rule_destination_address_row, column=cellcolumn).value = row_diaplay[i]
                #         rule_destination_address_row += 1
                # else:
                sheet.cell(row=cellrow, column=cellcolumn).value = rule_destination_detail

                cellcolumn += 1
                sheet.cell(row=cellrow, column=cellcolumn).value = rule_service
                cellcolumn += 1
                sheet.cell(row=cellrow, column=cellcolumn).value = rule_service_port
                sheet.cell(row=cellrow, column=cellcolumn).value = format_rule_str
                cellcolumn += 1
                sheet.cell(row=cellrow, column=cellcolumn).value = rule_action

                if rule_source_address_row > rule_destination_address_row:
                    sheet.row_dimensions[cellrow].height = 16 * rule_source_address_row
                else:
                    sheet.row_dimensions[cellrow].height = 16 * rule_destination_address_row

                rule_source_zone = ''
                rule_destination_zone = ''
                rule_source_address = ''
                rule_destination_address = ''
                rule_service = ''
                rule_action = ''

                cellrow = cellrow + 1
            elif '  source-zone' == tempStr1[:14]:
                rule_source_zone = tempStr1[14:]
                rule_source_zone = rule_name.strip

            elif '  destination-zone' == tempStr1[:19]:
                rule_destination_zone = tempStr1[19:]
                rule_destination_zone = rule_name.strip

            elif '  source-address' == tempStr1[:14]:
                rule_source_address = tempStr1[14:]
                rule_source_address = rule_name.strip

            elif '  service' == tempStr1[:10]:
                rule_source_zone = tempStr1[10:]
                rule_source_zone = rule_name.strip

            elif '  action' == tempStr1[:9]:
                rule_source_zone = tempStr1[9:]
                rule_source_zone = rule_name.strip

            else:
                print('Unknow keywork.')

# Edit sheet "rule" end
    try:
        workbook.save('cfg_new.xlsx')
    except:
        print("xlsx文件被锁定，无法保存。。。")
    finally:
        workbook.close()

def format_service_list(s_list):
    #格式化服务列表，将重名的内容去除。
    if s_list == "":
        return ""
    f_service_str = ''
    last_str1 = ""
    tmpList1 = s_list.split('\n')
    for tempInt1 in range(len(tmpList1)):
            tmp_str2 = tmpList1[tempInt1]
            tmpList2 = tmp_str2.split()
            if len(tmpList2) == 3:
                if last_str1 != tmpList2[0]:
                    if last_str1 == "":
                        if f_service_str == '':
                            f_service_str = tmpList2[0]
                        else:
                            f_service_str = f_service_str + "、" + tmpList2[0]
                    else:
                        f_service_str = f_service_str + "\n" +tmpList2[0]
                    last_str1 = tmpList2[0]
                    if tmpList2[1] == tmpList2[2]:
                        f_service_str = f_service_str + " " + tmpList2[1]
                    else:
                        f_service_str = f_service_str + " " + tmpList2[1]+"-" + tmpList2[2]
                else:
                    if tmpList2[1] == tmpList2[2]:
                        f_service_str = f_service_str + "、" + tmpList2[1]
                    else:
                        f_service_str = f_service_str + "、" + tmpList2[1]+"-" + tmpList2[2]
            else:
                if len(tmpList2) == 1:
                    if f_service_str == '':
                        f_service_str = tmp_str2
                    else:
                        f_service_str = f_service_str + "、" + tmp_str2

    return f_service_str

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


def get_block(filename, confile_blocked, wfilename):
    confile_block = []
    confile_raw = []
    confile_temp = []
    fpline = ''
    with open(filename, 'r', encoding='gbk') as fp:
        for fpline in fp:
            if len(fpline) > 1:
                fpline = fpline.rstrip('\n')
                if len(fpline.strip(" ")) < 1:
                    continue
                confile_raw.append(fpline)
    confile_block = copy.deepcopy(confile_raw)
    confile_blocked = copy.deepcopy(confile_raw)

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

def cfgxlsproc():
    xlsfile = 'HuaWeiUSG.xlsx'
    keyslist = []

    confile_blocked = []
    swcfgfile = 'vrpcfg.cfg'

    get_block(swcfgfile, confile_blocked, 'hw_block.txt')

if __name__ == '__main__':
    cfgxlsproc()
