import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from io import StringIO
from bs4 import BeautifulSoup
from datetime import datetime


class PocketParser:
    def __init__(self, path):
        self.path = path
        self.data = None

    def _fetch_content(self, path):
        HEADERS = {
            "User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
        }
        response = requests.get(path, headers=HEADERS)
        response.raise_for_status()
        return response.text

    def _get_last_publish_date(self):
        url = "https://nextinai.beehiiv.com/"
        html = self._fetch_content(url)

        soup = BeautifulSoup(html, "html.parser")

        # Find the first time tag and extract the datetime attribute
        time_element = soup.find("time")
        if time_element is not None:
            date_string = time_element["datetime"]
            last_published_date = datetime.fromisoformat(date_string)
            return last_published_date
        else:
            print("Could not find the last published date.")
            today = datetime.now()
            days_since_last_thursday = (today.weekday() - 3) % 7
            last_thursday_datetime = today - timedelta(days=days_since_last_thursday)
            return last_thursday_datetime

    def _last_thursday(self):
        today = datetime.now()
        days_since_last_thursday = (today.weekday() - 3) % 7
        last_thursday_datetime = today - timedelta(days=days_since_last_thursday)
        return last_thursday_datetime

    def new_articles(self):
        rss_feed = self._fetch_content(self.path)

        # Parse the RSS feed
        root = ET.fromstring(rss_feed)

        # Get the current date and time
        now = datetime.now()

        # Set the maximum age of the news articles (one week)
        max_age = self._get_last_publish_date()

        article_urls = []

        # Iterate through the items in the RSS feed
        for item in root.iter("item"):
            # Get the publication date of the news article
            pub_date = datetime.strptime(
                item.find("pubDate").text, "%a, %d %b %Y %H:%M:%S %z"
            )

            # If the news article is at most one week old, print its link
            if pub_date >= max_age:
                # Add link to article_urls
                article_urls.append(item.find("link").text)

        return article_urls
