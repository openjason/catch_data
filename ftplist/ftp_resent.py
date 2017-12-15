'''
主要作用：支持ftp上传，断点上传。
要支持目录的话，改改就行.原理是一样的.
断点下载也类似.

未测试
'''
#!/usr/bin/env python2.5.4
#coding:utf-8
from ftplib import FTP
import os
import sys
import traceback

class MyFTP(FTP):
#继承父类中的方法在子类中可以直接调用
#重载父类中storbinary的方法

    def storbinary(self, cmd , fd,fsize=0,rest=0):

        blocksize=1024
        cmpsize=rest
        conn = self.transfercmd(cmd, rest)
        while 1:
                if rest==0:
                        buf=fd.read(blocksize)
                else:
                        fd.seek(cmpsize)
                        buf=fd.read(blocksize)
                if buf:
                        conn.send(buf)
                else:
                        print( 'Ending.')
                        break
                cmpsize+=blocksize
        conn.close()
        fd.close()

def ConnectFTP(remoteip,remoteport,loginname,loginpassword):

    ftp=MyFTP()
    try:
        ftp.connect(remoteip,remoteport)
    except:
        return 0,'connect failed!'
    else:
        try:
            ftp.login(loginname,loginpassword)
        except:
            return (0,'login failed!')
        else:
            return (1,ftp)

def mywork(remoteip,remoteport,loginname,loginpassword,path,localfile,filesize):
    res=ConnectFTP(remoteip,remoteport,loginname,loginpassword)
    bufsize=1024
    if res[0]!=1:
        print(res[1])
        sys.exit()
    ftp=res[1]
    fd=open(localfile,'rb')
    ftp.set_pasv(0)
#到这一部出现连接超时请偿试设置非0值
    if path:
        ftp.cwd(path)
    file_list=ftp.nlst()
    if localfile in file_list:
        rest=ftp.size(localfile)
        print( 'Conntinue uploading:')
        ftp.storbinary('STOR %s' % localfile ,fd,filesize,rest)
    else:
        print ('Starting upload:...')

        ftp.storbinary('STOR %s' % localfile ,fd,filesize,0)
    ftp.set_debuglevel(0)

if __name__== '__main__':
        remoteip=sys.argv[1]
        remoteport=sys.arg[2]
        loginname=sys.arg[3]
        loginpassword=sys.arg[4]
        filename=sys.argv[5]
        path=sys.argv[6]
        port=21
        statinfo=os.stat(filename)
        size=int(statinfo.st_size)
        mywork(remoteip,port,loginname,loginpassword,path,filename,size)
