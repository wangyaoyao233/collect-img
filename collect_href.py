import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

base_url = "https://mitsui-shopping-park.com"

driver = webdriver.Chrome()

driver.get("https://mitsui-shopping-park.com/ec/shop/OPAQUECLIP/staff/12550")

driver.implicitly_wait(0.5)

# 设置一个显式等待
wait = WebDriverWait(driver, 10)


# 高亮显示按钮以确认选择是否正确
def highlight_element(element):
    driver.execute_script("arguments[0].style.border='3px solid red'", element)


# loop to click more items button
try:
    while True:
        # 等待“显示更多”按钮加载并可点击
        show_more_button = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//button[.//span[contains(text(), "コーディネートをもっと見る")]]',
                )
            )
        )
        highlight_element(show_more_button)
        print(show_more_button.text)

        # 点击按钮
        show_more_button.click()

        # 等待数据加载，适当调整时间
        time.sleep(2)

except Exception as e:
    # 捕获没有更多数据或按钮消失的情况
    print("No more 'Show More' button or loading completed:", e)

html_content = driver.page_source
soup = BeautifulSoup(html_content, "html.parser")

items = soup.find_all("li", class_="item")

href_list = []
# 只提取 /ec/coordinate/\d+ 格式的链接
pattern = re.compile(r"^/ec/coordinate/\d+$")
for item in items:
    # 找到 <a> 标签
    link = item.find("a", class_="link")
    if link and "href" in link.attrs and pattern.match(link["href"]):
        href_list.append(base_url + link["href"])

# 输出提取的 href 列表
print(f"href_list: {len(href_list)}")

# 获取所有已经完成的href
try:
    with open("done_href_list.txt", "r") as f:
        done_list = [line.strip() for line in f]
except FileNotFoundError:
    print("done_href_list.txt not found, starting fresh.")
    done_list = []

# 去除已经完成的href
new_href_list = list(set(href_list) - set(done_list))

# store the href_list to a file
with open("href_list.txt", "w") as f:
    for href in new_href_list:
        f.write(f"{href}\n")

driver.quit()
