import os

import re

import base64

for exp_file in os.listdir():

    if re.match('.*exp',exp_file):

        file2_name= str('.'.join(exp_file.split('.')[:-1])) +'.txt'

        with open (exp_file, 'rb') as f1:

            contents=f1.read()

            f2 = open(file2_name, 'w')

            f2.write(str((base64.b64decode(contents, altchars=None))).replace('&', '\n'))

        f2.close
        
