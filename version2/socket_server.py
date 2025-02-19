# -*- coding: UTF-8 -*-
import json
import time
import redis
import socket  # 导入 socket 模块
import requests
import threading

from index import *


def verify(credit_code, name):
    response = requests.get(f"http://open.api.tianyancha.com/services/open/ic/baseinfo/normal?keyword={credit_code}",
                            headers={'Authorization': TOKEN})
    result = json.loads(response.text)
    if result["result"]:  # 有数据
        api_name = result["result"]["name"]
        if name == api_name:
            msg = "success:成功"
            return msg, result["result"]["id"]
        else:
            response = requests.get(f"http://open.api.tianyancha.com/services/open/ic/baseinfo/normal?keyword={name}",
                                    headers={'Authorization': TOKEN})
            result = json.loads(response.text)
            if result["result"]:  # 有数据
                msg = "error:企业名称和统一社会信用代码不统一"
            else:  # 无数据
                msg = "error:企业名称填写错误"
    else:  # 无数据
        response = requests.get(f"http://open.api.tianyancha.com/services/open/ic/baseinfo/normal?keyword={name}",
                                headers={'Authorization': TOKEN})
        result = json.loads(response.text)
        if result["result"]:  # 有数据
            msg = "error:统一社会信用代码填写错误"
        else:  # 无数据
            msg = "error:该企业不存在"
    return msg, "error"


def search_company_list(word):
    response = requests.get(f"http://open.api.tianyancha.com/services/open/search/2.0?word={word}",
                            headers={'Authorization': TOKEN})
    res = json.loads(response.text)
    try:
        return_list = [{"name": item["name"], "companyId": ""} for item in res["result"]["items"]]
    except TypeError:
        return_list = []
    return return_list


def company_query_down(company_id, company_name):
    from handle.tianyancha_data import Tianyancha
    from handle.incopat_data import Incopat
    from handle.model_data import Model
    res = {"company_id": company_id, "company_name": company_name}
    # 查看是否已经存在
    res_list = [_ for _ in DOWNLOADING_LIST if _ == res]
    if not res_list:  # 如果已经存在则跳出
        DOWNLOADING_LIST.append(res)
        Tianyancha(company_id).query_down()
        print("下载列表", DOWNLOADING_LIST)
        if len(DOWNLOADING_LIST) == 1:
            # 进行一个公司的下载
            Incopat(USERNAME, PASSWORD, company_name, company_id).one_query_down()
            Model(company_id=company_id).save_db()
            DOWNLOADING_LIST.remove(res)
            while True:
                print("下载列表", DOWNLOADING_LIST)
                if len(DOWNLOADING_LIST) != 0:
                    company_id_list = [_["company_id"] for _ in DOWNLOADING_LIST]
                    company_name_list = [_["company_name"] for _ in DOWNLOADING_LIST]
                    # 进行多个公司的下载
                    Incopat(USERNAME, PASSWORD, query_list=company_name_list).some_query_down()
                    # 每个公司进行入库
                    [Model(company_id=_).save_db() for _ in company_id_list]
                    # 删除每个对象
                    for _ in range(len(company_name_list)):
                        res = {"company_id": company_id_list[_], "company_name": company_name_list[_]}
                        DOWNLOADING_LIST.remove(res)
                else:
                    break


def company_update(name):
    response = requests.get(f"http://open.api.tianyancha.com/services/open/ic/baseinfo/normal?keyword={name}",
                            headers={'Authorization': TOKEN})
    try:
        company_id = json.loads(response.text)["result"]["id"]
        company_query_down(company_id, name)
    except TypeError:
        pass


# 处理客户端的请求操作
def handle_client_request(service_client_socket, ip_port):
    # 循环接收客户端发送的数据
    while True:
        try:
            # 接收客户端发送的数据
            recv_data = service_client_socket.recv(1024)
        except ConnectionResetError:
            break
        # 容器类型判断是否有数据可以直接使用if语句进行判断，如果容器类型里面有数据表示条件成立，否则条件失败
        # 容器类型: 列表、字典、元组、字符串、set、range、二进制数据
        if recv_data:
            data = json.loads(recv_data.decode())  # 接收数据
            print("接收到的参数：", data)
            socket_type = data["socket_type"]
            if socket_type == "search_list":
                return_list = search_company_list(data["content"]["name"])
                print("查询到的列表：", return_list)
                res = json.dumps(return_list, ensure_ascii=False)
                service_client_socket.send(res.encode())
            elif socket_type == "register_verify":
                # 开始下载及入库
                msg, res = verify(data["content"]["credit_code"], data["content"]["name"])
                service_client_socket.send(msg.encode())
                if res != "error":
                    company_query_down(res, data["content"]["name"])
            elif socket_type == "update_name":
                service_client_socket.send("OK".encode())
                company_update(data["content"]["name"])
            elif socket_type == "business_predict":
                from handle.model_data import Model
                income_statement_dict = {
                    'total_revenue': data["content"]["total_revenue"],
                    'operating_costs': data["content"]["operating_costs"],
                    'op': data["content"]["op"],
                    'profit_total_amt': data["content"]["profit_total_amt"],
                    'income_tax_expenses': data["content"]["income_tax_expenses"]
                }
                result = Model(company_id=data["content"]["company_id"],
                               income_statement_dict=income_statement_dict).get_business_result()
                msg = str(result)
                print("经营预测结果：", msg)
                service_client_socket.send(msg.encode())
            elif socket_type == "back_door":
                # from handle.incopat_data import Incopat
                service_client_socket.send("OK".encode())
                # Incopat(USERNAME, PASSWORD, query_list=["海芈威（上海）智能科技有限公司", "宁波均普智能制造股份有限公司"]).some_query_down()
        else:
            print("客户端已经下线:", ip_port, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
            print()
            break
    # 终止和客户端进行通信
    service_client_socket.close()


if __name__ == '__main__':
    # 创建tcp服务端套接字
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 设置端口号复用，让程序退出端口号立即释放
    tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    # 绑定端口号
    tcp_server_socket.bind(("", 9090))
    # 设置监听, listen后的套接字是被动套接字，只负责接收客户端的连接请求
    tcp_server_socket.listen(128)
    # r = redis.Redis(host='localhost', port=6379, decode_responses=True, )
    # 循环等待接收客户端的连接请求
    while True:
        # 等待接收客户端的连接请求
        service_client_socket, ip_port = tcp_server_socket.accept()
        print("客户端连接成功:", ip_port, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        # 当客户端和服务端建立连接成功以后，需要创建一个子线程，不同子线程负责接收不同客户端的消息
        sub_thread = threading.Thread(target=handle_client_request, args=(service_client_socket, ip_port))
        # 设置守护主线程
        sub_thread.setDaemon(True)
        # 启动子线程
        sub_thread.start()
    # tcp服务端套接字可以不需要关闭，因为服务端程序需要一直运行
    # tcp_server_socket.close()
