#  -*- coding: utf-8 -*-
#userlist.txt :{'abc': '2018-08-09 20:20:51.590697 +0800', 'xxx': '2010-08-09 20:13:47', 'singtel': '2017-08-05 19:51:16.182888 +0800'}
import xml.etree.ElementTree as ET
import datetime
import os
import shutil

f = open('用户列表.txt','r')
a = f.read().lower()

user_dict = eval(a)
f.close()

flogin = open('成功登陆.txt','a+')
flogin.write('\n'+'='*40)
ffailed = open('登录验证失败.txt','a+')
ffailed.write('\n'+'='*40)
fillegal = open('非法用户登录.txt','a+')
fillegal.write('\n非法用户登录'+'='*40)

rootdir = 'log'
logfilelist = os.listdir(rootdir) #列出文件夹下所有的目录与文件
logfilelist.sort()

for filename in logfilelist:
    if 'BvSshServer' in filename:
        logfilename  = 'log//' + filename
        tree = ET.parse(logfilename)
        root = tree.getroot()
        print ("process filename :" + logfilename)
        print('root-tag:',root.tag,',root-attrib:',root.attrib,',root-text:',root.text)
        count = 1
        for child in root:
            ctag = child.attrib
            try:
                c_tag =  ctag['name']
                c_time = ctag['time']
            except:
                continue

            if ctag['name'] == 'I_LOGON_AUTH_SUCCEEDED' :
#                print('child-tag:',child.tag,',child.attrib：',child.attrib,',child.text：',child.text)
                for sub in child:
                    ctag = sub.attrib
                    if sub.tag == 'authentication':
#                        print('sub-tag:',sub.tag,',sub.attrib：',sub.attrib,',sub.text：',sub.text)
                        try:
                                c_tag = ctag['userName'].lower()
                                print('OK_:',c_tag,'TT:',c_time)
                                if c_tag.lower() in user_dict:
                                    flogin.write('\n'+'正常用户:'+c_tag+'   登录时间:'+c_time)
#                                    if  c_time > user_dict[c_tag]:
                                    flogin.write('\n' + '正常用户:' + c_tag + '           更新最新登录时间:' + user_dict[c_tag] + ' >> ' + c_time)
                                    user_dict[c_tag] = c_time
#                                    print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
#                                    print(c_time)
                                else:
                                    fillegal.write('\n'+'注意，非法用户登录:' + c_tag + '  登录时间:' + c_time )
                        except:
                            print("except 异常")
                            continue

            elif ctag['name'] == 'I_LOGON_AUTH_FAILED' or ctag['name'] == 'I_LOGON_AUTH_CACHE_ASSISTED_LOGON_FAILED':
#                print('child-tag:',child.tag,',child.attrib：',child.attrib,',child.text：',child.text)
                for sub in child:
                    ctag = sub.attrib
                    if sub.tag == 'authentication':
#                        print('sub-tag:',sub.tag,',sub.attrib：',sub.attrib,',sub.text：',sub.text)
                        try:
                            c_tag = ctag['userName']
                            print('Fail_:', c_tag, 'TT:', c_time)
        #                    if c_tag in user_dict:
                            ffailed.write('\n'+'用户密码验证失败：'+c_tag+'     登录时间:'+c_time)
                        except:
                            continue

for filename in logfilelist:
    if 'BvSshServer' in filename:
        sourcefilename  = 'log//' + filename
        destfilename = 'proced//' + filename
        shutil.move(sourcefilename,destfilename)


flogin.close()
ffailed.close()
fillegal.close()
f = open('用户列表.txt','w')
f.write(str(user_dict))
f.close()



f = open('用户最近一次登录时间.txt','a+')
for u in user_dict:
    daystr = user_dict[u]
    try:
        day1 =  datetime.datetime.now()
        day2 = datetime.datetime.strptime(daystr[:19], "%Y-%m-%d %H:%M:%S")
        days = (day1 - day2).days
        if days > 999:
            days = 999
            f.write('\n用户登录时间距今 '+str(days) + ' 天，用户名：'+u+ ' 登录时间：')
        else:
            f.write('\n用户登录时间距今 '+str(days) + ' 天，用户名：'+u+ ' 登录时间：'+str(user_dict[u]))
    except:
        days = 999
        f.write('\n用户登录时间距今 '+str(days) + ' 天，用户名：'+u+ ' 登录时间：')
f.close()
