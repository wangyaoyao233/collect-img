import os
import aiohttp
import asyncio
import json
from dotenv import load_dotenv

load_dotenv()

FOLDER_PATH = os.getenv("FOLDER_PATH")


def load_json(json_file):
    # 从文件中加载 JSON 数据
    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)


async def download_image(session, src, name, save_dir):
    try:
        print(f"Downloading: {src}")
        async with session.get(src) as response:
            response.raise_for_status()  # 检查请求是否成功

            # 保存图片
            filepath = os.path.join(save_dir, name + ".jpg")
            with open(filepath, "wb") as file:
                while True:
                    chunk = await response.content.read(1024)  # 异步读取数据
                    if not chunk:
                        break
                    file.write(chunk)
            print(f"Saved: {filepath}")
    except Exception as e:
        print(f"Failed to download {src}: {e}")


async def download_images_from_json(json_file, save_dir):
    # 创建保存图片的目录
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 加载 JSON 数据
    data = load_json(json_file)

    # 使用 aiohttp 会话下载图片
    async with aiohttp.ClientSession() as session:
        tasks = [
            download_image(session, item["src"], item["name"], save_dir)
            for item in data
        ]
        await asyncio.gather(*tasks)


# 调用主函数
if __name__ == "__main__":
    json_file = "img_list.json"  # JSON 文件路径
    asyncio.run(download_images_from_json(json_file, FOLDER_PATH))
