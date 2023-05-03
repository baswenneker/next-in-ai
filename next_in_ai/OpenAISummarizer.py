import requests
import openai
from bs4 import BeautifulSoup
import hashlib
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()
# Get the OpenAI API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")
if openai.api_key is None:
    raise Exception("Please set your OpenAI API key in the .env file")


class OpenAISummarizer:
    def __init__(self, url):
        self.url = url
        self.content = ""
        self.cache_dir = "cache"

    def _cache_filename(self):
        url_hash = hashlib.md5(self.url.encode("utf-8")).hexdigest()
        return os.path.join(self.cache_dir, f"{url_hash}_summary.txt")

    def _load_summary_from_cache(self):
        cache_file = self._cache_filename()
        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                return f.read()
        return None

    def _save_summary_to_cache(self, summary):
        os.makedirs(self.cache_dir, exist_ok=True)
        cache_file = self._cache_filename()
        with open(cache_file, "w") as f:
            f.write(summary)

    def _fetch_content(self):
        print("🌎 Getting the contents of the url.")
        HEADERS = {
            "User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
        }
        try:
            response_text = requests.get(
                self.url,
                headers=HEADERS,
                timeout=10,
                allow_redirects=True,
                verify=False,
            ).text
        except Exception as err:
            print("❌ Couldn't fetch content from {}: {}".format(self.url, err))
            return None

        soup = BeautifulSoup(response_text, "html.parser")

        text_elements = soup.find_all(["p", "h1", "h2", "h3"])
        self.content = " ".join([element.get_text() for element in text_elements])

    def _prompt(self):
        output_language = os.getenv("OUTPUT_LANGUAGE", "English")
        return [
            {
                "role": "system",
                "content": "You are an expert in summarizing texts for newsletters. You write in informal language and in the Dutch language.",
            },
            {
                "role": "user",
                "content": """Your output should use the following template:

[Emoji] Attention grabbing title here

### Summary

### Facts

- Bulletpoint

### Why this is interesting

Your task is to summarize the text I give you in up to 5 bulletpoints and start with a short and catchy summary. But, start with a title in up to 50 characters starting with a matching emoji and a title that will grab attention (add a space between the emoji and title). Additionally, write down why this is an interesting read for an executive interested in how AI can help business to grow.

Reply in Dutch.""",
            },
            {
                "role": "user",
                "content": f"Summarize the following text in Dutch:\n\n{self.content}",
            },
        ]
        return

    def summarize(self):
        cached_summary = self._load_summary_from_cache()
        if cached_summary is not None:
            print("🤗 Got summary from cache.")
            return cached_summary

        self._fetch_content()

        print("⏳ Summarizing the text.")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self._prompt(),
            max_tokens=400,
            temperature=0.7,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

        summary = response.choices[0].message["content"]
        self._save_summary_to_cache(summary)
        return summary
