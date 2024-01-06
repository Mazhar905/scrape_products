
# Replace 'image_url' with the actual image URL you want to download
import requests
# from bs4 import BeautifulSoup
import os
import mysql.connector
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] -%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
user = 'mazhar'
password = 'Mazhar123'

url = 'https://www.outletdelgiocattolo.it/pimages/L-Era-Dei-Dinosauri-Triceratopo-thumbnail-16122.jpg'
# url = "https://example.com/image.jpg"


def save_image(url):
    response = requests.get(url)

    if response.status_code == 200:
        # Extract the image name from the URL
        image_name = url.split("/")[-1]

        # Create a folder if it doesn't exist
        folder_path = "product_images"
        os.makedirs(folder_path, exist_ok=True)

        # Save the image to the folder
        with open(os.path.join(folder_path, image_name), "wb") as file:
            file.write(response.content)
            print(f"Image '{image_name}' downloaded and saved.")
    else:
        print(
            f"Failed to download the image. Status code: {response.status_code}")


def get_url():
    sql_query = "SELECT Image_URL FROM product"
    url_list = []
    try:
        mydb = mysql.connector.connect(
            host="localhost", user=user, password=password, database="product_data")
        db = mydb.cursor()
        if mydb.is_connected():
            logging.info("Connected to the database")
        db = mydb.cursor()
        db.execute(sql_query)
        results = db.fetchall()

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
    for x in results:
        # ('https://www.outletdelgiocattolo.it/pimages/L-Era-Dei-Dinosauri-Carnotauro-extra-big-16119.jpg, https://www.outletdelgiocattolo.it/pimages/L-Era-Dei-Dinosauri-Carnotauro-thumbnail-16119.jpg, https://www.outletdelgiocattolo.it/pimages/L-Era-Dei-Dinosauri-Carnotauro-thumbnail-16120.jpg, https://www.outletdelgiocattolo.it/pimages/L-Era-Dei-Dinosauri-Carnotauro-thumbnail-16121.jpg',)
        for i in x:
            # https://www.outletdelgiocattolo.it/pimages/L-Era-Dei-Dinosauri-Carnotauro-extra-big-16119.jpg, https://www.outletdelgiocattolo.it/pimages/L-Era-Dei-Dinosauri-Carnotauro-thumbnail-16119.jpg, https://www.outletdelgiocattolo.it/pimages/L-Era-Dei-Dinosauri-Carnotauro-thumbnail-16120.jpg, https://www.outletdelgiocattolo.it/pimages/L-Era-Dei-Dinosauri-Carnotauro-thumbnail-16121.jpg
            url_list += i.split(',')
    print(url_list)
    return url_list

if __name__ == "__main__":
    for i in get_url():
        save_image(i)
