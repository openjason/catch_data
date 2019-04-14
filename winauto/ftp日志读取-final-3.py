import re, time, os, shutil,datetime

'''
代码需求：
1、分析是否有非法登陆用户。
2、计算用户多少台未进行登陆。
脚本说明：
本代码供包括6个函数，分别为：读取日志文件、去除反复登陆的账户，比对非法登陆账户、计算账户未登陆天数，
以及两个备份源日志文件及过程结果文件的函数。由于函数没有进行内嵌，因此在主函数中顺序执行。

'''
#遍历日志的文件夹，指定了日志文件夹的存放路径，该路径下面根据IP地址命名各个主机日志存放的文件夹。
def eachFile(filepath):
    pathDir = os.listdir(filepath)
    for allDir in pathDir:
        child = os.path.join(filepath, allDir)

        if os.path.isdir(child):

            global new_folder

            folder_name = os.path.join(path_result, allDir)
            new_folder = folder_name + "_" + this_day_full
            os.mkdir(new_folder)#新建文件夹用于存放分析结果
            eachFile(child)
        else:
            readFile(child)

'''
读取日志文件，分析"> USER"字段出现的日志行，并进行登陆用户名的读取。为了方便日志结果的进一步分析，形成了
四个文档，分别为：将含有"> USER"字段的一整行读取出来放入文本文档（login_detail）；将登陆用户名、日期和时间
读取出来放入文本文档（login_information）；为了便于后续计算多久未进行登陆，将登陆日期和用户名写入文本文档
（data_name）；为了方便登陆用户去重，将登陆用户单独写入文本文档（login_name)。
'''

def readFile(filename):
    global new_folder
    keyword = "> USER"
    fopen = open(filename, "r", encoding='UTF-8')  # r 代表read
    for eachLine in fopen:
        # print("读取到得内容如下：",eachLine)
        if keyword in eachLine:
            #将包含"> USER"字段的整行内容写入到文本文件中
            print(eachLine, file=open(new_folder + "\\" + "login_detail" + this_day + ".txt", "a+"))
            line_list = re.split(r"\s", eachLine)
            #将包含"> USER"字段的一行中的登陆时间和用户名写入到文档中
            print(line_list[1], line_list[2], line_list[-2],
                  file=open(new_folder + "\\" + "login_information" + this_day + ".txt", "a+"))
            print(line_list[1], line_list[-2],
                  file=open(new_folder + "\\" + new_folder[-30:-16] + "data_name" + this_day + ".txt", "a+"))
            # 将包含"> USER"字段的一行中的用户名写入到文档中
            print(line_list[-2], file=open(new_folder + "\\" + "login_name" + this_day + ".txt", "a+"))


    fopen.close()

'''
读取只包含用户名的文档，去除重复登陆的用户名后重新写入新的文档(利用读取的login_name的文档进行去重），
新的文档为login_name_noDuplicates。
Q：root[-30:-16]这个是取了字符串的字段，目前采用的形式为XXX.XXX.XX.XXX,即3个3位IP及1个2位的IP，如果换成4个
3位的IP地址，这样的取法就会出现问题。是否可强制采用命名时必须使用4个3位进行，不够位数的使用0进行补充。
欢迎提供好的更好的解决办法进行优化！
'''
def loadDatadet_removeDuplicates(result_path):
     dataset = []
     for root, dirs, files in os.walk(result_path):
         for file in files:

             if os.path.splitext(file)[0].find("login_name") >= 0:#寻找文件中包含"login_name"的文件
                 f = open(os.path.join(root, file))

                 sourceInLine = f.readlines()

                 for line in sourceInLine:
                     temp = line.strip('\n')#去除换行符
                     # temp2=temp1.split('\t')
                     dataset.append(temp)
                 #print(dataset)
                 dataset_nodupl = list(set(dataset))#去除重复列表内容
                #将去除重复后的列表写入到文本文件
                 print(dataset_nodupl,
                       file=open(root + "\\" + root[-30:-16] + "login_name_noDuplicates" + this_day + ".txt", "a+"))
                 print(dataset_nodupl)

#备份日志原始文件
def move_logfile(move_path):
    filelist = os.listdir(move_path)
    logfile_backup_new = logfile_backup + "\\" + this_day_full + "\\" + "日志文件"
    os.makedirs(logfile_backup_new)  # 按照日期新建文件夹用于存放备份文件

    for f in filelist:
        filepath = os.path.join(move_path, f)
        shutil.move(filepath, logfile_backup_new)

#备份分析结果文件
def move_result(move_path):
    filelist = os.listdir(move_path)
    logfile_backup_new = logfile_backup + "\\" + this_day_full + "\\" + "分析结果"
    os.makedirs(logfile_backup_new)#按照日期新建文件夹用于存放备份文件

    for f in filelist:
        filepath = os.path.join(move_path, f)
        shutil.move(filepath, logfile_backup_new)

'''
#分析是否有非法登陆用户。读取login_name_noDuplicates文档中的用户名，与该电脑的用户名列表进行比对。
对比方法为：login_name_noDuplicates文档中的用户形成列表1，电脑用户名文档形成列表2，取列表1和列表2的交集
如果交集等于列表1，则说明没有非法用户登录。如果交集不等于列表1，则存在非法登陆用户。
如果存在非法用户，则遍历两个列表，找出非法用户并输出。
'''
def user_compare(user_table_path,path_result):
    illegal_login = open(result_final + "\\" + "user_illegal_login" + this_day_full + ".txt", "a+")
    for root, dirs, files in os.walk(path_result):

        for file in files:
            if os.path.splitext(file)[0].find("noDuplicates") >= 0:  # 寻找文件中包含"noDuplicates"文件

                for root1, dirs1, files1 in os.walk(user_table_path):#遍历用户列表
                    for i in files1:
                        user_document_name = i.replace(".txt", '')#取用户列表文档的名字，去掉用户名后缀

                        if os.path.splitext(file)[0].find(user_document_name) >= 0:#判断noDuplicates文件名中是或否包含IP表文件名中的IP，用于确认对比文件
                            f = open(os.path.join(root1, i))
                            sourceInLine = f.readlines()
                            for line in sourceInLine:
                                user_list = eval(line)#转换字符串为列表
                                #print("user_list",user_list)

                            g = open(os.path.join(root, file))
                            sourceInLine = g.readlines()

                            for line in sourceInLine:
                                result_user_list = eval(line)#转换字符串为列表
                                #print("result_user_list",result_user_list)

                            user_intersection = set(result_user_list).intersection(set(user_list))#取实际登陆用户和用户列表的交集
                            e3 = list(user_intersection)#将集合转换为列表
                            e3.sort()#对用户列表交集进行重新排序

                            d3 = list(result_user_list)
                            d3.sort()#对实际登陆用户的列表进行重新排序

                            if d3 == e3:
                                 print(user_document_name,"无异常登陆用户",file = illegal_login)

                            else:
                                 for i in range(0,len(d3)):
                                    #for j in range(0,len(user_list)):
                                        if d3[i] in user_list:
                                             pass
                                        else:
                                             print(user_document_name,"非法登陆用户为：",d3[i],file = illegal_login)
'''
计算用户登录时间。首先遍历结果文件夹中已经生成的含有“data_name”字段的文本文档，找到后，遍历列表文件夹
中的文件，读取文件名，去除文件后缀，获取IP地址。然后找到data_name文档中含有该IP地址的文档，找到文档后
执行以下操作：
1、将用户列表中的用户放入字典中，key为用户名，value多久未登陆，初始值为0.
2、将data_name文档中的用户和登陆日期放入字典，key为用户名，value为登陆日期。
3、获取系统当前日期，减去data_name文档形成字典的value值，获取登陆时间间隔。
4、将登陆时间间隔写入用户列表形成的字典中。
'''
def days_nologin(result_path):
    sss = {}
    hhh = {}
    user_list = []

    for root, dirs, files in os.walk(result_path):
        for file in files:

            if os.path.splitext(file)[0].find("data_name") >= 0:  # 寻找文件中包含"login_name"的文件
                for root1, dirs1, files1 in os.walk(user_table_path):#遍历用户列表
                    for i in files1:
                        user_document_name = i.replace(".txt", '')#取用户列表文档的名字，去掉用户名后缀

                        if os.path.splitext(file)[0].find(user_document_name) >= 0:
                            f = open(os.path.join(root1, i))
                            sourceInLine = f.readlines()
                            for line in sourceInLine:
                                user_list = eval(line)  # 转换字符串为列表
                            #print("11111", user_list)
                            for i in range(0,len(user_list)):
                                hhh.update({user_list[i]:0})

                            f = open(os.path.join(root, file))

                            for eachLine in f:
                                line_list = re.split(r"\s", eachLine)
                                key = line_list[1]
                                value = line_list[0]
                                value_data = datetime.datetime.strptime(value, '%Y/%m/%d').date().strftime("%Y/%m/%d")
                                this_day_new = time.strftime('%Y/%m/%d', time.localtime(time.time()))
                                #print("1",value_data)

                                d1 = datetime.datetime.strptime(value_data, '%Y/%m/%d')#转换字符串日期为时间格式
                                d2 = datetime.datetime.strptime(this_day_new, '%Y/%m/%d')#转换字符串日期为时间格式

                                #print("2",this_day_new)
                                #print(type(this_day_new))
                                days_Dvalue = (d2 - d1).days#获取最后一次登陆到现在的时间间隔
                                #print(days_Dvalue)
                                sss.update({key: days_Dvalue})
                            #print(sss)
                            #print(hhh)

                            dictMerged = hhh.copy()
                            dictMerged.update(sss)#先将字典拷贝给dictMerged，在执行update()操作完成合并
                            print(user_document_name,dictMerged)

                            #dicfile = open(result_final + "\\" + 'days_nologin' + this_day_full + '.txt', 'a+')
                            for i in dictMerged.keys():
                                print('{0:<2}{1:<15}{2:<2}{3:<2}'.format("用户名：",i,"未登陆天数：",dictMerged[i]),
                                      file=open(result_final + "\\" + user_document_name +"days_nologin" + this_day + ".txt", "a+"))


if __name__ == '__main__':
    starttime = datetime.datetime.now()
    global new_folder
    new_folder = ""

    filepath = r'E:\log\filezilla\logfile'
    path_result = r'E:\log\filezilla\result'
    logfile_backup = r"E:\log\filezilla\logfile_backup"
    user_table_path = r"E:\log\filezilla\user_table"
    result_final = r"E:\log\filezilla\result_final"
    this_day = time.strftime('%Y%m%d', time.localtime(time.time()))
    this_day_full = time.strftime('%Y%m%d-%H%M%S', time.localtime(time.time()))
    this_day_new = time.strftime('%Y/%m/%d', time.localtime(time.time()))
    eachFile(filepath)#分析文件
    loadDatadet_removeDuplicates(path_result)#去除重复文件名
    user_compare(user_table_path, path_result)  # 比对是否有非法登陆用户
    days_nologin(path_result)
    move_logfile(filepath)#移动备份原始文件
    move_result(path_result)#移动备份分析结果文件
    endtime = datetime.datetime.now()

    print("脚本运行时间为：",(endtime - starttime).seconds,"秒")




