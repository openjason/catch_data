#!/bin/env python
# -*- coding:utf-8 -*-

# program: ssh remote execute command
#          genaral data story local
# author: chenhao
# date: 2015-09-14

import sys
import paramiko
import xlwt
import time
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    filename='check.log',
                    filemode='w',
                    datefmt='%Y-%m-%d %X')
#reload(sys)
ISOTIMEFORMAT='%Y-%m-%d'
#sys.setdefaultencoding('utf-8')

def header(work_sheet):
  work_sheet.write(0, 0, '检查项目', style0)
  work_sheet.write(0, 1, '命令', style0)
  work_sheet.write(0, 2, '基准', style0)
  work_sheet.write(0, 3, '检查结果', style0)
  work_sheet.write(0, 4, '检查主机', style0)
  logging.info('header add ok!')
  return work_sheet
  
def run_host_cmd(host, port, username, password, work_sheet):
  ssh = paramiko.SSHClient()
  command_file = open('./hosts/' + host + '.cmd', 'r')

  for line in command_file.readlines():
    rows = len(work_sheet.rows)
    line = line.strip('\n')
    items = line.split('#')

##    check_type = items[0].decode('gbk').encode('utf-8')
##    check_cmd = items[1].decode('gbk').encode('utf-8')
##    check_base_line = items[2].decode('gbk').encode('utf-8')
    check_type = items[0]
    check_cmd = items[1]
    check_base_line = items[2]
    opration = check_base_line[0:1]
    base_value = check_base_line[1:]


    work_sheet.write(rows, 0, check_type)
    work_sheet.write(rows, 1, check_cmd)
    work_sheet.write(rows, 2, check_base_line)

    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
      ssh.connect(host, port, username, password, key_filename=None, timeout=2)
    except Exception as e:
      logging.error('can not connect host: ' + host)
      logging.error('command can not exec: ' + check_cmd)
      logging.error(e)
      continue
    stdin, stdout, stderr = ssh.exec_command(check_cmd)
    breturn_info = stdout.read().strip()
    return_info = str(breturn_info,encoding='utf-8')
    style_red = xlwt.easyxf('pattern: pattern solid, fore_colour red;' +
      'font: name Times New Roman, color-index black, bold on;' +
      'borders: left thick, right thick, top thick, bottom thick;' +
      'align: horiz center')

    error_flag = False

    if opration == '>':
      if str(base_value) > str(return_info):
        error_flag = True
    elif opration == '=':
      if str(return_info) != str(base_value):
        error_flag = True
    elif opration == '<':
      if str(base_value) < str(return_info):
        error_flag = True

    if error_flag:
      logging.warning(host + ' checked diff')
      logging.warning('command is: ' + check_cmd)
      work_sheet.write(rows, 3, str(return_info), style_red)
    else:
      work_sheet.write(rows, 3, return_info)

    work_sheet.write(rows, 4, 'server IP: ' + host)
	
    check_info = str(check_type) + '\t' + str(check_cmd) + '\t' + str(check_base_line) + '\t' + str(return_info)
    check_info = check_info.strip('\n')
    check_info += '\t' + 'server IP: ' + host
    logging.info(check_info)
  command_file.close()
  ssh.close()
  return work_sheet

if __name__=='__main__':
#   try:
#     main()
#   except Exception,e:
#     print e

  style0 = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;' +
    'font: name Times New Roman, color-index black, bold on;' +
    'borders: left thick, right thick, top thick, bottom thick;' +
    'align: horiz center',
    num_format_str='0,000.00')

  work_book = xlwt.Workbook(encoding='utf-8')
  work_sheet = work_book.add_sheet('A Test Sheet')
  work_sheet = header(work_sheet)
  
  hosts_file = open('./hosts/host.info', 'r')
  
  for line in hosts_file.readlines():
    if line[0:1] == '#': continue
    line = line.strip('\n')
    items = line.split()
    port = 22
    host = items[0]
    username = items[1]
    password = items[2]

    work_sheet = run_host_cmd(host, port, username, password, work_sheet)
    logging.info(host + ' check finish !\n')
  file_pre = time.strftime(ISOTIMEFORMAT, time.localtime(time.time()))
  work_book.save(file_pre + '_app.xls')

