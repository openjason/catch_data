import os,sys,time

PROCESSNAME="cfmd.exe"
f=open(r'e:\test\log.txt','a+')

def getallporcesses():
    command = 'tasklist'
    list=os.popen(command).read().split('\n')
    return list


def getprocess(list):
    NOW=time.strftime('%Y-%m-%d_%H:%M:%S',time.localtime(time.time()))
    for v in range(0,len(list)):
        pos=-1
        if PROCESSNAME in list[v]:
            log = NOW+'  '+list[v]+'\n'
            f.write(log)
            pos=v
            break;
        else:
            pass;
    if ( pos==-1):
        log = NOW+'  No Process!\n'
        f.write(log)

def main():
    while(1):
        getprocess(getallporcesses())
        f.flush()
        time.sleep(10)

if __name__ == '__main__':
    main()
