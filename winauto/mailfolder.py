#程序功能：copytree参数指定文件夹，获得文件夹内文件，不包括空文件夹，将同一个文件夹文件及路径用分号；分开，不同文件夹用#号分开，生成一长字符串。
#将同一文件夹文件作为附件，可多个附件，通过电子邮件方式发送出去，收件人电子邮件地址需修改。邮件主题用文件夹后两个文件夹名组成，附件名为原附件名称。
#程序启动后由于网络发送邮件可能无法退出，特别是发送大邮件时更为明显。
import os.path
import shutil
import getpass

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib


#创建一个带附件的实例

def sendmp3(uname,upwd,flist):
    msg = MIMEMultipart()

    #构造附件1

    fl = flist.split(';')
    for onefile in fl:
        if len(onefile) > 1:
            pname = os.path.abspath(onefile)
            srcname = os.path.basename(onefile)
            print(onefile)# + '|' + srcname)
            att1 = MIMEText(open(onefile, 'rb').read(), 'base64', 'gb2312')
            att1["Content-Type"] = 'application/octet-stream'
            #att1["Content-Disposition"] = 'attachment; filename='+srcname.encode('utf-8')
            att1.add_header('Content-Disposition', 'attachment', filename=('gbk', '', srcname))
            #这里的filename可以任意写，写什么名字，邮件中显示什么名字
            msg.attach(att1)

    #加邮件头
    fname=pname.split('/')
    msg['to'] = '2090554739@qq.com'
    msg['from'] = 'openjc@163.com'
    msg['subject'] = fname[len(fname)-3] + fname[len(fname)-2]
    #发送邮件
    try:
        server = smtplib.SMTP()
        server.connect('smtp.163.com')

        server.login(uname,upwd)#XXX为用户名，XXXXX为密码
        server.sendmail(msg['from'], msg['to'],msg.as_string())
        server.quit()
        print('发送成功')
    except Exception as e:
        print(str(e))

def copytree(src, dst,symlinks=False):

    names = os.listdir(src)
    #os.makedirs(dst)
    errors = []
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                dst = copytree(srcname, dst, symlinks)
            else:
                #print(srcname,end='')
                dst = dst + srcname+';'
                #+ dstname)
            # XXX What about devices, sockets etc.?

        except OSError as why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
    dst = dst +'#'
    return dst
    #try:
        #copystat(src, dst)

    #except OSError as why:
        # can't copy file access times on Windows
    #    if why.winerror is None:
    #        errors.extend((src, dst, str(why)))

    if errors:
        raise Error(errors)

if __name__ == "__main__":
    # execute only if run as a script
    str1=copytree('/media/jcc/4G/window','')
    flists=str1.split('#')
    uname = getpass.getuser()
    uname = 'openjc@163.com'
    upwd =  getpass.getpass()
    for flist in flists:
        if len(flist)>1:
#            print(len(flist))
            sendmp3(uname,upwd,flist)
