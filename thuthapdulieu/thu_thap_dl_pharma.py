from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from pymongo import MongoClient
import time
import re
import pandas as pd

# Kết nối MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['pharmacityDB2']
client.drop_database('pharmacityDB2')

products_collection = db['products']


columns = ["Product_ID", "Product_Name", "Price", "Link", "Likes", "Sold", "Product_Spec", "Product_origin"]
product_df = pd.DataFrame(columns=columns)

driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))

# Truy cập vào trang dược phẩm
driver.get("https://www.pharmacity.vn/duoc-pham")
time.sleep(3)


# Hàm cào dữ liệu từng sản phẩm
def scrape_product(product_link):
    driver.get(product_link)
    time.sleep(2)

    try:
        element = driver.find_element(By.XPATH, "//button[span[contains(text(), 'Hộp')]]")
        element.click()
    except:
        pass
    time.sleep(1)
    # Lấy mã sản phẩm
    try:
        product_code = driver.find_element(By.CSS_SELECTOR, "p.text-sm.leading-5.text-neutral-600").text
    except:
        product_code = "N/A"

    # Lấy tên sản phẩm
    try:
        product_name = driver.find_element(By.CSS_SELECTOR, "h1.text-neutral-900.font-semibold").text
    except:
        product_name = "N/A"

    # Lấy xuất xứ
    try:
        product_origin = driver.find_element(By.XPATH, '//*[@id="mainContent"]/div/div[1]/div[3]/div[1]/div[1]/div[2]/div/div[3]/div[9]/div[2]/div[5]/div').text
    except:
        product_origin = "N/A"


    # Lấy giá bán
    try:
        product_price = driver.find_element(By.XPATH, "//div[@id='mainContent']//div[contains(@class, 'grid-cols-1')]//div[contains(@class, 'font-bold') and contains(@class, 'text-primary-500')]").text
        # Sử dụng regex để loại bỏ các ký tự không phải số và dấu phân cách thập phân
        # Giữ lại số và dấu chấm (.)
        cleaned_price = re.search(r"\d+\.\d+", product_price)
        cleaned_price_str = cleaned_price.group()
        product_price = float(cleaned_price_str)*1000
    except:
        product_price = "N/A"

    # Lấy lượt yêu thích
    try:
        product_likes = driver.find_element(By.CSS_SELECTOR, 'div.space-x-1:nth-child(2) > p:nth-child(1)').text
        cleaned_likes_str = re.sub(r'[^\d.]', '', product_likes)
        product_likes = float(cleaned_likes_str) * 1000
    except:
        product_likes = "N/A"

    # Lấy số lượng bán
    try:
        product_sold = driver.find_element(By.CSS_SELECTOR, 'p.text-sm:nth-child(3)').text
        cleaned_sold_str = re.sub(r'[^\d.]', '', product_sold)
        product_sold = float(cleaned_sold_str) * 1000
    except:
        product_sold = "N/A"

    # Lấy quy cách
    try:
        product_spec = driver.find_element(By.CSS_SELECTOR, "h1.text-neutral-900.font-semibold").text
        ps = re.search(r'\((.*?)\)', product_spec)
        product_spec = ps.group(1)
    except:
        product_spec = "N/A"

    # Tạo từ điển lưu thông tin sản phẩm
    product_data = {
        "Product_ID": product_code,
        "Product_Name": product_name,
        "Price": product_price,
        "Likes": product_likes,
        "Sold": product_sold,
        "Product_Spec": product_spec,
        "Product_origin": product_origin,
    }

    products_collection.insert_one(product_data)
    print(f"Đã lưu: {product_name}")

# Hàm cuộn xuống cuối trang và nhấn nút xem thêm
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

# Lấy danh sách link sản phẩm
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

def export_to_excel():
    # Lấy tất cả dữ liệu từ MongoDB
    data = list(products_collection.find({}, {"_id": 0}))  # Loại bỏ trường _id

    # Chuyển đổi dữ liệu thành DataFrame
    df = pd.DataFrame(data)

    # Xuất dữ liệu ra file Excel
    df.to_excel("sp_pharma.xlsx", index=False)
    print("Đã xuất dữ liệu ra file sp_pharma.xlsx")


###########################################################################
load_all_products()
links = get_product_links()
print(f'Tổng số link sản phẩm {len(links)} \n')

# Cào dữ liệu từ trang web
for link in links:
    try:
        scrape_product(link)
    except:
        print("Lỗi")

export_to_excel()
driver.quit()

