import requests
import time
import schedule
from bs4 import BeautifulSoup
from flask import Flask, request

app = Flask(__name__)

# Telegram bot setup
bot_token = "YOUR_BOT_TOKEN"
chat_id = None
symbol = None
interval = None
job_running = False

def send_telegram(message):
    """Send a message via Telegram bot."""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {"chat_id": chat_id, "text": message}
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("Message sent successfully.")
        else:
            print("Error: Failed to send message.")
    except Exception as e:
        print(f"Exception occurred while sending message: {e}")

def get_stock_price(symbol):
    """Fetch the stock price of the given symbol from Google Finance."""
    try:
        url = f"https://www.google.com/finance/quote/{symbol}:NSE"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        class1 = "YMlKec fxKbKc"
        p = soup.find(class_=class1).text.strip()[1:].replace(',', '')
        return float(p)
    except Exception as e:
        print(f"Error fetching stock price: {e}")
        return None

def job():
    """Scheduled job to fetch stock price and send a message."""
    global symbol
    price = get_stock_price(symbol)
    if price:
        message = f"🔔 Current 💲 price of {symbol}:NSE is : {price}/-\nThank you 😊."
        send_telegram(message)
    else:
        send_telegram("Error: Unable to retrieve stock price.")

@app.route(f"/{bot_token}", methods=["POST"])
def telegram_webhook():
    global chat_id, symbol, interval, job_running

    data = request.json
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "").strip().lower()

        if text == "/start":
            send_telegram("Welcome! Please enter the stock symbol (e.g., BPCL):")
        elif symbol is None:  # Waiting for stock symbol
            symbol = text.upper()
            send_telegram(f"Got it! Tracking stock: {symbol}. Now, enter the interval time in seconds:")
        elif interval is None:  # Waiting for interval time
            try:
                interval = int(text)
                send_telegram(f"Interval set to {interval} seconds. Starting stock price tracking...")
                schedule.every(interval).seconds.do(job).tag("stock_tracking")
                job_running = True
            except ValueError:
                send_telegram("Invalid interval. Please enter a valid number in seconds.")
        elif text == "/stop":
            schedule.clear("stock_tracking")
            job_running = False
            symbol = None
            interval = None
            send_telegram("Stock price tracking stopped. Send /start to begin again.")

    return "OK", 200

def run_scheduler():
    """Run the scheduler in the background."""
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    from threading import Thread

    # Start the scheduler in a separate thread
    scheduler_thread = Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    # Start Flask app to handle Telegram webhook
    app.run(port=5000)
