import os,os.path
import zipfile
 
def zip_dir(dirname,zipfilename):

    if os.path.exists(zipfilename):
        if os.path.isfile(zipfilename):
            try:
                os.remove(zipfilename)
            except OSError:
                print('无法创建文件:',zipfilename)
                quit()
                
    filelist = []
    if os.path.isfile(dirname):
        filelist.append(dirname)
    else :
        for root, dirs, files in os.walk(dirname):
            for name in files:
                filelist.append(os.path.join(root, name))
         
    zf = zipfile.ZipFile(zipfilename, "w", zipfile.zlib.DEFLATED)
    password = zf.setpassword(b'abcd')
    for tar in filelist:
        arcname = tar[len(dirname):]
        #print arcname
        zf.write(tar,arcname)
        pwd = b'catdog' 
    zf.close()
 
if __name__ == '__main__':

    zip_dir('c:\\temp\\abcd',r'c:\\temp\\ttttest.zip')



