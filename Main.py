import datetime
import os
import sys
import psutil
import time
import requests

# import bpy  #bpy 库太容易报错

GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

# Blender可执行文件的路径
blender_path = "G:/Program Files/blender_ver3.6.5/blender.exe"
# "推送加"公众号的Token
token = ""
token_mom = ""
# 要检查的exe程序名称
exe_name = "blender.exe"
# 总渲染帧数
total_frame_number = 4924
# 当前时间戳
timestamp = time.time()
now_data = datetime.datetime.fromtimestamp(timestamp)
# 渲染路径文件夹
files_path = 'E:/MMD渲染序列/横竖撇点MMD_Saro'


# 获取渲染文件夹的文件个数
def get_render_number():
    render_number = len(os.listdir(files_path))
    return render_number


# 刷新当前进度
def refresh_progress(total_frame):
    render_number = len(os.listdir(files_path))
    progress = round((render_number / total_frame) * 100, 3)
    return progress


# 监测Blender进程是否存在
def check_blender_running(process_name):
    # 检查当前运行的进程
    for proc in psutil.process_iter(['pid', 'name', 'username']):  # type: ignore
        if process_name == proc.info['name']:
            return True
    return False


# 发送推送消息
def send_push_message(token, message, function):
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
        print(time.strftime('%Y-%m-%d %H:%M:%S'), GREEN + "Blender正在运行......" + RESET, "已经渲染帧数:",
              get_render_number(), "进度:", refresh_progress(total_frame_number), "%")
        send_count = 0  # 重置发送次数
    else:
        if send_count == 0:
            print("\nBlender.exe 停止时间：", time.strftime('%Y-%m-%d %H:%M:%S'))
            print(RED + "Blender已关闭，发送推送消息！" + RESET)
            send_push_message(token_mom, "Blender窗口已关闭!!!", "wechat")
            send_push_message(token, "Blender窗口已关闭!!!", "wechat")
            # bpy.ops.wm.open_mainfile(filepath='path_to_your_blend_file.blend')
            send_count += 1  # 更新发送次数
        elif send_count == 1:
            print("\nBlender.exe 停止时间：", time.strftime('%Y-%m-%d %H:%M:%S'))
            print(RED + "Blender已关闭，发送推送消息！" + RESET)
            send_push_message(token_mom, "Blender窗口已关闭!!!", "wechat")
            send_push_message(token, "Blender窗口已关闭!!!", "mail")
            send_count += 1  # 更新发送次数
        else:
            print("消息已发送两次，退出程序。")
            sys.exit()  # 退出循环
    time.sleep(10)  # 每隔10秒检查一次
