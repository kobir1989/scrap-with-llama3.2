import re


def create_prompt_payload(
    system_prompt: str,
    user_prompt: str,
    model_name="llama3.2",
):
    """
    Create Payload for LLM prompt with two param *system prompt and *user prompt.
    """
    payload = {
        "model": model_name,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    return payload


def clean_model_response(content: str):
    """
    Removes Markdown code block and lead/trail space.
    """
    content = content.strip()
    if content.startswith("```json") or content.startswith("```"):
        content = re.sub(r"^```(?:json)?|```$", "", content, flags=re.MULTILINE).strip()
        content = re.sub(r"^```(?:json)?|```$", "", content, flags=re.MULTILINE).strip()
    return content


