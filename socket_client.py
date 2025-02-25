# -*- coding: UTF-8 -*-
import socket  # 导入 socket 模块
import json

if __name__ == '__main__':
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建 socket 对象
    host = socket.gethostname()  # 获取本地主机名
    port = 9090  # 设置端口号
    sk.connect((host, port))
    # message = {"socket_type": "update_name", "content": {"name": "宁波镇洋企业管理咨询有限公司"}}
    # message = {'socket_type': 'business_predict', 'content': {'company_id': "4498877900", 'total_revenue': 100, 'operating_costs': 200, 'op': 1000000000, 'profit_total_amt': 100, 'income_tax_expenses': 800}}
    # message = {"socket_type": "register_verify", "content": {"credit_code": "91330200784349146B", "name": "宁波高松电子有限公司"}}
    # message = {"socket_type": "search_list", "content": {"name": "火凤祥"}}
    message = {"socket_type": "back_door"}
    message = json.dumps(message)
    sk.sendall(message.encode())
    print(sk.recv(1024).decode())
    sk.close()
