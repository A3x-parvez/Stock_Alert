import requests
import time
import schedule
from bs4 import BeautifulSoup
import telebot
import threading
import keys

# Telegram bot setup
bot_token = keys.BOT_API
bot = telebot.TeleBot(bot_token)

# Global dictionaries for user-specific state
user_data = {}
user_threads = {}
thread_lock = threading.Lock()

# Function to fetch stock price
def get_stock_price(symbol):
    url = f"https://www.google.com/finance/quote/{symbol}:NSE"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            class1 = "YMlKec fxKbKc"
            price_text = soup.find(class_=class1).text.strip()[1:].replace(',', '')
            return float(price_text)
        else:
            print(f"Failed to fetch stock price for {symbol}. HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching stock price for {symbol}: {e}")
        return None

# Function to send a Telegram message
def send_telegram(chat_id, message):
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {"chat_id": chat_id, "text": message}
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print(f"Failed to send message to {chat_id}. HTTP {response.status_code}")
    except Exception as e:
        print(f"Error sending message to {chat_id}: {e}")

# Function to start a user-specific scheduler
def start_schedule(chat_id, stock_name, duration):
    with thread_lock:
        # Stop any existing tracker for the user
        if chat_id in user_threads:
            stop_tracker(chat_id)

        # Create a new scheduler for this user
        user_scheduler = schedule.Scheduler()

        # Add job to this user's scheduler
        user_scheduler.every(duration).minutes.do(fetch_and_notify, chat_id, stock_name)

        # Start a thread to run this user's scheduler
        def run_user_scheduler():
            while True:
                user_scheduler.run_pending()
                time.sleep(1)

        # Store the new thread and scheduler for this user
        user_threads[chat_id] = threading.Thread(target=run_user_scheduler, daemon=True)
        user_threads[chat_id].start()

        # Update user data
        user_data[chat_id] = {
            "stock_name": stock_name,
            "time_duration": duration,
            "old_price": None,
        }

        send_telegram(chat_id, f"Tracking stock {stock_name} every {duration} minutes.")

# # Stop tracking for a specific user
# def stop_tracker(chat_id):
#     with thread_lock:
#         if chat_id in user_threads:
#             # Stop the thread gracefully
#             user_threads[chat_id].join(timeout=1)
#             del user_threads[chat_id]

#         # Clear user-specific scheduler
#         schedule.clear(chat_id)

#         # Reset user state
#         if chat_id in user_data:
#             del user_data[chat_id]

#         send_telegram(chat_id, "Stock tracker stopped.")


# Stop tracking for a specific user
def stop_tracker(chat_id):
    with thread_lock:
        if chat_id in user_threads:
            # Stop the thread gracefully
            user_threads[chat_id].join(timeout=1)
            del user_threads[chat_id]

        # Clear the user's scheduled jobs (specific job for that user)
        schedule.clear()  # This clears all scheduled jobs globally; we'd ideally cancel specific jobs if using a custom approach

        # Reset user-specific state data
        if chat_id in user_data:
            del user_data[chat_id]

        # Send confirmation message
        send_telegram(chat_id, "Stock tracker stopped.")

# Handling the '/stop' command
@bot.message_handler(commands=['stop'])
def stop(message):
    chat_id = message.chat.id
    stop_tracker(chat_id)

# Handling the '/start' command
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    stop_tracker(chat_id)  # Clear any existing tracker before starting a new one
    bot.send_message(chat_id, "Welcome! Enter the stock symbol to track:")

# Handling user input
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id not in user_data:
        user_data[chat_id] = {}

    if "stock_name" not in user_data[chat_id]:
        user_data[chat_id]["stock_name"] = text
        bot.send_message(chat_id, f"Stock name set to {text}. Enter update interval in minutes:")
    elif "time_duration" not in user_data[chat_id]:
        try:
            duration = int(text)
            if duration < 0:
                bot.send_message(chat_id, "Interval too short. Please enter at least 6 minutes.")
                return
            user_data[chat_id]["time_duration"] = duration
            start_schedule(chat_id, user_data[chat_id]["stock_name"], duration/6)
        except ValueError:
            bot.send_message(chat_id, "Invalid input. Please enter a number for the interval.")
    else:
        bot.send_message(chat_id, "Tracker is already running. Use /stop to reset.")

# # Job to fetch and notify stock price
# def fetch_and_notify(chat_id, stock_name):
#     price = get_stock_price(stock_name)
#     if price is not None:
#         # Get the old price or initialize it if None
#         old_price = user_data[chat_id].get("old_price")
#         if old_price is None:
#             old_price = price
#             user_data[chat_id]["old_price"] = price

#         # Determine the emoji based on price comparison
#         emoji = "🔺" if price > old_price else "🔻" if price < old_price else "🔷"

#         # Update old_price to the current price
#         user_data[chat_id]["old_price"] = price

#         # Send the message with the stock update
#         message = f"🔔 Current price of {stock_name} is ₹{price} {emoji}"
#     else:
#         message = "Error: Unable to retrieve stock price."

#     send_telegram(chat_id, message)

# Job to fetch and notify stock price
def fetch_and_notify(chat_id, stock_name): 
    price = get_stock_price(stock_name)
    if price is not None:
        # Initialize old_price to 0 if it's the first fetch or if it's None
        old_price = user_data[chat_id].get("old_price", 0)

        # If it's the first fetch (old_price is 0), update it to the current price
        if old_price == 0:
            user_data[chat_id]["old_price"] = price
            old_price = price  # Now, update old_price to the current price

        # Ensure old_price is never None (safety check)
        if old_price is None:
            old_price = 0
            user_data[chat_id]["old_price"] = old_price

        # Determine the emoji based on price comparison
        emoji = "🔺" if price > old_price else "🔻" if price < old_price else "🔷"

        # Update old_price to the current price
        user_data[chat_id]["old_price"] = price

        # Send the message with the stock update
        message = f"🔔 Current price of {stock_name}: ₹{price} {emoji}"
    else:
        message = "Error: Unable to retrieve stock price."

    send_telegram(chat_id, message)
    print("send message.")


# Run the bot
if __name__ == "__main__":
    print("Bot is running...")
    bot.polling()
