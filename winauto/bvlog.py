#  -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
tree = ET.parse('bvssh.log')
root = tree.getroot()
print('root-tag:',root.tag,',root-attrib:',root.attrib,',root-text:',root.text)
count = 1
for child in root:
    ctag = child.attrib
    try:
        c_tag =  ctag['name']
        c_time = ctag['time']
    except:
#        print('no keyword name')
        continue

    if ctag['name'] == 'I_LOGON_AUTH_SUCCEEDED' :
#        print('child-tag:',child.tag,',child.attrib：',child.attrib,',child.text：',child.text)
        for sub in child:
            ctag = sub.attrib
            if sub.tag == 'authentication':
#                print('sub-tag:',sub.tag,',sub.attrib：',sub.attrib,',sub.text：',sub.text)
                try:
                        c_tag = ctag['userName']
                        print('OK_sub-tag:',c_tag,'TT:',c_time)
                except:
    #                print('no keyword name')
                    continue

    elif ctag['name'] == 'I_LOGON_AUTH_FAILED':
        for sub in child:
            ctag = sub.attrib
            if sub.tag == 'authentication':
                #                print('sub-tag:',sub.tag,',sub.attrib：',sub.attrib,',sub.text：',sub.text)
                try:
                    c_tag = ctag['userName']
                    print('Fail_sub-tag:', c_tag, 'TT:', c_time)
                except:
                    continue
