import os
import re
import time
import math
import chardet
import pymysql
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sqlalchemy import create_engine
from sklearn.externals import joblib
from statsmodels.iolib.smpickle import load_pickle

from index import *

"""
# 一个公司模型入库
# Model(company_id="37760815").save_db()
# 全部公司模型入库
# Model().save_db()
# 一个公司的经营预测
# result = Model(company_id="1012382996",
#                income_statement_dict={
#                    'total_revenue': 100,
#                    'operating_costs': 100,
#                    'op': 100,
#                    'profit_total_amt': 100,
#                    'income_tax_expenses': 100
#                }).get_business_result()
# print(result)
"""


class Model:
    def __init__(self, company_id="", income_statement_dict={}):
        self.company_id = company_id
        self.income_statement_dict = income_statement_dict
        self.cn_unit = {
            '十': 10,
            '拾': 10,
            '百': 100,
            '佰': 100,
            '千': 1000,
            '仟': 1000,
            '万': 10000,
            '萬': 10000,
            '亿': 100000000,
            '億': 100000000,
            '兆': 1000000000000,
            '角': 0.1,
            '分': 0.01,
            '厘': 0.001,
            '毫': 0.0001,
        }
        self.cn_unm = {
            '〇': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '零': 0,
            '壹': 1, '贰': 2, '叁': 3, '肆': 4, '伍': 5, '陆': 6, '柒': 7, '捌': 8, '玖': 9, '貮': 2, '两': 2,
        }
        self.industry_dict = {
            '农业': '农、林、牧、渔业', '林业': '农、林、牧、渔业', '畜牧业': '农、林、牧、渔业', '渔业': '农、林、牧、渔业',
            '农、林、牧、渔专业及辅助性活动': '农、林、牧、渔业',
            '煤炭开采和洗选业': '采矿业', '石油和天然气开采业': '采矿业', '黑色金属矿采选业': '采矿业', '有色金属矿采选业': '采矿业', '非金属矿采选业': '采矿业',
            '开采专业及辅助性活动': '采矿业', '其他采矿业': '采矿业', '农副食品加工业': '制造业', '食品制造业': '制造业', '酒、饮料和精制茶制造业': '制造业',
            '烟草制品业': '制造业', '纺织业': '制造业', '纺织服装、服饰业': '制造业', '皮革、毛皮、羽毛及其制品和制鞋业': '制造业',
            '木材加工和木、竹、藤、棕、草制品业': '制造业',
            '家具制造业': '制造业', '造纸和纸制品业': '制造业', '印刷和记录媒介复制业': '制造业', '文教、工美、体育和娱乐用品制造业': '制造业',
            '石油、煤炭及其他燃料加工业': '制造业', '化学原料和化学制品制造业': '制造业', '医药制造业': '制造业', '化学纤维制造业': '制造业',
            '橡胶和塑料制品业': '制造业',
            '非金属矿物制品业': '制造业', '黑色金属冶炼和压延加工业': '制造业', '有色金属冶炼和压延加工业': '制造业', '金属制品业': '制造业',
            '通用设备制造业': '制造业',
            '专用设备制造业': '制造业', '汽车制造业': '制造业', '铁路、船舶、航空航天和其他运输设备制造业': '制造业', '电气机械和器材制造业': '制造业',
            '计算机、通信和其他电子设备制造业': '制造业', '仪器仪表制造业': '制造业', '其他制造业': '制造业', '废弃资源综合利用业': '制造业',
            '金属制品、机械和设备修理业': '制造业', '电力、热力生产和供应业': '电力、热力、燃气及水生产和供应业', '燃气生产和供应业': '电力、热力、燃气及水生产和供应业',
            '水的生产和供应业': '电力、热力、燃气及水生产和供应业', '房屋建筑业': '建筑业', '土木工程建筑业': '建筑业', '建筑安装业': '建筑业',
            '建筑装饰、装修和其他建筑业': '建筑业', '批发业': '批发和零售业', '零售业': '批发和零售业', '铁路运输业': '交通运输、仓储和邮政业',
            '道路运输业': '交通运输、仓储和邮政业', '水上运输业': '交通运输、仓储和邮政业', '航空运输业': '交通运输、仓储和邮政业', '管道运输业': '交通运输、仓储和邮政业',
            '多式联运和运输代理业': '交通运输、仓储和邮政业', '装卸搬运和仓储业': '交通运输、仓储和邮政业', '邮政业': '交通运输、仓储和邮政业', '住宿业': '住宿和餐饮业',
            '餐饮业': '住宿和餐饮业', '电信、广播电视和卫星传输服务': '信息传输、软件和信息技术服务业', '互联网和相关服务': '信息传输、软件和信息技术服务业',
            '软件和信息技术服务业': '信息传输、软件和信息技术服务业', '货币金融服务': '金融业', '资本市场服务': '金融业', '保险业': '金融业',
            '其他金融业': '金融业',
            '房地产业': '房地产业', '租赁业': '租赁和商务服务业', '商务服务业': '租赁和商务服务业', '研究和试验发展': '科学研究和技术服务业',
            '专业技术服务业': '科学研究和技术服务业', '科技推广和应用服务业': '科学研究和技术服务业', '水利管理业': '水利、环境和公共设施管理业',
            '生态保护和环境治理业': '水利、环境和公共设施管理业', '公共设施管理业': '水利、环境和公共设施管理业', '土地管理业': '水利、环境和公共设施管理业',
            '居民服务业': '居民服务、修理和其他服务业', '机动车、电子产品和日用产品修理业': '居民服务、修理和其他服务业', '其他服务业': '居民服务、修理和其他服务业',
            '教育': '教育',
            '卫生': '卫生和社会工作', '社会工作': '卫生和社会工作', '新闻和出版业': '文化、体育和娱乐业', '广播、电视、电影和录音制作业': '文化、体育和娱乐业',
            '文化艺术业': '文化、体育和娱乐业', '体育': '文化、体育和娱乐业', '娱乐业': '文化、体育和娱乐业', '中国共产党机关': '公共管理、社会保障和社会组织',
            '国家机构': '公共管理、社会保障和社会组织', '人民政协、民主党派': '公共管理、社会保障和社会组织', '社会保障': '公共管理、社会保障和社会组织',
            '群众团体、社会团体和其他成员组织': '公共管理、社会保障和社会组织', '基层群众自治组织及其他组织': '公共管理、社会保障和社会组织', '国际组织': '国际组织',
            np.nan: None,
            None: None
        }
        self.dtypes = {
            'total_revenue': np.dtype('float64'),
            'operating_costs': np.dtype('float64'),
            'op': np.dtype('float64'),
            'profit_total_amt': np.dtype('float64'),
            'income_tax_expenses': np.dtype('float64'),
            'web': pd.CategoricalDtype(categories=[0, 1], ordered=False),
            'email': pd.CategoricalDtype(categories=[0, 1], ordered=False),
            'economic_circle': pd.CategoricalDtype(categories=[0, 1], ordered=False),
            'reg_capital': np.dtype('float64'),
            'actual_capital': np.dtype('float64'),
            'built_year': np.dtype('int64'),
            'company_age': np.dtype('float64'),
            'business_status': pd.CategoricalDtype(categories=[0, 1, 2, 3, 4], ordered=False),
            'company_org_type': pd.CategoricalDtype(categories=['个人独资企业', '个体工商户', '其他', '合伙企业', '有限责任公司', '股份有限公司'],
                                                    ordered=False),
            'industry': pd.CategoricalDtype(
                categories=['农、林、牧、渔业', '采矿业', '制造业', '电力、热力、燃气及水生产和供应业', '建筑业', '批发和零售业', '交通运输、仓储和邮政业', '住宿和餐饮业',
                            '信息传输、软件和信息技术服务业', '金融业', '房地产业', '租赁和商务服务业', '科学研究和技术服务业', '水利、环境和公共设施管理业',
                            '居民服务、修理和其他服务业', '教育',
                            '卫生和社会工作', '文化、体育和娱乐业', '公共管理、社会保障和社会组织', '国际组织'], ordered=False),
            'staff_num_range': pd.CategoricalDtype(
                categories=['100-499人', '1000-4999人', '10000人以上', '50-99人', '500-999人',
                            '5000-9999人', '小于50人'], ordered=False),
            'social_staff_num': np.dtype('float64'),
            'business_scope': np.dtype('int64'),
            'disclosure_key_personnel': pd.CategoricalDtype(categories=[0, 1], ordered=False),
            'key_personnel_num': np.dtype('float64'),
            'top1_ratio': np.dtype('float64'),
            'top10_ratio': np.dtype('float64'),
            'standard_ratio': np.dtype('float64'),
            'total_invest_amount': np.dtype('float64'),
            'invest_success_rate': np.dtype('float64'),
            'invest_all_age': np.dtype('float64'),
            'branch_identify': pd.CategoricalDtype(categories=[0, 1], ordered=False),
            'branch_num': np.dtype('float64'),
            'branch_all_age': np.dtype('float64'),
            'recruitment_num': np.dtype('float64'),
            'recruitment_specie': np.dtype('float64'),
            'average_salary': np.dtype('float64'),
            'having_credit_china': pd.CategoricalDtype(categories=[0.0, 1.0], ordered=False),  ##
            'having_people_bank': pd.CategoricalDtype(categories=[0.0, 1.0], ordered=False),  ##
            'having_market_supervision': pd.CategoricalDtype(categories=[0.0, 1.0], ordered=False),  ##
            'lowest_grade': pd.CategoricalDtype(categories=['A', 'B'], ordered=False),
            'grade': pd.CategoricalDtype(categories=['A'], ordered=False),
            'certificate_type_num': np.dtype('float64'),
            'bidding_num': np.dtype('float64'),
            'disclose_supply': pd.CategoricalDtype(categories=[0, 1], ordered=False),
            'ratio_std': np.dtype('float64'),
            'amt_sum': np.dtype('float64'),
            'news_num': np.dtype('float64'),
            'disclose_core_team': pd.CategoricalDtype(categories=[0, 1], ordered=False),
            'core_team_num': np.dtype('float64'),
            'financing_process_num': np.dtype('float64'),
            'corporate_business_num': np.dtype('float64'),
            'financing_ratio': np.dtype('float64'),
            'competitor_num': np.dtype('float64'),
            'punishment_info_num': np.dtype('float64'),
            'punishment_money': np.dtype('float64'),
            'equity_pledge_num': np.dtype('float64'),
            'tax_contravention_num': np.dtype('float64'),
            'tax_arrears_num': np.dtype('float64'),
            'mortgage_num': np.dtype('float64'),
            'mortgage_amount_sum': np.dtype('float64'),
            'judicial_auction_num': np.dtype('float64'),
            'law_suit_num': np.dtype('float64'),
            'case_type_num': np.dtype('float64'),
            'consumption_restriction_num': np.dtype('float64'),
            'dishonest_num': np.dtype('float64'),
            'judicial_assistance_num': np.dtype('float64'),
            'judicial_assistance_money': np.dtype('float64'),
        }
        self.feature_columns = ['web', 'email', 'economic_circle', 'reg_capital', 'actual_capital', 'built_year',
                                'company_age',
                                'business_status', 'company_org_type', 'industry', 'social_staff_num', 'business_scope',
                                'disclosure_key_personnel', 'key_personnel_num', 'top1_ratio', 'top10_ratio',
                                'standard_ratio',
                                'total_invest_amount', 'invest_success_rate', 'invest_all_age', 'branch_identify',
                                'branch_num',
                                'branch_all_age', 'having_credit_china', 'having_people_bank',
                                'having_market_supervision',
                                'certificate_type_num', 'bidding_num', 'disclose_supply', 'ratio_std', 'amt_sum',
                                'news_num',
                                'disclose_core_team', 'financing_process_num', 'financing_ratio', 'competitor_num',
                                'punishment_info_num', 'punishment_money', 'equity_pledge_num', 'tax_contravention_num',
                                'tax_arrears_num', 'mortgage_num', 'mortgage_amount_sum', 'judicial_auction_num',
                                'law_suit_num',
                                'case_type_num', 'consumption_restriction_num', 'dishonest_num',
                                'judicial_assistance_num',
                                'judicial_assistance_money']

    def update_indicators(self, conn, engine, year, is_next):

        def cn2num(cn: str) -> float:
            ans = 0.0
            length = len(cn)
            start = 0
            if cn[0] in self.cn_unit:
                ans += self.cn_unit[cn[0]]
                start = 1
            for i in range(start, length, 1):
                try:
                    if cn[i] in self.cn_unm and cn[i + 1] in self.cn_unit:
                        val, unit = self.cn_unm[cn[i]], self.cn_unit[cn[i + 1]]
                        ans += val * unit
                    else:
                        continue
                except IndexError as e:
                    val = self.cn_unm[cn[i]]
                    ans += val * unit / 10
            return ans

        def business_scope_analysis(text):
            base = re.sub(r'[\(（].*?[\)）]', '', text).replace(';', '；').replace(',', '，')
            if '；' in text:
                a = re.sub('。', '；', base).split('；')
                a_new = [i for i in a if i != '']
            elif ',' in text:
                a = re.sub('。', ',', base).split(',')
                a_new = [i for i in a if i != '']
            else:
                a = re.sub('。', '、', base).split('、')
                a_new = [i for i in a if i != '']
            return len(a_new)

        def perocess_text(x):
            if pd.isnull(x) or (not x):
                return None
            else:
                try:
                    x = x.encode('utf-8').decode('unicode_escape').replace('text":"', '').replace('",', '')
                    return x
                except Exception as e:
                    if type(x) == bytes:
                        x = x.decode('unicode_escape').replace('text":"', '').replace('",', '')
                        return x
                    else:
                        return None

        if is_next:
            survival_risk_year = year + 1
        else:
            survival_risk_year = year
        sql_base_info = f"""SELECT  company_id,if(company_id in (SELECT DISTINCT(company_id) FROM base_info WHERE reg_status IN ('注销','吊销，未注销','吊销，已注销') AND (YEAR(revoke_date)={str(survival_risk_year)} OR (revoke_date IS NULL AND YEAR(cancel_date)={str(survival_risk_year)}))),0,1) survival_risk,IF(website_list IS NULL,0,1) AS web,IF(email IS NULL,0,1) AS email,IF(city IN ('上海市','南京市','无锡市','常州市','苏州市','南通市','盐城市','扬州市','镇江市','泰州市','杭州市','宁波市','嘉兴市','湖州市','绍兴市','金华市','舟山市','台州市','合肥市','芜湖市','马鞍山市','铜陵市','安庆市','滁州市','池州市','宣城市','广州市','佛山市','肇庆市','深圳市','东莞市','惠州市','珠海市','中山市','江门市','北京市','天津市','保定市','廊坊市','唐山市','石家庄市','邯郸市','秦皇岛市','张家口市','承德市','沧州市','邢台市','衡水市','定州市','辛集市','市辖区'),1,0) AS economic_circle,
        reg_capital*(CASE reg_capital_currency WHEN '人民币' THEN 1 WHEN '美元' THEN 6.36 WHEN '欧元' THEN 6.94 WHEN '港元' THEN 0.81 WHEN '新加坡元' THEN 4.67 ELSE 1 END) AS reg_capital
        ,actual_capital*(CASE actual_capital_currency WHEN '人民币' THEN 1 WHEN '美元' THEN 6.36 WHEN '欧元' THEN 6.94 WHEN '港元' THEN 0.81 WHEN '新加坡元' THEN 4.67 ELSE 1 END) AS actual_capital,
        YEAR(estiblish_time) AS built_year,TIMESTAMPDIFF(DAY,estiblish_time, '{str(year + 1)}-01-01 00:00:00')/365 AS company_age,FIND_IN_SET(reg_status,'存续,在业,开业,迁出,迁入') AS business_status,
        (CASE WHEN company_org_type='个人独资企业' THEN '个人独资企业' WHEN company_org_type='个体工商户' THEN '个体工商户' WHEN company_org_type LIKE '%股份有限公司%' THEN '股份有限公司' WHEN company_org_type LIKE '%有限责任公司%' THEN '有限责任公司' WHEN company_org_type LIKE '%合伙企业%' THEN '合伙企业' ELSE '其他' END ) AS company_org_type
        ,industry,staff_num_range,social_staff_num,business_scope
        FROM base_info WHERE YEAR(estiblish_time)<={str(year)} AND (company_id NOT IN (SELECT DISTINCT(company_id) FROM base_info WHERE reg_status IN ('注销','吊销，未注销','吊销，已注销') AND (YEAR(revoke_date)<={str(year)} OR (revoke_date IS NULL AND YEAR(cancel_date)<={str(year)})))){' AND company_id=' + str(self.company_id) if self.company_id else ''}#到经营范围（文本分析）
        """
        df_base_info = pd.read_sql(sql_base_info, conn)
        if df_base_info.empty:
            raise Exception("df_base_info is empty!")
        df_base_info['business_scope'] = df_base_info['business_scope'].apply(business_scope_analysis)
        sql_staff = f"""SELECT b.company_id,IF(s.staff_num IS NULL,0,1) disclosure_key_personnel,s.staff_num key_personnel_num FROM base_info b LEFT JOIN (SELECT company_id,COUNT(*) staff_num FROM staff {'WHERE company_id=' + str(self.company_id) if self.company_id else 'GROUP BY company_id'} ) s ON b.company_id=s.company_id {'WHERE b.company_id=' + str(self.company_id) if self.company_id else ''}"""
        df_staff = pd.read_sql(sql_staff, conn)
        sql_holder = f"""SELECT b.company_id,max(b.percent) top1_ratio,sum(b.percent) top10_ratio,std(b.percent) standard_ratio from {'(select company_id,percent from holder where company_id=' + str(self.company_id) + ' ORDER BY percent DESC limit 10) b' if self.company_id else '(select a.* from holder a where 10 > (select count(*) from holder where company_id = a.company_id and percent > a.percent ) order by a.company_id,a.percent desc ) b GROUP BY company_id WITH ROLLUP'} #股东信息"""
        df_holder = pd.read_sql(sql_holder, conn)
        df_holder.dropna(axis=0, subset=['company_id'], inplace=True)
        sql_invest = f"""SELECT company_id,SUM(amount*(CASE amount_suffix WHEN '万美元' THEN 6.36 WHEN '万香港元' THEN 0.81 ELSE 1 END)) AS total_invest_amount,SUM(IF(FIND_IN_SET(reg_status,'存续,在业,开业,迁出,迁入'),1,0))/COUNT(*) AS invest_success_rate,SUM(TIMESTAMPDIFF(DAY,estiblish_time, '{str(year + 1)}-01-01 00:00:00')/365) AS invest_all_age FROM invest WHERE YEAR(estiblish_time)<={str(year)} {'AND company_id=' + str(self.company_id) if self.company_id else 'GROUP BY company_id'}"""
        df_invest = pd.read_sql(sql_invest, conn)
        sql_parent_company = f"""SELECT company_id,IF(company_id IN (SELECT DISTINCT(company_id) FROM parent_company),1,0) AS branch_identify  FROM base_info {'where company_id=' + str(self.company_id) if self.company_id else ''}#是否为分公司"""
        df_parent_company = pd.read_sql(sql_parent_company, conn)
        sql_branch = f"""select company_id,sum(IF(YEAR(estiblish_time)={str(year)},1,0)) AS branch_num,sum(TIMESTAMPDIFF(DAY,estiblish_time, '{str(year + 1)}-01-01 00:00:00')/365) AS branch_all_age from branch where YEAR(estiblish_time)<={str(year)} AND reg_status in ('存续','在业','开业','迁出','迁入') {'AND company_id=' + str(self.company_id) if self.company_id else 'group by company_id'}#分支机构"""
        df_branch = pd.read_sql(sql_branch, conn)
        sql_enterprise_recruitment = f"""select a.company_id,a.recruitment_num,a.recruitment_specie,b.average_salary from 
        (select company_id,count(*) recruitment_num,COUNT(distinct(title)) recruitment_specie from enterprise_recruitment group by company_id) a
        left join (select company_id,avg(substring_index(salary,'－',1)+substring_index(substring_index(salary,'－',-1),'元',1))/2 average_salary FROM enterprise_recruitment WHERE salary!='面议' group by company_id) b
        on a.company_id=b.company_id {'WHERE a.company_id=' + str(self.company_id) if self.company_id else ''}"""
        df_enterprise_recruitment = pd.read_sql(sql_enterprise_recruitment, conn)
        sql_administrative_licensing = f"""select a.company_id,if(a.company_id in (SELECT DISTINCT(company_id) FROM administrative_licensing WHERE (NOT YEAR(decision_date)>{str(year)}) AND (NOT YEAR(end_date)<{str(year)}) AND SOURCE='信用中国'),1,0) having_credit_china,
        IF(a.company_id IN (SELECT DISTINCT(company_id) FROM administrative_licensing WHERE (NOT YEAR(decision_date)>{str(year)}) AND (NOT YEAR(end_date)<{str(year)}) AND SOURCE='中国人民银行'),1,0) having_people_bank,
        IF(a.company_id IN (SELECT DISTINCT(company_id) FROM administrative_licensing WHERE (NOT YEAR(decision_date)>{str(year)}) AND (NOT YEAR(end_date)<{str(year)}) AND SOURCE='国家市场监督管理总局'),1,0) having_market_supervision
        from (select distinct(company_id) FROM administrative_licensing WHERE (NOT YEAR(decision_date)>{str(year)}) AND (NOT YEAR(end_date)<{str(year)}) {'AND company_id=' + str(self.company_id) if self.company_id else ''}) a"""
        df_administrative_licensing = pd.read_sql(sql_administrative_licensing, conn)
        sql_tax_credit = f"""SELECT b.company_id,b.lowest_grade,c.grade FROM (SELECT company_id,grade lowest_grade FROM (SELECT company_id,grade FROM tax_credit WHERE YEAR<={str(year)} ORDER BY grade DESC) a GROUP BY a.company_id) b
        LEFT JOIN (SELECT company_id,grade FROM tax_credit WHERE YEAR={str(year)} GROUP BY company_id) c ON b.company_id=c.company_id {'where b.company_id=' + str(self.company_id) if self.company_id else ''}"""
        df_tax_credit = pd.read_sql(sql_tax_credit, conn)
        sql_certificate = f"""select company_id,count(*) certificate_type_num from certificate {'where company_id=' + str(self.company_id) if self.company_id else 'GROUP BY company_id'}#证书类型数量"""
        df_certificate = pd.read_sql(sql_certificate, conn)
        sql_bidding_information = f"""select company_id,COUNT(*) bidding_num FROM bidding_information WHERE YEAR(publish_time)={str(year)} {'and company_id=' + str(self.company_id) if self.company_id else 'GROUP BY company_id'} #区间招投标成功次数"""
        df_bidding_information = pd.read_sql(sql_bidding_information, conn)
        sql_supply = f"""select c.company_id,c.disclose disclose_supply,d.ratio_std,d.amt_sum from (SELECT a.company_id,IF(b.company_id,1,0) as disclose from base_info a left join (select distinct(company_id) from supply) b ON a.company_id = b.company_id) c left join #有无披露供货商 3612
        (SELECT company_id,std(ratio) ratio_std,sum(amt) amt_sum FROM supply where year(announcement_date)={str(year)} GROUP BY company_id) d on c.company_id=d.company_id {'where c.company_id=' + str(self.company_id) if self.company_id else ''}#区间供货商采购金额 ratio/amt金额有些沒有披露"""
        df_supply = pd.read_sql(sql_supply, conn)
        sql_news = f"""SELECT company_id,COUNT(*) news_num FROM news WHERE YEAR(rtm)<={str(year)} {'and company_id=' + str(self.company_id) if self.company_id else 'GROUP BY company_id'}"""
        df_news = pd.read_sql(sql_news, conn)
        sql_core_team = f"""select c.company_id,c.disclose disclose_core_team,d.core_team_num from 
        (SELECT a.company_id,IF(b.company_id,1,0) AS disclose from base_info a left join (select distinct(company_id) from core_team) b ON a.company_id = b.company_id) c left join #是否披露核心团队
        (SELECT company_id,COUNT(*) core_team_num FROM core_team GROUP BY company_id) d on c.company_id=d.company_id {'where c.company_id=' + str(self.company_id) if self.company_id else ''}#核心团队人员数量"""
        df_core_team = pd.read_sql(sql_core_team, conn)
        sql_financing_process = f"""SELECT company_id,COUNT(*) financing_process_num FROM financing_process WHERE YEAR(pub_time)<={str(year)} {'and company_id=' + str(self.company_id) if self.company_id else 'GROUP BY company_id'}#当前融资轮次总数量"""
        df_financing_process = pd.read_sql(sql_financing_process, conn)
        sql_corporate_business = f"""SELECT company_id,COUNT(*) corporate_business_num FROM corporate_business WHERE YEAR(setup_date)<={str(year)} {'and company_id=' + str(self.company_id) if self.company_id else 'GROUP BY company_id'}#当前产品数量"""
        df_corporate_business = pd.read_sql(sql_corporate_business, conn)
        sql_competitor_information = f"""SELECT company_id,SUM(IF(ROUND IS NULL,0,1))/COUNT(*) financing_ratio,COUNT(*) competitor_num FROM competitor_information WHERE YEAR(DATE)<={str(year)} {'and company_id=' + str(self.company_id) if self.company_id else 'GROUP BY company_id'}#当前竞品有融资轮次的百分比  当前竞品数量"""
        df_competitor_information = pd.read_sql(sql_competitor_information, conn)
        sql_punishment_info = f"SELECT company_id,COUNT(*) punishment_info_num FROM punishment_info WHERE YEAR(decision_date)<={str(year)} {'and company_id=' + str(self.company_id) if self.company_id else 'GROUP BY company_id'}#行政处罚次数"
        df_punishment_info = pd.read_sql(sql_punishment_info, conn)
        sql_punishment_info2 = """SELECT company_id,REGEXP_SUBSTR(content, '(合计|共计)(罚没{0,1}款){0,1}[0-9\.]+万{0,1}元') AS r0
        ,REGEXP_SUBSTR(content, '计(罚没{0,1}款){0,1}[0-9\.]+万{0,1}元') AS r1
        ,REGEXP_SUBSTR(content, '罚款(人民币){0,1}[0-9\.]+万{0,1}元整{0,1}') AS r2
        ,REGEXP_SUBSTR(content, '罚款(人民币){0,1}[壹贰叁肆伍陆柒捌玖零拾佰仟万亿兆角分毫厘元整圆正]+') AS r3
        ,REGEXP_SUBSTR(content, '[壹贰叁肆伍陆柒捌玖零拾佰仟万亿兆角分毫厘]+(元|圆){0,1}(整|正){0,1}的罚款') AS r4
        ,REGEXP_SUBSTR(content, '[一二三四五六七八九十百千仟万亿角分毫厘]+(元|圆){0,1}(整|正){0,1}的(行政){0,1}处罚') AS r5
        ,REGEXP_SUBSTR(content, '(人民币){0,1}[0-9\.]+万{0,1}元整{0,1}的{0,1}(行政){0,1}(处罚|罚款)') AS r6
        ,REGEXP_SUBSTR(content, '罚款(人民币){0,1}[一二三四五六七八九十百千仟万亿角分毫厘]+(元|圆){0,1}(整|正){0,1}') AS r7
        ,REGEXP_SUBSTR(content, 'text":".*?",') AS r8
         FROM punishment_info WHERE YEAR(decision_date)<=""" + str(year)
        if self.company_id:
            sql_punishment_info2 += ' and company_id=' + str(self.company_id)
        df_punishment_info2 = pd.read_sql(sql_punishment_info2, conn)
        if df_punishment_info2.empty:
            df_punishment_sum = pd.DataFrame([{'company_id': str(self.company_id), 'punishment_money': np.nan}])
        else:
            df_punishment_info2['r8'] = df_punishment_info2['r8'].map(perocess_text)
            ll = list(df_punishment_info2.columns)[1:]
            for index, row in df_punishment_info2.iterrows():
                extract_punishment_money = False
                for iind, rr in enumerate(ll):
                    if row[rr]:
                        if type(row[rr]) == bytes:
                            row[rr] = row[rr].decode(chardet.detect(row[rr])['encoding'])  # 进行相应解码，赋给原标识符（变量）
                        if iind in [0, 1, 2, 6]:
                            re_result = re.findall("[0-9\.]+", row[rr])
                            if len(re_result) == 1:
                                punishment_money = float(re_result[0]) * (10000 if "万元" in row[rr] else 1)
                            else:
                                raise Exception("len(re_result)!=1")
                        elif iind in [3, 4, 5, 7]:
                            re_result = re.findall("[一二三四五六七八九十百千壹贰叁肆伍陆柒捌玖零拾佰仟万亿兆角分毫厘元圆整正]+", row[rr])
                            if len(re_result) == 1:
                                punishment_money = cn2num(re_result[0])
                            else:
                                raise Exception("len(re_result)!=1")
                        else:
                            if re.findall("[0-9\.]+", row[rr]):
                                re_result = re.findall("[0-9\.]+", row[rr])
                                if len(re_result) == 1:
                                    punishment_money = float(re_result[0]) * (10000 if "万元" in row[rr] else 1)
                                else:
                                    raise Exception("len(re_result)!=1")
                            elif re.findall("[一二三四五六七八九十百千壹贰叁肆伍陆柒捌玖零拾佰仟万亿兆角分毫厘元圆整正]+", row[rr]):
                                re_result = re.findall("[一二三四五六七八九十百千壹贰叁肆伍陆柒捌玖零拾佰仟万亿兆角分毫厘元圆整正]+", row[rr])
                                if len(re_result) == 1:
                                    punishment_money = cn2num(re_result[0])
                                else:
                                    raise Exception("len(re_result)!=1")
                            else:
                                punishment_money = 0
                        df_punishment_info2.loc[index, 'punishment_money'] = punishment_money
                        extract_punishment_money = True
                        break
                if not extract_punishment_money:
                    df_punishment_info2.loc[index, 'punishment_money'] = 0
            df_punishment_info2 = df_punishment_info2[["company_id", "punishment_money"]]
            df_punishment_sum = df_punishment_info2.groupby(['company_id'], as_index=False).sum()
        sql_equity_pledge = f"""SELECT company_id,COUNT(*) equity_pledge_num FROM equity_pledge WHERE YEAR(reg_date)={str(year)} {'and company_id=' + str(self.company_id) if self.company_id else 'GROUP BY company_id'}#区间股权出质笔数"""
        df_equity_pledge = pd.read_sql(sql_equity_pledge, conn)
        sql_tax_contravention_detail = f"""SELECT company_id,COUNT(*) tax_contravention_num FROM tax_contravention_detail WHERE YEAR(publish_time)={str(year)} {'and company_id=' + str(self.company_id) if self.company_id else 'GROUP BY company_id'}#区间税收违法次数"""
        df_tax_contravention_detail = pd.read_sql(sql_tax_contravention_detail, conn)
        sql_tax_arrears_announcement = f"""SELECT company_id,COUNT(*) tax_arrears_num FROM tax_arrears_announcement WHERE YEAR(publish_date)={str(year)} {'and company_id=' + str(self.company_id) if self.company_id else 'GROUP BY company_id'}#区间欠税公告次数"""
        df_tax_arrears_announcement = pd.read_sql(sql_tax_arrears_announcement, conn)
        sql_mortgage_base_info = f"""SELECT company_id,COUNT(*) mortgage_num,sum(REGEXP_SUBSTR(amount, '[0-9\.]+')) mortgage_amount_sum FROM mortgage_base_info WHERE YEAR(publish_date)={str(year)} {'and company_id=' + str(self.company_id) if self.company_id else 'GROUP BY company_id'}#区间动产抵押次数 区间动产抵押金额"""
        df_mortgage_base_info = pd.read_sql(sql_mortgage_base_info, conn)
        sql_judicial_auction = f"""SELECT company_id,COUNT(*) judicial_auction_num FROM judicial_auction WHERE YEAR(SUBTIME)={str(year)} {'and company_id=' + str(self.company_id) if self.company_id else 'GROUP BY company_id'}#区间司法拍卖次数"""
        df_judicial_auction = pd.read_sql(sql_judicial_auction, conn)
        sql_law_suit = f"""SELECT company_id,COUNT(*) law_suit_num,COUNT(DISTINCT(case_type)) case_type_num FROM legal_proceedings {'WHERE company_id=' + str(self.company_id) if self.company_id else 'GROUP BY company_id'}#案件次数 #案由种类数"""
        df_law_suit = pd.read_sql(sql_law_suit, conn)
        sql_consumption_restriction = f"""SELECT company_id,COUNT(*) consumption_restriction_num FROM consumption_restriction WHERE YEAR(case_create_time)={str(year)} {'and company_id=' + str(self.company_id) if self.company_id else 'GROUP BY company_id'}#区间限令次数"""
        df_consumption_restriction = pd.read_sql(sql_consumption_restriction, conn)
        sql_dishonest = f"""SELECT company_id,COUNT(*) dishonest_num FROM dishonest WHERE YEAR(reg_date)={str(year)} {'and company_id=' + str(self.company_id) if self.company_id else 'GROUP BY company_id'}#区间失信次数"""
        df_dishonest = pd.read_sql(sql_dishonest, conn)
        sql_judicial_assistance = f"""SELECT company_id,COUNT(*) judicial_assistance_num,SUM(REGEXP_SUBSTR(equity_amount, '[0-9\.]+')*(IF(LOCATE('万美元',equity_amount)>0,6.36,1))) judicial_assistance_money FROM judicial_assistance {'WHERE company_id=' + str(self.company_id) if self.company_id else 'GROUP BY company_id'}#总执行总金额"""
        df_judicial_assistance = pd.read_sql(sql_judicial_assistance, conn)
        df_list = [df_base_info, df_staff, df_holder, df_invest, df_parent_company, df_branch,
                   df_enterprise_recruitment,
                   df_administrative_licensing, df_tax_credit, df_certificate, df_bidding_information, df_supply,
                   df_news,
                   df_core_team, df_financing_process, df_corporate_business, df_competitor_information,
                   df_punishment_info,
                   df_punishment_sum, df_equity_pledge, df_tax_contravention_detail, df_tax_arrears_announcement,
                   df_mortgage_base_info, df_judicial_auction, df_law_suit, df_consumption_restriction, df_dishonest,
                   df_judicial_assistance]
        for indexxx, df_ in enumerate(df_list):
            if (df_.empty or (len(df_invest) == 1 and (not df_.loc[0, 'company_id']))):
                if self.company_id:
                    df_.loc[0, 'company_id'] = self.company_id
            if not df_.empty:
                df_['company_id'] = df_['company_id'].astype('int64')
        df_middle = df_base_info.join(df_staff.set_index('company_id'), on='company_id', lsuffix='_l', rsuffix='_r')
        for indexx, df_ in enumerate(df_list[2:]):
            df_middle = df_middle.join(df_.set_index('company_id'), on='company_id', lsuffix='_l', rsuffix='_r')
        df_middle.fillna(value=np.nan)
        for cc in ['key_personnel_num', 'total_invest_amount', 'invest_success_rate', 'invest_all_age', 'branch_num',
                   'branch_all_age', 'having_credit_china', 'having_people_bank', 'having_market_supervision',
                   'certificate_type_num', 'bidding_num', 'ratio_std', 'amt_sum', 'news_num', 'financing_process_num',
                   'financing_ratio', 'competitor_num', 'punishment_info_num', 'punishment_money', 'equity_pledge_num',
                   'tax_contravention_num', 'tax_arrears_num', 'mortgage_num', 'mortgage_amount_sum',
                   'judicial_auction_num', 'law_suit_num', 'case_type_num', 'consumption_restriction_num',
                   'dishonest_num',
                   'judicial_assistance_num', 'judicial_assistance_money']:
            df_middle[cc].fillna(0, inplace=True)
        df_middle['year'] = year
        if 'survival_risk' in df_middle:
            del df_middle['survival_risk']
        df_middle['industry'] = df_middle['industry'].map(lambda x: self.industry_dict[x])
        df_middle.to_sql('model_predict_various_indicators', engine, if_exists='append', index=False)

        df_middle = df_middle.astype(dtype={i: self.dtypes[i] for i in self.feature_columns})
        return df_middle

    def investment_value_predict_update(self, engine, year, df):
        model = joblib.load(os.path.join(MODEL_DIR, "investment_value_predict_model.pkl"))
        predict_proba = model.predict_proba(df[self.feature_columns])[:, 1]
        df['proba_value'] = predict_proba
        df['predict_year'] = year + 1
        df[['company_id', 'predict_year', 'proba_value']].to_sql('investment_value_predict', engine, if_exists='append',
                                                                 index=False)

    def enterprise_credit_evaluation_update(self, engine, year, df):
        model = joblib.load(os.path.join(MODEL_DIR, "enterprise_credit_evaluation_lightgbm_2020.pkl"))
        predict_proba = model.predict_proba(df[self.feature_columns])[:, 0]
        df['proba_value'] = predict_proba
        df['predict_year'] = year + 1
        df[['company_id', 'predict_year', 'proba_value']].to_sql('survival_risk_predict', engine, if_exists='append',
                                                                 index=False)

    def patent_value_predict_update(self, conn, engine, company_id=None):
        def count_words(content):
            symbol_list = ['。', '，', '、', '；', '：', '？', '！', '“', '”', '‘', '’', '（', '）', '……', '——', '—', '《', '》',
                           '<', '>',
                           '·'] + [',', '.', '?', '!', ':', '...', ';', '-', '–', '—', '(', ')', '[', ']', '{', '}',
                                   '"', "'"]
            for i in symbol_list:
                content = content.replace(i, '')
            return len(content.replace(' ', ''))

        def multiply_process(patent_type, original_value):
            if patent_type in ["发明授权", "发明申请"]:
                return 5 * original_value
            elif patent_type == "实用新型":
                return 2 * original_value
            else:
                return original_value

        sql = f"""SELECT a.index incopat_id,a.company_id,a.publication_number,a.patent_type,IF(b.bond_name IS NULL,0,1) IndustrialandCommercialCode_num,a.technical_advanced AdvancedTechnology,a.patent_page DocumentPages,a.citation_family_forward_times NumberOfFamilyBe_cited,a.citation_family_times  NumberOfFamilyCitations,
            a.family_main_number NumberOfSimpleJomologies,a.citation_forward_times NumberOfTimesCited,a.examination_duration ReviewTime,a.claim_first RightofFirst,a.protection_scope ScopeOfProtection,
            YEAR(NOW())-YEAR(b.estiblish_time) Age,reg_capital Size,social_staff_num Labor FROM incopat_all a,base_info b WHERE a.company_id=b.company_id{' and a.company_id=' + str(company_id) if company_id else ''}"""
        df_incopat_all = pd.read_sql(sql, conn)
        if not df_incopat_all.empty:
            df_incopat_all["Size"].fillna(0, inplace=True)
            df_incopat_all["Labor"].fillna(0, inplace=True)
            df_incopat_all["NumberOfFamilyBe_cited"].fillna(0, inplace=True)
            df_incopat_all["ReviewTime"].fillna(20, inplace=True)
            df_incopat_all['RightofFirst'] = df_incopat_all['RightofFirst'].map(count_words)
            df_incopat_all["DocumentPages"].fillna(6, inplace=True)
            df_incopat_all["NumberOfFamilyCitations"].fillna(0, inplace=True)
            df_incopat_all["NumberOfTimesCited"].fillna(0, inplace=True)
            for cc in ['AdvancedTechnology', 'DocumentPages', 'NumberOfFamilyBe_cited', 'NumberOfFamilyCitations',
                       'NumberOfSimpleJomologies', 'NumberOfTimesCited', 'ReviewTime', 'RightofFirst',
                       'ScopeOfProtection',
                       'Age', 'Size', 'Labor']:
                df_incopat_all[cc] = df_incopat_all.apply(lambda row: multiply_process(row['patent_type'], row[cc]),
                                                          axis=1)
            regressor_OLS_y1 = load_pickle(os.path.join(MODEL_DIR, "regressor_OLS_y1.pickle"))
            predict_df = regressor_OLS_y1.predict(sm.add_constant(
                df_incopat_all[
                    ['IndustrialandCommercialCode_num', 'NumberOfFamilyBe_cited', 'ReviewTime', 'Age', 'Size',
                     'Labor']],
                has_constant='add'))
            df_incopat_all["predictive_value"] = predict_df
            df_incopat_all['predictive_value'] = df_incopat_all['predictive_value'].map(
                lambda x: 5078958 if x < 0 else x)
            df_incopat_all["predictive_value"] = df_incopat_all["predictive_value"] / 3
            regressor_OLS_y2 = load_pickle(os.path.join(MODEL_DIR, "regressor_OLS_y2.pickle"))
            predict_df2 = regressor_OLS_y2.predict(
                sm.add_constant(df_incopat_all[['AdvancedTechnology', 'DocumentPages', 'NumberOfFamilyBe_cited',
                                                'NumberOfFamilyCitations', 'NumberOfSimpleJomologies',
                                                'NumberOfTimesCited', 'ReviewTime', 'RightofFirst', 'ScopeOfProtection',
                                                'Size', 'Labor']], has_constant='add'))
            df_incopat_all["predictive_credit_line"] = predict_df2
            df_incopat_all['predictive_credit_line'] = df_incopat_all['predictive_credit_line'].map(
                lambda x: 1446783 if x < 0 else x)
            df_incopat_all["predictive_credit_line"] = df_incopat_all["predictive_credit_line"] / 3
            df_incopat_all[['incopat_id', 'predictive_value', 'predictive_credit_line']].to_sql('patent_value_predict',
                                                                                                engine,
                                                                                                if_exists='append',
                                                                                                index=False)

    def innovation_capability_index_update(self, conn, engine, company_id=None):
        df = pd.read_sql(
            f'SELECT `patent_type`,`company_id`  FROM incopat WHERE patent_status!="失效"{" and company_id=" + str(company_id) if company_id else ""}',
            conn)
        if not df.empty:
            score_dict = {'发明申请': 2, '实用新型': 2, '外观设计': 1, '发明授权': 5, "其他": 1}
            df["score"] = df['patent_type'].apply(lambda x: score_dict[x])
            df_score_sum = df.groupby(["company_id"], as_index=False)["score"].sum()
            df_score_sum["score"] = df_score_sum['score'].apply(lambda x: math.log(x + 1, 2000) * 100)
            if company_id:
                df_score_sum.to_sql('innovation_capability_score', engine, if_exists='append', index=False)
                pass
            else:
                df_ = pd.read_sql('SELECT `company_id`  FROM base_info', conn)
                df_['company_id'] = df_['company_id'].astype('int64')
                df_finally = df_.join(df_score_sum.set_index('company_id'), on='company_id', lsuffix='_l', rsuffix='_r')
                df_finally.fillna(value=0, inplace=True)
                df_finally.to_sql('innovation_capability_score', engine, if_exists='append', index=False)
        else:
            pd.DataFrame({'company_id': [company_id], 'score': [0]}).to_sql('innovation_capability_score', engine,
                                                                            if_exists='append', index=False)

    def save_db(self):
        conn = pymysql.connect(host=MYSQL_HOST, user='root', passwd=MYSQL_PASSWORD, db=MYSQL_DB, port=3306)
        engine = create_engine(f"mysql+pymysql://root:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}?charset=utf8mb4")
        year = int(time.strftime('%Y', time.localtime())) - 1
        df = self.update_indicators(conn, engine, year, False)
        self.investment_value_predict_update(engine, year, df)  # 训练用的是2021年的数据
        self.enterprise_credit_evaluation_update(engine, year, df)  # 训练用的是2020年的数据
        self.patent_value_predict_update(conn, engine, self.company_id)  # 不用管年份，用的ols模型
        self.innovation_capability_index_update(conn, engine, self.company_id)  # 不用管年份，直接计算得到
        print("模型全部入库成功")
        engine.dispose()
        conn.close()

    def get_business_result(self):
        conn = pymysql.connect(host=MYSQL_HOST, user='root', passwd=MYSQL_PASSWORD, db=MYSQL_DB, port=3306)
        specified_df = pd.read_sql(
            f'SELECT *  FROM model_predict_various_indicators WHERE company_id={str(self.company_id)}', conn)
        if specified_df.empty:
            result = 0
        elif specified_df.shape[0] > 1:
            result = -1
            print("model_predict_various_indicators表中有多条数据")
            # raise Exception("specified_df.shape[0]>1!")
        else:
            specified_df = specified_df[self.feature_columns]
            income_statement_list = ['total_revenue', 'operating_costs', 'op', 'profit_total_amt',
                                     'income_tax_expenses']
            for income_statement in income_statement_list:
                specified_df[income_statement] = self.income_statement_dict[income_statement]
            all_feature_columns = income_statement_list + self.feature_columns
            specified_df = specified_df.astype(dtype={i: self.dtypes[i] for i in all_feature_columns})
            model = joblib.load(os.path.join(MODEL_DIR, "net_profit_next_year_2020_model.pkl"))
            predict_proba = model.predict_proba(specified_df[all_feature_columns])[:, 1]
            result = predict_proba[0]
        conn.close()
        return result



