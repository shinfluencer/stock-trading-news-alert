import requests
from twilio.rest import Client
import os


STOCK_API_ENDPOINT = "https://www.alphavantage.co/query"
STOCK_API_KEY = os.environ.get("STOCK_API_KEY")
STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

NEWS_API_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")
MY_PHONE_NUMBER = os.environ.get("MY_PHONE_NUMBER")


def get_stock_data():
    params = {
        "function": "TIME_SERIES_WEEKLY",
        "symbol": STOCK,
        "apikey": STOCK_API_KEY
    }
    
    response = requests.get(url=STOCK_API_ENDPOINT, params=params)
    response.raise_for_status()
    data = response.json()
    
    try:
        stock_data = [data for (hour, data) in data["Weekly Time Series"].items()]
    except KeyError:
        get_stock_data()
    else:
        return stock_data
    

def get_news():
    params = {
        "apiKey": NEWS_API_KEY,
        "q": COMPANY_NAME
    }
    
    response = requests.get(url=NEWS_API_ENDPOINT, params=params)
    news_data = response.json()["articles"][0]
    
    headline = news_data["title"]
    brief = news_data["description"]
    
    return headline, brief


yesterday_closing_price = float(get_stock_data()[0]["4. close"])
day_before_yesterday_closing_price = float(get_stock_data()[1]["4. close"])

price_difference_percentage = abs(round((100 - ((yesterday_closing_price/day_before_yesterday_closing_price) * 100)), 2))

if price_difference_percentage >= 5:
    news = get_news()
    news_headline = news[0]
    news_brief = news[1]
    
    if yesterday_closing_price > day_before_yesterday_closing_price:
        difference_indicator = "🔺"
    else:
        difference_indicator = "🔻"
        
    message = \
    f"""
    {STOCK}: {difference_indicator} {price_difference_percentage}%
    Headline: {news_headline}
    Brief: {news_brief}
    """
    
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=TWILIO_PHONE_NUMBER,
        to=MY_PHONE_NUMBER
    )
