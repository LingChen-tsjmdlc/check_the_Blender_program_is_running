import datetime
import sys
import psutil
import time
import requests

GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

# Blender可执行文件的路径
blender_path = "G:/Program Files/blender_ver3.6.5/blender.exe"
# "推送加"公众号的Token
token = "ff684d6fdbe44e8f8db8180c029497db"
# 要检查的exe程序名称
exe_name = "blender.exe"
# 当前时间戳
timestamp = time.time()
now_data = datetime.datetime.fromtimestamp(timestamp)


# 监测Blender进程是否存在
def check_blender_running(process_name):
    # 检查当前运行的进程
    for proc in psutil.process_iter(['pid', 'name', 'username']):  # type: ignore
        if process_name == proc.info['name']:
            return True
    return False


# 发送推送消息
def send_push_message(message,function):
    # 文档: https://www.pushplus.plus/doc/guide/api.html
    payload = {}
    url = f"https://www.pushplus.plus/send?token={token}&title=Blender程序状态&content={message}&template=html&topic=&channel={function}&callbackUrl=&timestamp=&to="
    headers = {
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    print("推送加(公众号)接口返回：", response.text)

# 主循环
send_count = 0  # 发送计数器
while True:
    if check_blender_running(exe_name):
        print(time.strftime('%Y-%m-%d %H:%M:%S'), GREEN + "Blender正在运行..." + RESET)
        send_count = 0  # 重置发送次数
    else:
        if send_count == 0:
            print("Blender.exe 停止时间：", time.strftime('%Y-%m-%d %H:%M:%S'))
            print(RED + "Blender已关闭，发送推送消息！" + RESET)
            send_push_message("Blender窗口已关闭!!!","wechat")
            send_count += 1  # 更新发送次数
        elif send_count == 1:
            print("Blender.exe 停止时间：", time.strftime('%Y-%m-%d %H:%M:%S'))
            print("Blender已关闭，发送推送消息！")
            send_push_message("Blender窗口已关闭!!!", "mail")
            send_count += 1  # 更新发送次数
        else:
            print("消息已发送两次，退出程序。")
            sys.exit() # 退出循环
    time.sleep(10)  # 每隔10秒检查一次
