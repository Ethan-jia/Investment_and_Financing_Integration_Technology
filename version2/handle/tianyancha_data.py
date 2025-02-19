import shutil

import os
import re
import json
import glob
import time
import pymysql
import datetime
import requests
import numpy as np
import pandas as pd
from tqdm import tqdm
from sqlalchemy import create_engine

from index import *
from handle.tianyancha_sql import *
from tools.random_secret_key import get_secret_key
from tools.find_lately_dir import get_lately_dir

r"""
# 一家公司tianyancha的更新
Tianyancha("2309498815").query_down()
# 全部公司tianyancha的更新
Tianyancha().query_down()
# 已经下载的入库
Tianyancha(download_folder_path=r"G:\workSpace\workSpace_Python\PPP\tianyancha_file\2022-06-28aaaa").save_db()
"""


def change_field_type(error_str, conn):
    print("======================================================================")
    print(error_str)
    error_str = str(error_str)
    data_too_long_error = re.findall(r"Data too long for column '(\w*)'", error_str)
    if data_too_long_error:
        field_name = data_too_long_error[0]
        table_name = re.findall(r"INSERT INTO (\w*) \(", error_str)[0]
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        sql1 = f'select COLUMN_TYPE,COLUMN_COMMENT from information_schema.COLUMNS WHERE TABLE_NAME = "{table_name}" and COLUMN_NAME = "{field_name}"'
        cursor.execute(sql1)
        result = cursor.fetchone()
        field_type = result["COLUMN_TYPE"]
        field_comment = result["COLUMN_COMMENT"]
        # print(field_name, table_name, field_type, field_comment)
        if field_type == "text":
            sql2 = f'alter table {table_name} modify column {field_name} mediumtext comment "{field_comment}";'
        elif "varchar" in field_type:
            current_num = int(field_type.replace("varchar(", "").replace(")", ""))
            if current_num > 5000:
                field_type = "text"
            elif current_num > 1000:
                modify_num = current_num + 1000
                field_type = f"varchar({modify_num})"
            else:
                modify_num = 1001
                field_type = f"varchar({modify_num})"
            sql2 = f'alter table {table_name} modify column {field_name} {field_type} comment "{field_comment}";'
        cursor.execute(sql2)


def get_lower_case_name(text):
    lst = []
    for index, char in enumerate(text):
        if char.isupper() and index != 0:
            lst.append("_")
        lst.append(char)
    return "".join(lst).lower()


def translate_time(x):
    if pd.isna(x):
        return None
    if x:
        try:
            x = int(x)
        except Exception as e:
            if type(x) == datetime.datetime:
                return x.strftime("%Y-%m-%d %H:%M:%S")
            else:
                try:
                    if time.strptime(x, "%Y-%m-%d %H:%M:%S"):
                        return x
                except Exception as e:
                    try:
                        if time.strptime(x, "%Y-%m-%d"):
                            return x
                    except Exception as e:
                        if time.strptime(x, "%Y年%m月%d日"):
                            return x.replace("年", '-').replace("月", '-').replace("日", '')
        if x >= 0:
            if x == 253402185600000:
                return "9999-12-31 00:00:00"
            if x == 253392422400000:
                return "9999-09-09 00:00:00"
            if x == 95617555200000:
                return "5000-01-01 00:00:00"
            if x == 63872640000000:
                return "3994-01-17 00:00:00"
            if x == 64029024000000:
                return "3999-01-01 00:00:00"
            if x == 253391731200000:
                return "9999-09-01 00:00:00"
            try:
                return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(x) / 1000))
            except Exception as e:
                # print(e)
                # print(x)
                return None
        else:
            return datetime.datetime(1970, 1, 1, 8, 0) + datetime.timedelta(seconds=float(x) / 1000)
    else:
        return None


class Tianyancha:
    def __init__(self, company_id="", start_num=0, download_folder_path=""):
        self.company_id = company_id
        self.start_num = start_num
        if company_id:
            self.download_folder_path = os.path.join(TIANYANCHA_TEMPORARY_DIR, get_secret_key())
            self.download_lately_path = os.path.join(TIANYANCHA_DIR, get_lately_dir(TIANYANCHA_DIR))
        else:
            self.download_folder_path = download_folder_path
        self.df = ""
        self.token = TOKEN
        self.api_dict = {
            "工商信息": "cb/ic/2.0",
            "企业基本信息（含主要人员）": "ic/baseinfoV3/2.0",
            "企业股东": "ic/holder/2.0",
            "对外投资": "ic/inverst/2.0",
            "分支机构": "ic/branch/2.0",
            "总公司": "ic/parentCompany/2.0",
            "企业专利信息": "ipr/patents/3.0",
            "法律诉讼": "jr/lawSuit/3.0",
            "法律诉讼详情": "jr/lawSuit/detail",
            "资质证书": "m/certificate/2.0",
            "一般纳税人": "m/taxpayer/2.0",
            "融资历程": "cd/findHistoryRongzi/2.0",
            "动产抵押": "mr/mortgageInfo/2.0",
            "行政处罚": "mr/punishmentInfo/3.0",
            "经营异常": "mr/abnormal/2.0",
            "被执行人": "jr/zhixinginfo/2.0",
            "历史被执行人": "hi/zhixing/2.0",
            "失信人": "jr/dishonest/2.0",
            "历史失信人": "hi/dishonest/2.0",
            "限制消费令": "jr/consumptionRestriction/2.0",
            "税收违法": "mr/taxContravention/2.0",
            "行政许可": "m/getAdministrativeLicense/2.0",
            "税务评级": "m/taxCredit/2.0",
            "企业招投标信息": "m/bids/2.0",
            "供应商": "m/supply/2.0",
            "新闻舆情": "ps/news/2.0",
            "核心团队": "cd/findTeamMember/2.0",
            "企业业务": "cd/getProductInfo/2.0",
            "竞品信息": "cd/findJingpin/2.0",
            "股权出质": "mr/equityInfo/2.0",
            "欠税公告": "mr/ownTax/2.0",
            "司法拍卖": "mr/judicialSale/3.0",
            "司法协助": "judicial",
            "企业招聘": "m/employments/3.0",
            "利润表": "stock/profit/2.0",
        }
        self.api_dict_1 = {
            "企业基本信息（含主要人员）": 'base_info&staff',
            "企业股东": 'holder',
            "对外投资": 'invest',
            "分支机构": 'branch',
            "总公司": 'parent_company',
            "限制消费令": "consumption_restriction",
            "失信人": "dishonest",
            "被执行人": "executee_info",
            "经营异常": "abnormal",
            "行政处罚": "punishment_info",
            "税收违法详情": "tax_contravention_detail",
            "动产抵押": "mortgage_base_info&mortgage_people_info&mortgage_pawn_info&mortgage_change_info",
            "融资历程": "financing_process",
            "一般纳税人": "taxpayer",
            "资质证书": "certificate",
            "企业专利信息": "patents",
            "行政许可": "administrative_licensing",
            "税务评级": "tax_credit",
            "企业招投标信息": "bidding_information",
            "供应商": "supply",
            "新闻舆情": "news",
            "核心团队": "core_team",
            "企业业务": "corporate_business",
            "竞品信息": "competitor_information",
            "股权出质": "equity_pledge",
            "欠税公告": "tax_arrears_announcement",
            "司法拍卖": "judicial_auction",
            "司法协助": "judicial_assistance",
            "企业招聘": "enterprise_recruitment",
        }
        self.error_code_dict = {
            0: '请求成功',
            300000: '无数据',
            300001: '请求失败',
            300002: '账号失效',
            300003: '账号过期',
            300004: '访问频率过快',
            300005: '无权限访问此api',
            300006: '余额不足',
            300007: '剩余次数不足',
            300008: '缺少必要参数',
            300009: '账号信息有误',
            300010: 'URL不存在',
            300011: '此IP无权限访问此api',
            300012: '报告生成中'
        }
        self.port_name_list = [
            "企业基本信息（含主要人员）",
            "企业股东",
            "对外投资",
            "分支机构",
            "总公司",
            "企业专利信息",
            "资质证书",
            "一般纳税人",
            "融资历程",
            "动产抵押",
            "行政处罚",
            "经营异常",
            "被执行人",
            "历史被执行人",
            "失信人",
            "历史失信人",
            "限制消费令",
            "税收违法",
            "行政许可",
            "税务评级",
            "企业招投标信息",
            "供应商",
            "新闻舆情",
            "核心团队",
            "企业业务",
            "竞品信息",
            "股权出质",
            "欠税公告",
            "司法拍卖",
            "法律诉讼",
            "法律诉讼详情",
            "司法协助",
            "企业招聘",
        ]

    def one_save(self, port_name, detail_id="", page_num=1, page_size=20, year=None):
        # 名字处理
        if detail_id:
            res_name = f"{self.company_id}_{detail_id}_{port_name}"
            res_path = os.path.join(self.download_folder_path, f"{self.company_id}_{detail_id}_{port_name}.json")
        else:
            if year:
                res_name = f"{self.company_id}_{port_name}_{str(year)}"
                res_path = os.path.join(self.download_folder_path, f"{self.company_id}_{port_name}_{str(year)}.json")
            else:
                res_name = f"{self.company_id}_{port_name}{'' if page_num == 0 else '_' + str(page_num)}"
                res_path = os.path.join(self.download_folder_path,
                                        f"{self.company_id}_{port_name}{'' if page_num == 0 else '_' + str(page_num)}.json")
        # 如果文件存在跳出
        if os.path.exists(res_path):
            if page_num >= 1:
                if port_name == '新闻舆情' and page_num == 1:
                    return
                if port_name == "供应商":
                    self.one_save(port_name, detail_id=detail_id, page_num=page_num + 1, page_size=page_size)
                else:
                    with open(res_path, encoding="utf-8") as file:
                        response_text_json = json.load(file)
                    if page_num * page_size < int(response_text_json['result']['total']):
                        self.one_save(port_name, detail_id=detail_id, page_num=page_num + 1, page_size=page_size)
            return
        # url处理
        if detail_id:
            if port_name == "法律诉讼详情":
                url = f"http://open.api.tianyancha.com/services/open/jr/lawSuit/detail?uuid={detail_id}"
            else:
                url = f"http://open.api.tianyancha.com/services/open/mr/taxContravention/detail/2.0?id={detail_id}"
        else:
            if port_name == "司法协助":
                if page_num == 0:
                    url = f"http://open.api.tianyancha.com/services/v4/open/judicial?keyword={self.company_id}"
                else:
                    url = f"http://open.api.tianyancha.com/services/v4/open/judicial?keyword={self.company_id}&pageNum={str(page_num)}&pageSize={str(page_size)}"
            else:
                if page_num == 0:
                    if year:
                        url = f"http://open.api.tianyancha.com/services/open/{self.api_dict[port_name]}?keyword={self.company_id}&year={str(year)}"
                    else:
                        url = f"http://open.api.tianyancha.com/services/open/{self.api_dict[port_name]}?keyword={self.company_id}"
                else:
                    url = f"http://open.api.tianyancha.com/services/open/{self.api_dict[port_name]}?keyword={self.company_id}&pageNum={str(page_num)}&pageSize={str(page_size)}"
        # 发起请求
        while True:
            try:
                response = requests.get(url, headers={'Authorization': self.token})
            except Exception as e:
                print(e)
                time.sleep(3)
            else:
                break
        # 存储文件
        if response.status_code == 200:
            response_text = response.text
            response_text_json = json.loads(response_text)
            error_code = response_text_json['error_code']
            if error_code == 0:
                with open(res_path, 'w', encoding='utf-8') as file_obj:
                    file_obj.write(response_text)
                if port_name == "供应商":
                    self.one_save(port_name, detail_id=detail_id, page_num=page_num + 1, page_size=page_size)
                else:
                    if page_num == 0:
                        pass
                    else:
                        if port_name == '新闻舆情' and page_num == 1:
                            return
                        if page_num * page_size < int(response_text_json['result']['total']):
                            self.one_save(port_name, detail_id=detail_id, page_num=page_num + 1, page_size=page_size)
            elif error_code == 300000:
                pass
            else:
                with open(TIANYANCHA_ERROR_PATH, 'a', encoding='utf-8') as file_obj2:
                    file_obj2.write(f"{res_name} {self.error_code_dict[error_code]}！\n")
        else:
            with open(TIANYANCHA_ERROR_PATH, 'a', encoding='utf-8') as file_obj3:
                file_obj3.write(f"{res_name} 请求失败!\n")
            print(f"{res_name} 请求失败!")

    def one_down(self):
        for port_name in self.port_name_list:
            if port_name == "税收违法":
                self.one_save(port_name)
                result_list = glob.glob(
                    os.path.join(self.download_folder_path, f"{self.company_id}_{port_name}_*.json"))
                for result in result_list:
                    with open(result, 'r', encoding='utf8')as fp:
                        json_data = json.load(fp)
                    for item in json_data["result"]["items"]:
                        self.one_save(port_name="税收违法详情", page_num=0, detail_id=item["id"])
            elif port_name == "法律诉讼详情":
                legal_proceedings_list = glob.glob(
                    os.path.join(self.download_folder_path, f"{self.company_id}_法律诉讼_*.json"))
                for result in legal_proceedings_list:
                    with open(result, 'r', encoding='utf8')as fp:
                        json_data = json.load(fp)
                    for item in json_data["result"]["items"]:
                        self.one_save(port_name="法律诉讼详情", page_num=0, detail_id=item["uuid"])
            else:
                if port_name in ["企业基本信息（含主要人员）", "总公司"]:
                    self.one_save(port_name=port_name, page_num=0)
                else:
                    self.one_save(port_name)

    def one_query_down(self):
        # 创建文件夹
        os.mkdir(self.download_folder_path)

        # 下载当前company_id的天眼查文件
        self.one_down()

        # 入库
        self.save_db()

        # 把下载的文件移到最近的文件夹目录
        try:
            for i in os.listdir(self.download_folder_path):
                shutil.move(os.path.join(self.download_folder_path, i), self.download_lately_path)
        except:
            for i in os.listdir(self.download_folder_path):
                os.remove(os.path.join(self.download_folder_path, i))

        # 删除已有文件（如果有）
        for _ in os.listdir(self.download_folder_path):
            file_path = os.path.join(self.download_folder_path, _)
            os.remove(file_path)

        # 删除文件夹
        try:
            os.rmdir(self.download_folder_path)
        except:
            pass

    def all_query_down(self):
        from tools.query_company import get_company_excel
        # 获取当前时间
        now_time = time.strftime('%Y-%m-%d', time.localtime())
        self.download_folder_path = os.path.join(TIANYANCHA_DIR, now_time)
        # 创建文件夹
        os.mkdir(self.download_folder_path)

        # 重新获取基本信息表
        get_company_excel()

        # 获取所有company_id
        company_id_list = list(pd.read_excel(COMPANY_EXCEL_PATH)["company_id"])
        company_id_list = [str(int(c)) for c in company_id_list if not pd.isnull(c)]

        # 循环进行下载
        for res_company_id in tqdm(company_id_list[self.start_num:]):
            while True:
                try:
                    self.company_id = res_company_id
                    self.one_down()
                    break
                except Exception as e:
                    with open(TIANYANCHA_ERROR_PATH, "a", encoding="utf-8") as file:
                        file.write(
                            f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} {str(self.company_id)} {str(e)}\n")
                    time.sleep(0.3)

        # 入库
        self.company_id = ""
        self.save_db()

    def organize2dataframe(self, columns, result_, json_columns=[], modify_columns={}, extract_columns=[],
                           timestamp_columns=[], translate_dict={}, specific_category='', relate_name=''):

        def split_two_columns(x):
            if pd.isna(x):
                return None
            if ' ' in x:
                x_split = x.split(' ')
                if len(x_split) == 2:
                    return x_split[0]
            if len(x) - len(x.replace('。', '')) == 2:
                return x.split('。')[0] + '。'
            if len(x) - len(x.replace('依照', '')) == 1:
                return x.split('依照')[0]

        def split_two_columns2(x):
            if pd.isnull(x):
                return None
            if ' ' in x:
                x_split = x.split(' ')
                if len(x_split) == 2:
                    return x_split[1]
            if len(x) - len(x.replace('。', '')) == 2:
                return x.split('。')[1]
            if len(x) - len(x.replace('依照', '')) == 1:
                return '依照' + x.split('依照')[1]

        df_list = []
        for ind, file_path in enumerate(result_):
            with open(file_path, 'r', encoding='utf-8') as f:
                json_content = json.load(f)
            if json_content['error_code'] == 0:
                df_item = pd.DataFrame(columns=columns)
                index = 0
                split_list_ = os.path.splitext(os.path.basename(file_path))[0].split("_")
                company_id = split_list_[0]
                if relate_name:
                    relate_id = split_list_[1]
                if specific_category == 'staff':
                    if 'result' in json_content['result']['staffList']:
                        result = json_content['result']['staffList']['result']
                    else:
                        continue
                elif specific_category == 'supply':
                    result = json_content['result']['pageBean']['result']
                elif specific_category == 'profit':
                    result = json_content['result']['corpProfit']
                    if not result:
                        continue
                else:
                    result = json_content['result']
                ergodic = True if specific_category in ['staff', 'supply', 'profit'] else ('items' in result)
                if ergodic:
                    items = result if specific_category in ['staff', 'supply', 'profit'] else result['items']
                    for item in items:
                        if extract_columns:
                            for extract_column in extract_columns:
                                if ':' in extract_column:
                                    s1, s2 = extract_column.split(":")
                                    if isinstance(item[s1], dict):
                                        df_item.loc[index, s2] = item[s1][s2]
                                    elif isinstance(item[s1], list):
                                        if len(item[s1]) > 0:
                                            df_item.loc[index, s2] = item[s1][0][s2]
                                elif '__' in extract_column:
                                    extract_column_split = extract_column.split("__")
                                    if isinstance(item[extract_column_split[0]], dict):
                                        df_item.loc[index, extract_column_split[0] + '_' + extract_column_split[1]] = \
                                            item[extract_column_split[0]][extract_column_split[1]]
                                    else:
                                        raise Exception("!!!! isinstance(item[extract_column_split[0]], dict)")
                                else:
                                    if '[]' in extract_column:
                                        list_content = item[extract_column.replace("[]", "")]
                                        if list_content:
                                            for content_ in list_content:
                                                for k, v in content_.items():
                                                    df_item.loc[index, s2] = item[s1][s2]
                                                    df_item.loc[index, k] = v
                                                index += 1
                                        else:
                                            df_item.drop([index, ], inplace=True)
                                        index -= 1
                                    else:
                                        if isinstance(item[extract_column], dict):
                                            for k, v in item[extract_column].items():
                                                df_item.loc[index, k] = v
                                        elif isinstance(item[extract_column], list):
                                            if len(item[extract_column]) > 0:
                                                for k, v in item[extract_column][0].items():
                                                    df_item.loc[index, k] = v
                        for c in columns:
                            if c == 'company_id':
                                df_item.loc[index, 'company_id'] = company_id
                            elif c in json_columns:
                                if c in item:
                                    df_item.loc[index, c] = json.dumps(item[c], ensure_ascii=False)
                            else:
                                try:
                                    df_item.loc[index, c] = item[c]
                                except Exception as e:
                                    # print("df_item.loc Except:", e)
                                    if str(e).replace("'", "") not in ['id', 'unperformPart', 'performedPart']:
                                        raise Exception(str(e))
                        if relate_name:
                            df_item.loc[index, relate_name] = relate_id
                        index += 1
                else:
                    if extract_columns:
                        for extract_column in extract_columns:
                            if ':' in extract_column:
                                s1, s2 = extract_column.split(":")
                                if isinstance(result[s1], dict):
                                    df_item.loc[index, s2] = result[s1][s2]
                                elif isinstance(result[s1], list):
                                    df_item.loc[index, s2] = result[s1][0][s2]
                            else:
                                if isinstance(result[extract_column], dict):
                                    for k, v in result[extract_column].items():
                                        df_item.loc[index, k] = v
                                elif isinstance(result[extract_column], list):
                                    for k, v in result[extract_column][0].items():
                                        df_item.loc[index, k] = v
                    for c in columns:
                        if c == 'company_id':
                            df_item.loc[index, 'company_id'] = company_id
                        elif c in json_columns:
                            if c in result:
                                df_item.loc[index, c] = json.dumps(result[c], ensure_ascii=False)
                        else:
                            try:
                                df_item.loc[index, c] = result[c]
                            except Exception as e:
                                # print("df_item.loc Except:", e)
                                if str(e).replace("'", "") not in ['detail_id', 'case_fact', 'case_basis']:
                                    raise Exception(str(e))
                    if relate_name:
                        df_item.loc[index, relate_name] = relate_id
                    index += 1
                df_list.append(df_item)
            else:
                pass
        df = pd.concat(df_list, ignore_index=True)
        if specific_category == 'mortgage_change_info' and len(df.columns) == 1:
            df = pd.DataFrame(columns=columns)
            self.df = df
            return
        df.replace("", np.nan, inplace=True)
        df.replace("-", np.nan, inplace=True)
        if timestamp_columns:
            for timestamp_column in timestamp_columns:
                df[timestamp_column] = df[timestamp_column].map(translate_time)
        if translate_dict:
            for translate_column, translate_function in translate_dict.items():
                df[translate_column] = df[translate_column].map(translate_function)
        if 'case_info' in columns:
            df['case_fact'] = df['case_info'].map(split_two_columns)
            df['case_basis'] = df['case_info'].map(split_two_columns2)
        discard_columns = [column for column in df.columns if
                           column in ["overviewRemark", "overviewTerm", "overviewAmount", "overviewScope",
                                      "overviewType", ]]
        for discard_column in discard_columns:
            del df[discard_column]
        columns_ = [
            get_lower_case_name(modify_columns[cc]) if cc in modify_columns else get_lower_case_name(cc) for cc in
            df.columns
        ]
        replace_columns_dict = dict(zip(df.columns, columns_))
        df.rename(columns=replace_columns_dict, inplace=True)
        df.replace("", np.nan, inplace=True)
        df.replace("-", np.nan, inplace=True)
        self.df = df

    def save_major(self, conn, cursor, engine):
        for api_zh, api_en in self.api_dict_1.items():
            if api_zh in ["失信人", "被执行人"]:
                result = glob.glob(os.path.join(self.download_folder_path, f"{self.company_id}*{api_zh}*.json")) + \
                         glob.glob(os.path.join(self.download_folder_path, f"{self.company_id}*历史{api_zh}*.json"))
            else:
                result = glob.glob(os.path.join(self.download_folder_path, f"{self.company_id}*{api_zh}*.json"))
            if len(result) == 0:
                continue
            if api_zh == "企业基本信息（含主要人员）":
                for api_name in api_en.split('&'):
                    exec(f"""cursor.execute(sql_{api_name})\nconn.commit()""")
                    if api_name == "staff":
                        exec(
                            f"""self.organize2dataframe({api_name}_columns, result, json_columns={api_name}_json, modify_columns={api_name}_modify, extract_columns={api_name}_extract, timestamp_columns={api_name}_timestamp,translate_dict={api_name}_translate,specific_category='staff')""")
                    else:
                        exec(
                            f"""self.organize2dataframe({api_name}_columns, result, json_columns={api_name}_json, modify_columns={api_name}_modify, extract_columns={api_name}_extract, timestamp_columns={api_name}_timestamp,translate_dict={api_name}_translate)""")
                    self.df['company_category'] = "3"
                    while True:
                        try:
                            result_ = self.df.to_sql(api_name, engine, if_exists='append', index=False)
                        except Exception as e:
                            change_field_type(e, conn)
                        else:
                            break
                    print(f"{api_name}数据插入完毕！！！")
            elif api_zh == "动产抵押":
                for api_name in api_en.split('&'):
                    exec(f"""cursor.execute(sql_{api_name})\nconn.commit()""")
                    if api_name == "mortgage_base_info":
                        exec(
                            f"""self.organize2dataframe({api_name}_columns, result, json_columns={api_name}_json, modify_columns={api_name}_modify, extract_columns={api_name}_extract, timestamp_columns={api_name}_timestamp,translate_dict={api_name}_translate,)""")
                        self.df['company_category'] = "3"
                    elif api_name == "mortgage_people_info":
                        exec(
                            f"""self.organize2dataframe({api_name}_columns, result, json_columns={api_name}_json, modify_columns={api_name}_modify, extract_columns={api_name}_extract, timestamp_columns={api_name}_timestamp,translate_dict={api_name}_translate)""")
                    elif api_name == "mortgage_pawn_info":
                        exec(
                            f"""self.organize2dataframe({api_name}_columns, result, json_columns={api_name}_json, modify_columns={api_name}_modify, extract_columns={api_name}_extract, timestamp_columns={api_name}_timestamp,translate_dict={api_name}_translate)""")
                    else:
                        exec(
                            f"""self.organize2dataframe({api_name}_columns, result, json_columns={api_name}_json, modify_columns={api_name}_modify, extract_columns={api_name}_extract, timestamp_columns={api_name}_timestamp,translate_dict={api_name}_translate,specific_category='mortgage_change_info')""")
                    if not self.df.empty:
                        while True:
                            try:
                                self.df.to_sql(api_name, engine, if_exists='append', index=False)
                            except Exception as e:
                                change_field_type(e, conn)
                            else:
                                break
                    print(f"{api_name}数据插入完毕！！！")
            else:
                exec(f"""cursor.execute(sql_{api_en})\nconn.commit()""")
                if api_zh == '税收违法详情':
                    exec(
                        f"""self.organize2dataframe({api_en}_columns, result, json_columns={api_en}_json, modify_columns={api_en}_modify, extract_columns={api_en}_extract, timestamp_columns={api_en}_timestamp,translate_dict={api_en}_translate,relate_name='detail_id')""")
                elif api_zh in ["资质证书", "供应商", "利润表"]:
                    exec(
                        f"""self.organize2dataframe({api_en}_columns, result, json_columns={api_en}_json, modify_columns={api_en}_modify, extract_columns={api_en}_extract, timestamp_columns={api_en}_timestamp,translate_dict={api_en}_translate,specific_category='{api_en}')""")
                else:
                    exec(
                        f"""self.organize2dataframe({api_en}_columns, result, json_columns={api_en}_json, modify_columns={api_en}_modify, extract_columns={api_en}_extract, timestamp_columns={api_en}_timestamp,translate_dict={api_en}_translate)""")
                self.df['company_category'] = "3"
                while True:
                    try:
                        self.df.to_sql(api_en, engine, if_exists='append', index=False)
                    except Exception as e:
                        change_field_type(e, conn)
                    else:
                        print(f"{api_en}数据插入完毕！！！")
                        break

    def save_legal(self, conn, cursor, engine):
        result = glob.glob(os.path.join(self.download_folder_path, f"{self.company_id}*法律诉讼_*.json"))
        if len(result) == 0:
            return
        columns = [
            'company_id', 'docType', 'lawsuitUrl', 'lawsuitH5Url', 'title', 'court', 'judgeTime', 'uuid', 'caseNo',
            'caseType', 'caseReason', 'casePersons', 'case_status', 'case_result', 'caseMoney', 'submitTime'
        ]
        df_list = []
        for ind, file_path in enumerate(result):
            with open(file_path, 'r', encoding='utf-8') as f:
                legal_proceedings_json = json.load(f)
            if legal_proceedings_json['error_code'] == 0:
                df_item = pd.DataFrame(columns=columns)
                index = 0
                items = legal_proceedings_json['result']['items']
                res_company_id = os.path.splitext(os.path.basename(file_path))[0].split("_")[0]
                for item in items:
                    for c in columns:
                        if c == 'case_status':
                            continue
                        if c == 'company_id':
                            df_item.loc[index, 'company_id'] = res_company_id
                        elif c == 'case_result':
                            legal_proceedings_detail_path = os.path.join(self.download_folder_path,
                                                                         f"{res_company_id}_{item['uuid']}_法律诉讼详情.json")
                            if os.path.exists(legal_proceedings_detail_path):
                                with open(legal_proceedings_detail_path, 'r', encoding='utf-8') as ff:
                                    legal_proceedings_detail_json = json.load(ff)
                                if legal_proceedings_detail_json['error_code'] == 0:
                                    case_result = legal_proceedings_detail_json['result']['judgeResult']
                                    if case_result:
                                        case_result_ = re.sub(u"<.*?>", '', case_result).replace("\n", "").replace(" ",
                                                                                                                   "").strip()
                                        if case_result_:
                                            df_item.loc[index, 'case_result'] = case_result_
                                else:
                                    raise Exception(
                                        legal_proceedings_detail_path + " error_code:" + legal_proceedings_detail_json[
                                            'error_code'])
                            else:
                                pass
                                # print(f"{legal_proceedings_detail_path} 不存在！！！")
                        elif c == 'casePersons':
                            df_item.loc[index, c] = json.dumps(item[c], ensure_ascii=False)
                            if item[c]:
                                cursor.execute(f"SELECT name FROM base_info WHERE company_id='{res_company_id}'")
                                result_company_name = cursor.fetchone()[0]
                                for it in item[c]:
                                    if it['name'] == result_company_name:
                                        df_item.loc[index, 'case_status'] = it['role']
                                        break
                        else:
                            df_item.loc[index, c] = item[c]
                    index += 1
                df_list.append(df_item)
            else:
                raise Exception(file_path + " error_code:" + legal_proceedings_json['error_code'])
        df = pd.concat(df_list, ignore_index=True)
        replace_columns_dict = {}
        for cc in columns:
            lower_case_name = get_lower_case_name(cc)
            if lower_case_name != cc:
                replace_columns_dict[cc] = lower_case_name
        df.rename(columns=replace_columns_dict, inplace=True)
        df["submit_time"] = df["submit_time"].map(translate_time)
        df["judge_time"] = df["judge_time"].map(translate_time)
        df["case_money"] = df["case_money"].map(translate_money)
        df.replace("", np.nan, inplace=True)
        df.replace("-", np.nan, inplace=True)
        cursor.execute(sql_legal_proceedings)
        conn.commit()
        df['company_category'] = "3"
        while True:
            try:
                df.to_sql("legal_proceedings", engine, if_exists='append', index=False)
                print("legal_proceedings数据插入完毕！！！")
            except Exception as e:
                change_field_type(e, conn)
            else:
                break

    def save_legal_detail(self, conn, cursor, engine):

        def ChineseDate2EnglishDate(ChineseDate):
            if not ChineseDate:
                return ""
            ChineseDate = ChineseDate.replace(" ", "").replace("\n", "").replace("\t", "").replace("���〇",
                                                                                                   "二〇").replace("告诉十月",
                                                                                                                 "十月") \
                .replace("n", "").replace("二lig", "二〇").replace("是十二", "十二").replace("二○—八", "二○一八").replace(".",
                                                                                                             "").replace(
                "元月", "六月")
            map = dict(零=0, 〇=0, 一=1, 二=2, 三=3, 四=4, 五=5, 六=6, 七=7, 八=8, 九=9, 十=9)
            map.update({str(i): i for i in range(10)})
            map['０'] = 0
            map['○'] = 0
            map['O'] = 0
            map['Ｏ'] = 0
            map['o'] = 0
            map['Ο'] = 0
            year = ChineseDate.split("年")[0]
            if year == '××××':
                return ""
            month = ChineseDate.split("年")[1].split("月")[0]
            if month == '××':
                return ""
            day = ChineseDate.split("年")[1].split("月")[1].split("日")[0]
            if day == '××':
                return ""
            if len(day) >= 3:
                day = day[0] + day[2]
            try:
                year = "".join(str(map[i]) for i in year)
            except Exception as e:
                print(e)
                year = time.strftime('%Y', time.localtime())
            try:
                month = "".join(str(map[i]) for i in month)
            except Exception as e:
                print(e)
                month = "01"
            try:
                day = "".join(str(map[i]) for i in day)
            except Exception as e:
                print(e)
                day = "01"
            if len(month) == 3:
                month = month[0] + month[2]
            month = month.rjust(2, '0')
            if len(day) == 3:
                day = day[0] + day[2]
            day = day.rjust(2, '0')
            return year + '-' + month + '-' + day

        def tran_date(x):
            if not x:
                return None
            try:
                date_ = datetime.datetime.strptime(x, '%Y-%m-%d')
                return date_
            except Exception as e:
                if (not 13 > int(x.split('-')[1]) > 0) or (not 32 > int(x.split('-')[2]) > 0) or (
                        x in ['2021-02-29', '201-06-25']):
                    return None
                else:
                    if "day is out of range for month" in str(e):
                        return None
                    else:
                        # print(x)
                        # print(str(e))
                        raise Exception(e)

        result = glob.glob(os.path.join(self.download_folder_path, f"{self.company_id}*法律诉讼详情*.json"))
        if len(result) == 0:
            return
        columns = [
            'company_id', 'judgeDate', 'judgeResult', 'title', 'caseno', 'uuid', 'courtConsider', 'companies',
            'plaintiffRequest', 'courtInspect', 'trialProcedure', 'lawFirms', 'plaintiffRequestOfFirst',
            'defendantReplyOfFirst', 'trialPerson', 'plaintext', 'appellor', 'court', 'url', 'courtConsiderOfFirst',
            'doctype', 'trialAssistPerson', 'casetype', 'appellantRequest', 'defendantReply', 'courtInspectOfFirst',
            'appelleeArguing'
        ]
        df = pd.DataFrame(columns=columns)
        index = 0
        for ind, file_path in enumerate(result):
            with open(file_path, 'r', encoding='utf-8') as f:
                legal_proceedings_detail_json = json.load(f)
            if legal_proceedings_detail_json['error_code'] == 0:
                res_company_id = os.path.splitext(os.path.basename(file_path))[0].split("_")[0]
                item = legal_proceedings_detail_json['result']
                for c in columns:
                    if c == 'company_id':
                        df.loc[index, 'company_id'] = res_company_id
                    elif c in ['companies', 'lawFirms']:
                        df.loc[index, c] = json.dumps(item[c], ensure_ascii=False)
                    else:
                        df.loc[index, c] = item[c]
                index += 1
            else:
                raise Exception(file_path + " error_code:" + legal_proceedings_detail_json['error_code'])
        replace_columns_dict = {}
        for cc in columns:
            lower_case_name = get_lower_case_name(cc)
            if lower_case_name != cc:
                replace_columns_dict[cc] = lower_case_name
        df.rename(columns=replace_columns_dict, inplace=True)
        df["judge_date"] = df["judge_date"].map(ChineseDate2EnglishDate)
        df["judge_date"] = df["judge_date"].map(tran_date)
        df.replace("", np.nan, inplace=True)
        df.replace("-", np.nan, inplace=True)
        df.replace("None", np.nan, inplace=True)
        cursor.execute(sql_legal_proceedings_detail)
        conn.commit()
        while True:
            try:
                df.to_sql("legal_proceedings_detail", engine, if_exists='append', index=False)
                print("legal_proceedings_detail数据插入完毕！！！")
            except Exception as e:
                change_field_type(e, conn)
            else:
                break

    def save_db(self):
        conn = pymysql.connect(host=MYSQL_HOST, user='root', passwd=MYSQL_PASSWORD, db=MYSQL_DB, port=3306)
        cursor = conn.cursor()
        engine = create_engine(f"mysql+pymysql://root:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}?charset=utf8mb4")
        self.save_major(conn, cursor, engine)
        self.save_legal(conn, cursor, engine)
        self.save_legal_detail(conn, cursor, engine)
        engine.dispose()
        cursor.close()
        conn.close()

    def query_down(self):
        if self.company_id:
            self.one_query_down()
        else:
            self.all_query_down()

