import requests
import re

class PerplexityChatbot:
    def __init__(
            self,
            api_key,
            content_file_path="auwave_corpus.txt",
            contact_url="https://www.auwave.com/contact-us",
            services_url="https://www.auwave.com/services",
    ):
        self.api_key = api_key
        self.content_file_path = content_file_path
        self.contact_url = contact_url
        self.services_url = services_url

        self.full_text = self._load_content()
        self.valid_urls = self._extract_valid_urls()

    def _load_content(self):
        try:
            with open(self.content_file_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""

    def _extract_valid_urls(self):
        urls = set(re.findall(r"https?://[^\s,)]+", self.full_text))
        urls.add(self.contact_url)
        urls.add(self.services_url)
        return urls

    def _postprocess_answer(self, answer):
        answer = re.sub(r"\[\d+\]", "", answer)
        urls = re.findall(r"https?://[^\s,)]+", answer)
        lower_answer = answer.lower()

        for url in urls:
            if url not in self.valid_urls:
                if "service" in lower_answer or "solution" in lower_answer:
                    answer = answer.replace(url, self.services_url)
                else:
                    answer = answer.replace(url, self.contact_url)

        return answer

    def ask_question(self, user_question):
        if not self.full_text:
            return "Website content is not available."

        prompt = f"""
STRICT RULES:
- You are a chatbot for an IT services company website.
- Use ONLY provided website content.
- Always include exactly ONE valid company URL.

CONTENT:
{self.full_text}

User Question: {user_question}
Answer:
"""

        payload = {
            "model": "sonar",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 350,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            json=payload,
            headers=headers,
        )

        raw_answer = response.json()["choices"][0]["message"]["content"]
        return self._postprocess_answer(raw_answer)
