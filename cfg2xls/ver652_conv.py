# -*- coding: UTF-8 -*-
'''
sonicwall 6.5.2.x 格式与6.5.0.x（大部分使用的版本）导出的配置格式有不用主要是address-object 格式不同，
此程序主要将分行显示的address-object内容整合到一行，以便原程序正常解析内容。
author:jason chan
2018-07-24
'''
import os

def version652():
    with open('sw.log','r') as fp:
        for oneline in fp:
            if 'firmware-version' == oneline[:16]:
                if '6.5.2' in oneline:
                    return True
        return False

def cover652():
    os.rename('sw.log','sw_652.log')
    fw = open('sw.log','w')
    cover_switch = False
    add_string = ''
    address_string = ''
    zone_string = ''
    with open('sw_652.log','r') as fp:
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
    if version652():
        cover652()
    exit()