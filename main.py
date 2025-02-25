import os
import pymysql
import pandas as pd

# 项目名称
# PROJECT_NAME = "project_incopat_automatic_update"
PROJECT_NAME = "version2"

# 正在更新的公司名单
DOWNLOADING_LIST = []


# 项目根目录
BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), PROJECT_NAME)

# 数据库链接相关
MYSQL_HOST = '127.0.0.1'
MYSQL_DB = "tyc_api_model"
MYSQL_PASSWORD = 'Qwer1234'

# 天眼查的token
TOKEN = ""

# incopat用户信息
USER_DICT = {
    "Nottingham_Icopat": "",
    "Nottingham_Icopat": "",
    "Nottingham_Icopat": "",
}
USERNAME = ""
PASSWORD = ""

# 工具目录
TOOLS_DIR = os.path.join(BASE_DIR, "tools")

# driver地址
DRIVER_PATH = os.path.join(TOOLS_DIR, "chromedriver.exe")

# 公司名单excel文件目录
COMPANY_EXCEL_PATH = os.path.join(TOOLS_DIR, "宁波公司基本信息.xlsx")

# 公司名单txt文件目录
COMPANY_TXT_DIR = os.path.join(TOOLS_DIR, "company_txt")
if not os.path.exists(COMPANY_TXT_DIR):
    os.mkdir(COMPANY_TXT_DIR)

# 读取incopat字段中英文转换关系表
df_ = pd.read_excel(os.path.join(TOOLS_DIR, "incopat字段转换.xlsx"))
INCOPAT_CH_EN_DICT = df_.set_index(["title"])["name"].to_dict()
INCOPAT_EN_CH_DICT = df_.set_index(["name"])["title"].to_dict()

# 数据库incopat表字段
INCOPAT_COLUMNS_LIST = ["patent_title", "abstract", "applicant", "publication_number", "publication_date",
                        "application_number", "application_date", "patent_type", "publication_authority",
                        "title_translation", "abstract_translation", "claim_number", "patent_page",
                        "technical_effect_sentence", "technical_effect_phrase", "technical_effect_1",
                        "technical_effect_2", "technical_effect_3", "technical_effect_triz", "ipc_main", "ipc",
                        "locarno_classification", "applicant_translation", "current_patentee", "applicant_first",
                        "applicant_number", "applicant_type", "inventor", "inventor_first", "inventor_number", "agency",
                        "attorney", "family_main", "family_complete", "family_docdb", "family_main_id",
                        "family_complete_id", "family_docdb_id", "family_main_number", "family_complete_number",
                        "family_docdb_number", "family_country", "patent_status", "legal_status", "company_id"]

# incopat文件目录
INCOPAT_DIR = os.path.join(BASE_DIR, "incopat_file")
if not os.path.exists(INCOPAT_DIR):
    os.mkdir(INCOPAT_DIR)

# incopat临时文件目录
INCOPAT_TEMPORARY_DIR = os.path.join(INCOPAT_DIR, "temporary")
if not os.path.exists(INCOPAT_TEMPORARY_DIR):
    os.mkdir(INCOPAT_TEMPORARY_DIR)

# 天眼查报错txt文件目录
TIANYANCHA_ERROR_PATH = os.path.join(BASE_DIR, "request_error.txt")

# 天眼查文件目录
TIANYANCHA_DIR = os.path.join(BASE_DIR, "tianyancha_file")
if not os.path.exists(TIANYANCHA_DIR):
    os.mkdir(TIANYANCHA_DIR)

# 天眼查文件目录
TIANYANCHA_TEMPORARY_DIR = os.path.join(TIANYANCHA_DIR, "temporary")
if not os.path.exists(TIANYANCHA_TEMPORARY_DIR):
    os.mkdir(TIANYANCHA_TEMPORARY_DIR)

# 模型文件目录
MODEL_DIR = os.path.join(BASE_DIR, "model_file")
if not os.path.exists(MODEL_DIR):
    os.mkdir(MODEL_DIR)

INCOPAT_TABLE_SQL = """CREATE TABLE `incopat` (
`id` BIGINT ( 0 ) NOT NULL AUTO_INCREMENT COMMENT "序号",
PRIMARY KEY ( `id` ),
`patent_title` VARCHAR ( 155 ) COMMENT "标题",
`abstract` VARCHAR ( 1820 ) COMMENT "摘要",
`applicant` VARCHAR ( 172 ) COMMENT "申请人",
`publication_number` VARCHAR ( 63 ) COMMENT "公开（公告）号",
`publication_date` date COMMENT "公开（公告）日",
`application_number` VARCHAR ( 66 ) COMMENT "申请号",
`application_date` date COMMENT "申请日",
`patent_type` VARCHAR ( 54 ) COMMENT "专利类型",
`publication_authority` VARCHAR ( 52 ) COMMENT "公开国别",
`title_translation` VARCHAR ( 339 ) COMMENT "标题（翻译）",
`abstract_translation` VARCHAR ( 7133 ) COMMENT "摘要（翻译）",
`claim_number` DECIMAL ( 18, 4 ) COMMENT "权利要求数量",
`patent_page` DECIMAL ( 18, 4 ) COMMENT "文献页数",
`technical_effect_sentence` VARCHAR ( 1971 ) COMMENT "技术功效句",
`technical_effect_phrase` VARCHAR ( 506 ) COMMENT "技术功效短语",
`technical_effect_1` VARCHAR ( 232 ) COMMENT "技术功效1级",
`technical_effect_2` VARCHAR ( 332 ) COMMENT "技术功效2级",
`technical_effect_3` VARCHAR ( 520 ) COMMENT "技术功效3级",
`technical_effect_triz` VARCHAR ( 178 ) COMMENT "技术功效TRIZ参数",
`ipc_main` VARCHAR ( 62 ) COMMENT "IPC主分类",
`ipc` VARCHAR ( 500 ) COMMENT "IPC",
`locarno_classification` VARCHAR ( 125 ) COMMENT "洛迦诺分类号",
`applicant_translation` VARCHAR ( 354 ) COMMENT "申请人(翻译)",
`current_patentee` VARCHAR ( 141 ) COMMENT "当前权利人",
`applicant_first` VARCHAR ( 73 ) COMMENT "第一申请人",
`applicant_number` INT ( 0 ) COMMENT "申请人数量",
`applicant_type` VARCHAR ( 66 ) COMMENT "申请人类型",
`inventor` VARCHAR ( 230 ) COMMENT "发明人",
`inventor_first` VARCHAR ( 61 ) COMMENT "第一发明人",
`inventor_number` INT ( 0 ) COMMENT "发明人数量",
`agency` VARCHAR ( 100 ) COMMENT "代理机构",
`attorney` VARCHAR ( 100 ) COMMENT "代理人",
`family_main` VARCHAR ( 665 ) COMMENT "简单同族",
`family_complete` TEXT COMMENT "扩展同族",
`family_docdb` VARCHAR ( 616 ) COMMENT "DocDB同族",
`family_main_id` VARCHAR ( 68 ) COMMENT "简单同族ID",
`family_complete_id` VARCHAR ( 70 ) COMMENT "扩展同族ID",
`family_docdb_id` VARCHAR ( 68 ) COMMENT "DocDB同族ID",
`family_main_number` INT ( 0 ) COMMENT "简单同族个数",
`family_complete_number` INT ( 0 ) COMMENT "扩展同族个数",
`family_docdb_number` INT ( 0 ) COMMENT "DocDB同族个数",
`family_country` VARCHAR ( 164 ) COMMENT "同族国家",
`patent_status` VARCHAR ( 53 ) COMMENT "专利有效性",
`legal_status` VARCHAR ( 3795 ) COMMENT "法律状态",
`company_id` BIGINT ( 0 ) NOT NULL COMMENT "法律状态",
`insert_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` ) USING BTREE,
INDEX `patent_type` ( `patent_type` ) USING BTREE 
) DEFAULT charset = utf8 COMMENT = "incopat专利信息";"""
INCOPAT_ALL_TABLE_SQL = """CREATE TABLE `incopat_all` (
`index` BIGINT ( 0 ) NOT NULL AUTO_INCREMENT COMMENT "序号",
PRIMARY KEY ( `index` ),
`patent_title` text COMMENT '标题',
`abstract` text COMMENT '摘要',
`publication_number` text COMMENT '公开（公告）号',
`publication_date` datetime ( 0 ) NULL DEFAULT NULL COMMENT '公开（公告）日',
`application_number` text COMMENT '申请号',
`application_date` datetime ( 0 ) NULL DEFAULT NULL COMMENT '申请日',
`patent_type` text COMMENT '专利类型',
`publication_authority` text COMMENT '公开国别',
`link_incopat` text COMMENT '链接到incoPat',
`title_translation` text COMMENT '标题（翻译）',
`title_other_language` text COMMENT '标题（小语种原文）',
`abstract_translation` text COMMENT '摘要（翻译）',
`abstract_other_language` text COMMENT '摘要（小语种原文）',
`claim_first` text COMMENT '首项权利要求',
`independent_claims` text COMMENT '独立权利要求',
`claim_number` DOUBLE NULL DEFAULT NULL COMMENT '权利要求数量',
`independent_claims_number` DOUBLE NULL DEFAULT NULL COMMENT '独立权利要求数量',
`dependentclaim_number` DOUBLE NULL DEFAULT NULL COMMENT '从属权利要求数量',
`patent_page` DOUBLE NULL DEFAULT NULL COMMENT '文献页数',
`claim_count_first` DOUBLE NULL DEFAULT NULL COMMENT '首权字数',
`technical_effect_sentence` text COMMENT '技术功效句',
`technical_effect_phrase` text COMMENT '技术功效短语',
`technical_effect_1` text COMMENT '技术功效1级',
`technical_effect_2` text COMMENT '技术功效2级',
`technical_effect_3` text COMMENT '技术功效3级',
`technical_effect_triz` text COMMENT '技术功效TRIZ参数',
`ipc_main` text COMMENT 'IPC主分类',
`ipc` text COMMENT 'IPC',
`locarno_classification` text COMMENT '洛迦诺分类号',
`ec` text COMMENT 'EC',
`cpc` text COMMENT 'CPC',
`uc` text COMMENT 'UC',
`fi` text COMMENT 'FI',
`f_term` text COMMENT 'F-term',
`national_economy_industry_classification` text COMMENT '国民经济分类',
`emerging_industry_classification` text COMMENT '新兴产业分类',
`applicant_translation` text COMMENT '申请人(翻译)',
`applicant_original` text COMMENT '申请人(其他)',
`applicant_normalized` text COMMENT '标准化申请人',
`current_patentee_normalized` text COMMENT '标准化当前权利人',
`current_patentee` text COMMENT '当前权利人',
`applicant_first` text COMMENT '第一申请人',
`applicant_number` BIGINT ( 20 ) NULL DEFAULT NULL COMMENT '申请人数量',
`applicant_type` text COMMENT '申请人类型',
`applicant_country_code` text COMMENT '申请人国别代码',
`applicant_address` text COMMENT '申请人地址',
`applicant_address_other` text COMMENT '申请人地址(其他)',
`applicant_province_code` text COMMENT '申请人省市代码',
`applicant_city` text COMMENT '中国申请人地市',
`applicant_county` text COMMENT '中国申请人区县',
`business_dba` text COMMENT '工商别名',
`business_english_name` text COMMENT '工商英文名',
`business_address` text COMMENT '工商注册地址',
`business_company_type` text COMMENT '工商公司类型',
`business_company_establishment_time` text COMMENT '工商成立日期',
`business_uniform_social_credit_code` text COMMENT '工商统一社会信用代码',
`business_company_register_number` text COMMENT '工商注册号',
`business_company_list_code` text COMMENT '工商上市代码',
`business_company_status` text COMMENT '工商企业状态',
`inventor` text COMMENT '发明人',
`inventor_other_language` text COMMENT '发明(设计)人(其他)',
`inventor_first` text COMMENT '第一发明人',
`inventor_name` text COMMENT '当前发明人名称',
`inventor_number` BIGINT ( 20 ) NULL DEFAULT NULL COMMENT '发明人数量',
`inventor_country` text COMMENT '发明人国别',
`inventor_address` text COMMENT '发明人地址',
`inventor_address_other_language` text COMMENT '发明(设计)人地址（其他）',
`agency` text COMMENT '代理机构',
`attorney` text COMMENT '代理人',
`examiner` text COMMENT '审查员',
`citation` text COMMENT '引证专利',
`citation_forward` text COMMENT '被引证专利',
`citation_family` text COMMENT '家族引证',
`citation_family_forward` text COMMENT '家族被引证',
`citation_applicant` text COMMENT '引证申请人',
`citation_forward_applicant` text COMMENT '被引证申请人',
`citation_family_applicant` text COMMENT '家族引证申请人',
`citation_family_forward_applicant` text COMMENT '家族被引证申请人',
`citation_times` DOUBLE NULL DEFAULT NULL COMMENT '引证次数',
`citation_forward_times` DOUBLE NULL DEFAULT NULL COMMENT '被引证次数',
`citation_family_times` DOUBLE NULL DEFAULT NULL COMMENT '家族引证次数',
`citation_family_forward_times` DOUBLE NULL DEFAULT NULL COMMENT '家族被引证次数',
`citation_non_patent` text COMMENT '引证科技文献',
`citation_forward_authority` text COMMENT '被引证国别(forward)',
`citation_origin_code` text COMMENT '引证类别',
`family_main` text COMMENT '简单同族',
`family_complete` text COMMENT '扩展同族',
`family_docdb` text COMMENT 'DocDB同族',
`family_main_id` text COMMENT '简单同族ID',
`family_complete_id` text COMMENT '扩展同族ID',
`family_docdb_id` text COMMENT 'DocDB同族ID',
`family_main_number` BIGINT ( 20 ) NULL DEFAULT NULL COMMENT '简单同族个数',
`family_complete_number` BIGINT ( 20 ) NULL DEFAULT NULL COMMENT '扩展同族个数',
`family_docdb_number` BIGINT ( 20 ) NULL DEFAULT NULL COMMENT 'DocDB同族个数',
`family_country` text COMMENT '同族国家/地区',
`priority` text COMMENT '优先权信息',
`priority_number` text COMMENT '优先权号',
`priority_date` text COMMENT '优先权日',
`priority_date_earliest` text COMMENT '最早优先权日',
`priority_authority` text COMMENT '优先权国别',
`pct_application_number` text COMMENT 'PCT国际申请号',
`pct_publication_number` text COMMENT 'PCT国际公布号',
`pct_entering_national_phase` datetime ( 0 ) NULL DEFAULT NULL COMMENT 'PCT进入国家阶段日',
`application_parent` text COMMENT '母案',
`application_divisional` text COMMENT '分案',
`application_dual` text COMMENT '一案双申',
`patent_status` text COMMENT '专利有效性',
`legal_status_current` text COMMENT '当前法律状态',
`legal_status` text COMMENT '法律状态',
`legal_documents_date` text COMMENT '法律文书日期',
`legal_instrument_number` text COMMENT '法律文书编号',
`applicant_reexamination` text COMMENT '复审请求人',
`applicant_invalidation` text COMMENT '无效请求人',
`reexamination_decision` text COMMENT '复审决定',
`reexamination_invalidation_decision_date` text COMMENT '复审无效决定日',
`reexamination_invalidation_legal_basis` text COMMENT '复审无效法律依据',
`assign_times` DOUBLE NULL DEFAULT NULL COMMENT '转让次数',
`assignment_execution_date` text COMMENT '转让执行日',
`assignor` text COMMENT '转让人',
`assignee` text COMMENT '受让人',
`assignee_normalized` text COMMENT '标准受让人',
`license_times` DOUBLE NULL DEFAULT NULL COMMENT '许可次数',
`license_filing_date` text COMMENT '许可合同备案日期',
`licensor` text COMMENT '许可人',
`licensee` text COMMENT '被许可人',
`licensee_current` text COMMENT '当前被许可人',
`license_type` text COMMENT '许可类型',
`pledge_times` DOUBLE NULL DEFAULT NULL COMMENT '质押次数',
`pledge_term` text COMMENT '质押期限',
`pledgor` text COMMENT '出质人',
`pledgee` text COMMENT '质权人',
`pledgee_current` text COMMENT '当前质权人',
`litigation_times` DOUBLE NULL DEFAULT NULL COMMENT '诉讼次数',
`plaintiff` text COMMENT '原告',
`defendant` text COMMENT '被告',
`litigation_type` text COMMENT '诉讼类型',
`legal_court` text COMMENT '法庭',
`customs_record` DOUBLE NULL DEFAULT NULL COMMENT '海关备案',
`reexamination_decision_date` text COMMENT '复审决定日',
`invalidation_decision_date` text COMMENT '无效决定日',
`oral_hearing_date` text COMMENT '口审日期',
`legal_event` text COMMENT '法律事件',
`reexamination_request_date` text COMMENT '复审请求日',
`publication_date_first` datetime ( 0 ) NULL DEFAULT NULL COMMENT '首次公开日',
`grant_date` datetime ( 0 ) NULL DEFAULT NULL COMMENT '授权公告日',
`examination_substantive_date` datetime ( 0 ) NULL DEFAULT NULL COMMENT '实质审查生效日',
`examination_substantive_duration` DOUBLE NULL DEFAULT NULL COMMENT '提出实审时长',
`examination_duration` DOUBLE NULL DEFAULT NULL COMMENT '审查时长',
`expiry_date` datetime ( 0 ) NULL DEFAULT NULL COMMENT '失效日',
`patent_life` DOUBLE NULL DEFAULT NULL COMMENT '专利寿命（月）',
`standard_type` DOUBLE NULL DEFAULT NULL COMMENT '标准类型',
`standard_project` DOUBLE NULL DEFAULT NULL COMMENT '标准项目',
`standard_number` DOUBLE NULL DEFAULT NULL COMMENT '标准号',
`patent_value` BIGINT ( 20 ) NULL DEFAULT NULL COMMENT '合享价值度',
`technical_stability` BIGINT ( 20 ) NULL DEFAULT NULL COMMENT '技术稳定性',
`technical_advanced` BIGINT ( 20 ) NULL DEFAULT NULL COMMENT '技术先进性',
`protection_scope` BIGINT ( 20 ) NULL DEFAULT NULL COMMENT '保护范围',
`publication_kind` text COMMENT '文献种类代码',
`applicant` text COMMENT '申请人',
`company_id` DOUBLE NULL DEFAULT NULL COMMENT '天眼查ID',
`insert_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "插入数据时间",
`update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "更新数据时间",
INDEX `company_id` ( `company_id` ) USING BTREE 
) DEFAULT charset = utf8mb4 COMMENT = "incopat_all专利信息";"""
INNOVATION_TABLE_SQL = """CREATE TABLE `innovation_capability_score` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `company_category` TINYINT NOT NULL DEFAULT '3' COMMENT '公司类别',
  `company_id` VARCHAR(25) NOT NULL COMMENT '公司id',
  `score` FLOAT DEFAULT NULL COMMENT '创新能力分数',
  `insert_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入数据时间',
  `update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新数据时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `company_id` ( `company_id` )
) ENGINE=INNODB AUTO_INCREMENT=9593 DEFAULT CHARSET=utf8 COMMENT='创新能力分数'"""
MODEL_TABLE_SQL = """CREATE TABLE `model_predict_various_indicators` (
 `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT '自增id',
 `company_category` tinyint NOT NULL DEFAULT '3' COMMENT '公司类别',
 `company_id` bigint NOT NULL COMMENT '公司id',
 `year` int DEFAULT '2021' COMMENT '当前数据的年份',
 `web` tinyint DEFAULT NULL COMMENT '有无网址',
 `email` tinyint DEFAULT NULL COMMENT '有无邮箱',
 `economic_circle` tinyint DEFAULT NULL COMMENT '所在城市是不是在珠三角、长三角及京津冀经济圈内',
 `reg_capital` bigint DEFAULT NULL COMMENT '注册资本',
 `actual_capital` bigint DEFAULT NULL COMMENT '实缴资本',
 `built_year` int DEFAULT NULL COMMENT '成立年份',
 `company_age` float DEFAULT NULL COMMENT '公司年龄',
 `business_status` tinyint DEFAULT NULL COMMENT '经营状态',
 `company_org_type` varchar(100) DEFAULT NULL COMMENT '公司类型',
 `industry` varchar(100) DEFAULT NULL COMMENT '行业',
 `staff_num_range` varchar(100) DEFAULT NULL COMMENT '人员规模',
 `social_staff_num` int DEFAULT NULL COMMENT '参保人数',
 `business_scope` int DEFAULT NULL COMMENT '经营范围中的经营种类',
 `disclosure_key_personnel` tinyint DEFAULT NULL COMMENT '是否披露主要人员',
 `key_personnel_num` int DEFAULT NULL COMMENT '主要人员披露度（数量）',
 `top1_ratio` float DEFAULT NULL COMMENT '第一大股东持股比例',
 `top10_ratio` float DEFAULT NULL COMMENT '前十大股东持股比例',
 `standard_ratio` float DEFAULT NULL COMMENT '前十大股东股权分散度（标准差）',
 `total_invest_amount` int DEFAULT NULL COMMENT '区间对外投资总出资额',
 `invest_success_rate` float DEFAULT NULL COMMENT '区间对外投资成功率',
 `invest_all_age` float DEFAULT NULL COMMENT '存续公司总年龄',
 `branch_identify` tinyint DEFAULT NULL COMMENT '是否为分公司',
 `branch_num` int DEFAULT NULL COMMENT '存续分支机构数量加总',
 `branch_all_age` float DEFAULT NULL COMMENT '存续分支机构年龄加总',
 `recruitment_num` int DEFAULT NULL COMMENT '招聘条数',
 `recruitment_specie` int DEFAULT NULL COMMENT '不同岗位数',
 `average_salary` float DEFAULT NULL COMMENT '平均薪资',
 `having_credit_china` tinyint DEFAULT NULL COMMENT '当前有无行政许可（信用中国）',
 `having_people_bank` tinyint DEFAULT NULL COMMENT '当前有无行政许可（中国人民银行）',
 `having_market_supervision` tinyint DEFAULT NULL COMMENT '当前有无行政许可（国家市场监督管理总局）',
 `lowest_grade` varchar(10) DEFAULT NULL COMMENT '历史最低纳税人信用级别',
 `grade` varchar(10) DEFAULT NULL COMMENT '当前纳税人信用级别',
 `certificate_type_num` int DEFAULT NULL COMMENT '证书类型数量',
 `bidding_num` int DEFAULT NULL COMMENT '区间招投标成功次数',
 `disclose_supply` tinyint DEFAULT NULL COMMENT '有无披露供货商',
 `ratio_std` float DEFAULT NULL COMMENT '区间供货商分散度（标准差）',
 `amt_sum` float DEFAULT NULL COMMENT '区间供货商采购金额',
 `news_num` int DEFAULT NULL COMMENT '新闻数量',
 `disclose_core_team` tinyint DEFAULT NULL COMMENT '是否披露核心团队',
 `core_team_num` int DEFAULT NULL COMMENT '核心团队人员数量',
 `financing_process_num` int DEFAULT NULL COMMENT '当前融资轮次总数量',
 `corporate_business_num` int DEFAULT NULL COMMENT '当前产品数量',
 `financing_ratio` float DEFAULT NULL COMMENT '当前竞品有融资轮次的百分比',
 `competitor_num` int DEFAULT NULL COMMENT '当前竞品数量',
 `punishment_info_num` int DEFAULT NULL COMMENT '行政处罚次数',
 `punishment_money` float DEFAULT NULL COMMENT '行政处罚金额',
 `equity_pledge_num` int DEFAULT NULL COMMENT '区间股权出质笔数',
 `tax_contravention_num` int DEFAULT NULL COMMENT '区间税收违法次数',
 `tax_arrears_num` int DEFAULT NULL COMMENT '区间欠税公告次数',
 `mortgage_num` int DEFAULT NULL COMMENT '区间动产抵押次数',
 `mortgage_amount_sum` float DEFAULT NULL COMMENT '区间动产抵押金额',
 `judicial_auction_num` int DEFAULT NULL COMMENT '区间司法拍卖次数',
 `law_suit_num` int DEFAULT NULL COMMENT '案件次数',
 `case_type_num` int DEFAULT NULL COMMENT '案由种类数',
 `consumption_restriction_num` int DEFAULT NULL COMMENT '区间限令次数（总数）',
 `dishonest_num` int DEFAULT NULL COMMENT '区间失信次数',
 `judicial_assistance_num` int DEFAULT NULL COMMENT '司法协助-总执行次数',
 `judicial_assistance_money` float DEFAULT NULL COMMENT '司法协助-总执行总金额',
 `insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入数据时间',
 `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新数据时间',
 PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='模型各种指标表'"""
INVESTMENT_TABLE_SQL = """CREATE TABLE `investment_value_predict` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `company_id` bigint NOT NULL,
  `predict_year` year DEFAULT NULL COMMENT '预测年份',
  `proba_value` float DEFAULT NULL COMMENT '值得投资的概率',
  `insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入数据时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新数据时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `company_id` (`company_id`),
  KEY `proba_value` (`proba_value`)
) ENGINE=InnoDB CHARSET=utf8 COMMENT='投资价值预测'"""
PATENT_TABLE_SQL = """CREATE TABLE `patent_value_predict` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `incopat_id` bigint NOT NULL COMMENT 'incopat专利id',
  `predictive_value` int DEFAULT NULL COMMENT '专利预测价值',
  `predictive_credit_line` int DEFAULT NULL COMMENT '授信额度预测值',
  `insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入数据时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新数据时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `incopat_id` (`incopat_id`),
  KEY `predictive_value` (`predictive_value`),
  KEY `predictive_credit_line` (`predictive_credit_line`)
) ENGINE=InnoDB CHARSET=utf8 COMMENT='专利价值预测'"""
SURVIVAL_TABLE_SQL = """CREATE TABLE `survival_risk_predict` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `company_category` tinyint NOT NULL DEFAULT '3' COMMENT '公司类别',
  `company_id` bigint NOT NULL,
  `predict_year` year DEFAULT NULL COMMENT '预测年份',
  `proba_value` float DEFAULT NULL COMMENT '预测值',
  `insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入数据时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新数据时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `company_id` (`company_id`)
) ENGINE=InnoDB CHARSET=utf8 COMMENT='存续风险预测'"""
# 如果没有当前项目数据库啧进行创建
try:
    conn = pymysql.connect(host=MYSQL_HOST, user='root', passwd=MYSQL_PASSWORD, db=MYSQL_DB, port=3306)
    cursor = conn.cursor()
    try:
        cursor.execute(INCOPAT_TABLE_SQL)  # 创建incopat表
    except pymysql.err.OperationalError:
        pass
    try:
        cursor.execute(INCOPAT_ALL_TABLE_SQL)  # 创建incopat_all表
    except pymysql.err.OperationalError:
        pass
    try:
        cursor.execute(INNOVATION_TABLE_SQL)  # 创建innovation_capability_score表
    except pymysql.err.OperationalError:
        pass
    try:
        cursor.execute(MODEL_TABLE_SQL)  # 创建model_predict_various_indicators表
    except pymysql.err.OperationalError:
        pass
    try:
        cursor.execute(INVESTMENT_TABLE_SQL)  # 创建investment_value_predict表
    except pymysql.err.OperationalError:
        pass
    try:
        cursor.execute(PATENT_TABLE_SQL)  # 创建patent_value_predict表
    except pymysql.err.OperationalError:
        pass
    try:
        cursor.execute(SURVIVAL_TABLE_SQL)  # 创建survival_risk_predict表
    except pymysql.err.OperationalError:
        pass
except pymysql.err.OperationalError:
    conn = pymysql.connect(host=MYSQL_HOST, user='root', passwd=MYSQL_PASSWORD, db="information_schema", port=3306)
    cursor = conn.cursor()
    cursor.execute(f"create database {MYSQL_DB} DEFAULT CHARSET utf8 COLLATE utf8_general_ci;")  # 创建数据库
    cursor.close()
    conn.close()
    conn = pymysql.connect(host=MYSQL_HOST, user='root', passwd=MYSQL_PASSWORD, db=MYSQL_DB, port=3306)
    cursor = conn.cursor()
    cursor.execute(INCOPAT_TABLE_SQL)  # 创建incopat表
    cursor.execute(INCOPAT_ALL_TABLE_SQL)  # 创建incopat_all表
    cursor.execute(INNOVATION_TABLE_SQL)  # 创建innovation_capability_score表
    cursor.execute(MODEL_TABLE_SQL)  # 创建model_predict_various_indicators表
    cursor.execute(INVESTMENT_TABLE_SQL)  # 创建investment_value_predict表
    cursor.execute(PATENT_TABLE_SQL)  # 创建patent_value_predict表
    cursor.execute(SURVIVAL_TABLE_SQL)  # 创建survival_risk_predict表
finally:
    cursor.close()
    conn.close()
