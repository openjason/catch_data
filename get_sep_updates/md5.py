import hashlib
import os
import datetime

def GetFileMd5(filename):
    if not os.path.isfile(filename):
        print('no file open.')
        return
    myhash = hashlib.md5()
    f = open(filename,'rb')
    while True:
        b = f.read(8096)
        if not b :
            break
        myhash.update(b)
    f.close()
    return myhash.hexdigest()

if __name__ == '__main__':
    filepath = input('请输入文件路径：')

    # 输出文件的md5值以及记录运行时间
    starttime = datetime.datetime.now()
    print (GetFileMd5(filepath))
    endtime = datetime.datetime.now()
    print ('运行时间：%ds'%((endtime-starttime).seconds))