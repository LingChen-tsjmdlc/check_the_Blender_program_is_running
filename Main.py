import datetime
import os
import sys
import psutil
import time
import requests
import yaml
import random
from pynput.mouse import Controller, Button
from pynput.keyboard import Controller as KeyboardController
from pynput.keyboard import Key

# import bpy  #bpy 库太容易报错[弃用]

GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'


messages = [
    "Blender 窗口已关闭!及时查看电脑情况",
    "Blender 窗口已关闭!及时查看电脑情况.",
    "Blender 窗口已关闭!!及时查看电脑情况",
    "Blender 窗口已关闭!!!及时查看电脑情况",
    "Blender 窗口已关闭！及时查看电脑情况",
    "Blender 窗口已关闭！及时查看电脑情况。",
    "Blender 窗口已关闭！！及时查看电脑情况",
    "Blender 窗口已关闭！！！及时查看电脑情况"
]


# 读取根目录下的config.yaml文件
def read_config():
    # 打开并读取YAML文件
    with open('./config.yaml', 'r', encoding='utf-8') as file:
        config_data = yaml.safe_load(file)

    return config_data


# 使用读取的配置
config = read_config()
token_d = (config['token'][0])

# Blender可执行文件的路径
blender_path = config['path']['blender']
# "推送加"公众号的Token
token_me = config['token'][0]
token_mom = config['token'][1]
# 要检查的exe程序名称
exe_name = config['exeName']
# 总渲染帧数
total_frame_number = config['frame']['total']
# 当前时间戳
timestamp = time.time()
now_data = datetime.datetime.fromtimestamp(timestamp)
# 渲染路径文件夹
files_path = config['path']['output']


# 获取渲染文件夹的文件个数
def get_render_number():
    render_number = len(os.listdir(files_path))
    return render_number


def edit_start_time(now_file_number):
    # 如果文件数量为0，更新 timeStart
    if now_file_number == 0:
        current_time = int(time.time())
        config['timeStart'] = current_time
        # 将更新后的配置写回 YAML 文件
        with open('config.yaml', 'w', encoding='utf-8') as file:
            yaml.dump(config, file, allow_unicode=True)
        print(f"已更新开始时间戳： {current_time}")
    else:
        print(f"当前文件夹已经有文件了,渲染输出的文件内文件数量: {now_file_number}")


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
def send_push_message(token, function):
    # 从messages列表中随机选择一个消息
    random_message = random.choice(messages)
    # 文档: https://www.pushplus.plus/doc/guide/api.html
    payload = {}
    url = f"https://www.pushplus.plus/send?token={token}&title=Blender程序状态&content={random_message}&template=html&topic=&channel={function}&callbackUrl=&timestamp=&to="
    headers = {
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    print("推送加(公众号)接口返回：", response.text)


def ctrl_mouse_open_render_file():
    mouse = Controller()
    mouse.position = (1300, 786)
    time.sleep(1)
    mouse.click(Button.left)


# 控制鼠标
def ctrl_mouse_change_render_start_farm():
    mouse = Controller()
    mouse.position = (2366, 814)
    time.sleep(1)
    mouse.click(Button.left)


# 控制键盘输入帧数
def ctrl_keyboard_input():
    now_frame = str(get_render_number())
    keyboard = KeyboardController()
    keyboard.type(now_frame)
    time.sleep(1)
    keyboard.press(Key.enter)
    time.sleep(0.3)
    keyboard.release(Key.enter)
    time.sleep(2)
    keyboard.press(Key.ctrl)
    keyboard.press(Key.f12)
    time.sleep(0.3)
    keyboard.release(Key.f12)
    keyboard.release(Key.ctrl)


# 计算剩余时间（估计）
def estimate_remaining_time(start_time, current_progress_percent):
    current_time = time.time()
    elapsed_time = current_time - start_time

    if current_progress_percent == 0:
        return "无法估算"

    progress_percent_per_second = current_progress_percent / elapsed_time  # 计算每10秒完成的进度百分比
    remaining_progress_percent = 100 - current_progress_percent  # 计算剩余的进度百分比

    if progress_percent_per_second > 0:
        remaining_time = remaining_progress_percent / progress_percent_per_second
        return format_time(remaining_time)
    else:
        return "无法估算"


def format_time(seconds):
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}小时 {minutes}分钟 {seconds}秒"


def ctrl_v():
    keyboard = KeyboardController()
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)


# 主循环
send_count = 0  # 发送计数器
edit_start_time(get_render_number())
print("\t\t\t实时时间\t\t\t|\t\t\t状态\t\t\t|\t\t进度(帧)\t\t\t|\t\t剩余(帧)\t\t|\t\t进度(%)\t\t|\t\t\t预计剩余时间")
while True:
    if check_blender_running(exe_name):
        now_farm = get_render_number()
        remaining_time = estimate_remaining_time(config['timeStart'], refresh_progress(total_frame_number))
        if now_farm == total_frame_number:
            print(GREEN + "已经全部渲染完成！！！" + RESET)
            send_push_message(token_me, "wechat")
            sys.exit()
        print(time.strftime('%Y-%m-%d %H:%M:%S'), GREEN + "\t\t   Blender正在运行......" + RESET, "\t已经渲染帧数:",
              get_render_number(), "\t\t  剩余:", total_frame_number - get_render_number(), "\t\t\t进度:",
              refresh_progress(total_frame_number), "%", "\t\t预计剩余：", remaining_time)
        send_count = 0  # 重置发送次数
    else:
        if send_count == 0:
            print(time.strftime('%Y-%m-%d %H:%M:%S'), RED + "\t\t   Blender已关闭!开始推送消息" + RESET,
                  "\t已经渲染帧数:",
                  get_render_number(), "\t\t  剩余:", total_frame_number - get_render_number(), "\t\t\t进度:",
                  refresh_progress(total_frame_number), "%")
            print(RED + "Blender已关闭，发送推送消息！" + RESET)
            send_push_message(token_mom, "wechat")
            send_push_message(token_me, "wechat")
            send_push_message(token_me, "mail")

            print(time.strftime('%Y-%m-%d %H:%M:%S'), RED + "\t\t   准备重新渲染！" + RESET, "\t已经渲染帧数:",
                  get_render_number(), "\t\t  剩余:", total_frame_number - get_render_number(), "\t\t\t进度:",
                  refresh_progress(total_frame_number), "%")
            os.startfile(blender_path)  # TODO：临时方案，使用固定的鼠标点击和快捷键配合；需要采用更好的方案！
            time.sleep(8)
            ctrl_mouse_open_render_file()
            time.sleep(8)
            ctrl_mouse_change_render_start_farm()
            ctrl_keyboard_input()
        else:
            print("未知错误！")
            sys.exit()  # 退出程序
    time.sleep(config['sleep'])  # 间隔多少秒检查一次
