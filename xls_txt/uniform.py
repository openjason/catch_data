#-*- coding:utf-8 -*-
'''
处理前准备文件：
1.《流水表》 —— 由财务每天提供
2.《Oracle系统客户名称与区域关系表》 每半年维护一次从EBS后台导出，财务人员没有权限
3.《省市地址表》
4.《区域与省市关系表》
5.《区域与负责人分配表》 —— 配置文件
6.《EBS付款银行基础表》 —— 从流水表中取
处理后导出文件：
《银行流水统一格式》
处理逻辑
1.将《2019国内每日收款明细》银行流水表作为基础数据
2.特殊字段取值要求。
“收款银行”
取sheet表名称
“摘要”
交行：【摘要】
工行：【摘要】+【用途】+【个性化信息】
中行：【用途】
浦发：【备注】
建行：【余额】+【摘要】+【备注】
3.将《银行流水表》流水分类，筛选规则参考如下。
入账流水规则：
交行：贷方发生额>0
工行：贷方发生额 空白的去除 & 摘要包含“利息划入”去除
中行：交易类型筛选“来账”
浦发：贷方发生额去掉空白
建行：贷方发生额>0
其他流水规则：
不符合上述的入账流水规则
4.补充收款银行与收款人账号
交行 账号写在页面第一行
建行、浦发  没有账号，要求财务会计补充在页面第一行
工行、交行 在流水中取账号，要求财务会计补充在页面第一行
5.区分所属产品分类（国内卡产品与系统事业产品放在两个不同的sheet中）与区域
第一步：将付款人名称与《Oracle系统客户名称与区域关系表》的客户名称匹配，名称完全一致的可以匹配出产品分类与区域名称。
第二步：利用付款人名称带药字或者中文长度是3个字的属于系统事业产品（不用再执行第三步）；其他均为国内卡产品。
#（请忽略）第三步：国内卡产品付款人名称中会带省市词，例如1）“中国移动通信集团山东有限公司”，山东能匹配出《省市地址表》中的“山东”省份字段，再匹配出《区域与省市关系表》中的区域。2）“中国石化销售有限公司广东珠海石油分公司”珠海能匹配出《省市地址表》中的“珠海”城市字段，再匹配出《区域与省市关系表》中的区域。（先匹配城市，再匹配省市，无法匹配的置空）
东北:黑龙江 吉林 辽宁 3
华北:北京 天津 河北 内蒙 山西5
西北:陕西 甘肃 宁夏 青海 新疆5
华东:上海 江苏 浙江 安徽 山东 江西6
中南:河南 湖北 湖南3
华南:广东 广西 福建 海南4
西南:四川 重庆 贵州 云南 西藏5
(台湾，香港，澳门不在区域中)3
7.匹配负责人
按照《区域与负责人分配表》，进行负责人分配。
8.匹配银行表头与银行流水统一格式见《银行流水表字段数据》
9.请按《银行流水统一格式》填写3个sheet表
10.最终统一格式
'''

from configparser import ConfigParser
from os.path import exists as os_path_exists
from datetime import datetime
from openpyxl import load_workbook
import os
import logging
from logging.handlers import RotatingFileHandler
from openpyxl.styles import Border, Side, Alignment, PatternFill  #设置字体和边框需要的模块

xl_border = Border(left=Side(style='thin',color='FF000000'),right=Side(style='thin',color='FF000000'),top=Side(style='thin',color='FF000000'),bottom=Side(style='thin',color='FF000000'),diagonal=Side(style='thin',color='FF000000'),diagonal_direction=0,outline=Side(style='thin',color='FF000000'),vertical=Side(style='thin',color='FF000000'),horizontal=Side(style='thin',color='FF000000'))

dlevel = 1

#设置日志文件配置参数
def set_logging():
    global logger
    logger = logging.getLogger('balance_logger')
    handler = RotatingFileHandler('日志记录.log', maxBytes=5000000, backupCount=6)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    formatter = logging.Formatter('%(asctime)-12s %(filename)s %(lineno)d %(message)s')
    handler.setFormatter(formatter)

#定义类，脚本主要更能
class App():
    def __init__(self):

    # 脚本指定数据库名称sqlite3("db_dz.db3")
        self.customer_name = ''
        self.kehu_pos_datail = []
        self.data_dir = ''
        self.file_from_cangkujxc = ''
        self.file_from_youjiqingdan = ''
        self.file_from_jichu = ''
        self.curr_month = ''
        self.initWidgets()

# 按文件夹统计符合条件文件列表，逐个文件导入数据库
    def proc_folder(self, customer, work_dir):

        print("清空原有汇总统计数据（hztj）数据...")

        for parent, dirnames, filenames in os.walk(work_dir, followlinks=True):
            for filename in filenames:
                file_path = os.path.join(parent, filename)
                if '汇总统计' in filename:
                    print('文件名：%s' % filename)
                    print('文件完整路径：%s\n' % file_path)
                    self.xls_db('gsnx', file_path)

    #按字符查找符合条件文件名，返回文件列表
    def find_filename(self, curr_path, curr_filename_path):
        list_files = []
        for parent, dirnames, filenames in os.walk(curr_path, followlinks=True):
            for filename in filenames:
                file_path = os.path.join(parent, filename)
                if curr_filename_path in filename:
                    print('文件名：%s' % file_path)
                    list_files.append(file_path)
        if len(list_files) > 0:
            return (list_files[0])
        else:
            return (None)

    # 从数据库导出价格（基础表），返回含价格信息列表

#从数据库处理数据，导出对账文件excel
    def csvdata_list(self, customer, xlsfilename):

        print('导入文件数据： ',xlsfilename)
        int_first_row = 3
        customer_zone_list  = []

        # 获取明细表数据
        xlsfilename = self.data_dir + xlsfilename
        #workbook = load_workbook(xlsfilename)  # 打开excel文件
        logger.info('导入 ~开票平台中客户及区域~ 表' )
        #worksheetj = workbook['开票平台中客户及区域']  # 根据Sheet1这个sheet名字来获取该sheet
        i = 0
        #max_rows = worksheetj.max_row
        with open(xlsfilename,'r',encoding='UTF-8') as csvfile:
            csv_lines = csvfile.readlines()
            for line in range(0,len(csv_lines)):
                csv_cell = csv_lines[line].split(',')
                temp1 = csv_cell[0]
                temp1 = temp1.strip()
                temp2 = csv_cell[1]
                temp2 = temp2.strip()
                customer_zone_list.append([temp1,temp2])
                #print(temp1,temp2)
            logger.info(customer_zone_list)
            print('导入-开票平台中客户及区域-文件 （行）：', len(customer_zone_list))

        workbook_import = load_workbook('区域与负责人分配表.xlsx')  # 打开excel文件
        logger.info('导入 ~区域与负责人分配表~ 表' )
        print('导入 ~区域与负责人分配表~ 表' )
        worksheet_import = workbook_import['Sheet1']
        sheet_import_maxrow = worksheet_import.max_row
        qu_yu_yu_fu_ze_ren_fen_pei_list = []
        for i in range(1,sheet_import_maxrow +1):
            value1 = worksheet_import.cell(i,1).value
            value2 = worksheet_import.cell(i,2).value
            value3 = worksheet_import.cell(i,3).value
            qu_yu_yu_fu_ze_ren_fen_pei_list.append([value1,value2,value3])
        logger.info(qu_yu_yu_fu_ze_ren_fen_pei_list)
        print('导入-区域与负责人分配表-文件 （行）：', len(qu_yu_yu_fu_ze_ren_fen_pei_list))
        workbook_import.close()


        # 获取明细表数据
        #xlsfilename = self.data_dir + xlsfilename
        workbook_source = load_workbook('国内每日收款明细.xlsx')  # 打开excel文件
        logger.info('导入 ~国内每日收款明细~ 表' )

        workbook_target = load_workbook('银行流水统一格式.xlsx')  # 打开excel文件
        logger.info('转换到 ~银行流水统一格式~ 表' )


    #工行 数据处理 begin
        gong_hang_guo_nei_count  = 0
        gong_hang_xi_tong_count  = 0

        sheet_name = '工行'
        worksheet_source = workbook_source[sheet_name]  # 根据Sheet1这个sheet名字来获取该sheet
        sheet_source_maxrow = worksheet_source.max_row
        print('数据处理： ',sheet_name)

        first_row_target=3
        first_row_source=2
        
        #收款银行
        shou_kuan_yin_hang = '工商银行'
        #收款银行账号 对应 工行 本方账号
        shou_kuan_yin_hang_zhanghao_pos = 2
        #付款银行账号 对应 工行 对方账号
        fu_kuan_zhanghao_pos = 3
        #付款人账号名称 对应 工行 对方单位名称
        fu_kuan_ren_mingcheng_pos = 11
        #客户类型
        ke_hu_lei_xin = '国内'
        #币种
        bi_zhong = 'CNY'
        #金额 对应 工行 贷方发生额
        jin_e_pos = 7
        #交易时间
        jiao_yi_shi_jian_pos = 4
        #摘要
        zhai_yao_pos1 = 9   #摘要
        zhai_yao_pos2 = 10  #用途
        zhai_yao_pos3 = 13  #个性化信息
        #承办人
        cheng_ban_ren_content = ' '
        #贷方发生额
        dai_fang_fa_sheng_e_pos = 7

        #worksheet_target = workbook_target[sheet_name]  # 根据Sheet1这个sheet名字来获取该sheet
        #print(sheet_name)
        guo_nei_last_row_target = first_row_target
        xi_tong_shi_ye_last_row_target = first_row_target

        for i in (range(first_row_source,sheet_source_maxrow)):
            dai_fang_fa_sheng_e = worksheet_source.cell(i,dai_fang_fa_sheng_e_pos).value
            if worksheet_source.cell(i,zhai_yao_pos1).value == None:
                zhai_yao1 = ' '
            else:
                zhai_yao1 = worksheet_source.cell(i,zhai_yao_pos1).value
            if worksheet_source.cell(i,zhai_yao_pos2).value == None:
                zhai_yao2 = ' '
            else:
                zhai_yao2 = worksheet_source.cell(i,zhai_yao_pos2).value
            if worksheet_source.cell(i,zhai_yao_pos3).value == None:
                zhai_yao3 = ' '
            else:
                zhai_yao3 = worksheet_source.cell(i,zhai_yao_pos3).value

            zhai_yao_content = str(zhai_yao1) +';'+ str(zhai_yao2) +';'+ str(zhai_yao3)
            #logger.info('dai_fang_fa_sheng_e type: ' + str(dai_fang_fa_sheng_e))
            
            #排除 不符合上述的入账流水规则 begin
            if dai_fang_fa_sheng_e ==None:
                continue
            if len(str(dai_fang_fa_sheng_e)) ==0 :
                continue
            if '利息划入' in zhai_yao_content:
                continue
            #排除 不符合上述的入账流水规则 end

            fu_kuan_ren_mingcheng = worksheet_source.cell(i,fu_kuan_ren_mingcheng_pos).value
            if fu_kuan_ren_mingcheng != None:
                fu_kuan_ren_mingcheng = fu_kuan_ren_mingcheng.strip()
            #查找付款人名称所属区域 begin
            ke_hu_suo_shu_qu_yu = '' #客户所属区域
            for kehu_quyu_index in range(0,len(customer_zone_list)):
                kehu_quyu_search = customer_zone_list[kehu_quyu_index]
                if fu_kuan_ren_mingcheng == kehu_quyu_search[0]:
                    ke_hu_suo_shu_qu_yu = kehu_quyu_search[1]
                    logger.info('客户所属区域, getit: ' + fu_kuan_ren_mingcheng +';'+ ke_hu_suo_shu_qu_yu)
                    break
            #查找付款人名称所属区域 end
            #查找区域负责人 begin
            qu_yu_fu_ze_ren = ' '
            if ke_hu_suo_shu_qu_yu != '':
                for kehu_quyu_index in range(0,len(qu_yu_yu_fu_ze_ren_fen_pei_list)):
                    kehu_quyu_search = qu_yu_yu_fu_ze_ren_fen_pei_list[kehu_quyu_index]
                    if ke_hu_suo_shu_qu_yu == kehu_quyu_search[1]:
                        qu_yu_fu_ze_ren = kehu_quyu_search[2]
                        logger.info('区域负责人, getit: ' + qu_yu_fu_ze_ren)
                        cheng_ban_ren_content = qu_yu_fu_ze_ren
            #查找区域负责人 end

            #切换 系统事业产品 / 国内卡产品 begin
            if fu_kuan_ren_mingcheng ==None:
                sheet_name_switch = '国内卡产品'
            elif '药' in fu_kuan_ren_mingcheng:
                sheet_name_switch = '系统事业产品'
            else:
                sheet_name_switch = '国内卡产品'

            if sheet_name_switch == '系统事业产品':
                worksheet_target = workbook_target['系统事业产品']  # 根据Sheet1这个sheet名字来获取该sheet
                last_row_target = xi_tong_shi_ye_last_row_target
                xi_tong_shi_ye_last_row_target = xi_tong_shi_ye_last_row_target +1
                gong_hang_xi_tong_count = gong_hang_xi_tong_count +1
            else:
                worksheet_target = workbook_target['国内卡产品']  # 根据Sheet1这个sheet名字来获取该sheet
                last_row_target = guo_nei_last_row_target
                guo_nei_last_row_target = guo_nei_last_row_target +1
                gong_hang_guo_nei_count = gong_hang_guo_nei_count +1
            #切换 系统事业产品 / 国内卡产品 end

            #工行时间格式转换value = '2019-01-02 15:13:07'
            temp_str = worksheet_source.cell(i,jiao_yi_shi_jian_pos).value
            logger.info('processing line : '+str(i))
            gong_hang_shijian_datetime = datetime.strptime(temp_str, '%Y-%m-%d %H:%M:%S')
            gong_hang_shijian_str = gong_hang_shijian_datetime.strftime('%Y/%m/%d')

            worksheet_target.cell(last_row_target,1).value = ''
            worksheet_target.cell(last_row_target,2).value = shou_kuan_yin_hang
            worksheet_target.cell(last_row_target,3).value = worksheet_source.cell(i,shou_kuan_yin_hang_zhanghao_pos).value 
            worksheet_target.cell(last_row_target,4).value = worksheet_source.cell(i,fu_kuan_ren_mingcheng_pos).value 
            worksheet_target.cell(last_row_target,5).value = worksheet_source.cell(i,fu_kuan_zhanghao_pos).value 
            worksheet_target.cell(last_row_target,6).value = ke_hu_lei_xin #worksheet_source.cell(i,).value 
            worksheet_target.cell(last_row_target,7).value = bi_zhong #worksheet_source.cell(i,).value 
            worksheet_target.cell(last_row_target,8).value = worksheet_source.cell(i,jin_e_pos).value 
            worksheet_target.cell(last_row_target,9).value = gong_hang_shijian_str
            worksheet_target.cell(last_row_target,10).value = zhai_yao_content
            worksheet_target.cell(last_row_target,11).value = cheng_ban_ren_content
            
        print('处理记录总行数:',i+1-first_row_source)
        print('处理国内产品行数: ', gong_hang_guo_nei_count)
        print('处理系统事业产品行数: ', gong_hang_xi_tong_count)
        worksheet_target = workbook_target['其他流水']
        worksheet_target.cell(3,1).value = '工行'
        worksheet_target.cell(3,2).value = gong_hang_guo_nei_count + gong_hang_xi_tong_count
        worksheet_target.cell(3,3).value = i-1 - gong_hang_guo_nei_count + gong_hang_xi_tong_count
        worksheet_target.cell(3,4).value = i-1
    #工行数据处理end


    #交行 数据处理 begin
        jiao_hang_guo_nei_count  = 0
        jiao_hang_xi_tong_count  = 0

        sheet_name = '交行'
        worksheet_source = workbook_source[sheet_name]  # 根据Sheet1这个sheet名字来获取该sheet
        sheet_source_maxrow = worksheet_source.max_row
        print('数据处理： ',sheet_name)

        first_row_source=3
        
        #收款银行
        shou_kuan_yin_hang = '交通银行'
        #收款银行账号 对应 交行表格 第一行 第二列
        shou_kuan_yin_hang_zhanghao = worksheet_source.cell(1,2).value
        #付款银行账号 对应 交行 对方账号
        fu_kuan_zhanghao_pos = 10
        #付款人账号名称 对应 交行 对方单位名称
        fu_kuan_ren_mingcheng_pos = 11
        #客户类型
        ke_hu_lei_xin = '国内'
        #币种
        bi_zhong = 'CNY'
        #金额 对应 工行 贷方发生额
        jin_e_pos = 7
        #交易时间
        jiao_yi_shi_jian_pos = 1
        #摘要
        zhai_yao_pos1 = 2   #摘要
        #zhai_yao_pos2 = 10  #用途
        #zhai_yao_pos3 = 13  #个性化信息
        #承办人
        cheng_ban_ren_content = ' '
        #贷方发生额
        dai_fang_fa_sheng_e_pos = 7

        #worksheet_target = workbook_target[sheet_name]  # 根据Sheet1这个sheet名字来获取该sheet
        #print(sheet_name)

        for i in range(first_row_source,sheet_source_maxrow):
            dai_fang_fa_sheng_e = worksheet_source.cell(i,dai_fang_fa_sheng_e_pos).value
            if worksheet_source.cell(i,zhai_yao_pos1).value == None:
                zhai_yao1 = ' '
            else:
                zhai_yao1 = worksheet_source.cell(i,zhai_yao_pos1).value

            zhai_yao_content = str(zhai_yao1)
            #logger.info('dai_fang_fa_sheng_e type: ' + str(dai_fang_fa_sheng_e))
            
            #排除 不符合上述的入账流水规则 begin
            if dai_fang_fa_sheng_e ==None:
                continue
            if len(str(dai_fang_fa_sheng_e)) ==0 :
                continue
            if '利息划入' in zhai_yao_content:
                continue
            #排除 不符合上述的入账流水规则 end

            fu_kuan_ren_mingcheng = worksheet_source.cell(i,fu_kuan_ren_mingcheng_pos).value
            if fu_kuan_ren_mingcheng != None:
                fu_kuan_ren_mingcheng = fu_kuan_ren_mingcheng.strip()
            #查找付款人名称所属区域 begin
            ke_hu_suo_shu_qu_yu = '' #客户所属区域
            for kehu_quyu_index in range(0,len(customer_zone_list)):
                kehu_quyu_search = customer_zone_list[kehu_quyu_index]
                if fu_kuan_ren_mingcheng == kehu_quyu_search[0]:
                    ke_hu_suo_shu_qu_yu = kehu_quyu_search[1]
                    logger.info('客户所属区域, getit: ' + fu_kuan_ren_mingcheng +';'+ ke_hu_suo_shu_qu_yu)
                    break
            #查找付款人名称所属区域 end
            #查找区域负责人 begin
            qu_yu_fu_ze_ren = ' '
            if ke_hu_suo_shu_qu_yu != '':
                for kehu_quyu_index in range(0,len(qu_yu_yu_fu_ze_ren_fen_pei_list)):
                    kehu_quyu_search = qu_yu_yu_fu_ze_ren_fen_pei_list[kehu_quyu_index]
                    if ke_hu_suo_shu_qu_yu == kehu_quyu_search[1]:
                        qu_yu_fu_ze_ren = kehu_quyu_search[2]
                        logger.info('区域负责人, getit: ' + qu_yu_fu_ze_ren)
                        cheng_ban_ren_content = qu_yu_fu_ze_ren
            #查找区域负责人 end

            #切换 系统事业产品 / 国内卡产品 begin
            if fu_kuan_ren_mingcheng ==None:
                sheet_name_switch = '国内卡产品'
            elif '药' in fu_kuan_ren_mingcheng:
                sheet_name_switch = '系统事业产品'
            else:
                sheet_name_switch = '国内卡产品'

            if sheet_name_switch == '系统事业产品':
                worksheet_target = workbook_target['系统事业产品']  # 根据Sheet1这个sheet名字来获取该sheet
                last_row_target = xi_tong_shi_ye_last_row_target
                xi_tong_shi_ye_last_row_target = xi_tong_shi_ye_last_row_target +1
                jiao_hang_xi_tong_count = jiao_hang_xi_tong_count +1
            else:
                worksheet_target = workbook_target['国内卡产品']  # 根据Sheet1这个sheet名字来获取该sheet
                last_row_target = guo_nei_last_row_target
                guo_nei_last_row_target = guo_nei_last_row_target +1
                jiao_hang_guo_nei_count = jiao_hang_guo_nei_count +1
            #切换 系统事业产品 / 国内卡产品 end

            #交行时间格式转换value = '2019-01-02 15:13:07'
            temp_str = worksheet_source.cell(i,jiao_yi_shi_jian_pos).value
            logger.info('processing line : '+str(i))
            jiao_hang_shijian_datetime = datetime.strptime(temp_str, '%Y-%m-%d %H:%M:%S')
            jiao_hang_shijian_str = jiao_hang_shijian_datetime.strftime('%Y/%m/%d')


            worksheet_target.cell(last_row_target,1).value = ''
            worksheet_target.cell(last_row_target,2).value = shou_kuan_yin_hang
            worksheet_target.cell(last_row_target,3).value = shou_kuan_yin_hang_zhanghao #worksheet_source.cell(i,shou_kuan_yin_hang_zhanghao_pos).value 
            worksheet_target.cell(last_row_target,4).value = worksheet_source.cell(i,fu_kuan_ren_mingcheng_pos).value 
            worksheet_target.cell(last_row_target,5).value = worksheet_source.cell(i,fu_kuan_zhanghao_pos).value 
            worksheet_target.cell(last_row_target,6).value = ke_hu_lei_xin #worksheet_source.cell(i,).value 
            worksheet_target.cell(last_row_target,7).value = bi_zhong #worksheet_source.cell(i,).value 
            worksheet_target.cell(last_row_target,8).value = worksheet_source.cell(i,jin_e_pos).value 
            worksheet_target.cell(last_row_target,9).value = jiao_hang_shijian_str
            worksheet_target.cell(last_row_target,10).value = zhai_yao_content
            worksheet_target.cell(last_row_target,11).value = cheng_ban_ren_content
            
        print('处理交行记录总行数:',i+1-first_row_source)
        print('处理交行国内产品行数: ', jiao_hang_guo_nei_count)
        print('处理交行系统事业产品行数: ', jiao_hang_xi_tong_count)
        worksheet_target = workbook_target['其他流水']
        worksheet_target.cell(4,1).value = '交行'
        worksheet_target.cell(4,2).value = jiao_hang_guo_nei_count + jiao_hang_xi_tong_count
        worksheet_target.cell(4,3).value = i-1 - jiao_hang_guo_nei_count + jiao_hang_xi_tong_count
        worksheet_target.cell(4,4).value = i-1
    #交行数据处理end



    #中行 数据处理 begin
        zhong_hang_guo_nei_count  = 0
        zhong_hang_xi_tong_count  = 0

        sheet_name = '中行'
        worksheet_source = workbook_source[sheet_name]  # 根据Sheet1这个sheet名字来获取该sheet
        sheet_source_maxrow = worksheet_source.max_row
        print('数据处理： ',sheet_name)

        first_row_source=2
        
        #收款银行
        shou_kuan_yin_hang = '中国银行'
        #收款银行账号 对应 交行表格 第一行 第二列
        shou_kuan_yin_hang_zhanghao_pos = 9
        #中行交易类型，用于区分是否处理
        jiao_yi_lei_xing_pos = 1 #worksheet_source.cell(1,2).value

        #付款银行账号 对应 交行 对方账号
        fu_kuan_zhanghao_pos = 5
        #付款人账号名称 对应 交行 对方单位名称
        fu_kuan_ren_mingcheng_pos = 6
        #客户类型
        ke_hu_lei_xin = '国内'
        #币种
        bi_zhong = 'CNY'
        #金额 对应 工行 贷方发生额
        jin_e_pos = 14
        #交易时间
        jiao_yi_shi_jian_pos = 11
        #摘要
        zhai_yao_pos1 = 25   #摘要
        #zhai_yao_pos2 = 10  #用途
        #zhai_yao_pos3 = 13  #个性化信息
        #承办人
        cheng_ban_ren_content = ' '
        #贷方发生额
        dai_fang_fa_sheng_e_pos = 14

        #worksheet_target = workbook_target[sheet_name]  # 根据Sheet1这个sheet名字来获取该sheet
        #print(sheet_name)

        for i in (range(first_row_source,sheet_source_maxrow)):
            dai_fang_fa_sheng_e = worksheet_source.cell(i,dai_fang_fa_sheng_e_pos).value
            if worksheet_source.cell(i,zhai_yao_pos1).value == None:
                zhai_yao1 = ' '
            else:
                zhai_yao1 = worksheet_source.cell(i,zhai_yao_pos1).value

            zhai_yao_content = str(zhai_yao1)
            #logger.info('dai_fang_fa_sheng_e type: ' + str(dai_fang_fa_sheng_e))
            
            #排除 不符合上述的入账流水规则 begin
            jiao_yi_lei_xing_str =  worksheet_source.cell(i,jiao_yi_lei_xing_pos).value
            if jiao_yi_lei_xing_str != '来账':
                continue
            if dai_fang_fa_sheng_e ==None:
                continue
            if len(str(dai_fang_fa_sheng_e)) ==0 :
                continue
            if '利息划入' in zhai_yao_content:
                continue
            #排除 不符合上述的入账流水规则 end

            fu_kuan_ren_mingcheng = worksheet_source.cell(i,fu_kuan_ren_mingcheng_pos).value
            if fu_kuan_ren_mingcheng != None:
                fu_kuan_ren_mingcheng = fu_kuan_ren_mingcheng.strip()
            #查找付款人名称所属区域 begin
            ke_hu_suo_shu_qu_yu = '' #客户所属区域
            for kehu_quyu_index in range(0,len(customer_zone_list)):
                kehu_quyu_search = customer_zone_list[kehu_quyu_index]
                if fu_kuan_ren_mingcheng == kehu_quyu_search[0]:
                    ke_hu_suo_shu_qu_yu = kehu_quyu_search[1]
                    logger.info('客户所属区域, getit: ' + fu_kuan_ren_mingcheng +';'+ ke_hu_suo_shu_qu_yu)
                    break
            #查找付款人名称所属区域 end
            #查找区域负责人 begin
            qu_yu_fu_ze_ren = ' '
            if ke_hu_suo_shu_qu_yu != '':
                for kehu_quyu_index in range(0,len(qu_yu_yu_fu_ze_ren_fen_pei_list)):
                    kehu_quyu_search = qu_yu_yu_fu_ze_ren_fen_pei_list[kehu_quyu_index]
                    if ke_hu_suo_shu_qu_yu == kehu_quyu_search[1]:
                        qu_yu_fu_ze_ren = kehu_quyu_search[2]
                        logger.info('区域负责人, getit: ' + qu_yu_fu_ze_ren)
                        cheng_ban_ren_content = qu_yu_fu_ze_ren
            #查找区域负责人 end

            #切换 系统事业产品 / 国内卡产品 begin
            if fu_kuan_ren_mingcheng ==None:
                sheet_name_switch = '国内卡产品'
            elif '药' in fu_kuan_ren_mingcheng:
                sheet_name_switch = '系统事业产品'
            else:
                sheet_name_switch = '国内卡产品'

            if sheet_name_switch == '系统事业产品':
                worksheet_target = workbook_target['系统事业产品']  # 根据Sheet1这个sheet名字来获取该sheet
                last_row_target = xi_tong_shi_ye_last_row_target
                xi_tong_shi_ye_last_row_target = xi_tong_shi_ye_last_row_target +1
                zhong_hang_xi_tong_count = zhong_hang_xi_tong_count +1
            else:
                worksheet_target = workbook_target['国内卡产品']  # 根据Sheet1这个sheet名字来获取该sheet
                last_row_target = guo_nei_last_row_target
                guo_nei_last_row_target = guo_nei_last_row_target +1
                zhong_hang_guo_nei_count = zhong_hang_guo_nei_count +1
            #切换 系统事业产品 / 国内卡产品 end

            #中行时间格式转换value = '20190102'
            temp_str = worksheet_source.cell(i,jiao_yi_shi_jian_pos).value
            temp_str = temp_str.strip()
            logger.info('processing line : '+str(i))
            if dlevel > 3:
                print(len(temp_str),type(temp_str),temp_str)
            zhong_hang_shijian_datetime = datetime.strptime(temp_str, '%Y%m%d')
            zhong_hang_shijian_str = zhong_hang_shijian_datetime.strftime('%Y/%m/%d')

            worksheet_target.cell(last_row_target,1).value = ''
            worksheet_target.cell(last_row_target,2).value = shou_kuan_yin_hang
            worksheet_target.cell(last_row_target,3).value = worksheet_source.cell(i,shou_kuan_yin_hang_zhanghao_pos).value 
            worksheet_target.cell(last_row_target,4).value = worksheet_source.cell(i,fu_kuan_ren_mingcheng_pos).value 
            worksheet_target.cell(last_row_target,5).value = worksheet_source.cell(i,fu_kuan_zhanghao_pos).value 
            worksheet_target.cell(last_row_target,6).value = ke_hu_lei_xin #worksheet_source.cell(i,).value 
            worksheet_target.cell(last_row_target,7).value = bi_zhong #worksheet_source.cell(i,).value 
            worksheet_target.cell(last_row_target,8).value = worksheet_source.cell(i,jin_e_pos).value 
            worksheet_target.cell(last_row_target,9).value = zhong_hang_shijian_str
            worksheet_target.cell(last_row_target,10).value = zhai_yao_content
            worksheet_target.cell(last_row_target,11).value = cheng_ban_ren_content
            
        print('处理中行记录总行数:',i+1-first_row_source)
        print('处理中行国内产品行数: ', zhong_hang_guo_nei_count)
        print('处理中行系统事业产品行数: ', zhong_hang_xi_tong_count)
        worksheet_target = workbook_target['其他流水']
        worksheet_target.cell(5,1).value = '中行'
        worksheet_target.cell(5,2).value = zhong_hang_guo_nei_count + zhong_hang_xi_tong_count
        worksheet_target.cell(5,3).value = i-1 - zhong_hang_guo_nei_count + zhong_hang_xi_tong_count
        worksheet_target.cell(5,4).value = i-1
    #中行数据处理end

    #建行 数据处理 begin
        jian_hang_guo_nei_count  = 0
        jian_hang_xi_tong_count  = 0

        sheet_name = '建行'
        worksheet_source = workbook_source[sheet_name]  # 根据Sheet1这个sheet名字来获取该sheet
        sheet_source_maxrow = worksheet_source.max_row
        print('数据处理： ',sheet_name)

        first_row_source=3
        
        #收款银行
        shou_kuan_yin_hang = '建国银行'
        #收款银行账号 对应 建行表格 第一行 第二列
        shou_kuan_yin_hang_zhanghao = worksheet_source.cell(1,2).value

        #收款银行账号 对应 建行表格 第一行 第二列
        shou_kuan_yin_hang_zhanghao_pos = 1
        #建行交易类型，用于区分是否处理
        jiao_yi_lei_xing_pos = 1 #worksheet_source.cell(1,2).value

        #付款银行账号 对应 交行 对方账号
        fu_kuan_zhanghao_pos = 7
        #付款人账号名称 对应 交行 对方单位名称
        fu_kuan_ren_mingcheng_pos = 8
        #客户类型
        ke_hu_lei_xin = '国内'
        #币种
        bi_zhong = 'CNY'
        #金额 对应 工行 贷方发生额
        jin_e_pos = 3
        #交易时间
        jiao_yi_shi_jian_pos = 1
        #摘要
        zhai_yao_pos1 = 10   #摘要
        zhai_yao_pos2 = 4  #余额
        zhai_yao_pos3 = 11  #备注
        #承办人
        cheng_ban_ren_content = ' '
        #贷方发生额
        dai_fang_fa_sheng_e_pos = 3

        #worksheet_target = workbook_target[sheet_name]  # 根据Sheet1这个sheet名字来获取该sheet
        #print(sheet_name)

        for i in (range(first_row_source,sheet_source_maxrow)):
            dai_fang_fa_sheng_e = worksheet_source.cell(i,dai_fang_fa_sheng_e_pos).value

            if worksheet_source.cell(i,zhai_yao_pos1).value == None:
                zhai_yao1 = ' '
            else:
                zhai_yao1 = worksheet_source.cell(i,zhai_yao_pos1).value
            if worksheet_source.cell(i,zhai_yao_pos2).value == None:
                zhai_yao2 = ' '
            else:
                zhai_yao2 = worksheet_source.cell(i,zhai_yao_pos2).value
            if worksheet_source.cell(i,zhai_yao_pos3).value == None:
                zhai_yao3 = ' '
            else:
                zhai_yao3 = worksheet_source.cell(i,zhai_yao_pos3).value

            zhai_yao_content = str(zhai_yao1) +';'+ str(zhai_yao2) +';'+ str(zhai_yao3)

            
            #排除 不符合上述的入账流水规则 begin
            if dai_fang_fa_sheng_e == None:
                continue
            if dai_fang_fa_sheng_e <= 0 :
                continue
            #排除 不符合上述的入账流水规则 end

            fu_kuan_ren_mingcheng = worksheet_source.cell(i,fu_kuan_ren_mingcheng_pos).value
            if fu_kuan_ren_mingcheng != None:
                fu_kuan_ren_mingcheng = fu_kuan_ren_mingcheng.strip()
            #查找付款人名称所属区域 begin
            ke_hu_suo_shu_qu_yu = '' #客户所属区域
            for kehu_quyu_index in range(0,len(customer_zone_list)):
                kehu_quyu_search = customer_zone_list[kehu_quyu_index]
                if fu_kuan_ren_mingcheng == kehu_quyu_search[0]:
                    ke_hu_suo_shu_qu_yu = kehu_quyu_search[1]
                    logger.info('客户所属区域, getit: ' + fu_kuan_ren_mingcheng +';'+ ke_hu_suo_shu_qu_yu)
                    break
            #查找付款人名称所属区域 end
            #查找区域负责人 begin
            qu_yu_fu_ze_ren = ' '
            if ke_hu_suo_shu_qu_yu != '':
                for kehu_quyu_index in range(0,len(qu_yu_yu_fu_ze_ren_fen_pei_list)):
                    kehu_quyu_search = qu_yu_yu_fu_ze_ren_fen_pei_list[kehu_quyu_index]
                    if ke_hu_suo_shu_qu_yu == kehu_quyu_search[1]:
                        qu_yu_fu_ze_ren = kehu_quyu_search[2]
                        logger.info('区域负责人, getit: ' + qu_yu_fu_ze_ren)
                        cheng_ban_ren_content = qu_yu_fu_ze_ren
            #查找区域负责人 end

            #切换 系统事业产品 / 国内卡产品 begin
            if fu_kuan_ren_mingcheng ==None:
                sheet_name_switch = '国内卡产品'
            elif '药' in fu_kuan_ren_mingcheng:
                sheet_name_switch = '系统事业产品'
            else:
                sheet_name_switch = '国内卡产品'

            if sheet_name_switch == '系统事业产品':
                worksheet_target = workbook_target['系统事业产品']  # 根据Sheet1这个sheet名字来获取该sheet
                last_row_target = xi_tong_shi_ye_last_row_target
                xi_tong_shi_ye_last_row_target = xi_tong_shi_ye_last_row_target +1
                jian_hang_xi_tong_count = jian_hang_xi_tong_count +1
            else:
                worksheet_target = workbook_target['国内卡产品']  # 根据Sheet1这个sheet名字来获取该sheet
                last_row_target = guo_nei_last_row_target
                guo_nei_last_row_target = guo_nei_last_row_target +1
                jian_hang_guo_nei_count = jian_hang_guo_nei_count +1
            #切换 系统事业产品 / 国内卡产品 end

            #时间格式转换
            temp_str = worksheet_source.cell(i,jiao_yi_shi_jian_pos).value
            temp_str = temp_str.strip()
            logger.info('processing line : '+str(i))
            if dlevel > 3:
                print(len(temp_str),type(temp_str),temp_str)
            jian_hang_shijian_datetime = datetime.strptime(temp_str, '%Y%m%d %H:%M:%S')
            jian_hang_shijian_str = jian_hang_shijian_datetime.strftime('%Y/%m/%d')

            worksheet_target.cell(last_row_target,1).value = ''
            worksheet_target.cell(last_row_target,2).value = shou_kuan_yin_hang
            worksheet_target.cell(last_row_target,3).value = shou_kuan_yin_hang_zhanghao #worksheet_source.cell(i,shou_kuan_yin_hang_zhanghao_pos).value 
            worksheet_target.cell(last_row_target,4).value = worksheet_source.cell(i,fu_kuan_ren_mingcheng_pos).value 
            worksheet_target.cell(last_row_target,5).value = worksheet_source.cell(i,fu_kuan_zhanghao_pos).value 
            worksheet_target.cell(last_row_target,6).value = ke_hu_lei_xin #worksheet_source.cell(i,).value 
            worksheet_target.cell(last_row_target,7).value = bi_zhong #worksheet_source.cell(i,).value 
            worksheet_target.cell(last_row_target,8).value = worksheet_source.cell(i,jin_e_pos).value 
            worksheet_target.cell(last_row_target,9).value = jian_hang_shijian_str
            worksheet_target.cell(last_row_target,10).value = zhai_yao_content
            worksheet_target.cell(last_row_target,11).value = cheng_ban_ren_content
            
        print('处理建行记录总行数:',i+1-first_row_source)
        print('处理建行国内产品行数: ', jian_hang_guo_nei_count)
        print('处理建行系统事业产品行数: ', jian_hang_xi_tong_count)
        worksheet_target = workbook_target['其他流水']
        worksheet_target.cell(6,1).value = '建行'
        worksheet_target.cell(6,2).value = jian_hang_guo_nei_count + jian_hang_xi_tong_count
        worksheet_target.cell(6,3).value = i-1 - jian_hang_guo_nei_count + jian_hang_xi_tong_count
        worksheet_target.cell(6,4).value = i-1
    #建行数据处理end

    #浦发 数据处理 begin
        pu_fa_guo_nei_count  = 0
        pu_fa_xi_tong_count  = 0

        sheet_name = '浦发'
        worksheet_source = workbook_source[sheet_name]  # 根据Sheet1这个sheet名字来获取该sheet
        sheet_source_maxrow = worksheet_source.max_row
        print('数据处理： ',sheet_name)

        first_row_source=3
        
        #收款银行
        shou_kuan_yin_hang = '浦发银行'
        #收款银行账号 对应 浦发表格 第一行 第二列
        shou_kuan_yin_hang_zhanghao_pos = 9
        #浦发交易类型，用于区分是否处理
        #收款银行账号 对应 建行表格 第一行 第二列
        shou_kuan_yin_hang_zhanghao = worksheet_source.cell(1,2).value

        jiao_yi_lei_xing_pos = 1 #worksheet_source.cell(1,2).value

        #付款银行账号 对应 浦发 对方账号
        fu_kuan_zhanghao_pos = 7
        #付款人账号名称 对应 浦发 对方单位名称
        fu_kuan_ren_mingcheng_pos = 8
        #客户类型
        ke_hu_lei_xin = '国内'
        #币种
        bi_zhong = 'CNY'
        #金额 对应 浦发 贷方发生额
        jin_e_pos = 5
        #交易时间
        jiao_yi_shi_jian_pos = 1
        #摘要
        zhai_yao_pos1 = 9   #摘要
        #zhai_yao_pos2 = 10  #用途
        #zhai_yao_pos3 = 13  #个性化信息
        #承办人
        cheng_ban_ren_content = ' '
        #贷方发生额
        dai_fang_fa_sheng_e_pos = 5

        #worksheet_target = workbook_target[sheet_name]  # 根据Sheet1这个sheet名字来获取该sheet
        #print(sheet_name)

        for i in range(first_row_source,sheet_source_maxrow+1):
            dai_fang_fa_sheng_e = worksheet_source.cell(i,dai_fang_fa_sheng_e_pos).value
            if worksheet_source.cell(i,zhai_yao_pos1).value == None:
                zhai_yao1 = ' '
            else:
                zhai_yao1 = worksheet_source.cell(i,zhai_yao_pos1).value

            zhai_yao_content = str(zhai_yao1)
            #logger.info('dai_fang_fa_sheng_e type: ' + str(dai_fang_fa_sheng_e))
            
            #排除 不符合上述的入账流水规则 begin
            jiao_yi_lei_xing_str =  worksheet_source.cell(i,jiao_yi_lei_xing_pos).value
            if dai_fang_fa_sheng_e ==None:
                continue
            if len(str(dai_fang_fa_sheng_e)) ==0 :
                continue
            #排除 不符合上述的入账流水规则 end

            fu_kuan_ren_mingcheng = worksheet_source.cell(i,fu_kuan_ren_mingcheng_pos).value
            if fu_kuan_ren_mingcheng != None:
                fu_kuan_ren_mingcheng = fu_kuan_ren_mingcheng.strip()
            #查找付款人名称所属区域 begin
            ke_hu_suo_shu_qu_yu = '' #客户所属区域
            for kehu_quyu_index in range(0,len(customer_zone_list)):
                kehu_quyu_search = customer_zone_list[kehu_quyu_index]
                if fu_kuan_ren_mingcheng == kehu_quyu_search[0]:
                    ke_hu_suo_shu_qu_yu = kehu_quyu_search[1]
                    logger.info('客户所属区域, getit: ' + fu_kuan_ren_mingcheng +';'+ ke_hu_suo_shu_qu_yu)
                    break
            #查找付款人名称所属区域 end
            #查找区域负责人 begin
            qu_yu_fu_ze_ren = ' '
            if ke_hu_suo_shu_qu_yu != '':
                for kehu_quyu_index in range(0,len(qu_yu_yu_fu_ze_ren_fen_pei_list)):
                    kehu_quyu_search = qu_yu_yu_fu_ze_ren_fen_pei_list[kehu_quyu_index]
                    if ke_hu_suo_shu_qu_yu == kehu_quyu_search[1]:
                        qu_yu_fu_ze_ren = kehu_quyu_search[2]
                        logger.info('区域负责人, getit: ' + qu_yu_fu_ze_ren)
                        cheng_ban_ren_content = qu_yu_fu_ze_ren
            #查找区域负责人 end

            #切换 系统事业产品 / 国内卡产品 begin
            if fu_kuan_ren_mingcheng ==None:
                sheet_name_switch = '国内卡产品'
            elif '药' in fu_kuan_ren_mingcheng:
                sheet_name_switch = '系统事业产品'
            else:
                sheet_name_switch = '国内卡产品'

            if sheet_name_switch == '系统事业产品':
                worksheet_target = workbook_target['系统事业产品']  # 根据Sheet1这个sheet名字来获取该sheet
                last_row_target = xi_tong_shi_ye_last_row_target
                xi_tong_shi_ye_last_row_target = xi_tong_shi_ye_last_row_target +1
                pu_fa_xi_tong_count = pu_fa_xi_tong_count +1
            else:
                worksheet_target = workbook_target['国内卡产品']  # 根据Sheet1这个sheet名字来获取该sheet
                last_row_target = guo_nei_last_row_target
                guo_nei_last_row_target = guo_nei_last_row_target +1
                pu_fa_guo_nei_count = pu_fa_guo_nei_count +1
            #切换 系统事业产品 / 国内卡产品 end

            #中行时间格式转换value = '20190102'
            temp_str = worksheet_source.cell(i,jiao_yi_shi_jian_pos).value
            temp_str = temp_str.strip()
            logger.info('processing line : '+str(i))
            if dlevel > 3:
                print(len(temp_str),type(temp_str),temp_str)
            zhong_hang_shijian_datetime = datetime.strptime(temp_str, '%Y%m%d')
            zhong_hang_shijian_str = zhong_hang_shijian_datetime.strftime('%Y/%m/%d')

            worksheet_target.cell(last_row_target,1).value = ''
            worksheet_target.cell(last_row_target,2).value = shou_kuan_yin_hang
            worksheet_target.cell(last_row_target,3).value = shou_kuan_yin_hang_zhanghao #worksheet_source.cell(i,shou_kuan_yin_hang_zhanghao_pos).value 
            worksheet_target.cell(last_row_target,4).value = worksheet_source.cell(i,fu_kuan_ren_mingcheng_pos).value 
            worksheet_target.cell(last_row_target,5).value = worksheet_source.cell(i,fu_kuan_zhanghao_pos).value 
            worksheet_target.cell(last_row_target,6).value = ke_hu_lei_xin #worksheet_source.cell(i,).value 
            worksheet_target.cell(last_row_target,7).value = bi_zhong #worksheet_source.cell(i,).value 
            worksheet_target.cell(last_row_target,8).value = worksheet_source.cell(i,jin_e_pos).value 
            worksheet_target.cell(last_row_target,9).value = zhong_hang_shijian_str
            worksheet_target.cell(last_row_target,10).value = zhai_yao_content
            worksheet_target.cell(last_row_target,11).value = cheng_ban_ren_content
            
        print('处理浦发记录总行数:',i+1-first_row_source)
        print('处理浦发国内产品行数: ', pu_fa_guo_nei_count)
        print('处理浦发系统事业产品行数: ', pu_fa_xi_tong_count)
        worksheet_target = workbook_target['其他流水']
        worksheet_target.cell(7,1).value = '浦发'
        worksheet_target.cell(7,2).value = pu_fa_guo_nei_count + pu_fa_xi_tong_count
        worksheet_target.cell(7,3).value = i-1 - pu_fa_guo_nei_count + pu_fa_xi_tong_count
        worksheet_target.cell(7,4).value = i-1
    #浦发数据处理end



        workbook_target.save(os.path.join(self.data_dir , '银行流水统一格式（export）.xlsx'))  # 保存修改后的excel

    def excel_cell_rowcell_to_position(self,int_row,int_column):
        if int_row < 26:
            str_excel_cell_pos = chr(64+int_row)
            str_excel_cell_pos = str_excel_cell_pos + str(int_column)
        return str_excel_cell_pos

# 整合数据，导出生成excel文件

# 程序主gui界面。
    def initWidgets(self):
        cp = ConfigParser()
        try:
            cp = cp
            #cp.read('配置文件.ini', encoding='gbk')
            # str_kehu_name = cp.get('配置信息', '客户名称')
            # kehu_name_list = str_kehu_name.split("|")
            # for i in range(0,len(kehu_name_list)):
            #     temp_pos0 = cp.get(kehu_name_list[i], '表格名称')
            #     temp_pos1 = cp.get(kehu_name_list[i], '回款编号')
            #     temp_pos2 = cp.get(kehu_name_list[i], '收款银行')
            #     temp_pos3 = cp.get(kehu_name_list[i], '收款银行账号')
            #     temp_pos4 = cp.get(kehu_name_list[i], '付款人名称')
            #     temp_pos5 = cp.get(kehu_name_list[i], '付款账号')
            #     temp_pos6 = cp.get(kehu_name_list[i], '客户类型')
            #     temp_pos7 = cp.get(kehu_name_list[i], '币种')
            #     temp_pos8 = cp.get(kehu_name_list[i], '金额')
            #     temp_pos9 = cp.get(kehu_name_list[i], '交易时间')
            #     temp_pos10 = cp.get(kehu_name_list[i], '摘要')
            #     temp_pos11 = cp.get(kehu_name_list[i], '承办人')
            #     self.kehu_pos_datail.append([kehu_name_list[i],temp_pos1,temp_pos2,temp_pos3,temp_pos4,temp_pos5,temp_pos6,temp_pos7,temp_pos8,temp_pos9,temp_pos10,temp_pos11])

            # print(self.kehu_pos_datail)

        except Exception as err_message:
            print(err_message)
            logger.info('无法打开配置文件.ini或配置有误!' )
            exit(2)

        #print('host: ', str_kehu_name)
        #print(self.file_from_youjiqingdan)

        #temp_last_datetime = datetime.date.today() - datetime.timedelta(days=10)

    # 退出键
    def command_btn_exit(self):
        self.master.destroy()

    # 主功能键
    def command_btn_run(self):

        #if self.pricexls_db(self.customer_sname, self.file_from_jichu) == 'no':
         #   return (1)

        work_dir = '..\\仓库文件\\'
        #self.proc_folder(self.customer_sname, work_dir)
        #甘肃农信有多个文件夹、多个文件excel需导入到数据库，使用处理文件夹方式导入明细数据

        self.csvdata_list(self.customer_name, '开票平台中客户及区域.csv')

        print('完成...                     ')
        return 0

if __name__ == '__main__':
    set_logging()
    run_app = App()
    run_app.command_btn_run()
