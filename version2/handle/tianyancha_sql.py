import pandas as pd


def translate_date(x):
    if pd.isna(x):
        return None
    if "--" in x:
        return x.replace("--", "-01-")
    return x


def translate_money(x):
    if pd.isna(x):
        return None
    if x:
        x = x.replace("人民币", "").replace("美元", "").replace("欧元", "").replace("香港元", "").replace("港元", "").replace(
            "新加坡元", "").replace("元", "")
        if '万' in x:
            return float(x.replace('万', "")) * 10000
        else:
            if x in ['-', '——']:
                return None
            return float(x)
    else:
        return None


def translate_percent(x):
    if x and (not pd.isna(x)):
        if x == "-":
            return None
        return float(x.replace('%', "")) / 100
    else:
        return None


company_category = "3"
sql_survival_risk_predict = f"""CREATE TABLE IF NOT EXISTS `survival_risk_predict` (
`id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT "自增id",
`company_category` TINYINT NOT NULL DEFAULT {company_category} COMMENT "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL COMMENT "公司id",
`predict_year` year COMMENT "预测年份",
`proba_value` float COMMENT "预测概率",
`insert_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP  COMMENT "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="存续风险预测";
"""
# 企业基本信息（含主要人员）
# 企业基本信息 base_info
base_info_columns = [
    'company_id', 'staffNumRange', 'fromTime', 'type', 'bondName', 'isMicroEnt', 'usedBondName',
    'regNumber', 'percentileScore', 'regCapital', 'name', 'regInstitute', 'regLocation', 'industry',
    'approvedTime', 'updateTimes', 'socialStaffNum', 'tags', 'taxNumber', 'businessScope', 'property3',
    'alias', 'orgNumber', 'regStatus', 'estiblishTime', 'bondType', 'legalPersonName', 'toTime',
    'actualCapital', 'companyOrgType', 'base', 'creditCode', 'historyNames', 'historyNameList',
    'bondNum', 'regCapitalCurrency', 'actualCapitalCurrency', 'email', 'websiteList', 'phoneNumber',
    'revokeDate', 'revokeReason', 'cancelDate', 'cancelReason', 'city', 'district',
]
base_info_json = ['historyNameList']  # json转成str
base_info_modify = {}  # 修改的 key:value  源字段名：目标字段名
base_info_extract = ['industryAll']  # 需要从list的下一级提取出来的
base_info_timestamp = ['fromTime', 'approvedTime', 'updateTimes', 'estiblishTime', 'toTime', 'revokeDate',
                       'cancelDate']  # 时间戳转换
base_info_translate = {'regCapital': translate_money, 'actualCapital': translate_money}  # key:value  字段名：转换函数
sql_base_info = f"""CREATE TABLE IF NOT EXISTS `base_info` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT {company_category} comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`staff_num_range` varchar(200) comment "人员规模",
`from_time` datetime comment "经营开始时间",
`type` TINYINT comment "法人类型，1 人 2 公司",
`bond_name` varchar(20) comment "股票名",
`is_micro_ent` TINYINT comment "是否是小微企业 0不是 1是",
`used_bond_name` varchar(50) comment "股票曾用名",
`reg_number` varchar(31) comment "注册号",
`percentile_score` SMALLINT comment "企业评分",
`reg_capital` BIGINT comment "注册资本",
`name` varchar(255) comment "企业名",
`reg_institute` varchar(255) comment "登记机关",
`reg_location` varchar(255) comment "注册地址",
`industry` varchar(255) comment "行业",
`approved_time` TIMESTAMP comment "核准时间",
`update_times` TIMESTAMP comment "更新时间",
`social_staff_num` int(10) comment "参保人数",
`tags` varchar(255) comment "企业标签",
`tax_number` varchar(255) comment "纳税人识别号",
`business_scope` varchar(4091) comment "经营范围",
`property3` varchar(255) comment "英文名",
`alias` varchar(255) comment "简称",
`org_number` varchar(31) comment "组织机构代码",
`reg_status` varchar(31) comment "企业状态（经营状态）",
`estiblish_time` datetime comment "成立日期（注册日期）",
`bond_type` varchar(31) comment "股票类型",
`legal_person_name` varchar(120) comment "法人",
`to_time` DATETIME comment "经营结束时间",
`actual_capital` BIGINT comment "实收注册资金",
`company_org_type` varchar(127) comment "企业类型",
`base` varchar(31) comment "省份简称",
`credit_code` varchar(255) comment "统一社会信用代码",
`history_names` varchar(255) comment "曾用名",
`history_name_list` varchar(2000) comment "曾用名",
`bond_num` varchar(20) comment "股票号",
`reg_capital_currency` varchar(10) comment "注册资本币种 人民币 美元 欧元 等",
`actual_capital_currency` varchar(10) comment "实收注册资本币种 人民币 美元 欧元 等",
`email` varchar(1500) comment "邮箱",
`website_list` varchar(255) comment "网址",
`phone_number` varchar(2050) comment "企业联系方式",
`revoke_date` TIMESTAMP comment "吊销日期",
`revoke_reason` varchar(500) comment "吊销原因",
`cancel_date` TIMESTAMP comment "注销日期",
`cancel_reason` varchar(500) comment "注销原因",
`city` varchar(20) comment "市",
`district` varchar(20) comment "区",
`category` varchar(255) comment "国民经济行业分类门类",
`category_big` varchar(255) comment "国民经济行业分类大类",
`category_middle` varchar(255) comment "国民经济行业分类中类",
`category_small` varchar(255) comment "国民经济行业分类小类",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="企业基本信息";"""
# 主要人员 staff
staff_columns = ['company_id', 'id', 'name', 'typeJoin', 'type']
staff_json = ['typeJoin']  # json转成str
staff_modify = {'id': 'staff_id'}  # 修改的 key:value  源字段名：目标字段名
staff_extract = []  # 需要从list的下一级提取出来的
staff_timestamp = []  # 时间戳转换
staff_translate = {}  # key:value  字段名：转换函数
sql_staff = f"""CREATE TABLE IF NOT EXISTS `staff` (`id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT "自增id",
`company_category` TINYINT NOT NULL DEFAULT {company_category} COMMENT "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL COMMENT "公司id",
`staff_id` VARCHAR(25) COMMENT "公司id",
`name` VARCHAR(255) COMMENT "主要人员名称",
`type_join` VARCHAR(200) COMMENT "职位",
`type` TINYINT COMMENT "1-公司 2-人",
`insert_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP  COMMENT "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="主要人员";"""
# 企业股东 holder
holder_columns = ['company_id', 'id', 'cgid', 'hcgid', 'logo', 'name', 'alias', 'capitalActl', 'type']
holder_json = ['capitalActl']  # json转成str
holder_modify = {'id': 'corr_id'}  # 修改的 key:value  源字段名：目标字段名
holder_extract = ['capital']  # 需要从list的下一级提取出来的 两种情况 {} [{}] list取第一个
holder_timestamp = []  # 时间戳转换
holder_translate = {'percent': translate_percent}  # key:value  字段名：转换函数
sql_holder = f"""CREATE TABLE IF NOT EXISTS `holder` (`id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT "自增id",
`company_category` TINYINT NOT NULL DEFAULT {company_category} COMMENT "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL COMMENT "公司id",
`corr_id` BIGINT(20) COMMENT "对应表id",
`cgid` VARCHAR(25) COMMENT "股东公司id",
`hcgid` VARCHAR(64) COMMENT "人员hcgid",
`logo` VARCHAR(150) COMMENT "logo",
`name` VARCHAR(250) COMMENT "股东名",
`alias` VARCHAR(50) COMMENT "简称",
`capital_actl` VARCHAR(3500) COMMENT "实际出资列表",
`type` TINYINT COMMENT "股东类型 1-公司 2-人 3-其它",
`amomon` varchar(1000) COMMENT "出资金额",
`time` DATE COMMENT "出资时间",
`percent` DOUBLE COMMENT "占比",
`paymet` VARCHAR(30) COMMENT "认缴方式",
`insert_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP  COMMENT "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="企业股东";"""
# 对外投资 invest   还有历史对外投资
invest_columns = ['company_id', 'orgType', 'business_scope', 'percent', 'regStatus', 'estiblishTime',
                  'legalPersonName', 'type', 'amount', 'id', 'category', 'regCapital', 'name', 'base', 'creditCode',
                  'personType', 'alias', 'amountSuffix']
invest_json = []  # json转成str
invest_modify = {'id': 'invested_company_id'}  # 修改的 key:value  源字段名：目标字段名
invest_extract = []  # 需要从list的下一级提取出来的 两种情况 {} [{}]
invest_timestamp = ['estiblishTime']  # 时间戳转换
invest_translate = {'percent': translate_percent}  # key:value  字段名：转换函数
sql_invest = f"""CREATE TABLE IF NOT EXISTS `invest` (`id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT "自增id",
`company_category` TINYINT NOT NULL DEFAULT {company_category} COMMENT "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL COMMENT "公司id",
`org_type` VARCHAR(127) COMMENT "公司类型",
`business_scope` VARCHAR(4091) COMMENT "经营范围",
`percent` DOUBLE COMMENT "投资占比",
`reg_status` VARCHAR(50) COMMENT "企业状态",
`estiblish_time` datetime COMMENT "开业时间",
`legal_person_name` VARCHAR(120) COMMENT "法人",
`type` TINYINT COMMENT "1-公司 2-人（被投资公司类型）",
`amount` DOUBLE COMMENT "投资金额",
`invested_company_id` VARCHAR(25) COMMENT "被投资公司id",
`category` VARCHAR(256) COMMENT "行业",
`reg_capital` varchar(50) COMMENT "注册资金",
`name` VARCHAR(255) COMMENT "被投资公司",
`base` VARCHAR(10) COMMENT "省份简称",
`credit_code` VARCHAR(18) COMMENT "统一社会信用代码",
`person_type` TINYINT COMMENT "1 人 2 公司（被投资法人类型）",
`alias` VARCHAR(30) COMMENT "简称",
`amount_suffix` VARCHAR(30) COMMENT "投资金额单位",
`insert_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP  COMMENT "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="对外投资";"""
# 分支机构 branch
branch_columns = [
    'company_id', 'logo', 'alias', 'estiblishTime', 'regStatus', 'legalPersonName', 'id', 'category', 'regCapital',
    'name', 'base', 'personType'
]
branch_json = []  # json转成str
branch_modify = {'id': 'branch_company_id'}  # 修改的 key:value  源字段名：目标字段名
branch_extract = []  # 需要从list的下一级提取出来的 两种情况 {} [{}]
branch_timestamp = ['estiblishTime']  # 时间戳转换
branch_translate = {}  # key:value  字段名：转换函数
sql_branch = f"""CREATE TABLE IF NOT EXISTS `branch` (`id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT "自增id",
`company_category` TINYINT NOT NULL DEFAULT {company_category} COMMENT "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL COMMENT "公司id",
`logo` VARCHAR(150) COMMENT "logo",
`alias` VARCHAR(30) COMMENT "简称",
`estiblish_time` datetime COMMENT "开业时间",
`reg_status` VARCHAR(31) COMMENT "企业状态",
`legal_person_name` VARCHAR(120) COMMENT "法人",
`branch_company_id` VARCHAR(25) COMMENT "公司id",
`category` VARCHAR(50) COMMENT "行业code",
`reg_capital` varchar(50) COMMENT "注册资金",
`name` VARCHAR(255) COMMENT "公司名",
`base` VARCHAR(10) COMMENT "省份简称",
`person_type` TINYINT COMMENT "法人类型 1-人 2-公司",
`insert_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP  COMMENT "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="分支机构";"""
# 总公司 parentCompany parent_company
parent_company_columns = [
    'company_id', 'reg_capital', 'estiblish_time', 'legalPersonName', 'personLogo', 'reg_status', 'name', 'logo',
    'alias', 'id'
]
parent_company_json = []  # json转成str
parent_company_modify = {'id': 'parent_company_id'}  # 修改的 key:value  源字段名：目标字段名
parent_company_extract = []  # 需要从list的下一级提取出来的 两种情况 {} [{}]
parent_company_timestamp = []  # 时间戳转换
parent_company_translate = {}  # key:value  字段名：转换函数
sql_parent_company = f"""CREATE TABLE IF NOT EXISTS `parent_company` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT {company_category} comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`reg_capital` varchar(50) comment "注册资本",
`estiblish_time` DATE comment "成立日期",
`legal_person_name` varchar(255) comment "法人",
`person_logo` varchar(150) comment "法人图片",
`reg_status` varchar(120) comment "经营状态",
`name` varchar(255) comment "总公司名",
`logo` varchar(150) comment "logo",
`alias` varchar(120) comment "公司简称",
`parent_company_id` varchar(25) comment "总公司id",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="总公司";
"""

# 司法风险-限制消费令
consumption_restriction_columns = [
    "company_id", "caseCode", "qyinfoAlias", "filePath", "qyinfo", "caseCreateTime", "alias", "id", "xname", "cid",
    "hcgid", "applicant", "applicantCid", "publishDate"
]
consumption_restriction_json = []  # json转成str
consumption_restriction_modify = {
    "id": "cor_id",
    "qyinfoAlias": "company_info_alias",
    "qyinfo": "company_info"
}  # 修改的 key:value  源字段名：目标字段名
consumption_restriction_extract = []  # 需要从list的下一级提取出来的
consumption_restriction_timestamp = ["caseCreateTime", "publishDate"]  # 时间戳转换
consumption_restriction_translate = {}  # key:value  字段名：转换函数
sql_consumption_restriction = f"""CREATE TABLE IF NOT EXISTS `consumption_restriction` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT {company_category} comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`case_code` varchar(50) comment "案号",
`company_info_alias` varchar(100) comment "企业信息简称",
`file_path` varchar(150) comment "pdf文件地址",
`company_info` varchar(100) comment "企业信息",
`case_create_time` timestamp comment "立案时间",
`alias` varchar(100) comment "别名",
`cor_id` varchar(25) comment "对应表id",
`xname` varchar(60) comment "限制消费者名称",
`cid` varchar(25) comment "企业id",
`hcgid` varchar(50) comment "限制消费者id",
`applicant` varchar(255) comment "申请人信息",
`applicant_cid` varchar(255) comment "申请人id",
`publish_date` timestamp comment "发布日期",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="限制消费令";
"""
# 司法风险-失信人
dishonest_columns = [
    "company_id", "businessentity", "areaname", "courtname", "unperformPart", "staff", "type", "performedPart", "iname",
    "disrupttypename", "casecode", "cardnum", "performance", "regdate", "publishdate", "gistunit", "duty", "gistid"
]
dishonest_json = ["staff"]  # json转成str
dishonest_modify = {
    "businessentity": "business_entity", "areaname": "area_name", "courtname": "court_name",
    "disrupttypename": "disrupt_type_name",
    "casecode": "case_code", "cardnum": "card_num", "regdate": "reg_date",
    "publishdate": "publish_date", "gistunit": "gist_unit",
    "gistid": "gist_id"
}  # 修改的 key:value  源字段名：目标字段名
dishonest_extract = []  # 需要从list的下一级提取出来的
dishonest_timestamp = ['regdate', 'publishdate']  # 时间戳转换
dishonest_translate = {}  # key:value  字段名：转换函数
sql_dishonest = f"""CREATE TABLE IF NOT EXISTS `dishonest` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT {company_category} comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`business_entity` varchar(60) comment "法人、负责人姓名",
`area_name` varchar(30) comment "省份地区",
`court_name` varchar(50) comment "法院",
`unperform_part` mediumtext comment "未履行部分",
`staff` varchar(4000) comment "法定负责人/主要负责人信息",
`type` tinyint comment "失信人类型，0代表人，1代表公司",
`performed_part` mediumtext comment "已履行部分",
`iname` varchar(60) comment "失信人名称",
`disrupt_type_name` varchar(2000) comment "失信被执行人行为具体情形",
`case_code` varchar(50) comment "案号",
`card_num` varchar(30) comment "身份证号码/组织机构代码",
`performance` varchar(60) comment "履行情况",
`reg_date` timestamp comment "立案时间",
`publish_date` timestamp comment "发布时间",
`gist_unit` varchar(60) comment "做出执行的依据单位",
`duty` mediumtext comment "生效法律文书确定的义务",
`gist_id` varchar(100) comment "执行依据文号",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="失信人";
"""

# 司法风险-被执行人
executee_info_columns = [
    "company_id", "caseCode", "execCourtName", "pname", "partyCardNum", "caseCreateTime", "execMoney"
]
executee_info_json = []  # json转成str
executee_info_modify = {}  # 修改的 key:value  源字段名：目标字段名
executee_info_extract = []  # 需要从list的下一级提取出来的
executee_info_timestamp = ["caseCreateTime"]  # 时间戳转换
executee_info_translate = {'execMoney': translate_money}  # key:value  字段名：转换函数
sql_executee_info = f"""CREATE TABLE IF NOT EXISTS `executee_info` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT {company_category} comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`case_code` varchar(50) comment "案号",
`exec_court_name` varchar(50) comment "执行法院",
`pname` varchar(60) comment "被执行人名称",
`party_card_num` varchar(60) comment "身份证号／组织机构代码",
`case_create_time` timestamp comment "创建时间",
`exec_money` varchar(20) comment "执行标的（元）",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="被执行人";
"""

# 经营风险-经营异常
abnormal_columns = [
    "company_id", "removeDate", "putReason", "putDepartment", "removeDepartment", "removeReason", "putDate"
]
abnormal_json = []  # json转成str
abnormal_modify = {}  # 修改的 key:value  源字段名：目标字段名
abnormal_extract = []  # 需要从list的下一级提取出来的
abnormal_timestamp = []  # 时间戳转换
abnormal_translate = {}  # key:value  字段名：转换函数
sql_abnormal = f"""CREATE TABLE IF NOT EXISTS `abnormal` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT {company_category} comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`remove_date` DATE comment "移出日期",
`put_reason` varchar(4091) comment "列入异常名录原因",
`put_department` varchar(200) comment "决定列入异常名录部门(作出决定机关)",
`remove_department` varchar(200) comment "移出部门",
`remove_reason` varchar(4091) comment "移除异常名录原因",
`put_date` DATE comment "列入日期",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="经营异常";
"""
# 经营风险-行政处罚
punishment_info_columns = [
    "company_id", "decisionDate", "punishNumber", "reason", "content", "departmentName", "source", "legalPersonName",
    "remark", "punishStatus", "type", "typeSecond", "evidence", "punishName"
]
punishment_info_json = []  # json转成str
punishment_info_modify = {}  # 修改的 key:value  源字段名：目标字段名
punishment_info_extract = []  # 需要从list的下一级提取出来的
punishment_info_timestamp = []  # 时间戳转换
punishment_info_translate = {}  # key:value  字段名：转换函数
sql_punishment_info = f"""CREATE TABLE IF NOT EXISTS `punishment_info` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT {company_category} comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`decision_date` DATE comment "处罚日期",
`punish_number` varchar(256) comment "决定文书号",
`reason` text comment "处罚事由/违法行为类型",
`content` varchar(8192) comment "处罚结果/内容",
`department_name` varchar(512) comment "处罚单位",
`source` varchar(30) comment "数据来源",
`legal_person_name` varchar(120) comment "法定代表人（source=国家市场监督管理总局时返回数据）",
`remark` varchar(100) comment "备注（source=国家市场监督管理总局时返回数据）",
`punish_status` varchar(10) comment "处罚状态（source=信用中国时返回数据）",
`type` varchar(100) comment "处罚类别1（source=信用中国时返回数据）",
`type_second` varchar(100) comment "处罚类别2（source=信用中国时返回数据）",
`evidence` varchar(1000) comment "处罚依据（source=信用中国时返回数据）",
`punish_name` varchar(500) comment "处罚名称（source=信用中国时返回数据）",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="行政处罚";
"""

# 经营风险-税收违法详情
tax_contravention_detail_columns = [
    "company_id", "detail_id", "res_person_id_type", "res_person_sex", "address",
    "responsible_department", "res_department_name", "taxpayer_code", "case_info",
    "case_fact", "case_basis", "legal_person_sex", "case_type",
    "legal_person_id_number", "res_person_name", "res_department_sex", "taxpayer_name",
    "legal_person_id_type", "publish_time", "legal_person_name", "res_person_id_number",
    "taxpayer_number", "department", "res_department_id_type",
    "res_department_id_number"
]
tax_contravention_detail_json = []  # json转成str
tax_contravention_detail_modify = {}  # 修改的 key:value  源字段名：目标字段名
tax_contravention_detail_extract = []  # 需要从list的下一级提取出来的
tax_contravention_detail_timestamp = []  # 时间戳转换
tax_contravention_detail_translate = {"publish_time": translate_date}  # key:value  字段名：转换函数
sql_tax_contravention_detail = f"""CREATE TABLE IF NOT EXISTS `tax_contravention_detail` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT {company_category} comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`detail_id` varchar(25) NOT NULL comment "详情id",
`res_person_id_type` varchar(32) comment "负有责任的财务负责人证件名称",
`res_person_sex` varchar(32) comment "负有直接责任的财务负责人性别",
`address` varchar(100) comment "注册地址",
`responsible_department` varchar(255) comment "所属税务机关",
`res_department_name` varchar(255) comment "负有直接责任的中介机构从业人员姓名",
`taxpayer_code` varchar(50) comment "组织机构代码",
`case_info` varchar(1000) comment "主要违法事实、相关法律依据及税务处理处罚情况",
`case_fact` varchar(512) comment "主要违法事实",
`case_basis` varchar(512) comment "相关法律依据",
`legal_person_sex` varchar(32) comment "法定代表人或负责人性别",
`case_type` varchar(100) comment "案件性质",
`legal_person_id_number` varchar(255) comment "法定代表人或负责人证件号码",
`res_person_name` varchar(255) comment "负有直接责任的财务负责人姓名",
`res_department_sex` varchar(32) comment "负有直接责任的中介机构从业人员性别",
`taxpayer_name` varchar(100) comment "纳税人名称",
`legal_person_id_type` varchar(32) comment "法定代表人或负责人证件名称",
`publish_time` Date comment "发布时间",
`legal_person_name` varchar(255) comment "法定代表人或负责人",
`res_person_id_number` varchar(255) comment "负有责任的财务负责人证件号码",
`taxpayer_number` varchar(50) comment "纳税人识别号",
`department` varchar(200) comment "负有直接责任的中介机构",
`res_department_id_type` varchar(32) comment "负有直接责任的中介机构从业人员证件名称",
`res_department_id_number` varchar(255) comment "负有直接责任的中介机构从业人员证件号码",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="税收违法详情";
"""

# 经营风险-税收违法 //这个不用了
tax_contravention_columns = ["company_id", "publish_time", "case_type", "id", "department", "taxpayer_name"]
tax_contravention_json = []  # json转成str
tax_contravention_modify = {"id": "detail_id"}  # 修改的 key:value  源字段名：目标字段名
tax_contravention_extract = []  # 需要从list的下一级提取出来的
tax_contravention_timestamp = []  # 时间戳转换
tax_contravention_translate = {}  # key:value  字段名：转换函数
sql_tax_contravention = f"""CREATE TABLE IF NOT EXISTS `tax_contravention` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT {company_category} comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`publish_time` DATE comment "发布时间",
`case_type` varchar(100) comment "案件性质",
`detail_id` varchar(20) comment "违法id",
`department` varchar(200) comment "所属税务机关",
`taxpayer_name` varchar(100) comment "纳税人名称",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="税收违法";
"""

# 经营风险-动产抵押
mortgage_base_info_columns = ["company_id", ]
mortgage_base_info_json = []  # json转成str
mortgage_base_info_modify = {}  # 修改的 key:value  源字段名：目标字段名
mortgage_base_info_extract = ["baseInfo", ]  # 需要从list的下一级提取出来的
mortgage_base_info_timestamp = ["cancelDate", "publishDate"]  # 时间戳转换
mortgage_base_info_translate = {}  # key:value  字段名：转换函数
sql_mortgage_base_info = f"""CREATE TABLE IF NOT EXISTS `mortgage_base_info` (
`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT {company_category} comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`amount` varchar(50) comment "被担保债权数额",
`cancel_date` timestamp comment "注销日期",
`publish_date` timestamp comment "公示日期",
`reg_date` DATE comment "登记日期",
`remark` varchar(1000) comment "备注",
`type` varchar(50) comment "被担保债权种类",
`reg_department` varchar(255) comment "登记机关",
`reg_num` varchar(100) comment "登记编号",
`scope` varchar(1000) comment "担保范围",
`term` varchar(1000) comment "债务人履行债务的期限",
`cancel_reason` varchar(500) comment "注销原因",
`status` varchar(100) comment "状态",
`base` varchar(4) comment "省份",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="动产抵押";
"""
mortgage_people_info_columns = ['id']
mortgage_people_info_json = []  # json转成str
mortgage_people_info_modify = {'id': 'base_info_id'}  # 修改的 key:value  源字段名：目标字段名
mortgage_people_info_extract = ["baseInfo:id", "peopleInfo[]", ]  # 需要从list的下一级提取出来的
mortgage_people_info_timestamp = []  # 时间戳转换
mortgage_people_info_translate = {}  # key:value  字段名：转换函数
sql_mortgage_people_info = """CREATE TABLE IF NOT EXISTS `mortgage_people_info` (
`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`base_info_id` bigint UNSIGNED NOT NULL comment "动产抵押mortgage_base_info表中的id",
`licese_type` varchar(255) comment "抵押权人证照/证件类型",
`people_name` varchar(255) comment "抵押权人名称",
`license_num` varchar(30) comment "证照/证件号码",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
FOREIGN KEY(base_info_id) REFERENCES mortgage_base_info(id)
) COMMENT="动产抵押-抵押权人信息";
"""
mortgage_pawn_info_columns = ['id']
mortgage_pawn_info_json = []  # json转成str
mortgage_pawn_info_modify = {'id': 'base_info_id'}  # 修改的 key:value  源字段名：目标字段名
mortgage_pawn_info_extract = ["baseInfo:id", "pawnInfoList[]"]  # 需要从list的下一级提取出来的
mortgage_pawn_info_timestamp = []  # 时间戳转换
mortgage_pawn_info_translate = {}  # key:value  字段名：转换函数
sql_mortgage_pawn_info = """CREATE TABLE IF NOT EXISTS `mortgage_pawn_info` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`base_info_id` bigint UNSIGNED NOT NULL comment "动产抵押mortgage_base_info表中的id",
`pawn_name` varchar(255) comment "名称",
`ownership` varchar(100) comment "所有权归属",
`remark` varchar(200) comment "备注",
`detail` varchar(5000) comment "数量、质量、状况、所在地等情况",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
FOREIGN KEY(base_info_id) REFERENCES mortgage_base_info(id)
) COMMENT="动产抵押-抵押物信息";
"""
mortgage_change_info_columns = ['id']
mortgage_change_info_json = []  # json转成str
mortgage_change_info_modify = {'id': 'base_info_id'}  # 修改的 key:value  源字段名：目标字段名
mortgage_change_info_extract = ["baseInfo:id", "changeInfoList[]"]  # 需要从list的下一级提取出来的
mortgage_change_info_timestamp = ['changeDate']  # 时间戳转换
mortgage_change_info_translate = {}  # key:value  字段名：转换函数
sql_mortgage_change_info = """CREATE TABLE IF NOT EXISTS `mortgage_change_info` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`base_info_id` bigint UNSIGNED NOT NULL comment "动产抵押mortgage_base_info表中的id",
`change_content` varchar(2000) comment "变更内容",
`change_date` timestamp comment "变更日期",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
FOREIGN KEY(base_info_id) REFERENCES mortgage_base_info(id)
) COMMENT="动产抵押-变更信息";
"""

# 公司发展-融资历史
financing_process_columns = ["company_id", "companyName", "date", "pubTime", "investorName", "money", "newsTitle",
                             "newsUrl", "round", "share", "value"]
financing_process_json = []  # json转成str
financing_process_modify = {}  # 修改的 key:value  源字段名：目标字段名
financing_process_extract = []  # 需要从list的下一级提取出来的
financing_process_timestamp = ["date", "pubTime"]  # 时间戳转换
financing_process_translate = {}  # key:value  字段名：转换函数
sql_financing_process = f"""CREATE TABLE IF NOT EXISTS `financing_process` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT {company_category} comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`company_name` varchar(255) comment "公司名",
`date` timestamp comment "融资时间",
`pub_time` timestamp comment "披露时间",
`investor_name` varchar(512) comment "投资企业",
`money` varchar(64) comment "金额",
`news_title` varchar(255) comment "新闻标题",
`news_url` varchar(512) comment "新闻url",
`round` varchar(32) comment "轮次",
`share` varchar(64) comment "投资比例",
`value` varchar(64) comment "估值",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="融资历史";
"""

# 经营状况-一般纳税人
taxpayer_columns = ["company_id", "taxpayerQualificationType", "endDate", "name", "logo", "alias",
                    "taxpayerIdentificationNumber", "startDate"]
taxpayer_json = []  # json转成str
taxpayer_modify = {}  # 修改的 key:value  源字段名：目标字段名
taxpayer_extract = []  # 需要从list的下一级提取出来的
taxpayer_timestamp = []  # 时间戳转换
taxpayer_translate = {}  # key:value  字段名：转换函数
sql_taxpayer = f"""CREATE TABLE IF NOT EXISTS `taxpayer` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT {company_category} comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`taxpayer_qualification_type` varchar(50) comment "证书编号",
`end_date` DATE comment "结束日期",
`name` varchar(250) comment "公司名",
`logo` varchar(150) comment "公司logo",
`alias` varchar(50) comment "公司简称",
`taxpayer_identification_number` varchar(50) comment "纳税人识别号",
`start_date` DATE comment "开始时间",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="一般纳税人";
"""

# 经营状况-资质证书
certificate_columns = ["company_id", "certNo", "id", "certificateName", "startDate", "endDate", "detail"]
certificate_json = ['detail']  # json转成str
certificate_modify = {"id": "uuid"}  # 修改的 key:value  源字段名：目标字段名
certificate_extract = []  # 需要从list的下一级提取出来的
certificate_timestamp = []  # 时间戳转换
certificate_translate = {}  # key:value  字段名：转换函数
sql_certificate = f"""CREATE TABLE IF NOT EXISTS `certificate` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT {company_category} comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`cert_no` varchar(255) comment "证书编号",
`uuid` varchar(25) comment "uuid",
`certificate_name` varchar(255) comment "证书类型",
`start_date` DATE comment "发证日期",
`end_date` DATE comment "截止日期",
`detail` varchar(13000) comment "详细信息",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="资质证书";
"""

# 知识产权-企业专利信息
patents_columns = ["company_id", 'mainCatNum', 'createTime', 'pubnumber', 'appnumber', 'id', 'lawStatus', 'title',
                   'patentName', 'grantNumber', 'grantDate', 'priorityInfo', 'postCode', 'applicationTime',
                   'applicantname', 'patentType', 'pubDate', 'agency', 'uni', 'inventor', 'cat', 'agent',
                   'applicationPublishTime', 'patentNum', 'imgUrl', 'allCatNum', 'abstracts', 'address', 'uuid',
                   'patentStatus']
patents_json = ['lawStatus', 'priorityInfo']  # json转成str
patents_modify = {
    "id": "corr_id",
    "pubnumber": "pubNumber",
    "appnumber": "appNumber",
    "applicantname": "applicantName",
}  # 修改的 key:value  源字段名：目标字段名
patents_extract = []  # 需要从list的下一级提取出来的
patents_timestamp = ['createTime']  # 时间戳转换 remove_date
patents_translate = {}  # key:value  字段名：转换函数
sql_patents = f"""CREATE TABLE IF NOT EXISTS `patents` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT {company_category} comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`main_cat_num` varchar(255) comment "主分类号",
`create_time` TIMESTAMP comment "创建时间",
`pub_number` varchar(20) comment "申请公布号",
`app_number` varchar(20) comment "申请号",
`corr_id` varchar(50) comment "对应表id",
`law_status` varchar(5000) comment "法律状态",
`title` varchar(500) comment "名称",
`patent_name` varchar(500) comment "专利名称",
`grant_number` varchar(255) comment "授权公告号",
`grant_date` DATE comment "授权公告日",
`priority_info` VARCHAR(3000) comment "优先权信息",
`post_code` varchar(255) comment "邮编",
`application_time` DATE comment "申请日",
`applicant_name` varchar(350) comment "申请人",
`patent_type` varchar(100) comment "专利类型",
`pub_date` DATE comment "公开公告日",
`agency` varchar(255) comment "代理机构",
`uni` varchar(255) comment "唯一标识符",
`inventor` varchar(300) comment "发明人",
`cat` varchar(255) comment "分类",
`agent` varchar(1000) comment "代理人",
`application_publish_time` DATE comment "申请公布日",
`patent_num` varchar(20) comment "申请号/专利号",
`img_url` text comment "图片url",
`all_cat_num` varchar(1000) comment "全部分类号",
`abstracts` TEXT comment "摘要",
`address` varchar(500) comment "地址",
`uuid` varchar(255) comment "唯一标识符",
`patent_status` varchar(255) comment "专利状态",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="企业专利信息";"""

# 行政许可 administrative_licensing
administrative_licensing_columns = ["company_id", 'decisionDate', 'endDate', 'licenseNumber', 'licenceName',
                                    'licenceDepartment',
                                    'licenceContent', 'source', 'auditType', 'legalPersonName', 'areaCode',
                                    'dataUpdateTime']
administrative_licensing_json = []  # json转成str
administrative_licensing_modify = {}  # 修改的 key:value  源字段名：目标字段名
administrative_licensing_extract = []  # 需要从list的下一级提取出来的
administrative_licensing_timestamp = ['decisionDate']  # 时间戳转换
administrative_licensing_translate = {}  # key:value  字段名：转换函数
sql_administrative_licensing = f"""CREATE TABLE IF NOT EXISTS `administrative_licensing` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT {company_category} comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`decision_date` date comment "决定日期/有效期自",
`end_date` date comment "截止日期/有效期至",
`license_number` varchar(255) comment "许可文件编号/文书号",
`licence_name` varchar(255) comment "许可文件名称",
`licence_department` varchar(500) comment "决定许可机关",
`licence_content` varchar(5000) comment "许可内容",
`source` varchar(255) comment "数据来源",
`audit_type` varchar(255) comment "审核类型（source=信用中国时返回数据）",
`legal_person_name` varchar(255) comment "法定代表人（source=信用中国时返回数据）",
`area_code` varchar(255) comment "地方编码（source=信用中国时返回数据）",
`data_update_time` varchar(255) comment "数据更新时间（source=信用中国时返回数据）",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="行政许可";"""
# 税务评级 tax_credit
tax_credit_columns = ["company_id", 'grade', 'year', 'evalDepartment', 'type', 'idNumber', 'name']
tax_credit_json = []  # json转成str
tax_credit_modify = {}  # 修改的 key:value  源字段名：目标字段名
tax_credit_extract = []  # 需要从list的下一级提取出来的
tax_credit_timestamp = []  # 时间戳转换
tax_credit_translate = {}  # key:value  字段名：转换函数
sql_tax_credit = f"""CREATE TABLE IF NOT EXISTS `tax_credit` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT {company_category} comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`grade` varchar(10) comment "纳税等级",
`year` varchar(10) comment "年份",
`eval_department` varchar(100) comment "评价单位",
`type` varchar(6) comment "类型",
`id_number` varchar(50) comment "纳税人识别号",
`name` varchar(255) comment "纳税人名称",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="税务评级";"""
# 企业招投标信息 bidding_information
bidding_information_columns = ["company_id", 'purchaser', 'publishTime', 'link', 'bidUrl', 'content', 'id', 'title',
                               'proxy', 'uuid', 'type', 'province', 'bidWinner', 'bidAmount']
bidding_information_json = []  # json转成str
bidding_information_modify = {"id": "corr_id"}
bidding_information_extract = []  # 需要从list的下一级提取出来的
bidding_information_timestamp = ['publishTime']  # 时间戳转换
bidding_information_translate = {}  # key:value  字段名：转换函数
sql_bidding_information = f"""CREATE TABLE IF NOT EXISTS `bidding_information` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT {company_category} comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`purchaser` varchar(2000) comment "采购人",
`publish_time` TIMESTAMP comment "发布时间",
`link` varchar(128) comment "详细信息链接",
`bid_url` varchar(128) comment "天眼查链接",
`content` longtext comment "正文信息",
`corr_id` bigint(20) comment "id",
`title` varchar(256) comment "标题",
`proxy` varchar(256) comment "代理机构",
`uuid` varchar(50) comment "uuid",
`type` varchar(50) comment "公告类型",
`province` varchar(50) comment "省份地区",
`bid_winner` text comment "供应商",
`bid_amount` varchar(1050) comment "中标金额",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="企业招投标信息";"""
# 供应商 supply
supply_columns = ["company_id", 'supplier_graphId', 'announcement_date', 'amt', 'logo', 'alias', 'supplier_name',
                  'relationship',
                  'dataSource', 'ratio']
supply_json = []  # json转成str
supply_modify = {}
supply_extract = []  # 需要从list的下一级提取出来的
supply_timestamp = ['announcement_date']  # 时间戳转换
supply_translate = {'ratio': translate_percent}  # key:value  字段名：转换函数
sql_supply = f"""CREATE TABLE IF NOT EXISTS `supply` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT {company_category} comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`supplier_graph_id` bigint(20) comment "供应商id",
`announcement_date` TIMESTAMP comment "报告期",
`amt` decimal(24,4) comment "采购金额（万元）",
`logo` varchar(150) comment "logo",
`alias` varchar(255) comment "简称",
`supplier_name` varchar(200) comment "供应商名称",
`relationship` varchar(200) comment "关联关系",
`data_source` varchar(50) comment "数据来源",
`ratio` decimal(24,4) comment "采购占比",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="供应商";"""
# 新闻舆情 news
news_columns = ["company_id", 'website', 'abstracts', 'docid', 'rtm', 'title', 'uri', 'tags', 'emotion']
news_json = ['tags']  # json转成str
news_modify = {}
news_extract = []  # 需要从list的下一级提取出来的
news_timestamp = ['rtm']  # 时间戳转换
news_translate = {}  # key:value  字段名：转换函数
sql_news = f"""CREATE TABLE IF NOT EXISTS `news` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT {company_category} comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`website` varchar(50) comment "数据来源",
`abstracts` varchar(500) comment "简介",
`docid` varchar(255) comment "新闻唯一标识符",
`rtm` TIMESTAMP comment "发布时间",
`title` varchar(6300) comment "标题",
`uri` varchar(550) comment "新闻url",
`tags` varchar(2000) comment "标签",
`emotion` int(11) comment "情感分类（1-正面，0-中性，-1-负面）",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="新闻舆情" ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"""
# 核心团队 core_team
core_team_columns = ["company_id", 'companyName', 'desc', 'graphId', 'hid', 'icon', 'iconOssPath', 'isDimission',
                     'name', 'title']
core_team_json = []  # json转成str
core_team_modify = {}
core_team_extract = []  # 需要从list的下一级提取出来的
core_team_timestamp = []  # 时间戳转换
core_team_translate = {}  # key:value  字段名：转换函数
sql_core_team = f"""CREATE TABLE IF NOT EXISTS `core_team` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT {company_category} comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`company_name` varchar(255) comment "公司名",
`desc` text comment "描述",
`graph_id` bigint(20) comment "公司id",
`hid` bigint(20) comment "人id",
`icon` varchar(512) comment "logo",
`icon_oss_path` varchar(256) comment "logo存放位置",
`is_dimission` int(11) comment "0-现有成员 1-过往成员",
`name` varchar(128) comment "姓名",
`title` varchar(256) comment "标签",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="核心团队";"""
# 企业业务 corporate_business
corporate_business_columns = ["company_id", 'companyName', 'graphId', 'round', 'hangye', 'logo', 'logoOssPath',
                              'product', 'setupDate', 'yewu']
corporate_business_json = []  # json转成str
corporate_business_modify = {}
corporate_business_extract = []  # 需要从list的下一级提取出来的
corporate_business_timestamp = ['setupDate']  # 时间戳转换
corporate_business_translate = {}  # key:value  字段名：转换函数
sql_corporate_business = f"""CREATE TABLE IF NOT EXISTS `corporate_business` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT {company_category} comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`company_name` varchar(255) comment "公司名",
`graph_id` bigint(20) comment "公司id",
`round` varchar(128) comment "融资轮次",
`hangye` varchar(128) comment "行业",
`logo` varchar(512) comment "logo",
`logo_oss_path` varchar(256) comment "logo存放位置",
`product` varchar(256) comment "产品名",
`setup_date` date comment "成立时间",
`yewu` varchar(256) comment "业务范围",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="企业业务";"""
# 竞品信息 competitor_information
competitor_information_columns = ["company_id", 'companyName', 'date', 'graphId', 'hangye', 'icon', 'iconOssPath',
                                  'jingpinProduct', 'location', 'product',
                                  'round', 'setupDate', 'value', 'yewu']
competitor_information_json = []  # json转成str
competitor_information_modify = {}
competitor_information_extract = []  # 需要从list的下一级提取出来的
competitor_information_timestamp = ['date', 'setupDate']  # 时间戳转换
competitor_information_translate = {}  # key:value  字段名：转换函数
sql_competitor_information = f"""CREATE TABLE IF NOT EXISTS `competitor_information` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT {company_category} comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`company_name` varchar(255) comment "公司名",
`date` date comment "时间",
`graph_id` bigint(20) comment "公司id",
`hangye` varchar(128) comment "行业",
`icon` varchar(512) comment "logo",
`icon_oss_path` varchar(150) comment "logo存放位置",
`jingpin_product` varchar(255) comment "竞品名",
`location` varchar(100) comment "地区",
`product` varchar(255) comment "产品",
`round` varchar(32) comment "当前轮次",
`setup_date` date comment "投资时间",
`value` varchar(64) comment "估值",
`yewu` varchar(256) comment "业务范围",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="竞品信息";"""
# 股权出质 equity_pledge
equity_pledge_columns = ["company_id", 'pledgeeList', 'companyList', 'pledgorList', 'regDate', 'pledgor',
                         'certifNumberR', 'pledgee', 'regNumber', 'certifNumber', 'equityAmount', 'id', 'state',
                         'putDate']
equity_pledge_json = ['pledgeeList', 'companyList', 'pledgorList']  # json转成str
equity_pledge_modify = {"id": "equity_info_id"
                        }  # 修改的 key:value  源字段名：目标字段名
equity_pledge_extract = ['targetCompany__name', 'targetCompany__id']  # 需要从list的下一级提取出来的
equity_pledge_timestamp = ['regDate', 'putDate']  # 时间戳转换 remove_date
equity_pledge_translate = {}  # key:value  字段名：转换函数
sql_equity_pledge = f"""CREATE TABLE IF NOT EXISTS `equity_pledge` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT {company_category} comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`pledgee_list` varchar(2000) comment "质权人列表",
`reg_date` TIMESTAMP comment "股权出质设立登记日期",
`pledgor` varchar(255) comment "出质人",
`certif_number_r` varchar(20) comment "质权人证照/证件号码",
`pledgee` varchar(255) comment "质权人",
`reg_number` varchar(50) comment "登记编号",
`certif_number` varchar(20) comment "出质人证照/证件号码",
`company_list` varchar(2000) comment "公司列表",
`target_company_name` varchar(255) comment "出质股权标的企业-公司名",
`target_company_id` varchar(50) comment "出质股权标的企业-公司id",
`pledgor_list` varchar(2000) comment "出质人列表",
`equity_amount` varchar(20) comment "出质股权数额",
`equity_info_id` bigint(20) comment "股权出质id",
`state` varchar(31) comment "状态",
`put_date` TIMESTAMP comment "股权出质设立发布日期",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="股权出质";"""
# 欠税公告 tax_arrears_announcement
tax_arrears_announcement_columns = ["company_id", 'taxIdNumber', 'newOwnTaxBalance', 'ownTaxAmount', 'publishDate',
                                    'ownTaxBalance', 'type', 'personIdNumber',
                                    'taxCategory', 'taxpayerType', 'personIdName', 'name', 'location', 'department',
                                    'regType', 'legalpersonName']
tax_arrears_announcement_json = []  # json转成str
tax_arrears_announcement_modify = {'legalpersonName': 'legalPersonName'}  # 修改的 key:value  源字段名：目标字段名
tax_arrears_announcement_extract = []  # 需要从list的下一级提取出来的
tax_arrears_announcement_timestamp = []  # 时间戳转换 remove_date
tax_arrears_announcement_translate = {}  # key:value  字段名：转换函数
sql_tax_arrears_announcement = f"""CREATE TABLE IF NOT EXISTS `tax_arrears_announcement` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT {company_category} comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`tax_id_number` varchar(150) comment "纳税人识别号",
`new_own_tax_balance` varchar(20) comment "当前新发生欠税余额",
`own_tax_amount` varchar(50) comment "欠税金额",
`publish_date` date comment "发布时间",
`own_tax_balance` varchar(20) comment "欠税余额",
`type` varchar(10) comment "税务类型",
`person_id_number` varchar(150) comment "证件号码",
`tax_category` varchar(255) comment "欠税税种",
`taxpayer_type` varchar(10) comment "纳税人类型",
`person_id_name` varchar(50) comment "法人证件名称",
`name` varchar(255) comment "纳税人名称",
`location` varchar(150) comment "经营地点",
`department` varchar(200) comment "税务机关",
`reg_type` varchar(50) comment "注册类型",
`legal_person_name` varchar(105) comment "法人或负责人名称",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="欠税公告" ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"""
# 司法拍卖 judicial_auction
judicial_auction_columns = ["company_id", 'scopeDate', 'targetObject', 'auctionType', 'court', 'title', 'subtime',
                            'content', 'startingPrice',
                            'evaluationPrice', 'biddingInstructionsUrl', 'itemFormUrl', 'itemAddressDetail']
judicial_auction_json = ['imgUrlList', 'fileUrlList']  # json转成str
judicial_auction_modify = {}  # 修改的 key:value  源字段名：目标字段名
judicial_auction_extract = []  # 需要从list的下一级提取出来的
judicial_auction_timestamp = ['subtime']  # 时间戳转换 remove_date
judicial_auction_translate = {}  # key:value  字段名：转换函数
sql_judicial_auction = f"""CREATE TABLE IF NOT EXISTS `judicial_auction` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT {company_category} comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`scope_date` varchar(255) comment "拍卖起止时间",
`target_object` varchar(255) comment "拍卖标的",
`auction_type` varchar(20) comment "拍卖阶段",
`court` varchar(255) comment "执行法院",
`title` varchar(2000) comment "公告标题",
`subtime` TIMESTAMP comment "公告日期",
`content` text comment "竞买公告",
`starting_price` varchar(20) comment "起拍价（元）",
`evaluation_price` varchar(20) comment "评估价（元）",
`bidding_instructions_url` varchar(200) comment "竞买须知链接",
`item_form_url` varchar(150) comment "标的物介绍链接",
`item_address_detail` varchar(100) comment "标的物位置",
`img_url_list` varchar(2000) comment "图片链接集合",
`file_url_list` varchar(2000) comment "附件链接集合",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="司法拍卖";"""

# 法律诉讼 law_suit
law_suit_columns = ["company_id", 'id', 'caseMoney', 'submitTime', 'docType', 'lawsuitUrl', 'lawsuitH5Url', 'uuid',
                    'title', 'court', 'judgeTime', 'caseNo', 'caseType', 'caseReason', 'casePersons']
law_suit_json = ['casePersons']  # json转成str
law_suit_modify = {"id": "corr_id"}  # 修改的 key:value  源字段名：目标字段名
law_suit_extract = []  # 需要从list的下一级提取出来的
law_suit_timestamp = ['submitTime']  # 时间戳转换 remove_date
law_suit_translate = {}  # key:value  字段名：转换函数
sql_law_suit = f"""CREATE TABLE IF NOT EXISTS `law_suit` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT {company_category} comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`corr_id` bigint(20) comment "对应表id",
`case_money` varchar(100) comment "案件金额",
`submit_time` TIMESTAMP comment "发布日期",
`doc_type` varchar(1000) comment "文书类型",
`lawsuit_url` varchar(150) comment "天眼查url（Web）",
`lawsuit_h5_url` varchar(150) comment "天眼查url（H5）",
`uuid` varchar(50) comment "uuid",
`title` varchar(2000) comment "案件名称",
`court` varchar(100) comment "审理法院",
`judge_time` date comment "裁判日期",
`case_no` varchar(1000) comment "案号",
`case_type` varchar(50) comment "案件类型",
`case_reason` varchar(500) comment "案由",
`case_persons` text comment "涉案方",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="法律诉讼";"""
# 司法协助 judicial_assistance
judicial_assistance_columns = ["company_id", 'id', 'equityAmount', 'typeState', 'executedPersonHid', 'executiveCourt',
                               'executedPerson', 'executeNoticeNum', 'executedPersonCid', 'assId', 'executedPersonType',
                               'publicityDate', 'stockExecutedCompany', 'stockExecutedCid']
judicial_assistance_json = []  # json转成str
judicial_assistance_modify = {"id": "corr_id"}  # 修改的 key:value  源字段名：目标字段名
judicial_assistance_extract = []  # 需要从list的下一级提取出来的
judicial_assistance_timestamp = []  # 时间戳转换 remove_date
judicial_assistance_translate = {}  # key:value  字段名：转换函数
sql_judicial_assistance = f"""CREATE TABLE IF NOT EXISTS `judicial_assistance` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT {company_category} comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`corr_id` bigint comment "对应表id",
`equity_amount` varchar(50) comment "股权数额",
`type_state` varchar(50) comment "类型状态",
`executed_person_hid` bigint comment "被执行人hgid",
`executive_court` varchar(100) comment "执行法院",
`executed_person` varchar(50) comment "被执行人",
`execute_notice_num` varchar(200) comment "执行通知书文号",
`executed_person_cid` bigint comment "执行人公司id",
`ass_id` varchar(100) comment "司法协助基本信息id",
`executed_person_type` varchar(50) comment "执行人类型，2-人,1-公司",
`publicity_date` TIMESTAMP comment "公示日期",
`stock_executed_company` varchar(255) comment "股权被执行的企业",
`stock_executed_cid` bigint(20) comment "股权被执行的企业id",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="司法协助";"""
# 企业招聘 enterprise_recruitment
enterprise_recruitment_columns = ["company_id", 'education', 'city', 'companyName', 'source', 'title',
                                  'experience', 'startDate', 'companyGid', 'salary', 'webInfoPath']
enterprise_recruitment_json = []  # json转成str
enterprise_recruitment_modify = {}  # 修改的 key:value  源字段名：目标字段名
enterprise_recruitment_extract = []  # 需要从list的下一级提取出来的
enterprise_recruitment_timestamp = ["startDate"]  # 时间戳转换 remove_date
enterprise_recruitment_translate = {}  # key:value  字段名：转换函数
sql_enterprise_recruitment = f"""CREATE TABLE IF NOT EXISTS `enterprise_recruitment` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT {company_category} comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`education` varchar(60) comment "学历",
`city` varchar(30) comment "地区",
`company_name` varchar(100) comment "公司名称",
`source` varchar(50) comment "招聘信息来源",
`title` varchar(100) comment "招聘职位",
`experience` varchar(60) comment "工作经验",
`start_date` timestamp comment "发布日期",
`company_gid` varchar(10) comment "公司id",
`salary` varchar(50) comment "薪资",
`web_info_path` varchar(500) comment "招聘信息地址url",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="企业招聘";"""

# 利润表 profit
profit_columns = ["company_id", 'total_compre_income_atsopc', 'profit_deduct_nrgal_ly_sq', 'showYear',
                  'financing_expenses', 'revenue', 'profit_total_amt', 'operating_costs', 'sales_fee', 'manage_fee',
                  'op', 'asset_impairment_loss', 'total_compre_income', 'invest_income', 'rad_cost',
                  'operating_taxes_and_surcharge', 'basic_eps', 'income_tax_expenses', 'total_revenue', 'net_profit',
                  'net_profit_atsopc', 'invest_incomes_from_rr', 'operating_cost', 'non_operating_income',
                  'othr_income', 'non_operating_payout', 'income_from_chg_in_fv', 'minority_gal',
                  'dlt_earnings_per_share', 'othr_compre_income', 'othr_compre_income_atoopc',
                  'othr_compre_income_atms', 'total_compre_income_atms']
profit_json = []  # json转成str
profit_modify = {}  # 修改的 key:value  源字段名：目标字段名
profit_extract = []  # 需要从list的下一级提取出来的
profit_timestamp = []  # 时间戳转换 remove_date
profit_translate = {}  # key:value  字段名：转换函数
sql_profit = f"""CREATE TABLE IF NOT EXISTS `profit` (`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT {company_category} comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`total_compre_income_atsopc` varchar(32) comment '归属于母公司所有者的综合收益总额',
`profit_deduct_nrgal_ly_sq` varchar(32) comment '扣除非经常性损益后的净利润',
`show_year` varchar(32) comment '年度',
`financing_expenses` varchar(32) comment '财务费用',
`revenue` varchar(32) comment '营业收入',
`profit_total_amt` varchar(32) comment '利润总额',
`operating_costs` varchar(32) comment '营业总成本',
`sales_fee` varchar(32) comment '销售费用',
`manage_fee` varchar(32) comment '管理费用',
`op` varchar(32) comment '营业利润',
`asset_impairment_loss` varchar(32) comment '资产减值损失',
`total_compre_income` varchar(32) comment '综合收益总额',
`invest_income` varchar(32) comment '加:投资收益',
`rad_cost` varchar(32) comment '研发费用',
`operating_taxes_and_surcharge` varchar(32) comment '营业税金及附加',
`basic_eps` varchar(32) comment '基本每股收益',
`income_tax_expenses` varchar(32) comment '减:所得税费用',
`total_revenue` varchar(32) comment '营业总收入',
`net_profit` varchar(32) comment '净利润',
`net_profit_atsopc` varchar(32) comment '其中:归属于母公司股东的净利润',
`invest_incomes_from_rr` varchar(32) comment '其中:对联营企业和合营企业的投资收益',
`operating_cost` varchar(32) comment '营业成本',
`non_operating_income` varchar(32) comment '加:营业外收入',
`othr_income` varchar(32) comment '其他经营收益',
`non_operating_payout` varchar(32) comment '减:营业外支出',
`income_from_chg_in_fv` varchar(32) comment '加:公允价值变动收益',
`minority_gal` varchar(32) comment '少数股东损益',
`dlt_earnings_per_share` varchar(32) comment '稀释每股收益',
`othr_compre_income` varchar(64) comment '其他综合收益',
`othr_compre_income_atoopc` varchar(64) comment '归属于母公司股东的其他综合收益',
`othr_compre_income_atms` varchar(64) comment '归属于少数股东的其他综合收益',
`total_compre_income_atms` varchar(32) comment '归属于少数股东的综合收益总额',
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="利润表";"""

sql_legal_proceedings = """CREATE TABLE IF NOT EXISTS `legal_proceedings` (
`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT 3 comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`doc_type` varchar(1000) comment "文书类型",
`lawsuit_url` varchar(150) comment "天眼查url（Web）",
`lawsuit_h5_url` varchar(150) comment "天眼查url（H5）",
`title` varchar(2000) comment "案件名称",
`court` varchar(100) comment "审理法院",
`judge_time` DATE comment "裁判日期",
`uuid` varchar(50) comment "uuid",
`case_no` varchar(1000) comment "案号",
`case_type` varchar(50) comment "案件类型",
`case_reason` varchar(500) comment "案由",
`case_persons` text comment "涉案方",
`case_status` varchar(50) comment "在本案中身份",
`case_result` varchar(5000) comment "裁判结果",
`case_money` double comment "案件金额",
`submit_time` TIMESTAMP comment "发布日期",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="法律诉讼";
"""

sql_legal_proceedings_detail = """CREATE TABLE IF NOT EXISTS `legal_proceedings_detail` (
`id` bigint UNSIGNED AUTO_INCREMENT primary key comment "自增id",
`company_category` tinyint NOT NULL DEFAULT 3 comment "公司类别",
`company_id` BIGINT ( 0 ) NOT NULL comment "公司id",
`judge_date` DATE comment "裁判日期",
`judge_result` text comment "本案裁判结果",
`title` varchar(255) comment "标题",
`caseno` varchar(255) comment "案号",
`uuid` varchar(255) comment "uuid",
`court_consider` text comment "本院认为",
`companies` varchar(2000) comment "相关公司",
`plaintiff_request` text comment "原告诉称",
`court_inspect` text comment "本院查明",
`trial_procedure` text comment "审理经过",
`law_firms` varchar(2000) comment "相关律所",
`plaintiff_request_of_first` text comment "一审原告诉称",
`defendant_reply_of_first` text comment "一审被告辩称",
`trial_person` varchar(2000) comment "审判人员",
`plaintext` text comment "诉讼正文",
`appellor` text comment "当事人信息",
`court` varchar(255) comment "法院",
`url` varchar(255) comment "源路径",
`court_consider_of_first` text comment "一审法院认为",
`doctype` varchar(255) comment "文书类型",
`trial_assist_person` text comment "审判辅助人员",
`casetype` varchar(255) comment "案件类型",
`appellant_request` text comment "上诉人诉称",
`defendant_reply` text comment "被告辩称",
`court_inspect_of_first` text comment "一审法院查明",
`appellee_arguing` text comment "被上诉人辩称",
`insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP  comment "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` )) COMMENT="法律诉讼详情";
"""
