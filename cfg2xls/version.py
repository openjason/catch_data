# -*- coding: UTF-8 -*-
'''
根据华为防火墙配置文件配置内容，提取分类内容，保存到excel文件不同的sheet相应栏目中
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
            if 'address-object' == oneline[:14]:
                cover_switch = True
                add_string = ''
            if '    exit' == oneline[:8]:
                cover_switch = False
                add_string = add_string + address_string + zone_string
                fw.write(add_string)
            if cover_switch:
                if 'address-object' == oneline[:14]:
                    add_string = oneline
                if '    zone' == oneline[:8]:
                    zone_string = oneline
                if '    host' == oneline[:8]:
                    address_string = oneline
                if '    network' == oneline[:11]:
                    address_string = oneline
                if '    range' == oneline[:9]:
                    address_string = oneline
    fw.close()

if __name__ == '__main__':
    if version652():
        cover652()
    exit()