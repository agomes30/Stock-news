import requests
import os
from twilio.rest import Client
from twilio.http.http_client import TwilioHttpClient

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

STOCK_API_KEY = "V7E951ZXF4UAUWM0"
NEWS_API_KEY = "39cb38414eca4d16b3c950b2d623a995"

TWILIO_SID = os.environ.get("ID")
TWILIO_AUTH_TOKEN = os.environ.get("AUTH_TOKEN")

stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": STOCK_API_KEY,
}
stock_response = requests.get(STOCK_ENDPOINT, params=stock_params)
data = stock_response.json()["Time Series (Daily)"]
# Get yesterday's closing stock price.
data_list = [value for (key, value) in data.items()]
last_day_data = data_list[0]
last_day_closing_price = last_day_data["4. close"]
# Get the day before yesterday's closing stock price
day_before_last_day_data = data_list[1]
day_before_last_day_closing_price = day_before_last_day_data["4. close"]
# Find the positive difference between 1 and 2.
difference = float(last_day_closing_price) - float(day_before_last_day_closing_price)
up_down = None
if difference > 0:
    up_down = "🔺"
else:
    up_down = "🔻"
# Work out the percentage difference
diff_percent = round((difference / float(last_day_closing_price)) * 100)

if abs(diff_percent) > 5:
    news_params = {
        "apiKey": NEWS_API_KEY,
        "qInTitle": COMPANY_NAME,
    }
    news_response = requests.get(NEWS_ENDPOINT, params=news_params)
    articles = news_response.json()["articles"]
    three_articles = articles[:3]

    # Create a new list of the first 3 article's headline and description using list comprehension.
    formatted_art = [f"{STOCK_NAME}: {up_down}{diff_percent}%\nHeadline: {article['title']}. \nBrief: {article['description']}" for article in three_articles]
    # Send each article as a separate message via Twilio.
    proxy_client = TwilioHttpClient()
    proxy_client.session.proxies = {'https': os.environ['https_proxy']}
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN, http_client=proxy_client)
    for article in formatted_art:
        message = client.messages.create(
            body=article,
            from_='+13165308650',
            to='YOUR_NUMBER',
        )

    print(message.status)
