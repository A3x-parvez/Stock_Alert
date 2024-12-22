# Stock_Price_Alert_BOT
This project is a stock price tracker and alert bot for any  `ex:BPCL (Bharat Petroleum Corporation Limited)` stocks on the NSE (National Stock Exchange). It fetches real-time stock prices and sends alerts to a configured Telegram chat using the Telegram Bot API.

## Features
- Fetches real-time stock prices from Google Finance.
- Sends stock price alerts to a Telegram chat.
- Simple, automated scheduler for periodic updates.
- It is completely free.

## Requirements
- Python 3.x
- Required Python Libraries: `requests`, `schedule`, `BeautifulSoup` (from `bs4`)
- A Telegram bot API token and chat ID.

## Installation
1. **Clone the Repository :**
     ```bash
     git clone https://github.com/A3x-parvez/BPCL-Stock-Price-Alert-Bot.git
     cd BPCL-Stock-Price-Alert-Bot
     ```
2. **Install Dependencies :**
    ```bash
    pip install -r requirement.txt
    ```
3. **Setup Teligram Bot :**
    - **Create a bot using** [BotFather](https://core.telegram.org/bots#botfather) and get the API token.

    - **Find the Bot chat ID** :

       1. Open Telegram and search for your bot (use the bot username you created in BotFather).

       2. Start the bot by clicking the Start button or sending a `/start` command.
       3. Replace `YOUR_BOT_TOKEN` with your bot's API token and paste the following URL into your browser:
          ```bash
          https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
          ```
          ***Example :***
          ```bash
          https://api.telegram.org/bot123456789:ABCdEfGhIJKlmnOpQrSTuVWxyz123456/getUpdates
          ```
        4. If the bot has received a message (e.g., you sent a `/start`command), you’ll see a JSON response containing details about the messages.
        5. Look for the chat object in the JSON response. It should contain a field called id.
           - **Example of JSON response :**
             ```bash
             {
                "ok": true,
                "result": [
                     {
                        "update_id": 123456789,
                        "message": {
                           "chat": {
                               "id": 987654321,
                               "first_name": "John",
                               "type": "private"
                            }, 
                            "date": 1609459200,
                            "text": "/start"
                        }
                    }  
                ]
             }
             ```
        6. The id field (`987654321` in this example) is the chat ID.

4. **Create a `keys.py` File :**
   
     Inside the project directory, create a keys.py file with the following content:
     ```bash
     BOT_API = "your_telegram_bot_api_token"
     CHAT_ID = "your_telegram_chat_id"
     ```
     Replace `your_telegram_bot_api_token` and `your_telegram_chat_id` with your actual Telegram bot API token and chat ID.

## Dependencies
Install the following Python libraries:

- `requests` : For HTTP requests to Google Finance and Telegram API.
- `BeautifulSoup` (`bs4`) : For parsing HTML from Google Finance.
- `schedule` : For periodic job scheduling.
 
**To install these libraries:**
```bash
pip install requests beautifulsoup4 schedule
```
## Run the Script 
```bash
python Stock_price_V3.py
```
## Customization
- **Stock Symbol :** Replace `BPCL` with your desired stock symbol in the following line :
```bash
symbol="BPCL"
```
- **Schedule Timing :** Adjust the frequency of updates in:
```bash
schedule.every(1/30).minutes.do(job)
```
- **Telegram Notifications :** Customize the message content in:
```bash
message = f"🔔Current 💲price of BPCL:NSE is : {price}/-\nThank you😊."
```

## Acknowledgments
- Google Finance for real-time stock prices.
- Telegram Bot API for sending alerts.
- **Libraries :** `BeautifulSoup`, `requests`, `schedule`.

## File Structure
```bash
Stock_Price_Alert_BOT/
├── keys.py             # Contains the Telegram bot token and chat ID.
├── Stock_price_V3.py   # Main script to fetch stock price and send alerts.
├── Stock_price_V4.py   # Incomplete Version 4 script currently not working.
├── requirements.txt    # Python dependencies.
└── README.md           # Documentation.

```
## NOTE :
The current version (V3) is available and serves as a simple, straightforward program with no complexities. I am currently working on Version 4 (V4), which will include advanced features, improved user-friendliness, and plans for hosting the application in the future. Feel free to contribute if you're interested in collaborating on this project.
- **Version 3 (Current Version)**
  - Fetches real-time stock prices from Google Finance.
  - Sends stock price alerts to a Telegram chat.
  - Simple, automated scheduler for periodic updates.
  - Easy-to-understand code suitable for beginners.
- **Version 4 (Work in Progress)**
  - Advanced features and improved user-friendliness.
  - Enhanced error handling and customization options.
  - Plans to host the application for broader accessibility.
  - Open for contributions—feel free to collaborate on this  version!

## Contact Me
If you have any questions, feedback, or suggestions, feel free to reach out!
 - **LinkedIn :**  [Rijwanool Karim](https://www.linkedin.com/in/rijwanool-karim-89b6b5255?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app) 
 - **GitHub :** [A3x-parvez](https://github.com/A3x-parvez)
 - **Email :** [Parvez](rijwanoolkarim143r@gmail.com)




