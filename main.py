from next_in_ai.PocketParser import *
from next_in_ai.BatchSummarizer import *

if __name__ == "__main__":
    p = PocketParser("https://getpocket.com/users/*sso1456990609615e33/feed/all")
    latest_article_urls = p.new_articles()

    # Get first 2 articles
    latest_article_urls = latest_article_urls[:2]

    batch_summarizer = BatchSummarizer(latest_article_urls)
    batch_summarizer.create_summary_document()
