import sys
import time
from selenium import webdriver
from bs4 import BeautifulSoup
import mysql.connector
import logging

# Set up logging
# logging.basicConfig(level=logging.DEBUG,format='%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] -%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
user = 'mazhar'
password = 'Mazhar123'
database = "product_data"


def insert_product_data(table_name, url):
    sql_query = f"""
        INSERT INTO {table_name} (
            product_url, scrape
        ) VALUES (%s, %s)    
            """
    val = (url, 'F')
    try:
        mydb = mysql.connector.connect(
            host="localhost", user=user, password=password, database=database)
        db = mydb.cursor()
        if mydb.is_connected():
            logging.info("Connected to the database")
        db = mydb.cursor()
        sql = f"SELECT COUNT(*) FROM {table_name}"
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


def create_table(table_name):
    sql = f"""CREATE TABLE IF NOT EXISTS {table_name} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        product_url VARCHAR(255),
        scrape VARCHAR(255),
        UNIQUE (id),
        UNIQUE (product_url)
        )"""
    try:
        mydb = mysql.connector.connect(
            host="localhost", user=user, password=password, database=database
        )
        # Using context manager to ensure cursor is closed even if an exception occurs
        with mydb.cursor() as db:
            table_name = 'product'
            db.execute(sql)
            # Commit Changes
            mydb.commit()
            db.close()
            logging.info(f"{table_name} table created successfully.")
    except mysql.connector.Error as err:
        logging.error(f"Error creating {table_name} table: {str(e)}")
    finally:
        if mydb.is_connected():
            mydb.close()
            logging.info("Connection closed.")


def data_dump(table_name, data):
    create_table(table_name)
    row = 0
    for i in data:
        row += insert_product_data(table_name, i)
    return row


def extrct_page_url(driver, url):
    try:
        driver.get(url)
        page = driver.page_source
    except Exception as e:
        logging.error(
            f"{url}, {e}")
    soup = BeautifulSoup(page, 'html.parser')
    # Extracting links from the list items
    element = soup.find('form', class_='catalog-pagination-form')
    links = [url]
    # print(element)
    if element:
        total_page = int(element.text.split('di')[-1].strip())
        print(total_page)
        for i in range(total_page+1):
            if i == 0 or i == 1:
                continue
            links.append(f"{url}page-{i}/")
    else:
        links += [a['href']
                  for a in soup.select('.catalog-pagination ul li a')]
        # Remove duplicates
        links = list(set(links))

    # print(unique_list)
    # print(links)
    return links


def product_links(driver, url):
    site_url = "https://www.outletdelgiocattolo.it/"
    try:
        driver.get(url)
        page = driver.page_source
    except Exception as e:
        logging.error(
            f"{url}, {e}")

    soup = BeautifulSoup(page, 'html.parser')
    links = [site_url+a['href'] for a in soup.select('.product-list-info p a')]
    print(f"Total links {len(links)} on this URl : {url}")
    return links


def main(product_url):
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
    cat_link = category_link(driver, url)
    dict = {
        'accessori-travestimento': 124,
        'bambole-dolls': 100,
        'biciclette': 5,
        'costumi': 341,
        'dinosauri': 18,
        'elettronica-per-bambini': 17,
        'giochi-creativi': 19,
        'giochi-da-esterno': 79,
        'giochi-da-tavolo': 128,
        'giochi-di-costruzione': 55,
        "giochi-d-imitazione": 35,
        "giochi-educativi": 93,
        "monopattini-pattini": 56,
        "occhiali-da-sole": 32,
        "peluche": 18,
        "personaggi": 70,
        "playset-da-gioco": 24,
        "prima-infanzia": 52,
        "puzzle": 11,
        "veicoli-giocattolo": 216,
        "zaini-trolley": 78,
        "prodotti-outlet": 10
    }
    for i in cat_link:
        category = i.split('/')[-2]
        print(category)
        if i == 1:
            break
        if table_exists(category) and dict[category] == total_rows(category):
            print("The Table is Already Exist and all the product urls are present")
            continue
        page_links = extrct_page_url(driver, i)
        if '-' in category:
            category = category.replace('-', '_')
        product_urls = []
        for i in page_links:
            links = (product_links(driver, i))
            for i in links:
                product_urls.append(i)
        print(product_urls)
        data_dump(category, product_urls)
        print(product_urls)
        print(len(product_urls))
    driver.quit()
    end_time = time.time()
    # logging.info("INFO ---------- Ending Time:",time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time)))
    duration = end_time - start_time
    # logging.info("Execution Time (in seconds):", duration)
    # logging.info("Execution Time (in minutes):", duration / 60)


def total_rows(table_name):
    try:
        mydb = mysql.connector.connect(
            host="localhost", user=user, password=password, database=database)
        db = mydb.cursor()
        if mydb.is_connected():
            logging.info("Connected to the database")
        db = mydb.cursor()
        sql = f"SELECT COUNT(*) FROM {table_name}"
        db.execute(sql)
        record_count = db.fetchone()[0]
        print(record_count)
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
    print('Total rows', record_count)
    return record_count


def table_exists(table_name):
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
    
    if table_name in result:
            print("The Table is already exists")
            return True
    else:
        return False


def category_link(driver, url):
    site_url = "https://www.outletdelgiocattolo.it/"
    try:
        driver.get(url)
        page = driver.page_source
    except Exception as e:
        logging.error(
            f"{url}, {e}")
    soup = BeautifulSoup(page, 'html.parser')
    category_links = [site_url+a['href']
                      for a in soup.select('.list-unstyled.menu3dd-left .text-truncate')]
    print(f"Total links {len(category_links)} on this Site")
    return category_links


if __name__ == "__main__":
    url = "https://www.outletdelgiocattolo.it/it/costumi/"
    main(url)
