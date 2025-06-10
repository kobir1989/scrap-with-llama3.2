import json
import re
import requests
from app.scraper.web_scraper import WebScraper

link_system_prompt = (
    "You are provided with a list of links on a webpage. "
    "You are to decide which of the links are most relevant for a brochure about the company, "
    "such as links to an about page, company page, or careers page.\n"
    "You must respond with JSON like this:\n"
    "{\n"
    '  "links": [\n'
    '    {"type": "about page", "url": "https://example.com/about"},\n'
    '    {"type": "careers page", "url": "https://example.com/careers"}\n'
    "  ]\n"
    "}"
)
                                  <

def get_links_user_prompt(website):
    return (
        f"Here is the list of links on the website of {website.url}:\n"
        "Decide which of these are relevant links for a company brochure. "
        "Only include full https URLs. Ignore privacy policies, terms, emails, etc.\n\n"
        + "\n".join(website.links)
    )


def clean_model_response(content):
    """
    Removes Markdown code block and lead/trail space.
    """
    content = content.strip()
    if content.startswith("```json") or content.startswith("```"):
        content = re.sub(r"^```(?:json)?|```$", "", content, flags=re.MULTILINE).strip()
    return content


def get_links(url):
    website = WebScraper(url)
    user_prompt = get_links_user_prompt(website)

    payload = {
        "model": "llama3.2",
        "stream": False,
        "messages": [
            {"role": "system", "content": link_system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    try:
        response = requests.post("http://localhost:11434/api/chat", json=payload)
        response.raise_for_status()

        raw_content = response.json()["message"]["content"]

        cleaned_content = clean_model_response(raw_content)
        parsed = json.loads(cleaned_content)

        return parsed.get("links", [])

    except requests.RequestException as e:
        print("Request failed:", e)
    except json.JSONDecodeError as e:
        print("Cleaned response:\n", cleaned_content)

    return []


def get_all_details(url):
    result = "Landing Page:\n"
    result += WebScraper(url).get_contents()

    links = get_links(url)

    for link in links:
        result += f"\n\n{link['type'].title()}:\n"
        result += WebScraper(link["url"]).get_contents()
        result += "\n\n"

    return result


if __name__ == "__main__":
    details = get_all_details("https://anthropic.com")
    print(details)
