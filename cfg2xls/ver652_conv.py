# -*- coding: UTF-8 -*-
'''
sonicwall 6.5.2.x/6.5.3.x 格式与6.5.0.x（大部分使用的版本）导出的配置格式有不用主要是address-object 格式不同，
此程序主要将分行显示的address-object内容整合到一行，以便原程序正常解析内容。
增加了处理address object ipv4 前多一个空格的情况。（将多余的一个空格删除）
author:jason chan
2020-03-12 9:03
'''
import os

def version652():
    with open('sw.log','r') as fp:
        for oneline in fp:
            if 'firmware-version' == oneline[:16]:
                if '6.5.2' in oneline:
                    return True
        return False

def version653():
    with open('sw.log','r') as fp:
        for oneline in fp:
            if 'firmware-version' == oneline[:16]:
                if '6.5.3' in oneline:
                    return True
        return False

def cover653():
    #os.rename('sw.log','sw_raw.log')
    fw = open('sw_ready.log','w')
    print('sw.log ->sw_ready; Convert sonicwall configure file to low version file format...')
    cover_switch = False
    add_string = ''
    address_string = ''
    zone_string = ''
    with open('sw.log','r') as fp:
        for oneline in fp:
            fw.write(oneline)

            #处理偶尔出现在address-object前多一个空格情况，另外，如果前面有4个空格以上将是group下的，所以只处理多一个空格
            if ' address-object ipv4' == oneline[:20]:
                cover_switch = True
                add_string = ''
                address_string = ''
                zone_string = ''
                print('info: process content of line one more space: ', oneline)
            if 'address-object ipv4' == oneline[:19]:
                cover_switch = True
                add_string = ''
                address_string = ''
                zone_string = ''
            if '    exit' == oneline[:8] and cover_switch:
                cover_switch = False
                add_string = add_string + address_string + zone_string
                fw.write(add_string)
            if cover_switch:
                if 'address-object ipv4' == oneline[:19]:
                    add_string = oneline[:len(oneline)-1]
                if ' address-object ipv4' == oneline[:20]:
                    add_string = oneline[1:len(oneline)-1]
                if '    zone' == oneline[:8]:
                    zone_string = oneline[3:len(oneline)-1]
                if '    host' == oneline[:8]:
                    address_string = oneline[3:len(oneline)-1]
                if '    network' == oneline[:11]:
                    address_string = oneline[3:len(oneline)-1]
                if '    range' == oneline[:9]:
                    address_string = oneline[3:len(oneline)-1]
    fw.close()

def cover652():
    os.rename('sw.log','sw_raw.log')
    fw = open('sw.log','w')
    print('sw.log ->sw_raw; Convert sonicwall configure file to low version file format...')
    cover_switch = False
    add_string = ''
    address_string = ''
    zone_string = ''
    with open('sw_raw.log','r') as fp:
        for oneline in fp:
            fw.write(oneline)
            if 'address-object ipv4' == oneline[:19]:
                cover_switch = True
                add_string = ''
                address_string = ''
                zone_string = ''
            if '    exit' == oneline[:8] and cover_switch:
                cover_switch = False
                add_string = add_string + address_string + zone_string
                fw.write(add_string)
            if cover_switch:
                if 'address-object ipv4' == oneline[:19]:
                    add_string = oneline[:len(oneline)-1]
                if '    zone' == oneline[:8]:
                    zone_string = oneline[3:len(oneline)-1]
                if '    host' == oneline[:8]:
                    address_string = oneline[3:len(oneline)-1]
                if '    network' == oneline[:11]:
                    address_string = oneline[3:len(oneline)-1]
                if '    range' == oneline[:9]:
                    address_string = oneline[3:len(oneline)-1]
    fw.close()

if __name__ == '__main__':
    if os.path.exists('sw_ready.log'):
        os.remove('sw_ready.log')
    if version652() or version653():
        cover653()
        print('\nProcessing completed.')
    else:
        print('configura file version is not 652 or 653...pls check it.')

