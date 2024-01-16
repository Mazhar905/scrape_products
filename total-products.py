dict = {
'accessori-travestimento' : 124,
'bambole-dolls' : 100,
'biciclette' : 5,
'costumi' : 341,
'dinosauri' : 18,
'elettronica-per-bambini' : 17,
'giochi-creativi' : 19,
'giochi-da-esterno' : 79,
'giochi-da-tavolo' : 128,
'giochi-di-costruzione' : 55,
"giochi-d-imitazione" : 35,
"giochi-educativi" : 93,
"monopattini-pattini" : 56,
"occhiali-da-sole" : 32,
"peluche":18,
"personaggi" : 70,
"playset-da-gioco" : 24,
"prima-infanzia": 52,
"puzzle" : 11,
"veicoli-giocattolo" :216,
"zaini-trolley" : 78,
"prodotti-outlet" :10
}

# for k, v in dict.items():
#     k = k.lower().replace('-')
    # print(k.lower())
    # dict[k.capitalize().replace('-', ' ')']
total_value= sum(dict.values())
print(total_value)
import mysql.connector
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] -%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
user = 'mazhar'
password = 'Mazhar123'
database = "product_data"
def product_links(table_name):
    try:
        mydb = mysql.connector.connect(
            host="localhost", user=user, password=password, database=database)
        db = mydb.cursor()
        if mydb.is_connected():
            logging.info("Connected to the database")
        sql = f"SELECT product_url FROM {table_name}"
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
    table_name = ['product', 'testing', 'product_bak', 'your_table']
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
            if not j in table_name:
                categories.append(j)
    # print(categories)
    print(len(categories))
    print(len(result))
    return categories

def dump_url(url):
    print(url)
    table = 'your_table'
    sql_query = f"INSERT INTO your_table (url) VALUES ('{url}')"
    # val = (url)
    try:
        mydb = mysql.connector.connect(
            host="localhost", user=user, password=password, database=database)
        db = mydb.cursor()
        if mydb.is_connected():
            logging.info("Connected to the database")
        db = mydb.cursor()
        db.execute(sql_query)
        mydb.commit()
        logging.info("Data inserted successfully.")
        # logging.info(db.rowcount, "record inserted.")
    except mysql.connector.Error as err:
        logging.error("Error: ", (err))
    finally:
        # Close the database connection when done
        if mydb.is_connected():
            db.close()
            mydb.close()
            logging.info("Connection closed.")


url = 0
for i in get_categories():
    print(i)
    for j in product_links(i):
        print(j)
        print(type(j))
        dump_url(j)
        url+=1

print(url)