# -*- coding: utf-8 -*-

import ftplib
import os
import socket
#HOST是远程FTP地址
HOST = '192.168.2.170'
HOST = '1.1.1.231'
USER = 'test'
USERPWD = 'test'
DIRN = '/'


def ftplistdir(f,dir):
#遍历指定ftp服务器dir下目录，返回所遍历的文件路径列表
#参数f：已打开的ftp服务器连接，dir：指定需遍历的路径
    try:
       #得到DIRN的工作目录
        f.cwd(dir)
    except:
        print('列出当前目录失败')
        f.quit()
        return
    #创建列表，用于保存遍历的文件（含路径）
    retflist = []
    downloadlist = f.mlsd()
    for i in downloadlist:
#        print('one',i)
        #若是目录，进入并继续遍历
        cdir=dir + '/' + i[0]
        if i[1]['type'] == 'dir':
            retflist = retflist + ftplistdir(f,cdir)
        else:
            cdir = cdir.replace('//','/')
            #print('filelist:',cdir)
            retflist.append(cdir)
    return retflist
        
def matchftpfile(f,dir,matchfile):
#遍历指定ftp服务器dir下目录，返回匹配的文件路径，无匹配则返回空列表
#参数f：已打开的ftp服务器连接，dir：指定需遍历的路径，matchfile:需查找匹配的的文件名。
#匹配文件名 大小写敏感。
    try:
       #得到DIRN的工作目录
        f.cwd(dir)
    except ftplib.error_perm:
        print('列出当前目录失败:',dir)
        f.quit()
        return
    #创建列表，用于保存遍历的文件（含路径）
    retflist = []
    downloadlist = f.mlsd()
    for i in downloadlist:
#        print('one',i)
        #若是目录，进入并继续遍历
        rawfilename = i[0]
        cdir=dir + '/' + rawfilename
        if i[1]['type'] == 'dir':
            retflist = retflist + matchftpfile(f,cdir,matchfile)
        else:
            cdir = cdir.replace('//','/')
            #print(matchfile,rawfilename)
            if matchfile == i[0]:
                retflist.append(cdir)
#                print (retflist)
                return retflist
            #print('filelist:',cdir)
            #retflist.append(cdir)
    return retflist

def DlFtpFile(f,downloadlist):
    localdir = os.getcwd()
    for getfile in downloadlist:

        pathname = os.path.dirname(getfile)
        rawfilename = os.path.basename(getfile)

        localfilepath = localdir + pathname
#        localfilepath = localfilepath.replace('/','\\')
#        localfilepath = localfilepath.replace('\\','\\\\')
        print('getfile:',getfile,' l:',localfilepath,' r:',rawfilename)
        
        #创建本地指定文件夹
        if not os.path.exists(localfilepath):
            try:
                os.makedirs(localfilepath)
            except:
                print('无法创建文件夹',localfilepath)
              #切换到css文件夹，也就是改变当前工作目录，目的是为了将要下载的文件下载到这个文件夹
        try:
            os.chdir(localfilepath)
        except:
            print('chdir error:')
           #遍历刚才返回的文件名列表

        try:
           #ftp 转到指定工作目录
            f.cwd(pathname)
        except :
            print('error cwd')
            f.quit()
            return
        
        #print('RETR %s' % rawfilename)
        try:
            f.retrbinary('RETR %s' % rawfilename,open(rawfilename,'wb').write)
            
        except :
            print('无法读取"%s"' % getfile)
            os.unlink(getfile)
        print('文件"%s"下载成功' % getfile)
    return
      
def ftpmain():
    try:
        f = ftplib.FTP(HOST)
        f.encode = 'utf-8'
    except :
        print('无法连接到"%s"' % HOST)
        return
    print('连接到"%s"' % HOST)
   
    try:
        #user是FTP用户名，pwd就是密码了
        f.login(USER,USERPWD)
    except ftplib.error_perm:
        print('登录失败')
        f.quit()
        return
    print('登陆成功')

#retfl = ftplistdir(f,DIRN)

    matchfile = 'ulist.txt'

    retfl = matchftpfile(f,DIRN,matchfile)    
    if retfl == None:
        exit()
    if len(retfl) <1 :
        print("can not match file:",matchfile)
    else:
#        print ((retfl))
        DlFtpFile(f,retfl)
        f.quit()

   
   
   
if __name__ == '__main__':
    ftpmain()
