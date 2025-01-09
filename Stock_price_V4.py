import requests
import time
import schedule
from bs4 import BeautifulSoup
import telebot
import threading
import keys

# Telegram bot setup
bot_token = keys.BOT_API

# Initialize the Telegram bot engine using the provided token.
bot = telebot.TeleBot(bot_token)

# Global dictionary to store user data and threads
user_data = {}
user_threads = {}
chat_id = ""

# Function to fetch the stock price
def get_stock_price(symbol):
    url = f"https://www.google.com/finance/quote/{symbol}:NSE"
    print(f"Fetching stock price for {symbol} from: {url}")

    response = requests.get(url)
    print(f"Fetching stock price for {symbol}... Status Code: {response.status_code}")
    soup = BeautifulSoup(response.text, 'html.parser')
    class1 = "YMlKec fxKbKc"
    p = soup.find(class_=class1).text.strip()[1:].replace(',', '')
    price = float(p)
    if response.status_code == 200:
        return price
    else:
        print("Something went wrong.")
        return None

# Function to send message to Telegram user
def send_telegram(chat_id, message):
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

# Function to start the scheduler in a new thread for each user
def start_schedule(chat_id, stock_name, duration):
    # Prevent duplicate job creation if already running
    if chat_id in user_threads and user_threads[chat_id].is_alive():
        send_telegram(chat_id, "A stock tracker is already running. Please stop the current tracker first.")
        return

    # Schedule the job to run every 'duration' minutes
    job_id = schedule.every(duration / 6).minutes.do(job, chat_id, stock_name)
    
    # Running the scheduler in a separate thread so it doesn't block other bot interactions
    user_threads[chat_id] = threading.Thread(target=run_scheduler)
    user_threads[chat_id].start()

    send_telegram(chat_id, f"Stock tracker started for {stock_name} with updates every {duration} minutes.")

# Running the scheduler
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# The job function that sends the stock price update
def job(chat_id, stock_name):
    # Fetch the new stock price
    price = get_stock_price(stock_name)

    if price is not None:
        # Get the previous stock price for comparison
        if chat_id in user_data and 'old_price' in user_data[chat_id]:
            old_price = user_data[chat_id]['old_price']
        else:
            old_price = price  # If no old price exists, consider the current price as old
        
        # Store the current price as the new old price for the next check
        user_data[chat_id]['old_price'] = price
        
    if old_price < price:
        emoji = "🔺"
    elif old_price == price:
        emoji = "🔷"
    else:
        emoji = "🔻"
        
    old_price = price
    
    if price:
        message = f"🔔 Current 💲 price of {stock_name}:NSE is : {price}/- {emoji}\nThank you😊."
    else:
        message = "Error: Unable to retrieve stock price."
    send_telegram(chat_id, message)

# Handling the '/start' command
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    # Initialize user state
    user_data[chat_id] = {"step": "ask_stock", "stock_name": None, "time_duration": None}
    bot.send_message(chat_id, "Welcome! Please enter the stock name you want to track (e.g., BPCL).")

# Handling the '/stop' command
@bot.message_handler(commands=['stop'])
def stop(message):
    chat_id = message.chat.id
    if chat_id in user_data:
        # Clear any scheduled jobs for the user
        if chat_id in user_threads:
            if user_threads[chat_id].is_alive():
                print(f"Stopping scheduler for chat_id {chat_id}.")
                schedule.clear()  # Clear all scheduled jobs
                print(f"Waiting for thread to finish for chat_id {chat_id}.")
                user_threads[chat_id].join(1)  # Wait for the thread to finish
                print(f"Thread finished for chat_id {chat_id}.")
            user_threads.pop(chat_id)  # Remove the thread from the manager
            print(f"Thread removed for chat_id {chat_id}.")
        
        # Reset all user data
        user_data[chat_id] = {"step": "ask_stock", "stock_name": None, "time_duration": None}
        print(f"User data reset for chat_id {chat_id}.")
        print(f"User threads: {user_threads}")
        # Inform the user that the stock tracker has been stopped
        send_telegram(chat_id, "The stock tracker has been stopped. All data is reset.")
    else:
        send_telegram(chat_id, "You haven't started tracking a stock yet.")

# Handling any user input
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text.strip()

    # If the user is not yet tracked, initialize user state
    if chat_id not in user_data:
        user_data[chat_id] = {"step": "ask_stock", "stock_name": None, "time_duration": None}

    state = user_data[chat_id]

    if state["step"] == "ask_stock":
        # Store the stock name and ask for the time duration
        state["stock_name"] = text
        state["step"] = "ask_duration"
        bot.send_message(chat_id, f"Stock name set to {text}. Please enter the update interval in minutes.")
    elif state["step"] == "ask_duration":
        try:
            # Validate and store the time duration
            time_duration = int(text)
            state["time_duration"] = time_duration
            state["step"] = "complete"
            bot.send_message(chat_id, f"Update interval set to {time_duration} minutes.")
            
            # Start the scheduler
            start_schedule(chat_id, state['stock_name'], state['time_duration'])
        except ValueError:
            # Handle invalid time input
            bot.send_message(chat_id, "Invalid input. Please enter a valid number for the time duration.")
    else:
        bot.send_message(chat_id, "You have already provided the required details. Use /start to reset.")

# Main function to keep the bot running
def main():
    print("Bot is running...")
    bot.polling()

if __name__ == '__main__':
    main()
