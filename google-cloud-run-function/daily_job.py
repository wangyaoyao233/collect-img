import base64
import functions_framework
from io import BytesIO
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from datetime import date, datetime, timedelta
import requests
import json
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# 设置无头模式
chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
)


# 创建上下文管理器
class WebDriverContext:
    def __init__(self, options=None):
        self.options = options
        self.driver = None

    def __enter__(self):
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.implicitly_wait(5)
        return self.driver

    def __exit__(self, exc_type, exc_value, traceback):
        if self.driver:
            self.driver.quit()


class ImgObject:
    def __init__(self, src: str, date: str, file: str, id: int):
        self.src = src
        self.date = date
        self.file = file
        self.id = id

    def to_json(self):
        return {"src": self.src, "name": f"{self.date}_{self.file}_{self.id}.jpg"}


def get_hrefs(driver: WebDriver, job_date: date):
    base_url = "https://mitsui-shopping-park.com"
    driver.get("https://mitsui-shopping-park.com/ec/shop/OPAQUECLIP/staff/12550")

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, "html.parser")

    items = soup.find_all("li", class_="item")

    href_list = []
    # 只提取 /ec/coordinate/\d+ 格式的链接
    pattern = re.compile(r"^/ec/coordinate/\d+$")
    for item in items:
        # 找到日期 %Y/%m/%d
        date_node = item.find("p", class_="date")
        if not date_node:
            continue
        date_str = date_node.text
        parsed_date = datetime.strptime(date_str, "%Y/%m/%d").date()
        if parsed_date != job_date:
            continue

        # 找到 <a> 标签
        link = item.find("a", class_="link")
        if link and "href" in link.attrs and pattern.match(link["href"]):
            href_list.append(base_url + link["href"])

    # 输出提取的 href 列表
    print(f"href_list: {href_list}")
    return href_list


def get_imgs_from_url(driver: WebDriver, url: str):
    print(f"Getting imgs from {url}")
    driver.get(url)

    # 等待页面中的 <p class="date"> 加载
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "date"))
    )

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, "html.parser")

    # get date
    date_text = soup.find("p", class_="date")
    if not date_text:
        raise ValueError("get_imgs_from_url: Date not found")
    date_text = date_text.text
    # transform "YYYY/MM/DD" to "YYYYMMDD"
    date = datetime.strptime(date_text, "%Y/%m/%d").strftime("%Y%m%d")

    target_div = soup.find("div", class_="swiper-wrapper")
    imgs = target_div.find_all("img")

    src_list = []
    img_objects = []
    for img in imgs:
        src = img.get("src")
        clean_src = src.split("?")[0]
        src_list.append(clean_src)
    src_list = list(set(src_list))
    for i, src in enumerate(src_list):
        img_objects.append(ImgObject(src, date, url.split("/")[-1], i))
    return img_objects


def get_imgs(driver: WebDriver, href_list):
    # img_objects is json like {"src": str, "name": str}
    img_objects = []
    for href in href_list:
        img_objects.extend(get_imgs_from_url(driver, href))

    # 转换为 JSON 格式
    return [img.to_json() for img in img_objects]


def download_upload_img(img_objects):
    for img in img_objects:
        print(f"Downloading: {img['src']}")
        print(f"Uploading: {img['name']}")
        # download img
        response = requests.get(img["src"], stream=True)
        response.raise_for_status()
        image_data = BytesIO(response.content)
        # upload img
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        files = {
            "document": (
                img["name"],
                image_data,
                "image/jpeg",
            )
        }
        data = {"chat_id": CHANNEL_ID}
        response = requests.post(url, data=data, files=files)
        print(response.json())
        time.sleep(1)


# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def main(cloud_event):
    try:
        # Print out the data from Pub/Sub, to prove that it worked
        print(base64.b64decode(cloud_event.data["message"]["data"]))
        if "message" in cloud_event.data and "data" in cloud_event.data["message"]:
            encoded_data = cloud_event.data["message"]["data"]
            decoded_data = base64.b64decode(encoded_data).decode("utf-8")
            data_dict = json.loads(decoded_data)
        else:
            print("Invalid Pub/Sub message format.")
            return
        today = date.today()
        job_date = today - timedelta(days=7)
        if "date" in data_dict:
            job_date = datetime.strptime(data_dict["date"], "%Y%m%d").date()

        print(f"Job date: {job_date.strftime('%Y%m%d')}")
        with WebDriverContext(options=chrome_options) as driver:
            href_list = get_hrefs(driver, job_date)
            img_objects = get_imgs(driver, href_list)

        download_upload_img(img_objects)
        print("Function executed successfully.")

    except Exception as e:
        print(f"Error occurred: {str(e)}")
