import os
import json
import requests

def call_une_function(method: str, params: dict, model: str = "groq"):
    """Allow Groq/Gemini/OpenAI to call UNE functions via simple routing"""
    # You can expand this with actual API calls
    # For now it returns the local result
    from .une_atomic_library import globals as lib_globals
    if method in lib_globals:
        return lib_globals[method](**params)
    return {"error": "Method not found"}
