# -*- coding: utf-8 -*-
import time
import subprocess
import re
# print ’popen3:’
def external_cmd(cmd, msg_in=''):   
    try:       
        proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,)        
        stdout_value, stderr_value = proc.communicate(msg_in) 
        return stdout_value, stderr_value    
    except ValueError: 
        # log("IOError: %s" % err)       
        return None, None

def zip7z(cl):
    befortime = time.time()
    command7z =cl
    stdout_val, stderr_val = external_cmd(command7z)    
    std_val=str(stdout_val)
    if re.search('Everything is Ok',std_val):
        std=std_val.split('\\r\\n')
        j = 0
        for i in std:
            j += 1
            if not i.find('Scanning the drive'): break
        print('[',command7z,']',std[j])
    else:
        print('命令执行出错: ',command7z)
        print(stderr_val.decode('gbk','ignore'))

    print ("耗时:",time.time()-befortime)

if __name__ == '__main__':    

    
    zip7z('7z a n.zip 7z.*')


