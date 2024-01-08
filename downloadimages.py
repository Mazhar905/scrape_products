import requests
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


def save_image(folder_path, url):
    print(url)
    # Extract the image name from the URL
    image_name = url.split("/")[-1]
    tag = image_name.split(".")[-1]
    print(tag)
    if tag == 'svg':
        return
    response = requests.get(url)

    if response.status_code == 200:
        # Create a folder if it doesn't exist
        os.makedirs(folder_path, exist_ok=True)

        # Save the image to the folder
        with open(os.path.join(folder_path, image_name), "wb") as file:
            file.write(response.content)
            print(f"Image '{image_name}' downloaded and saved.")
        check_image(url)

    else:
        print(
            f"Failed to download the image. Status code: {response.status_code}")


def check_image(url):
    # print(url)
    sql = """UPDATE product SET Image_Downloaded = 'T' WHERE Image_URL = %s"""
    mydb = mysql.connector.connect(
        host="localhost", user=user, password=password, database="product_data")
    db = mydb.cursor()
    db.execute(sql, (url,))
    print("Done True")
    mydb.commit()
    mydb.close()


def get_url():
    sql_query = "SELECT Image_URL FROM product WHERE Image_Downloaded = 'F'"
    sql = "SELECT COUNT(*) FROM product"
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
        db.execute(sql)
        record_count = db.fetchone()[0]
        # logging.info("Data inserted successfully.")
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
    print(len(url_list))
    print(record_count)
    return url_list


if __name__ == "__main__":
    urls = get_url()
    # Get the current working directory
    current_directory = os.getcwd()
    # Using list comprehension to create chunks of five elements
    chunks = [urls[i:i+180] for i in range(0, len(urls), 180)]
    # print(chunks)
    print(len(chunks[0]))
    # Creating a dictionary and assigning keys as 'chunk1', 'chunk2', ...
    my_dict = {f'images_{i + 1}': chunk for i, chunk in enumerate(chunks)}
    # print(my_dict)
    for k, v in my_dict.items():
        # Create the full path for the new folder
        new_folder_path = os.path.join(current_directory, k)
        # Check if the folder already exists
        if not os.path.exists(new_folder_path):
            # Create the folder
            os.makedirs(new_folder_path)
            print(f"Folder '{k}' created successfully at: {new_folder_path}")
        elif os.path.exists(new_folder_path):
            new_folder_path = os.path.join(current_directory, k+'-50')
            os.makedirs(new_folder_path)
            print(f"Folder '{k+'-50'}' created successfully at: {new_folder_path}")
        else:
            print(f"Folder '{k}' already exists at: {new_folder_path}")
        for i in v:
            print(v.index(i))
            save_image(new_folder_path,i)
