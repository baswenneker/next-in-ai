import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from io import StringIO
from bs4 import BeautifulSoup
from datetime import datetime
import os
import pytz

requests.packages.urllib3.disable_warnings()


class PocketParser:
    def __init__(self):
        self.path = os.getenv("POCKET_RSS_FEED")
        self.data = None

    def _fetch_content(self, path):
        HEADERS = {
            "User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
        }
        try:
            response = requests.get(
                path, headers=HEADERS, timeout=10, allow_redirects=True, verify=False
            )
            return response.text
        except Exception as err:
            print(f"❌ Couldn't fetch content from {path}: {err}")
            return None

    def last_month_articles(self):
        return self.new_articles_from_days_ago(30)

    def new_articles_from_days_ago(self, days):
        max_age = datetime.now().replace(tzinfo=pytz.UTC) - timedelta(days=days)

        return self._get_articles(max_age)

    def new_articles(self):
        # Set the maximum age of the news articles (one week)
        max_age = self._get_last_publish_date()

        return self._get_articles(max_age)

    def _get_last_publish_date(self):
        url = os.getenv("BEEHIIV_URL", None)

        if url == "" or url is None:
            return datetime.now().replace(tzinfo=pytz.UTC) - timedelta(days=7)

        html = self._fetch_content(url)

        soup = BeautifulSoup(html, "html.parser")

        # Find the first time tag and extract the datetime attribute
        time_element = soup.find("time")
        if time_element is not None:
            # get the datetime attribute
            date_string = time_element.get("datetime")

            last_published_date = datetime.strptime(
                date_string, "%Y-%m-%dT%H:%M:%S.%fZ"
            )
            last_published_date = last_published_date.replace(tzinfo=pytz.UTC)
            return last_published_date
        else:
            print("Could not find the last published date, using 7 days ago.")
            return datetime.now().replace(tzinfo=pytz.UTC) - timedelta(days=7)

    def _get_articles(self, max_age):
        rss_feed = self._fetch_content(self.path)

        if "Page Not Found" in rss_feed:
            raise Exception("Could not fetch RSS feed, check your POCKET_RSS_FEED url.")

        # Parse the RSS feed
        root = ET.fromstring(rss_feed)

        # Get the current date and time
        now = datetime.now()

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
