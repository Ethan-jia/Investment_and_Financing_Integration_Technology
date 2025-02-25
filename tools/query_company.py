from index import *


def get_company_txt():
    # 清空文件夹
    [os.remove(os.path.join(COMPANY_TXT_DIR, txt_name)) for txt_name in os.listdir(COMPANY_TXT_DIR)]

    df = pd.read_excel(COMPANY_EXCEL_PATH)
    company_name_list = list(df["name"])

    def split(index):
        txt_str = ""
        res_str = ""
        for company_name in company_name_list[index:]:
            if len(txt_str + company_name) > 10000:
                res_str = company_name
                break
            txt_str += company_name
            txt_str += "\n"
        if res_str == "":
            return len(company_name_list), txt_str
        else:
            next_index = company_name_list.index(res_str)
            return next_index, txt_str

    # 写入TXT文件
    next_index = 0
    while True:
        next_index, txt_str = split(next_index)
        file_path = rf"{COMPANY_TXT_DIR}\{next_index}.txt"
        with open(file_path, 'w', encoding='utf-8') as fb:
            fb.write(txt_str)
        if next_index == len(company_name_list):
            break


def get_company_excel():
    # 从数据库中获取文件
    conn = pymysql.connect(host=MYSQL_HOST, user='root', passwd=MYSQL_PASSWORD, db=MYSQL_DB, port=3306)
    get_company_sql = "SELECT company_id,`name` FROM base_info"
    try:
        # 如果数据库中有则更新
        df = pd.read_sql(get_company_sql, conn)
        df.to_excel(COMPANY_EXCEL_PATH, index=False)
    except:
        pass
