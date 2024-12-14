from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
import json

# 设置无头模式
chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式

driver = webdriver.Chrome(options=chrome_options)

# 读取href_list.txt中所有的href
href_list = []
with open("href_list.txt", "r") as f:
    href_list = [line.strip() for line in f]


class ImgObject:
    def __init__(self, src: str, date: str, file: str, id: int):
        self.src = src
        self.date = date
        self.file = file
        self.id = id

    def to_json(self):
        return {"src": self.src, "name": f"{self.date}_{self.file}_{self.id}"}


img_objects = []


def get_imgs_from_url(url: str):
    print(f"Processing URL: {url}")
    driver.get(url)
    driver.implicitly_wait(0.5)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, "html.parser")

    # get date
    date_text = soup.find("p", {"class": "date"}).text
    # transform "YYYY/MM/DD" to "YYYYMMDD"
    date = datetime.strptime(date_text, "%Y/%m/%d").strftime("%Y%m%d")

    target_div = soup.find("div", {"class": "swiper-wrapper"})
    # imgs = target_div.find_all("img", {"data-v-59df6b70": True})
    imgs = target_div.find_all("img")

    src_list = []
    for img in imgs:
        src = img.get("src")
        clean_src = src.split("?")[0]
        src_list.append(clean_src)
    src_list = list(set(src_list))
    for i, src in enumerate(src_list):
        img_objects.append(ImgObject(src, date, url.split("/")[-1], i))


for href in href_list:
    try:
        get_imgs_from_url(href)
    except Exception as e:
        print(f"Failed to process URL {href.strip()}: {e}")

# 获取所有已经完成的img
try:
    with open("done_img_list.json", "r", encoding="utf-8") as f:
        done_list = json.load(f)
except FileNotFoundError:
    print("done_img_list.json not found, starting fresh.")
    done_list = []

# 去除已经完成的 img
new_img_objects = [img for img in img_objects if img.to_json() not in done_list]

# write to json, beautify it
with open("img_list.json", "w", encoding="utf-8") as f:
    json.dump(
        [img.to_json() for img in new_img_objects], f, ensure_ascii=False, indent=2
    )

# update done_href_list.txt
with open("done_href_list.txt", "a") as f:
    for href in href_list:
        f.write(f"{href}\n")

# clear href_list.txt
with open("href_list.txt", "w") as f:
    pass

driver.quit()
