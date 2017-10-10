import urllib.request
from md5 import GetFileMd5

url = 'http://definitions.symantec.com/defs/ips/20171009-013-IPS_IU_SEP.exe'
f = urllib.request.urlopen(url)
with open('f:\\test\\test.zip','wb') as code:
    code.write(f.read())

md5 = GetFileMd5('f:\\test\\test.zip')
print (md5)