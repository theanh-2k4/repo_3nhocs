from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import pandas as pd

# Khởi tạo driver
driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))

# Tạo url
url = 'https://nhathuoclongchau.com.vn/thuc-pham-chuc-nang/vitamin-khoang-chat'

# Truy cập
driver.get(url)

# Tạm dừng khoảng 2 giây
time.sleep(1)

# Tìm phần tử body của trang để gửi phím mũi tên xuống
body = driver.find_element(By.TAG_NAME, "body")
time.sleep(3)

def load_all_products():
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        try:
            # Tìm nút "Xem thêm" và nhấn vào nó
            load_more_button = driver.find_element(By.XPATH, "//button[span[contains(text(), 'Xem thêm')]]")
            load_more_button.click()
            time.sleep(2)
        except:
            break

def get_product_links():
    product_links = []
    try:
        products = driver.find_elements(By.CSS_SELECTOR, "a:has(h3.line-clamp-2.h-10.text-sm.font-semibold)")
        for product in products:
            product_link = product.get_attribute("href")
            product_links.append(product_link)
            print(product_link)
    except Exception as e:
        print(f"Error: {e}")
    return product_links

load_all_products()
links = get_product_links()

# Tao cac list
stt = []
ten_san_pham = []
gia_ban = []
hinh_anh = []

# Tìm tất cả các button có nội dung là "Chọn mua"
buttons = driver.find_elements(By.XPATH, "//button[text()='Chọn mua']")

print(len(buttons))

# lay tung san pham
for i, bt in enumerate(buttons, 1):
    # Quay ngược 3 lần để tìm div cha
    parent_div = bt
    for _ in range(3):
        parent_div = parent_div.find_element(By.XPATH, "./..")  # Quay ngược 1 lần

    sp = parent_div
    # Lat ten sp
    try:
        tsp = sp.find_element(By.TAG_NAME, 'h3').text
    except:
        tsp = ''

    # Lat gia sp
    try:
        gsp = sp.find_element(By.CLASS_NAME, 'text-blue-5').text
    except:
        gsp = ''

    # Lat hinh anh
    try:
        ha = sp.find_element(By.TAG_NAME, 'img').get_attribute('src')
    except:
        ha = ''

    # Chi them vao ds neu co ten sp
    if (len(tsp) > 0):
        stt.append(i)
        ten_san_pham.append(tsp)
        gia_ban.append(gsp)
        hinh_anh.append(ha)

# Tạo df
df = pd.DataFrame({
    "STT": stt,
    "Tên sản phẩm": ten_san_pham,
    "Giá bán": gia_ban,
    "Hình ảnh": hinh_anh
})
df.to_excel('danh_sach_sp_3.xlsx', index=False)

driver.quit()