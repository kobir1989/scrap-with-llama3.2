import json
import requests
from app.scraper.web_scraper import WebScraper
from app.utils import utils
from app.constants import constants


def get_links_user_prompt(website):
    return (
        f"Here is the list of links on the website of {website.url}:\n"
        "Decide which of these are relevant links for a company brochure. "
        "Only include full https URLs. Ignore privacy policies, terms, emails, etc.\n\n"
        + "\n".join(website.links)
    )


# get all scraped links and request to llama to keep relevant links only.
def get_links(url):
    website = WebScraper(url)
    user_prompt = get_links_user_prompt(website)

    payload = utils.create_prompt_payload(user_prompt, constants.LINK_SYSTEM_PROMPT)

    try:
        response = requests.post(constants.MODEL_URL, json=payload)
        response.raise_for_status()

        raw_content = response.json()["message"]["content"]

        cleaned_content = utils.clean_model_response(raw_content)
        parsed = json.loads(cleaned_content)

        return parsed.get("links", [])

    except requests.RequestException as e:
        print("Request failed:", e)
    except json.JSONDecodeError as e:
        print("Cleaned response:\n", cleaned_content)

    return []


# Run scraper to get all the details from llama returned links.
def get_all_details(url):
    result = "Landing Page:\n"
    result += WebScraper(url).get_contents()

    links = get_links(url)

    for link in links:
        result += f"\n\n{link['type'].title()}:\n"
        result += WebScraper(link["url"]).get_contents()
        result += "\n\n"

    return result


def get_brochure_user_prompt(company_name, url):
    user_prompt = f"You are looking at a company called: {company_name}\n"
    user_prompt += (
        f"Here are the contents of its landing page and other "
        f"relevant pages; use this information to build a short "
        f"brochure of the company in markdown.\n"
    )
    user_prompt += get_all_details(url)
    user_prompt = user_prompt[:5000]
    return user_prompt


# Request again to llama to Create Brochure with the scraped details from the links
def create_brochure(company_name, url):
    user_prompt = get_brochure_user_prompt(company_name, url)
    payload = utils.create_prompt_payload(user_prompt, constants.BROCHURE_SYSTEM_PROMPT)
    response = requests.post(constants.MODEL_URL, json=payload)
    response.raise_for_status()
    return response.json()["message"]["content"]


def translate_brochure(lang):
    details_response = create_brochure("Anthropic", "https://anthropic.com")
    print("DETAILS RESPONSE:", details_response)
    if not details_response:
        return f"Failed to translate Brochure!"

    user_prompt = f"Translate the following brochure into {lang}, for a social media post:\n\n Here is the Details:\n\n{details_response[:5000]}"
    request_payload = utils.create_prompt_payload(
        user_prompt, constants.TRANSLATE_SYSTEM_PROMPT
    )

    response = requests.post(constants.MODEL_URL, json=request_payload)
    response.raise_for_status()

    return response.json()["message"]["content"]


if __name__ == "__main__":
    final_output = translate_brochure("Bangla")
    print(final_output)
