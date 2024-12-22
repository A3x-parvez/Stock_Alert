import requests
import time
import schedule
from bs4 import BeautifulSoup
import keys

symbol="BPCL"
url1="https://www.google.com/finance/quote/BPCL:NSE"

def get_stock_price(symbol):
    
        url = f"https://www.google.com/finance/quote/{symbol}:NSE"
        print(f"Fetching stock price for {symbol} from: {url}")
        
        response = requests.get(url)
        print(f"Fetching stock price for {symbol}... Status Code: {response.status_code}")
        soup=BeautifulSoup(response.text,'html.parser')
        class1="YMlKec fxKbKc"
        p=soup.find(class_=class1).text.strip()[1:].replace(',', '')
        price=float(p)
        if response.status_code == 200:
            return price
        else:
            print("Something went Wrong.")


# Telegram bot setup
bot_token = keys.BOT_API
chat_id = keys.CHAT_ID

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {"chat_id": chat_id, "text": message}
        response = requests.post(url, data=data)
        print(f"Sending message... Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Message sent successfully.")
        else:
            print("Error: Failed to send message.")
    except Exception as e:
        print(f"Exception occurred while sending message: {e}")

def job():
    price = get_stock_price("BPCL")  # BPCL stock symbol
    if price:
        message = f"🔔Current 💲price of BPCL:NSE is : {price}/-\nThank you😊."
    else:
        message = "Error: Unable to retrieve stock price."
    send_telegram(message)

schedule.every(1/30).minutes.do(job)

print("Starting the scheduler...")
send_telegram(f"Welcome😍 to stock price tracker for BPCL:NSE .(Developed by Parvez.)")
while True:
    schedule.run_pending()
    time.sleep(1)
