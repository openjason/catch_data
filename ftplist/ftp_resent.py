'''
主要作用：支持ftp上传，断点上传。
要支持目录的话，改改就行.原理是一样的.
断点下载也类似.

未测试
'''
#
# #!/usr/bin/env python2.5.4
# #coding:utf-8
# from ftplib import FTP
# import os
# import sys
# import traceback
#
# class MyFTP(FTP):
# #继承父类中的方法在子类中可以直接调用
# #重载父类中storbinary的方法
#
#     def storbinary(self, cmd , fd,fsize=0,rest=0):
#
#         blocksize=1024
#         cmpsize=rest
#         conn = self.transfercmd(cmd, rest)
#         while 1:
#                 if rest==0:
#                         buf=fd.read(blocksize)
#                 else:
#                         fd.seek(cmpsize)
#                         buf=fd.read(blocksize)
#                 if buf:
#                         conn.send(buf)
#                 else:
#                         print( 'Ending.')
#                         break
#                 cmpsize+=blocksize
#         conn.close()
#         fd.close()
#
# def ConnectFTP(remoteip,remoteport,loginname,loginpassword):
#
#     ftp=MyFTP()
#     try:
#         ftp.connect(remoteip,remoteport)
#     except:
#         return 0,'connect failed!'
#     else:
#         try:
#             ftp.login(loginname,loginpassword)
#         except:
#             return (0,'login failed!')
#         else:
#             return (1,ftp)
#
# def mywork(remoteip,remoteport,loginname,loginpassword,path,localfile,filesize):
#     res=ConnectFTP(remoteip,remoteport,loginname,loginpassword)
#     bufsize=1024
#     if res[0]!=1:
#         print(res[1])
#         sys.exit()
#     ftp=res[1]
#     fd=open(localfile,'rb')
#     ftp.set_pasv(0)
# #到这一部出现连接超时请偿试设置非0值
#     if path:
#         ftp.cwd(path)
#     file_list=ftp.nlst()
#     if localfile in file_list:
#         rest=ftp.size(localfile)
#         print( 'Conntinue uploading:')
#         ftp.storbinary('STOR %s' % localfile ,fd,filesize,rest)
#     else:
#         print ('Starting upload:...')
#
#         ftp.storbinary('STOR %s' % localfile ,fd,filesize,0)
#     ftp.set_debuglevel(0)
#
# if __name__== '__main__':
#         remoteip=sys.argv[1]
#         remoteport=sys.arg[2]
#         loginname=sys.arg[3]
#         loginpassword=sys.arg[4]
#         filename=sys.argv[5]
#         path=sys.argv[6]
#         port=21
#         statinfo=os.stat(filename)
#         size=int(statinfo.st_size)
#         mywork(remoteip,port,loginname,loginpassword,path,filename,size)
import socket
from ftplib import FTP
ftp_server='xx.xx.xx.xx'
ftp_user='xxxxx'
ftp_password='xxxxx'
ftp_backup_dir='backup'

newday = date.today()  #获取今天的日期
oldday = date.today()-timedelta(5)  #获得5天前的日期
newfile = '/home/backup/' + 'backup_data_' + str(newday.year) + '.' + str(newday.month) + '.' + str(newday.day) + '.zip'  #本次备份文件名(绝对路径)
oldfile = '/home/backup/' + 'backup_data_' + str(oldday.year) + '.' + str(oldday.month) + '.' + str(oldday.day) + '.zip'  #5天前备份的文件名(绝对路径)

def upload():
    socket.setdefaulttimeout(60)  #超时FTP时间设置为60秒
    ftp = FTP(ftp_server)
    print("login ftp...")
    try:
        ftp.login(ftp_user, ftp_password)
        print(ftp.getwelcome())  #获得欢迎信息

        try:
            if ftp_backup_dir in ftp.nlst():
                print("found backup folder in ftp server, upload processing.")
            else:
                print("don't found backup folder in ftp server, try to build it.")
                ftp.mkd(ftp_backup_dir)
        except:
            print("the folder" + ftp_backup_dir + "doesn't exits and can't be create!")
            sys.exit()
    except:
        print("ftp login failed.exit.")
        sys.exit()
    ftp.cwd(ftp_backup_dir)  #设置FTP路径

    print("upload data...")
    try:
        ftp.storbinary('STOR ' + os.path.basename(newfile), open(newfile,'rb'), 1024)  #上传备份文件
    except:
        print("upload failed. check your permission.")

    print("delte old file...")
    try:
        ftp.delete(os.path.basename(oldfile))  #删除5天前的备份文件
    except:
        print("the old file in ftp doesn't exists, jumped.")

    print("ftp upload successful.exit...")
    ftp.quit()

if __name__== '__main__':
    upload()