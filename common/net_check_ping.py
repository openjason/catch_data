#!/usr/bin/envpython3
#author: from www
#date:2016-08-05

import socket

def checkip(ipaddr,port):
    try:
        sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((ipaddr,port))
        return True
    except socket.error as e:
        return alse
    finally:
        sock.close()

if __name__=='__main__':
    file=open("ip_list.txt")
    checkinfo=open("check_info.txt",'w+')
    line=file.readline()
    while line:
        if line=="":
            continue
        iplist=line.split('')
        ipaddr=iplist[0]
        port=int(iplist[1])
        status=checkip(ipaddr,port)
        if status == True:
            info='%s%sisOK'%(ipaddr,port)+'/n'
            checkinfo.write(info)
        else:
            info='%s%sisFail'%(ipaddr,port)+'/n'
        checkinfo.write(info)
        line=file.readline()
    file.close()