from next_in_ai.PocketParser import *
from next_in_ai.BatchSummarizer import *
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()

    p = PocketParser()
    latest_pocket_urls = p.new_articles_from_days_ago(7)
    batch_summarizer = BatchSummarizer(latest_pocket_urls)
    batch_summarizer.create_summary_document(debug=False)
