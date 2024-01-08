import sys
import time
from selenium import webdriver
from bs4 import BeautifulSoup
import mysql.connector
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] -%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
user = 'mazhar'
password = 'Mazhar123'
database = "product_data"


def insert_product_data(data):
    first_iteration = True
    print(len(data['Image Src']))
    # Removed 'EAN'
    for i in range(len(data['Image Src'])):
        if first_iteration:
            print("First Image")
            sql_query = """
            INSERT INTO product (
                Handle, Title, Body, Vendor, Product_Category, Type, Tags, Published,
                Option1_Name, Option1_Value, Option2_Name, Option2_Value, Option3_Name, Option3_Value,
                Variant_SKU, Variant_Grams, Variant_Inventory_Qty, Variant_Price,
                Variant_Compare_At_Price, Variant_Barcode, Image_Src, Image_Position,
                Image_Alt_Text, Variant_Weight_Unit, Status, url, Image_URL, Collection, Image_Downloaded, Features
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s)
            """
            # Extract values from the 'data' dictionary
            # data['Image Position'][i],
            val = (
                data['Handle'], data['Title'], data['Body'], data['Vendor'], data['Product Category'],
                data['Type'], data['Tags'], data['Published'], data['Option1 Name'],
                data['Option1 Value'], data['Option2 Name'], data['Option2 Value'],
                data['Option3 Name'], data['Option3 Value'], data['SKU'],
                data['Variant Grams'], data['Variant Inventory Qty'], data['Price'],
                data['Sale Price'], data['Variant Barcode'], data['Image Src'][i],
                i+1,
                data['Image Alt Text'][i], data['Variant Weight Unit'],
                data['Status'], data['URL'], data['Image URL'][i], data['Collection'], data['Image Downloaded'], data['Features']
            )
            first_iteration = False
        else:  # Add a comma to separate each row of the VALUES clause
            print("Others Image")
            sql_query = """
            INSERT INTO product (
                Handle,Image_Src, Image_Position,Image_Alt_Text, Image_URL, Image_Downloaded
            ) VALUES (%s, %s, %s, %s, %s, %s)    
                """
            val = (
                data['Handle'], data['Image Src'][i], i +
                1, data['Image Alt Text'][i], data['Image URL'][i], data['Image Downloaded']
            )
        try:
            mydb = mysql.connector.connect(
                host="localhost", user=user, password=password, database=database)
            db = mydb.cursor()
            if mydb.is_connected():
                logging.info("Connected to the database")
            db = mydb.cursor()
            sql = "SELECT COUNT(*) FROM product where Image_Downloaded = 'F'"
            db.execute(sql)
            record_count = db.fetchone()[0]
            print(record_count)
            db.execute(sql_query, val)
            mydb.commit()
            logging.info("Data inserted successfully.")
            # logging.info(db.rowcount, "record inserted.")
        except mysql.connector.Error as err:
            logging.error("Error: {}".format(err))
        finally:
            # Close the database connection when done
            if mydb.is_connected():
                db.close()
                mydb.close()
                logging.info("Connection closed.")
    return record_count


def product_exists(url):
    try:
        mydb = mysql.connector.connect(
            host="localhost", user=user, password=password, database=database
        )
        # Using context manager to ensure cursor is closed even if an exception occurs
        with mydb.cursor() as db:
            table_name = 'product'
            query = f"SELECT * FROM {table_name} WHERE url = %s"
            db.execute(query, (url,))
            result = db.fetchone()
            exists = result is not None
            # print(exists)
            return exists
    except mysql.connector.Error as err:
        logging.error(f"Error: {err}")
    finally:
        if mydb.is_connected():
            mydb.close()
            logging.info("Connection closed.")


def data_dump(data):
    product_id = insert_product_data(data)
    logging.info(f"Product inserted with ID: {product_id}")
    return product_id


def scrape_data(driver, url):
    try:
        driver.get(url)
        page = driver.page_source
    except Exception as e:
        logging.error(
            f"{url}, {e}")
    product_details, url_list = product_data(page, url)
    dump = data_dump(product_details)
    print("Total records: ", dump)
    # if dump >= 150:
    #     print("Record count is greater than or equal to 200.")
    #     return
    # if url_list:
    #     for i in url_list:
    #         print(product_exists(i))
    #         if product_exists(i):  # Checking the Duplication
    #             next_url = None
    #             logging.info(
    #                 f"The Product '{i}' already exists in the database.")
    #             logging.info(f"We have the data of this product {i}")
    #             continue
    #         else:
    #             next_url = i
    #             logging.info(f'Continue with this {i}')
    #             break
    # if next_url:
    #     scrape_data(driver, next_url)


def product_data(page, product_url):
    soup = BeautifulSoup(page, 'html.parser')
    print(product_url)
    title = soup.h1.get_text()
    description = soup.find('div', class_="card-body inner-link-underline")
    description = f'{description}'
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
    charc_dict = {row.find('td').text: row.find('td').find_next('td').text for row in table_rows}
    try:
        feaures_table = soup.select('#p-add-to-cart-form table tbody.product-item-features-tbody tr')
        features_dict = {row.find('td').text: row.find('td').find_next('td').text for row in feaures_table}
        if len(features_dict):
            features = 'T'
        else: 
            features = 'F'
    except Exception as e:
        features = 'F'        
        logging.error(e)

    product_code = soup.find('span', id='p-attr-code').text
    availability = soup.find('span', id='p-availability').text
    a_tags = soup.select('div p.product-list-name a')
    url = 'https://www.outletdelgiocattolo.it/'
    p_image = 'https://www.outletdelgiocattolo.it/pimages/'
    new_domain = 'https://efc1e8-2.myshopify.com/cdn/shop/files/'
    href_list = [url+a.get('href') for a in a_tags]
    pri_image = soup.select('div.product-item-img img')
    primary_image_url = pri_image[0].get('src') if pri_image else None
    primary_image_alt_text = pri_image[0].get('alt') if pri_image else None
    imag_tags = soup.select('div.product-item-gallery.zoogallery img')
    image_url = [primary_image_url]+[img.get('src') for img in imag_tags]
    img_alt_text = [primary_image_alt_text] + \
        [img.get('alt') for img in imag_tags]
    image_src = [primary_image_url.replace(
        p_image, new_domain)]+[img.get('src').replace(p_image, new_domain) for img in imag_tags]
    type = ''
    tags = ''
    published = True
    option1_name = 'Title'
    option1_value = 'Default Title'
    option2_name = ''
    option2_value = ''
    option3_name = ''
    option3_value = ''
    variant_grams = 1
    variant_barcode = ''
    variant_inventery_qty = 10
    weight_unit = 'kg'
    product_detail = {}
    product_detail['Handle'] = title.replace(' ', '-').lower()
    product_detail['Title'] = '"'+title+'"'
    product_detail['Body'] = '"'+description.replace('"', '""')+'"'
    # print(product_detail['Body'])
    # product_detail['Body'] = description.replace('\n', '').replace('\r', '')
    # Brand
    product_detail['Vendor'] = charc_dict['Marca'] if 'Marca' in charc_dict else None
    # category
    product_detail['Product Category'] = charc_dict['Categoria'] if 'Categoria' in charc_dict else None
    product_detail['Collection'] = "'" + charc_dict['Categoria'].upper() + \
        "'" if 'Categoria' in charc_dict else None
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
    product_detail['Price'] = float(
        regular_price.replace(',', '.').replace('€ ', '').strip()) if regular_price else float(regular_price.replace(',', '.'))
    product_detail['Sale Price'] = float(
        sale_price.replace(',', '.')) if sale_price else sale_price
    product_detail['Variant Barcode'] = variant_barcode
    product_detail['Image Src'] = image_src
    # product_detail['Image Position'] = 1
    product_detail['Image URL'] = image_url
    product_detail['Image Alt Text'] = img_alt_text
    product_detail['Image Downloaded'] = 'F'
    product_detail['Variant Weight Unit'] = weight_unit
    product_detail['Status'] = 'active'
    product_detail['Availability'] = availability
    product_detail['Features'] = features
    # product_detail['EAN'] = charc_dict['EAN'] if charc_dict['EAN'] else None
    product_detail['URL'] = product_url
    print(product_detail)
    return product_detail, href_list


def main(product_url):
    if not product_exists(product_url):
        start_time = time.time()
        # logging.info("INFO ---------- Starting Time:",time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time)))
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
        scrape_data(driver, product_url)
        driver.quit()
    else:
        logging.info(
            f"The product with URL '{product_url}' already exists in the database. Try with another one....")
    end_time = time.time()
    # logging.info("INFO ---------- Ending Time:",time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time)))
    # duration = end_time - start_time
    # logging.info("Execution Time (in seconds):", duration)
    # logging.info("Execution Time (in minutes):", duration / 60)

def product_links(table_name):
    try:
        mydb = mysql.connector.connect(
            host="localhost", user=user, password=password, database=database)
        db = mydb.cursor()
        if mydb.is_connected():
            logging.info("Connected to the database")
        db = mydb.cursor()
        sql = f"SELECT product_url FROM {table_name} WHERE scrape = 'F'"
        db.execute(sql)
        result = db.fetchall()
        logging.info("Data inserted successfully.")
        # logging.info(db.rowcount, "record inserted.")
    except mysql.connector.Error as err:
        logging.error("Error: {}".format(err))
    finally:
        # Close the database connection when done
        if mydb.is_connected():
            db.close()
            mydb.close()
            logging.info("Connection closed.")
    product_urls = []
    for i in result:
        for j in i:
            # print(i)
            if not table_name == j:
                product_urls.append(j)
    # print(categories)
    print(len(product_urls))
    print(len(result))
    return product_urls


def get_categories():
    table_name = 'product'
    try:
        mydb = mysql.connector.connect(
            host="localhost", user=user, password=password, database=database)
        db = mydb.cursor()
        if mydb.is_connected():
            logging.info("Connected to the database")
        db = mydb.cursor()
        sql = f"SHOW TABLES"
        db.execute(sql)
        result = db.fetchall()
        print(result)
        logging.info("Data inserted successfully.")
        # logging.info(db.rowcount, "record inserted.")
    except mysql.connector.Error as err:
        logging.error("Error: {}".format(err))
    finally:
        # Close the database connection when done
        if mydb.is_connected():
            db.close()
            mydb.close()
            logging.info("Connection closed.")
    categories = []
    for i in result:
        for j in i:
            print(i)
            if not table_name == j:
                categories.append(j)
    # print(categories)
    print(len(categories))
    print(len(result))
    return categories


def add_trailing_slash(url):
    # Check if the URL doesn't end with "/"
    if not url.endswith('/'):
        # If not, append "/"
        url += '/'
    return url

def scraped_product(table_name, url):
    try:
        mydb = mysql.connector.connect(
            host="localhost", user=user, password=password, database=database)
        db = mydb.cursor()
        if mydb.is_connected():
            logging.info("Connected to the database")
        db = mydb.cursor()
        sql = f"UPDATE {table_name} SET scrape = 'T' WHERE product_url = '{url}'"
        db.execute(sql)
        mydb.commit()
        # result = db.fetchall()
        logging.info("Update the Scrape COlumn successfully.")
        # logging.info(db.rowcount, "record inserted.")
    except mysql.connector.Error as err:
        logging.error("Error: {}".format(err))
    finally:
        # Close the database connection when done
        if mydb.is_connected():
            db.close()
            mydb.close()
            logging.info("Connection closed.")
    return 

if __name__ == "__main__":
    categories = get_categories()
    for i in categories:
        product_urls = product_links(i)
        for j in product_urls:
            print(j)
            n = add_trailing_slash(j)
            main(n)
            scraped_product(i, j)

