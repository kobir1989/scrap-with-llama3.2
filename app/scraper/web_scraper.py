from typing import List

import requests
from bs4 import BeautifulSoup


class WebScraper:
    url: str
    title: str
    body: str
    links: List[str]

    def __init__(self, url):
        self.url = url
        response = requests.get(url)
        self.body = response.content
        soup = BeautifulSoup(self.body, "html.parser")
        self.title = soup.title.string if soup.title else "No Title found!"
        links = [link.get("href") for link in soup.find_all("a")]
        self.links = [link for link in links if link]
        if soup.body:
            for irrelevant in soup.body(["script", "img", "input"]):
                irrelevant.decompose()
            self.text = soup.body.get_text(strip=True)
        else:
            self.text = ""

    def get_contents(self):
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"
