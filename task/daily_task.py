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
import os

from dotenv import load_dotenv

load_dotenv()

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

    # 等待页面加载
    time.sleep(2)

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


def get_imgs_from_url(driver: WebDriver, url: str, job_date: date):
    print(f"Getting imgs from {url}")
    driver.get(url)

    imgs_set = set()
    while True:
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")
        target_div = soup.find("div", class_="swiper-wrapper")
        imgs = target_div.find_all("img")
        for img in imgs:
            src = img.get("src")
            clean_src = src.split("?")[0]
            imgs_set.add(clean_src)
        try:
            next_button = driver.find_element(By.CLASS_NAME, "swiper-button-next")
            next_button.click()
            time.sleep(1)
        except:
            break

    job_date = job_date.strftime("%Y%m%d")
    img_objects = []
    for i, img in enumerate(imgs_set):
        img_objects.append(ImgObject(img, job_date, url.split("/")[-1], i))

    # print
    for img in img_objects:
        print(img.to_json())

    return img_objects


def get_imgs(driver: WebDriver, href_list, job_date: date):
    # img_objects is json like {"src": str, "name": str}
    img_objects = []
    for href in href_list:
        img_objects.extend(get_imgs_from_url(driver, href, job_date))

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


# Main function
def main():
    try:
        today = date.today()
        job_date = today - timedelta(days=7)

        # 从 .env 中加载日期（如果提供）
        if "DATE" in os.environ:
            job_date = datetime.strptime(os.getenv("DATE"), "%Y%m%d").date()

        print(f"Job date: {job_date.strftime('%Y%m%d')}")
        with WebDriverContext(options=chrome_options) as driver:
            href_list = get_hrefs(driver, job_date)
            img_objects = get_imgs(driver, href_list, job_date)

        download_upload_img(img_objects)
        print("Script executed successfully.")

    except Exception as e:
        print(f"Error occurred: {str(e)}")


if __name__ == "__main__":
    main()
