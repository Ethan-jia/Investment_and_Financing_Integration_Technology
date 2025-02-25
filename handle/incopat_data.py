import os
import re
import time
import random
import shutil
import selenium
import win32gui
import win32con
import pandas as pd
from selenium import webdriver
from sqlalchemy import create_engine
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from index import *
from tools.random_secret_key import get_secret_key
from tools.find_lately_dir import get_lately_dir

r"""
# 一家公司incopat的更新
Incopat(USERNAME, PASSWORD, "宁波高松电子有限公司", "2309498815").one_query_down()
# 全部公司incopat的更新
Incopat(USERNAME, PASSWORD).all_query_down()
# 已经下载的入库
Incopat(USERNAME, PASSWORD,
        download_folder_path=r"G:\workSpace\workSpace_Python\PPP\incopat_file\2022-07-04").all_save_db()

# Incopat(USERNAME, PASSWORD, "宁波高松电子有限公司", "2309498815").one_query_down()
# 全部公司incopat的更新
# Incopat(USERNAME, PASSWORD).all_query_down()
# Incopat(USERNAME, PASSWORD,
#         query_list=["盘锦辽鹏商贸有限公司", "海芈威（上海）智能科技有限公司", "北京中视鸣达文化传媒有限公司", "宁波均普智能制造股份有限公司"]).some_query_down()
# input()

"""


class Incopat:
    def __init__(self, username, password, query_name="", company_id="", download_folder_path="", query_list=[]):
        if query_name and company_id:
            self.download_folder_path = os.path.join(INCOPAT_TEMPORARY_DIR, get_secret_key())
            self.download_lately_path = os.path.join(INCOPAT_DIR, get_lately_dir(INCOPAT_DIR))
        elif query_list:
            self.download_folder_path = os.path.join(INCOPAT_TEMPORARY_DIR, get_secret_key())
            self.download_lately_path = os.path.join(INCOPAT_DIR, get_lately_dir(INCOPAT_DIR))
        else:
            self.download_folder_path = download_folder_path
        self.driver = ""
        self.username = username
        self.password = password
        self.query_name = query_name
        self.company_id = company_id
        self.query_list = query_list

    def get_driver(self):
        # driver配置信息
        driver_option = webdriver.ChromeOptions()

        # 下载配置
        prefs = {
            "default_content_settings": 0,
            "download.default_directory": self.download_folder_path
        }

        # 反爬配置
        driver_option.add_experimental_option("prefs", prefs)
        driver_option.add_experimental_option("excludeSwitches", ["enable-logging"])
        driver_option.add_argument("--disable-blink-features=AutomationControlled")
        # driver_option.add_argument("--headless")

        # 启动driver
        driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=driver_option)
        print("启动成功")
        # 反爬配置
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator,"webdriver",{
                    get: () => undefined
                })
            """
        })

        # 隐式等待
        driver.implicitly_wait(10)

        # 全屏窗口
        driver.maximize_window()
        return driver

    def login(self):
        # 打开登录页面
        self.driver.get("https://www.incopat.com/newLogin?locale=zh")
        time.sleep(random.randint(3, 5))
        # 输出账号
        self.driver.find_element_by_xpath('//*[@id="u"]').click()
        time.sleep(random.randint(3, 5))
        self.driver.find_element_by_xpath('//*[@id="u"]').send_keys(self.username)
        time.sleep(random.randint(3, 5))

        # 输入密码
        self.driver.find_element_by_xpath('//*[@id="p"]').click()
        time.sleep(random.randint(3, 5))
        self.driver.find_element_by_xpath('//*[@id="p"]').send_keys(self.password)
        time.sleep(random.randint(3, 5))

        # 点击同意须知
        self.driver.find_element_by_xpath('//*[@id="clauseCheckBox"]').click()
        time.sleep(random.randint(3, 5))

        # 点击登陆
        self.driver.find_element_by_xpath('//*[@id="loginBtn"]').click()

        # 如果被登陆,挤掉
        try:
            WebDriverWait(self.driver, 10).until(EC.alert_is_present())
            self.driver.switch_to_alert().accept()
        except selenium.common.exceptions.TimeoutException:
            pass

        # 关闭广告  ----好像没用(id对着)
        try:
            self.driver.find_element_by_xpath('//*[@id="baseAdvice1"]/a').click()
        except selenium.common.exceptions.NoSuchElementException:
            try:
                self.driver.find_element_by_xpath('//*[@id="baseAdvice0"]/a').click()
            except selenium.common.exceptions.NoSuchElementException:
                pass
        except selenium.common.exceptions.Webself.driverException:
            try:
                self.driver.find_element_by_xpath('//*[@id="baseAdvice0"]/a').click()
            except selenium.common.exceptions.NoSuchElementException:
                pass
            pass

    def logout(self):
        # 跳转到主页
        self.driver.get("https://www.incopat.com/")
        time.sleep(random.randint(3, 5))

        try:
            # 点击个人菜单
            self.driver.find_element_by_xpath('//div[@class="user"]/div[2]').click()
            time.sleep(random.randint(3, 5))

            # 点击退出
            self.driver.find_element_by_xpath('//a[@id="logout"]').click()
            time.sleep(random.randint(3, 5))
        except selenium.common.exceptions.ElementNotVisibleException:
            # 点击个人菜单
            self.driver.find_element_by_xpath('//div[@class="user"]/div[2]').click()
            time.sleep(random.randint(3, 5))

            # 点击退出
            self.driver.find_element_by_xpath('//a[@id="logout"]').click()
            time.sleep(random.randint(3, 5))

    def one_download(self):
        # 跳转到本周下载历史页面
        self.driver.get("https://www.incopat.com/history/downloadhistoryinit")
        time.sleep(random.randint(1, 4))

        print("等待专利查询完成....")
        # 查看当前页状态情况
        content_list = self.driver.find_elements_by_xpath('//table[@id="table"]/tr/td[3]')
        state_list = self.driver.find_elements_by_xpath('//table[@id="table"]/tr/td[10]')
        download_list = self.driver.find_elements_by_xpath(
            '//table[@id="table"]/tr/td[11]/a[@_label="download"]')  # 下载按钮
        delete_list = self.driver.find_elements_by_xpath('//table[@id="table"]/tr/td[11]/a[@_label="delete"]')  # 删除按钮
        for idx in range(len(content_list)):
            company_name = content_list[idx].text.replace("ALL=(", "").replace(")", "")
            if company_name == self.query_name:
                # 等待查询完成
                if state_list[idx].text == "已完成":
                    print("确认已完成")
                    download_list[idx].click()  # 点击下载
                    print("点击下载")
                    time.sleep(random.randint(1, 4))
                    # 等待下载完成
                    while True:
                        time.sleep(random.randint(1, 4))
                        return_ = False
                        download_dir = os.listdir(self.download_folder_path)  # 下载地址文件列表
                        for file_name in download_dir:
                            if ".xls.crdownload" not in file_name:
                                return_ = True
                                break
                        if return_:
                            break
                    print("等待下载完成")
                    # 更改名字： 有可能有错-到时候测试
                    file_now_path = os.path.join(self.download_folder_path,
                                                 f"{time.strftime('%Y-%m-%d', time.localtime())}.xls")
                    file_modify_path = os.path.join(self.download_folder_path, f"{self.query_name}.xls")
                    try:
                        os.rename(file_now_path, file_modify_path)  # 替换名字
                    except FileExistsError:
                        os.remove(file_now_path)

                    # 点击删除
                    delete_list[idx].click()

                    # 弹出窗口中确认
                    self.driver.switch_to_alert().accept()
                    time.sleep(random.randint(3, 5))
                    return True
        return False

    def one_query_down(self):
        # 获取浏览器driver
        self.driver = self.get_driver()

        # 创建文件夹
        os.mkdir(self.download_folder_path)

        # 登陆
        self.login()

        # 打开简单查询的网页
        self.driver.get("https://www.incopat.com/advancedSearch/simpleInit")
        time.sleep(random.randint(3, 5))

        # 找到搜索框,并输入内容
        self.driver.find_element_by_xpath('//*[@id="searchValue"]').send_keys(self.query_name)
        time.sleep(random.randint(3, 5))

        # 点击搜索
        self.driver.find_element_by_xpath('//*[@id="simpleSearchBtn"]').click()
        time.sleep(random.randint(10, 15))

        # 此次的下载量
        try:
            once_download_number = int(self.driver.find_element_by_id("totalCountspan").text)
        except selenium.common.exceptions.NoSuchElementException:
            time.sleep(random.randint(10, 15))
            once_download_number = int(self.driver.find_element_by_id("totalCountspan").text)
        time.sleep(random.randint(3, 5))

        # 如果没有
        if once_download_number == 0:
            # 登出
            self.logout()
            self.driver.close()
            # 删除文件夹
            try:
                os.rmdir(self.download_folder_path)
            except:
                pass
            return "none"

        #  点击保存著作项
        self.driver.find_element_by_xpath('//*[@id="rightTool"]/ul/li[1]/img').click()  # 点击保存著作项
        time.sleep(random.randint(5, 8))

        # 切换窗口
        handles = self.driver.window_handles
        self.driver.switch_to.window(handles[-1])

        # 点击全选
        self.driver.find_element_by_xpath('//*[@id="downloadResultDiv"]/div[2]/div/label/input').click()
        time.sleep(random.randint(5, 8))

        # 点击下载
        self.driver.find_element_by_xpath('//*[@id="buttonDiv"]/div[1]/input').click()
        time.sleep(random.randint(3, 5))

        # 关闭当前窗口
        self.driver.close()
        time.sleep(random.randint(3, 5))

        # 切换到主窗口
        self.driver.switch_to.window(self.driver.window_handles[-1])
        time.sleep(random.randint(3, 5))

        # 等待下载完成
        time.sleep(random.randint(10, 15))
        print("查询完了")

        # 删除已有文件（如果有）
        for _ in os.listdir(self.download_folder_path):
            file_path = os.path.join(self.download_folder_path, _)
            os.remove(file_path)

        # 下载
        while True:
            time.sleep(random.randint(3, 5))
            msg = self.one_download()
            if msg:
                break

        # 登出
        self.logout()
        self.driver.close()
        self.driver = ""

        # 存入数据库
        self.one_save_db()
        return "success"

    def one_save_db(self):
        excel_path = os.path.join(self.download_folder_path, f"{self.query_name}.xls")
        df_incopat_excel = pd.read_excel(excel_path)
        df_incopat_excel["company_id"] = self.company_id
        # 列名转换成英文
        res = df_incopat_excel.columns.to_series()
        df_incopat_excel.columns = res.map(INCOPAT_CH_EN_DICT).fillna(res)
        # 删除序号
        del df_incopat_excel["index"]
        # 保存到数据库 incopat_all
        engine = create_engine(f"mysql+pymysql://root:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}?charset=utf8mb4")
        df_incopat_excel.to_sql("incopat_all", engine, if_exists='append', index=False)
        # 保存到数据库 incopat
        df_incopat_excel[INCOPAT_COLUMNS_LIST].to_sql("incopat", engine, if_exists='append', index=False)

        # 把下载的文件移到最近的文件夹目录
        file_path = os.path.join(self.download_folder_path, f"{self.query_name}.xls")
        file_move_path = os.path.join(self.download_lately_path, f"{self.query_name}.xls")
        shutil.move(file_path, file_move_path)

        # 删除已有文件（如果有）
        for _ in os.listdir(self.download_folder_path):
            file_path = os.path.join(self.download_folder_path, _)
            os.remove(file_path)

        # 删除文件夹
        try:
            os.rmdir(self.download_folder_path)
        except:
            pass

    def some_query(self, txt_path):
        # 获取浏览器driver
        self.driver = self.get_driver()

        # 登陆
        self.login()

        print("开始删除....")
        # 跳转到本周下载历史页面
        self.driver.get("https://www.incopat.com/history/downloadhistoryinit")
        time.sleep(random.randint(1, 4))
        while True:
            try:
                # 点击第一行的删除
                self.driver.find_element_by_xpath('//table[@id="table"]/tr/td[11]/a[@_label="delete"]').click()
                time.sleep(random.randint(1, 4))

                # 弹出窗口中确认
                self.driver.switch_to_alert().accept()
                time.sleep(1)
            except selenium.common.exceptions.ElementNotVisibleException:
                break
            except selenium.common.exceptions.NoSuchElementException:
                break
            except selenium.common.exceptions.StaleElementReferenceException:
                time.sleep(3)
        print("完成删除")

        # 获取查询txt列表
        self.all_query_process(txt_path)  # 查询保存
        print("txt查询完成")

        # 删除txt文件
        try:
            os.remove(txt_path)
        except FileNotFoundError:
            pass

        # 登出
        self.logout()
        self.driver.close()
        self.driver = ""

    def some_donwnload(self):
        # 跳转到本周下载历史页面
        self.driver.get("https://www.incopat.com/history/downloadhistoryinit")
        time.sleep(random.randint(1, 4))
        print("开始下载....")

        count = 0  # 总数
        # 下载过程
        while True:
            time.sleep(random.randint(10, 20))
            download_list = self.driver.find_elements_by_xpath(
                '//table[@id="table"]/tr/td[11]/a[@_label="download"]')  # 下载按钮
            type_list = self.driver.find_elements_by_xpath('//table[@id="table"]/tr/td[4]')  # 筛选

            # 处理
            for i in range(len(download_list)):
                # 跳过不是公司的
                if type_list[i].text == "":
                    download_list[i].click()  # 点击下载
                    time.sleep(random.randint(1, 4))
                    count += 1
                    print("下载第", count, "个文件")

                    # 等待下载完成
                    while True:
                        time.sleep(random.randint(1, 4))
                        return_ = False
                        download_dir = os.listdir(self.download_folder_path)  # 下载地址文件列表
                        for file_name in download_dir:
                            if ".xls.crdownload" not in file_name:
                                return_ = True
                                break
                        if return_:
                            break

            # 点击下一页
            try:
                self.driver.find_element_by_link_text('下一页').click()
                print("翻入下一页...")
            except selenium.common.exceptions.NoSuchElementException:
                break
        print("完成下载,共下载", count, "个文件")

        print("开始删除....")
        # 跳转到本周下载历史页面
        self.driver.get("https://www.incopat.com/history/downloadhistoryinit")
        time.sleep(random.randint(1, 4))
        while True:
            try:
                # 点击第一行的删除
                self.driver.find_element_by_xpath('//table[@id="table"]/tr/td[11]/a[@_label="delete"]').click()
                time.sleep(random.randint(1, 4))

                # 弹出窗口中确认
                self.driver.switch_to_alert().accept()
                time.sleep(1)
            except selenium.common.exceptions.ElementNotVisibleException:
                break
            except selenium.common.exceptions.NoSuchElementException:
                break
            except selenium.common.exceptions.StaleElementReferenceException:
                time.sleep(3)
        print("完成删除")

        # 登出
        self.logout()
        self.driver.close()
        self.driver = ""

    def some_query_down(self):
        # 创建文件夹
        os.mkdir(self.download_folder_path)

        # 临时txt文件
        txt_path = os.path.join(self.download_folder_path, "query_list.txt")

        # 生成txt文件
        with open(txt_path, 'w', encoding='utf-8') as fb:
            fb.write("\n".join(self.query_list))

        # 进行查询
        self.some_query(txt_path)

        # 等待查询完成
        while True:
            rep = self.all_wait_inspection()
            if rep:
                break

        # 进行下载
        self.some_donwnload()

        # 保存到数据库
        self.all_save_db()

        # 把下载的文件移到最近的文件夹目录
        for idx, excel_name in enumerate(os.listdir(self.download_folder_path)):
            print(idx, excel_name)
            excel_path = os.path.join(self.download_folder_path, excel_name)
            new_name = get_secret_key() + ".xls"
            excel_new_path = os.path.join(self.download_folder_path, new_name)
            os.rename(excel_path, excel_new_path)
            file_move_path = os.path.join(self.download_lately_path, new_name)
            shutil.move(excel_new_path, file_move_path)

        # 删除已有文件（如果有）
        for _ in os.listdir(self.download_folder_path):
            file_path = os.path.join(self.download_folder_path, _)
            os.remove(file_path)

        # 删除文件夹
        try:
            os.rmdir(self.download_folder_path)
        except:
            pass

    def all_query_process(self, txt_name, txt_path=""):
        def upload_file(file_path):
            # 调用windows用于浏览器上传文件
            dialog = win32gui.FindWindow("#32770", "打开")
            comboxex32 = win32gui.FindWindowEx(dialog, 0, "ComboBoxEx32", None)
            combox = win32gui.FindWindowEx(comboxex32, 0, "ComboBox", None)
            edit = win32gui.FindWindowEx(combox, 0, "Edit", None)
            button = win32gui.FindWindowEx(dialog, 0, "Button", "打开(&0)")
            win32gui.SendMessage(edit, win32con.WM_SETTEXT, None, file_path)
            win32gui.SendMessage(dialog, win32con.WM_COMMAND, 1, button)

        # 打开批量查询网页
        self.driver.get("https://www.incopat.com/batchSearch/init")
        time.sleep(random.randint(3, 5))

        # 点击申请人
        self.driver.find_element_by_xpath('//*[@id="batchschform"]/div[1]/ul/li[5]').click()
        time.sleep(random.randint(3, 5))

        # 点击上传TXT按钮
        self.driver.find_element_by_xpath('//*[@id="batchschform"]/div[2]/div').click()
        time.sleep(random.randint(3, 5))

        # 文件路径
        if not txt_path:
            txt_path = os.path.join(COMPANY_TXT_DIR, txt_name)

        # 上传文件
        upload_file(txt_path)
        time.sleep(random.randint(3, 5))

        # 点击检索按钮
        self.driver.find_element_by_id("query_0").click()
        time.sleep(random.randint(10, 15))

        # 此次的下载量
        try:
            once_download_number = int(self.driver.find_element_by_id("totalCountspan").text)
        except selenium.common.exceptions.NoSuchElementException:
            time.sleep(random.randint(10, 15))
            once_download_number = int(self.driver.find_element_by_id("totalCountspan").text)
        time.sleep(random.randint(3, 5))

        #  点击保存著作项
        self.driver.find_element_by_xpath('//*[@id="rightTool"]/ul/li[1]/img').click()  # 点击保存著作项
        time.sleep(random.randint(5, 8))

        # 切换窗口
        handles = self.driver.window_handles
        self.driver.switch_to.window(handles[-1])

        # 点击全选
        self.driver.find_element_by_xpath('//*[@id="downloadResultDiv"]/div[2]/div/label/input').click()
        time.sleep(random.randint(5, 8))

        # 从头开始下载
        query_begin = 1
        query_end = query_begin + 10000 - 1
        for i in range(10):
            if query_end > once_download_number:
                sendkey = f'{query_begin}-{once_download_number}'
            else:
                sendkey = f'{query_begin}-{query_end}'
            self.driver.find_element_by_id("rangeValue").clear()
            self.driver.find_element_by_id("rangeValue").send_keys(sendkey)
            time.sleep(1)
            self.driver.find_element_by_xpath('//*[@id="buttonDiv"]/div[1]/input').click()  # 点击下载
            time.sleep(1)

            # 下载额度不够了
            limit_switch = False
            try:
                tips_id = "xubox_layer" + str(i + 2)
                ele = self.driver.find_element_by_id(tips_id).text
                if "请升级为正式用户后继续下载" in ele:
                    limit_switch = True
                else:
                    limit_switch = False
            except:
                pass
            if limit_switch:
                msg = self.driver.find_element_by_id("limitMsg").text
                print(msg)
                time.sleep(1)
                self.driver.find_element_by_xpath('//*[@id="limitMoban"]/div[3]/input').click()
                print("该下载: " + str(query_begin) + "-" + str(query_end))
                break

            if query_end > once_download_number:
                break

            query_begin += 10000
            query_end += 10000

        # 关闭当前窗口
        self.driver.close()
        time.sleep(random.randint(3, 5))

        # 切换到主窗口
        self.driver.switch_to.window(self.driver.window_handles[-1])
        time.sleep(random.randint(3, 5))

    def all_query(self):
        # 获取浏览器driver
        self.driver = self.get_driver()

        # 登陆
        self.login()

        print("开始删除....")
        # 跳转到本周下载历史页面
        self.driver.get("https://www.incopat.com/history/downloadhistoryinit")
        time.sleep(random.randint(1, 4))
        while True:
            try:
                # 点击第一行的删除
                self.driver.find_element_by_xpath('//table[@id="table"]/tr/td[11]/a[@_label="delete"]').click()
                time.sleep(random.randint(1, 4))

                # 弹出窗口中确认
                self.driver.switch_to_alert().accept()
                time.sleep(1)
            except selenium.common.exceptions.ElementNotVisibleException:
                break
            except selenium.common.exceptions.NoSuchElementException:
                break
            except selenium.common.exceptions.StaleElementReferenceException:
                time.sleep(3)
        print("完成删除")

        # 获取查询txt列表
        txt_list = os.listdir(COMPANY_TXT_DIR)
        for txt_name in txt_list:
            print("正在查询", txt_name)
            self.all_query_process(txt_name)  # 查询保存
        print("txt查询完成")

        # 登出
        self.logout()
        self.driver.close()
        self.driver = ""

    def all_wait(self):
        # 查看当前页状态情况
        state_list = self.driver.find_elements_by_xpath('//table[@id="table"]/tr/td[10]')
        time.sleep(1)
        state_list = [i.text for i in state_list]

        # 有未下载情况
        if any("队列中" in s for s in state_list):
            return False
        if any("下载中" in s for s in state_list):
            return False

        # 点击下一页
        try:
            self.driver.find_element_by_link_text('下一页').click()
            return "next"
        except selenium.common.exceptions.NoSuchElementException:
            return True

    def all_wait_inspection(self):
        # 获取浏览器driver
        self.driver = self.get_driver()

        # 登陆
        self.login()

        # 跳转到本周下载历史页面
        self.driver.get("https://www.incopat.com/history/downloadhistoryinit")
        time.sleep(random.randint(1, 4))

        # 查看下载状态
        while True:
            rep = self.all_wait()
            if rep == "next":
                time.sleep(random.randint(1, 4))
                continue
            elif rep:
                break
            else:
                print("等待完成...")
                # 登出
                self.logout()
                self.driver.close()
                self.driver = ""
                return False

        print("已经全部查询完成...")
        return True

    def all_download(self):
        # 跳转到本周下载历史页面
        self.driver.get("https://www.incopat.com/history/downloadhistoryinit")
        time.sleep(random.randint(1, 4))
        print("开始下载....")

        count = 0  # 总数
        # 下载过程
        while True:
            time.sleep(random.randint(10, 20))
            download_list = self.driver.find_elements_by_xpath(
                '//table[@id="table"]/tr/td[11]/a[@_label="download"]')  # 下载按钮
            type_list = self.driver.find_elements_by_xpath('//table[@id="table"]/tr/td[4]')  # 筛选

            # 处理
            for i in range(len(download_list)):
                # 跳过不是公司的
                if type_list[i].text == "":
                    download_list[i].click()  # 点击下载
                    time.sleep(random.randint(1, 4))
                    count += 1
                    print("下载第", count, "个文件")

                    # 等待下载完成
                    while True:
                        time.sleep(random.randint(1, 4))
                        return_ = False
                        download_dir = os.listdir(self.download_folder_path)  # 下载地址文件列表
                        for file_name in download_dir:
                            if ".xls.crdownload" not in file_name:
                                return_ = True
                                break
                        if return_:
                            break

            # 点击下一页
            try:
                self.driver.find_element_by_link_text('下一页').click()
                print("翻入下一页...")
            except selenium.common.exceptions.NoSuchElementException:
                break
        print("完成下载,共下载", count, "个文件")

        # 等待半小时确认下载完成
        time.sleep(1800)

        print("开始删除....")
        # 跳转到本周下载历史页面
        self.driver.get("https://www.incopat.com/history/downloadhistoryinit")
        time.sleep(random.randint(1, 4))
        while True:
            try:
                # 点击第一行的删除
                self.driver.find_element_by_xpath('//table[@id="table"]/tr/td[11]/a[@_label="delete"]').click()
                time.sleep(random.randint(1, 4))

                # 弹出窗口中确认
                self.driver.switch_to_alert().accept()
                time.sleep(1)
            except selenium.common.exceptions.ElementNotVisibleException:
                break
            except selenium.common.exceptions.NoSuchElementException:
                break
            except selenium.common.exceptions.StaleElementReferenceException:
                time.sleep(3)
        print("完成删除")

        # 登出
        self.logout()
        self.driver.close()
        self.driver = ""

    def all_df(self):
        # 读取所有数据
        df_all_list = []
        for excel_name in os.listdir(self.download_folder_path):
            excel_path = os.path.join(self.download_folder_path, excel_name)
            df_one = pd.read_excel(excel_path)
            df_all_list.append(df_one)
        # 拼接到一起
        df_all = pd.concat(df_all_list)
        # 重新设置索引
        df_all = df_all.reset_index(drop=True)
        # 重新设置序号
        del df_all["序号"]
        df_all.insert(0, "序号", df_all.index, True)
        return df_all

    def all_save_db(self):
        from tools.query_company import get_company_excel
        def change_field_type(error_str):
            conn = pymysql.connect(host=MYSQL_HOST, user='root', passwd=MYSQL_PASSWORD, db=MYSQL_DB, port=3306)
            print("入库时候出问题了===========================================")
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
                    print(field_type, '=========')
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
                    print(sql2, '++++++')
                cursor.execute(sql2)
            cursor.close()
            conn.close()

        def query_company_id(df_all, query_name):

            # 处理括号函数
            def handle_brackets(x):
                return x['name'].replace("（", "(").replace("）", ")")

            if len(df_all) != 0:
                # 对照表
                df_id = pd.read_excel(COMPANY_EXCEL_PATH)
                # 处理括号
                df_id["name"] = df_id.apply(handle_brackets, axis=1)
                # 更改原表列名
                df_id = df_id.rename(columns={"name": query_name})
                # 按; 拆分数据
                df_all = df_all.drop([query_name], axis=1).join(
                    df_all[query_name].str.split('; ', expand=True).stack().reset_index(level=1, drop=True).rename(
                        query_name))
                try:
                    del df_all["Unnamed: 0"]
                except KeyError:
                    pass
                # 进行查询
                df_result = df_all.join(df_id.set_index(query_name), on=query_name, lsuffix="_")
                # 找到不重复数据
                df_no_repeat = df_result[~df_result.duplicated(subset=["序号"], keep=False)]
                # 找到重复数据
                df_repeat = df_result[df_result.duplicated(subset=["序号"], keep=False)]
                # 排序
                df_repeat = df_repeat.sort_values(by=["company_id"], ascending=True)
                # 删除重复的
                df_repeat.drop_duplicates(subset=["序号"], inplace=True)
                # 处理后重复的和没处理的不重复的拼起来
                df_ = pd.concat([df_no_repeat, df_repeat])
                # 重新设置索引
                df_ = df_.reset_index(drop=True)
                # 重新设置序号
                del df_["序号"]
                df_.insert(0, "序号", df_.index, True)
                try:
                    del df_["company_id_"]
                except KeyError:
                    pass
                return df_
            return df_all

        # 获取所有数据
        df_all = self.all_df()

        # 重新获取基本信息表
        get_company_excel()

        # 要查询字段的列表
        query_name_list = ["申请人", "标准化当前权利人", "当前权利人", "第一申请人"]
        # 去查询company_id
        df_all_list = []
        for query_name in query_name_list:
            df = query_company_id(df_all, query_name)
            # 取出 company_id 不为空的行
            df_all_list.append(df[df[['company_id']].notnull().T.any()])
            # 取出 company_id 为空的行
            df_all = df[df[['company_id']].isnull().T.any()]

        # 最终结果进行拼接
        df_incopat_excel = pd.concat(df_all_list)
        # 重新设置索引
        df_incopat_excel = df_incopat_excel.reset_index(drop=True)
        # 删除序号
        del df_incopat_excel["序号"]

        # 列名转换成英文
        res = df_incopat_excel.columns.to_series()
        df_incopat_excel.columns = res.map(INCOPAT_CH_EN_DICT).fillna(res)
        print(list(df_incopat_excel.columns))
        del df_incopat_excel["dependentclaim_number"]
        del df_incopat_excel["inventor_name"]
        del df_incopat_excel["independent_claims"]
        del df_incopat_excel["independent_claims_number"]
        del df_incopat_excel["power_translation"]
        del df_incopat_excel["license_number"]
        del df_incopat_excel["pledge_number"]
        del df_incopat_excel["address_transferee"]
        del df_incopat_excel["转让登记号"]
        del df_incopat_excel["转让登记日"]
        # 保存到数据库 incopat_all
        engine = create_engine(f"mysql+pymysql://root:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}?charset=utf8mb4")
        df_incopat_excel.to_sql("incopat_all", engine, if_exists='append', index=False)
        # 保存到数据库 incopat
        while True:
            try:
                df_incopat_excel[INCOPAT_COLUMNS_LIST].to_sql("incopat", engine, if_exists='append', index=False)
            except Exception as e:
                change_field_type(e)
            else:
                break

    def all_query_down(self):
        from tools.query_company import get_company_txt, get_company_excel

        # 获取当前时间
        now_time = time.strftime('%Y-%m-%d', time.localtime())
        self.download_folder_path = os.path.join(INCOPAT_DIR, now_time)
        # 创建文件夹
        os.mkdir(self.download_folder_path)

        # 重新获取基本信息表
        get_company_excel()

        # 生成txt文件
        get_company_txt()

        # 进行查询
        self.all_query()

        # 等待查询完成 -- 预估2个半小时下载完毕
        time.sleep(3600 * 2.5)
        while True:
            rep = self.all_wait_inspection()
            if rep:
                break

        # 进行下载
        self.all_download()

        # 保存到数据库
        self.all_save_db()

    def aaa(self):
        import warnings
        warnings.warn("更改注释")
        table_name = "incopat_all"
        conn = ""
        # conn = pymysql.connect(host=MYSQL_HOST, user='root', passwd=MYSQL_PASSWORD, db=MYSQL_DB, port=3306)
        # 获取当前表的信息
        df = pd.read_sql(f'select * from information_schema.COLUMNS WHERE TABLE_NAME = "{table_name}"', conn)
        column_name_list = list(df["COLUMN_NAME"])
        data_type_list = list(df["DATA_TYPE"])
        # 更改注释
        cursor = conn.cursor()
        for index in range(len(column_name_list)):
            if column_name_list[index] == "index":
                sql = f'alter table {table_name} modify column `index` bigint comment "序号";'
                cursor.execute(sql)
                continue
            if data_type_list[index] in ("text", "datetime", "double"):
                sql = f'alter table {table_name} modify column {column_name_list[index]} {data_type_list[index]} comment "{INCOPAT_EN_CH_DICT[column_name_list[index]]}";'
                cursor.execute(sql)
            elif data_type_list[index] == "bigint":
                if column_name_list[index] == "index":
                    continue
                sql = f'alter table {table_name} modify column {column_name_list[index]} bigint(20) comment "{INCOPAT_EN_CH_DICT[column_name_list[index]]}";'
                cursor.execute(sql)
            else:
                print(data_type_list[index])
        cursor.close()
        conn.close()


Incopat(USERNAME, PASSWORD,
        download_folder_path=r"G:\workSpace\workSpace_Python\project_incopat_automatic_update\version2\incopat_file\2022-08-24").all_save_db()