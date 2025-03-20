
import requests
def get_news_from_gnews():
    # Replace with your GNews API key
    api_key = '096d43cec18d84451acfe3fd899bb1c4'
    max_ = 3
    url = f'https://gnews.io/api/v4/top-headlines?token={api_key}&country=in&lang=en&max={max_}'

    # Make the request to GNews API
    response = requests.get(url)
    data = response.json()

    # Check if the request was successful
    if response.status_code == 200:
        headlines = data['articles']
        news = ''
        for article in headlines:
            news = news + f"{article['title']}. "
        return news


