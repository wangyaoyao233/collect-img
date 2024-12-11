import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
FOLDER_PATH = os.getenv("FOLDER_PATH")


def get_all_files(folder_path):
    file_list = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list


def send_file_to_channel(bot_token, channel_id, file_path):
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    with open(file_path, "rb") as file:
        files = {"document": file}
        data = {"chat_id": channel_id}
        response = requests.post(url, data=data, files=files)
    return response.json()


# 主函数：上传文件夹中的所有文件
def upload_folder_files(bot_token, channel_id, folder_path, delay=1):
    files = get_all_files(folder_path)
    with open("uploaded.txt", "a") as log:  # 打开日志文件，保持文件流
        for file_path in files:
            print(f"Uploading {file_path}...")
            response = send_file_to_channel(bot_token, channel_id, file_path)
            print(f"Response: {response}")
            if not response.get("ok"):
                print(f"Failed to upload {file_path}: {response}")
            else:
                log.write(f"{file_path}\n")
                log.flush()
            time.sleep(delay)  # 防止触发速率限制


# 执行上传
upload_folder_files(BOT_TOKEN, CHANNEL_ID, FOLDER_PATH)
