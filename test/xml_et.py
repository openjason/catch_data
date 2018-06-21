#  -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
tree = ET.parse('462.xml')
root = tree.getroot()
print('root-tag:',root.tag,',root-attrib:',root.attrib,',root-text:',root.text)
for child in root:
    print('child-tag:',child.tag,',child.attrib：',child.attrib,',child.text：',child.text)
    for sub in child:
#        print('sub-tag:',sub.tag,',sub.attrib：',sub.attrib,',sub.text：',sub.text)
        if sub.tag == 'User':
            str_temp = sub.attrib['Name']
            print(str_temp,end = '\t')
        for sub2 in sub:
            #print('sub-tag是：',sub2.tag,',sub.attrib：',sub2.attrib,',sub.text：',sub2.text)
            for sub3 in sub2:
                if sub3.tag == 'Permission':
                    #print(type(sub3.tag))
#                    print('sub-tag3:',sub3.tag,',sub3.attrib:',sub3.attrib,',sub.text:',sub3.text)
                    print(sub3.attrib['Dir'])
