from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import schedule
import time
import datetime
from pymongo import MongoClient
import requests
from flask import Flask
from dotenv import load_dotenv
import os
from threading import Thread

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Environment variables
MONGODB_URI = os.getenv('MONGODB_URI')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_GROUP_CHAT_ID = int(os.getenv('TELEGRAM_GROUP_CHAT_ID'))
PORT = int(os.getenv('PORT', 3000))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
SCRAPE_INTERVAL_MINUTES = int(os.getenv('SCRAPE_INTERVAL_MINUTES', 10))
PRODUCTS = [
    "iPhone 13 128",
    "iPhone 13 256",
    "iPhone 14 128",
    "iPhone 14 256",
    "iPhone 15 128",
    "iPhone 15 256",
]

# Desired companies
DESIRED_COMPANIES = [
    "Amazon",
    "Flipkart",
    "Vijay Sales",
    "Reliance Digital",
    "Jiomart",
    "Croma"
]

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/usr/bin/google-chrome"  # Path to Chrome binary in Docker
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def match_product_names(name1, name2):
    normalized_name1 = ''.join(e for e in name1 if e.isalnum() or e.isspace()).lower().replace('gb', "")
    normalized_name2 = ''.join(e for e in name2 if e.isalnum() or e.isspace()).lower().replace('gb', "")
    return normalized_name1 in normalized_name2

def scrape_google_shopping(driver, product):
    wait = WebDriverWait(driver, 10)
    results = set()
    
    try:
        temp = product.replace(" ", "+")
        driver.get(f"https://www.google.com/search?q={temp}")
        
        shopping_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-name='stores']")))
        shopping_tab.click()
        
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.AHFItb')))
        time.sleep(5)
        table = driver.find_element(By.CSS_SELECTOR, 'table.AHFItb')
        rows = table.find_elements(By.CSS_SELECTOR, 'tr.LvCS6d')
        
        for row in rows:
            cols = row.find_elements(By.CSS_SELECTOR, 'td.gWeIWe') 
            Product = cols[1].text
            Company = cols[0].text
            if match_product_names(product, Product) and any(desired_company.lower() in Company.lower() for desired_company in DESIRED_COMPANIES):
                Price = cols[3].text.replace("₹", "").replace(",", "")
                results.add((Company, Product, Price))
        return results
    except Exception as e:
        print(f"An error occurred while scraping: {e}")
        return results

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_GROUP_CHAT_ID,
        'text': message
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Telegram alert sent successfully")
    except requests.exceptions.RequestException as e:
        print(f"Error sending Telegram alert: {e}")

def save_results(results, product):
    try:
        client = MongoClient(MONGODB_URI, tls=True, tlsAllowInvalidCertificates=True)
        db = client['test']
        collection = db['iphone_prices']

        for result in results:
            existing_document = collection.find_one({'Company': result[0], 'Product': result[1]})
            if existing_document:
                if existing_document['Price'] != result[2]:
                    collection.update_one(
                        {'_id': existing_document['_id']},
                        {'$set': {'Price': result[2], 'Timestamp': datetime.datetime.now()}}
                    )
                    message = f"Price Update for:\nCompany: {result[0]}\nProduct: {result[1]}\nNew Price: {result[2]}"
                    send_telegram_alert(message)
            else:
                document = {
                    'Company': result[0],
                    'Product': result[1],
                    'Price': result[2],
                    'Timestamp': datetime.datetime.now()
                }
                message = f"New product added \nCompany : {result[0]}\nProduct : {result[1]}\nPrice : {result[2]}"
                send_telegram_alert(message)
                collection.insert_one(document)

        print(f"Scraping completed for {product}. Results saved to MongoDB.")
    except Exception as e:
        print(f"Error saving results: {e}")

def run_scraper(product):
    driver = setup_driver()
    results = scrape_google_shopping(driver, product)
    save_results(results, product)
    driver.quit()

def start_scraper():
    print(f"iPhone Price Scraper started. Will run every {SCRAPE_INTERVAL_MINUTES} minutes.")
    
    for product in PRODUCTS:
        schedule.every(SCRAPE_INTERVAL_MINUTES).minutes.do(run_scraper, product)

    # Run once immediately
    for product in PRODUCTS:
        run_scraper(product)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route("/", methods=["GET"])
def home():
    if not hasattr(app, 'scraper_thread') or not app.scraper_thread.is_alive():
        app.scraper_thread = Thread(target=start_scraper)
        app.scraper_thread.start()
    return "Scraper started", 200

if __name__ == "__main__":
    app.run(debug=DEBUG, port=PORT)
