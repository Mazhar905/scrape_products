import sys
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from pydal import DAL, Field
import mysql.connector
# import logging

# Set up logging
# logging.basicConfig(level=logging.DEBUG)
user = 'mazhar'
password = 'Mazhar123'

mydb = mysql.connector.connect(
    host="localhost",
    user=user,
    password=password,
    database="product_data"
)
db = mydb.cursor()


def insert_product_data(db, data):
    sql_query = """
    INSERT INTO product (
        Title, Body, Vendor, Product_Category, Type, Tags, Published,
        Option1_Name, Option1_Value, Option2_Name, Option2_Value, Option3_Name, Option3_Value,
        Variant_SKU, Variant_Grams, Variant_Inventory_Qty, Variant_Price,
        Variant_Compare_At_Price, Variant_Barcode, Image_Src, Image_Position,
        Image_Alt_Text, Variant_Weight_Unit, Status, EAN, url
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    # Extract values from the 'data' dictionary
    values = (
        data['Title'], data['Body'], data['Vendor'], data['Product Category'],
        data['Type'], data['Tags'], data['Published'], data['Option1 Name'],
        data['Option1 Value'], data['Option2 Name'], data['Option2 Value'],
        data['Option3 Name'], data['Option3 Value'], data['SKU'],
        data['Variant Grams'], data['Variant Inventory Qty'], data['Price'],
        data['Sale Price'], data['Variant Barcode'], data['Image Src'],
        data['Image Position'], data['Image Alt Text'], data['Variant Weight Unit'],
        data['Status'], data['EAN'], data['URL']
    )

    try:
        db.execute(sql_query, values)
        db.commit()
        print("Data inserted successfully.")
    except Exception as e:
        print(f"Error: {e}")
        # db.rollback()
    finally:
        db.close()


def product_exists(db, url):
    table_name = 'product'
    query = f"SELECT * FROM {table_name} WHERE url = %s"
    db.execute(query, (url,))
    result = db.fetchone()
    exists = result is not None
    db.close()
    print(exists)
    return exists


def data_dump(data):
    # create_table(db)
    product_id = insert_product_data(db, data)
    print(f"Product inserted with ID: {product_id}")
    return True


def scrape_data(driver, url):
    try:
        driver.get(url)
        page = driver.page_source
    except Exception as e:
        print(
            f"{url}")
    product_details, url_list = product_data(page, url)
    dump = data_dump(product_details)
    if url_list:
        for i in url_list:
            print(product_exists(db, i))
            if product_exists(db, i):  # Checking the Duplication
                next_url = None
                print(f"The Product '{i}' already exists in the database.")
                print(f"We have the data of this product {i}")
                continue
            else:
                next_url = i
                print(f'Continue with this {i}')
                break
    if next_url:
        scrape_data(driver, next_url)


def product_data(page, product_url):
    soup = BeautifulSoup(page, 'html.parser')
    title = soup.h1.get_text()
    description = soup.find('div', class_="card-body inner-link-underline")
    price1 = soup.find('strike', class_='p-price-strike')
    price2 = soup.find('span', class_='p-price-val')
    if price1.text:
        regular_price = price1.text
        sale_price = price2.text
    else:
        regular_price = price2.text
        sale_price = None
    # Find the table rows (tr) inside the specified div
    table_rows = soup.select('#p-acc-details-d2 .card-body table tbody tr')
    # Create a dictionary from the table rows
    charc_dict = {row.find('td').text: row.find(
        'td').find_next('td').text for row in table_rows}
    product_code = soup.find('span', id='p-attr-code').text
    availability = soup.find('span', id='p-availability').text
    a_tags = soup.select('div p.product-list-name a')
    url = 'https://www.outletdelgiocattolo.it/'
    href_list = [url+a.get('href') for a in a_tags]
    pri_image = soup.select('div.product-item-img img')
    primary_image_url = pri_image[0].get('src') if pri_image else None
    primary_image_alt_text = pri_image[0].get('alt') if pri_image else None
    print(primary_image_url)
    imag_tags = soup.select('div.product-item-gallery.zoogallery img')
    gallery_img = [img.get('src') for img in imag_tags]
    img_alt_text = [primary_image_alt_text] + \
        [img.get('alt') for img in imag_tags]
    gallery_img = [primary_image_url] + gallery_img
    print(img_alt_text)
    print(gallery_img)
    type = ''
    tags = ''
    published = True
    option1_name = ''
    option1_value = ''
    option2_name = ''
    option2_value = ''
    option3_name = ''
    option3_value = ''
    variant_grams = ''
    variant_barcode = ''
    variant_inventery_qty = ''
    weight_unit = ''
    product_detail = {}
    product_detail['Title'] = title
    product_detail['Body'] = description
    # Brand
    product_detail['Vendor'] = charc_dict['Marca'] if charc_dict['Marca'] else None
    # category
    product_detail['Product Category'] = charc_dict['Categoria'] if charc_dict['Categoria'] else None
    product_detail['Type'] = type
    product_detail['Tags'] = tags
    product_detail['Published'] = published
    product_detail['Option1 Name'] = option1_name
    product_detail['Option1 Value'] = option1_value
    product_detail['Option2 Name'] = option2_name
    product_detail['Option2 Value'] = option2_value
    product_detail['Option3 Name'] = option3_name
    product_detail['Option3 Value'] = option3_value
    product_detail['SKU'] = product_code
    product_detail['Variant Grams'] = variant_grams
    product_detail['Variant Inventory Qty'] = variant_inventery_qty
    product_detail['Price'] = regular_price
    product_detail['Sale Price'] = sale_price
    product_detail['Variant Barcode'] = variant_barcode
    product_detail['Image Src'] = gallery_img
    product_detail['Image Position'] = 1
    product_detail['Image Alt Text'] = img_alt_text
    product_detail['Variant Weight Unit'] = weight_unit
    product_detail['Status'] = 'active'
    product_detail['Availability'] = availability
    product_detail['EAN'] = charc_dict['EAN'] if charc_dict['EAN'] else None
    product_detail['URL'] = product_url
    print(product_detail)
    return product_detail, href_list


def main(product_url):
    start_time = time.time()
    print("INFO ---------- Starting Time:",
          time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time)))
    # create_table(db)
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument("--incognito")
    options.add_argument("--nogpu")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,1280")
    options.add_argument("--no-sandbox")
    options.add_argument("--enable-javascript")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-blink-features=AutomationControlled')
    # ua = UserAgent()
    # userAgent = ua.random
    driver = webdriver.Chrome(options=options)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    # driver.execute_cdp_cmd('Network.setUserAgentOverride', {
    #    "userAgent": userAgent})
    if not product_exists(db, product_url):
        scrape_data(driver, product_url)
    else:
        print(
            f"The product with URL '{product_url}' already exists in the database. Try with another one....")
    driver.quit()
    end_time = time.time()
    print("INFO ---------- Ending Time:",
          time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time)))
    duration = end_time - start_time
    print("Execution Time (in seconds):", duration)
    print("Execution Time (in minutes):", duration / 60)


if __name__ == "__main__":
    # product_url = "https://www.outletdelgiocattolo.it/it/casco-da-cantiere/"
    product_url = "https://www.outletdelgiocattolo.it/it/-dinosauro-furious-t-rex-/#22:315"
    # product_url = "https://www.outletdelgiocattolo.it/it/monopattino-paw-patrol-twist-roll-3-ruote/"
    # website_url = 'https://www.dextools.io/app/en/ether/pair-explorer/'
    main(product_url)
