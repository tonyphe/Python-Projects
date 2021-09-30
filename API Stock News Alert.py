# Create a stock news alert messaging system using APIs to pull data from financial and news websites

import requests
from twilio.rest import Client

# Your desired stock
STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

# Redacted my information, but you would include yours here
STOCK_API_KEY = "YOUR STOCK API KEY"
NEWS_API_KEY = "YOU NEWS API KEY"

account_sid = "YOUR ACCT SID"
auth_token = "YOU AUTH TOKEN"

stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "outputsize": "compact",
    "datatype": "json",
    "apikey": STOCK_API_KEY,
}

#calculate price of stock at the end of yesterday
stock_response = requests.get(STOCK_ENDPOINT, params=stock_params)
stock_response.raise_for_status()
stock_data = stock_response.json()["Time Series (Daily)"]

stock_data_list = [value for (key, value) in stock_data.items()]
yesterday_data = stock_data_list[0]
yesterday_closing_price = yesterday_data["4. close"]

#calculate price of stock at the end of the day before yesterday
day_before_yesterday_data = stock_data_list[1]
day_before_yesterday_closing_price = day_before_yesterday_data["4. close"]

#assign price change with arrow
difference = (float(yesterday_closing_price) - float(day_before_yesterday_closing_price))
up_down = None
if difference > 0:
    up_down = "🔺"
else:
    up_down = "🔻"

diff_percent = round(difference / float(yesterday_closing_price) * 100)

# if difference of stock changes by .05% to send alert (reason this is low is because Tesla has not had big swings recently)

if abs(diff_percent) > .5:
    news_params = {
        "apiKey": NEWS_API_KEY,
        "qInTitle": COMPANY_NAME,
    }
  
    # grab 3 most recent news articles if absolute price change is triggered
    news_response = requests.get(NEWS_ENDPOINT, params=news_params)
    news_response.raise_for_status()
    news_data = news_response.json()["articles"]
    
    #format and partition out necessary data to send
    three_articles = news_data[:3]

    formatted_articles = [f"{STOCK_NAME}:{up_down}{diff_percent}% \nHeadline: {article['title']}. \nBrief: {article['description']}" for article in three_articles]

    client = Client(account_sid, auth_token)
    
    # use twilio messaging system to send an automated text when triggered
    for article in formatted_articles:
        message = client.messages.create(
            body=article,
            from_='+19282385436',
            to='+YOUR NUMBER'
        )
