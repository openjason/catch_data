#coding=utf-8  
''''' 
    Description: 可逆的加密与解密 
'''''
import os  
import sys  
class Code(object):  
    '''''可逆的加密与解密'''
    def __init__(self, key = "eastcompeace"):  
        self.__src_key = key  
        self.__key = self.__get_strascii(self.__src_key, True)  
    def encode(self, value):  
        '''''加密函数, 加密后为一串数字'''
        return  "%d" % (self.__get_strascii(value, True) ^ self.__key)  
    def decode(self, pwd):  
        '''''解密函数'''
        if self.is_number(pwd):  
            return self.__get_strascii( (int(pwd)) ^ self.__key, False )  
        else:  
            print ('require number.')
    def reset_key(self, key):  
        '''''重新设置key'''
        self.__src_key = key  
        self.__key = self.__get_strascii(self.__src_key, True)  
#===============================================================================  
#        内部调用接口  
#===============================================================================  
    def __get_strascii(self, value, bFlag):  
        if bFlag:  
            return self.__get_str2ascii(value)   
        else:  
            return self.__get_ascii2str(value)  
    def __get_str2ascii(self, value):  
        ls = []  
        for i in value:  
            ls.append( self.__get_char2ascii( i ) )  
        return int("".join(ls))  
    def __get_char2ascii(self, char):  
        '''''获取单个字符的acsii码值'''
        try:  
            return "%03.d" % ord(char)  
        except (TypeError, ValueError):  
            print ("key error.")
            exit(1)  
    def __get_ascii2char(self, ascii):  
        if self.is_ascii_range(ascii):  
            return chr(ascii)  
        else:  
            print ("ascii error(%d)" % ascii  )
            exit(1)         
    def __get_ascii2str(self, n_chars):  
        ls = []  
        s = "%s" % n_chars  
        n, p = divmod(len(s), 3)  
        if p > 0:  
            nRet = int(s[0 : p])  
            ls.append( self.__get_ascii2char(nRet))  
        pTmp = p  
        while pTmp < len(s):  
            ls.append( self.__get_ascii2char( int(s[pTmp: pTmp + 3])) )
            pTmp += 3
        return "".join(ls)  
#================================================================================  
#        工具接口  
#================================================================================  
    def is_number(self, value):  
        try:  
            int(value)  
            return True
        except (TypeError, ValueError):  
            pass
        return False
    def is_ascii_range(self, n):  
        return 0 <= n < 256
    def is_custom_ascii_range(self, n):  
        return 33 <= n <48 or 58 <= n < 126        




if __name__ == '__main__':  

    encode = Code()
    print(encode.encode('test@pwd'))
    print(encode.decode('101097115101257476712341401883855082'))
