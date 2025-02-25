import os
import time
import datetime


def get_lately_dir(dir_path):
    res_list = []
    for _ in os.listdir(dir_path):
        try:
            res = datetime.datetime.strptime(str(_), "%Y-%m-%d")
            res_list.append(res)
        except ValueError:
            continue
    res_list.sort()
    try:
        result = datetime.datetime.strftime(res_list[-1], "%Y-%m-%d")
    except IndexError:
        now_time = time.strftime('%Y-%m-%d', time.localtime())
        path = os.path.join(dir_path, now_time)
        os.mkdir(path)
        return now_time
    return result
