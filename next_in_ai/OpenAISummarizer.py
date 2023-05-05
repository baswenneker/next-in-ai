import requests
import openai
import hashlib
import os
from dotenv import load_dotenv
import trafilatura

# Load the .env file
load_dotenv()
# Get the OpenAI API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")
if openai.api_key is None:
    raise Exception("Please set your OpenAI API key in the .env file")


class OpenAISummarizer:
    def __init__(self, url, disable_cache=False):
        self.url = url
        self.content = None
        self.disable_cache = disable_cache
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
            downloaded = trafilatura.fetch_url(self.url)

            self.content = trafilatura.extract(
                downloaded, include_comments=False, include_images=False
            )
            print(self, self.content)
        except Exception as err:
            self.content = None

        if self.content is None:
            print("❌ Couldn't fetch content from {}".format(self.url))
            return

        if "Please complete the security check to access" in self.content:
            print(
                "❌ Couldn't fetch content from {}, blocked by Captcha.".format(self.url)
            )
            self.content = None
            return

    def _prompt(self):
        # Get the output language setting from ENV, English = Default
        output_language = os.getenv("OUTPUT_LANGUAGE", "English")

        # Inspired by Jarno Duursma's summary prompt.
        return [
            {
                "role": "system",
                "content": f"""You are an expert in summarizing blog posts for newsletters.
                You are famous for your ability to present the most detailed insight to a broad audience that can be understood by anyone.
                Create an objective summary between 100 and 120 words for a first-year student, capturing the key points and overall message of the text.
                You write in {output_language}.
                Ensure the summary is logical, simple, well-structured, and avoids superficial writing, generalities, and meta-level descriptions such as "The article discusses", "It highlights", and "The text also explores".
                Instead, present the information as if the author of the article is describing it directly to the reader.
                Include one key quote at the end of the summary.
                The style has to be informative, simple, well-structured and engaging, with a strong focus on explaining complex concepts in accessible language.
                """,
            },
            {
                "role": "user",
                "content": """Use the following summary format:

[Emoji] Attention grabbing title here

[Summary here]

- 5 summarizing Bulletpoints with statements from the text

[Why this text is interesting to read, but don't include things like "This is interesting because..."]

For example:

🤖 AI is the new electricity

AI is the new electricity is what BCG tells people. And the rest of the summary here...

Key points:
- Bulletpoint 1
- Bulletpoint 2
...
- Bulletpoint 5

This article shows how AI is changing the world.

"This is a quote from the text included at the end of the summary."
""",
            },
            {
                "role": "user",
                "content": f"Summarize the following text in {output_language}:\n\n{self.content}",
            },
        ]
        return

    def summarize(self):
        if not self.disable_cache:
            cached_summary = self._load_summary_from_cache()
            if cached_summary is not None:
                print("🤗 Got summary from cache.")
                return cached_summary

        self._fetch_content()

        if self.content is None:
            return None

        print("⏳ Summarizing the text.")
        response = openai.ChatCompletion.create(
            model=os.getenv("MODEL", "gpt-3.5-turbo"),
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
