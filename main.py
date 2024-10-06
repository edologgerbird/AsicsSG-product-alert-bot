import requests
from bs4 import BeautifulSoup
from telegram import Bot
import time
import os
from dotenv import load_dotenv
import logging
import asyncio

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
if CHAT_ID is not None:
    CHAT_ID = int(CHAT_ID)

# Configure logging
logging.basicConfig(filename='bot.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s:%(message)s')


URL = "https://www.asics.com/sg/en-sg/mens-running-shoes/?start=0&sz=300"

def get_product_list(URL):
    response = requests.get(URL)
    soup = BeautifulSoup(response.content, "html.parser")
    products = soup.find_all("a", class_="product-tile__link js-product-tile text-left")
    product_list_process = [process_product(product) for product in products]
    return product_list_process

def process_product(product):
    product_url = product.get("href")
    image_url = product.find("img").get('data-src')
    product_details = [
        e
        for e in product.get_text().split("\n")
        if e not in ["", " ", "\n", "New", "Exclusive", "Sale", "Quickview"]
        and "colour" not in e.lower()
        and "colours" not in e.lower()
        and "Men's Running Shoes" not in e
    ]
    product_name = product_details[0]
    product_price = product_details[1]

    return {
        "product_name": product_name,
        "product_price": product_price,
        "product_url": product_url,
        "image_url": image_url,
    }

def query_availability(products, product_name):
    query_results = []
    for product in products:
        if product_name.lower() in product["product_name"].lower():
            query_results.append(product)
        
    return query_results

async def send_message(message, image_url=None):
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        if image_url:
            await bot.send_photo(chat_id=CHAT_ID, photo=image_url, caption=message)
        else:
            await bot.send_message(chat_id=CHAT_ID, text=message)
        logging.info("Message sent to group.")
    except Exception as e:
        logging.error(f"Error sending message: {e}")

def format_message(query_results):
    output = []
    
    for result in query_results:
        message = ""
        message += f"Product: {result['product_name']}\nPrice: {result['product_price']}\nURL: {result['product_url']}\n\n"
        output.append((message, result['image_url']))
    return output


if __name__ == '__main__':
    products = get_product_list(URL)
    query_results = format_message(query_availability(products, "novablast"))
    print(query_results)
    for message, image_url in query_results:
        asyncio.run(send_message(message, image_url))
        time.sleep(0.5)
    # asyncio.run(send_message("Hello, this is a test message."))