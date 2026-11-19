import os
from openai import OpenAI

def _clients():
    mode = os.getenv("OPENROOT_MODE", "hybrid").lower()
    online_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENROOT_ONLINE_API_KEY")
    offline_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENROOT_OFFLINE_API_KEY") or "ollama"
    if mode == "offline" or not online_key:
        base_url = os.getenv("OPENROOT_OFFLINE_ENDPOINT", "http://127.0.0.1:11434/v1")
        model = os.getenv("OPENROOT_OFFLINE_MODEL", "local/qwen2.5-coder:7b")
        return OpenAI(base_url=base_url, api_key=offline_key), model
    base_url = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
    model = os.getenv("OPENROOT_ONLINE_MODEL", "openai/gpt-4o-mini")
    return OpenAI(base_url=base_url, api_key=online_key), model

def ask_flint(messages, **kwargs):
    client, model = _clients()
    kwargs.setdefault("temperature", 0.2)
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        **kwargs,
    )
    return completion.choices[0].message.content

def ask_flint_json(messages, **kwargs):
    text = ask_flint(messages, **kwargs)
    import json
    return json.loads(text)
