import requests

import os

from dotenv import load_dotenv

load_dotenv()

def translate(source_language, translation_language, text):

    url = 'https://translation-api.translate.com/translate/v1/mt'

    api_key = os.getenv('TRANSLATE_API_KEY')

    headers = {
        'accept': '*/*',
        'x-api-key': api_key,
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRF-TOKEN': '',
    }
    data = {
        'source_language': source_language,
        'translation_language': translation_language,
        'text': text,
    }

    translate_language = requests.post(url, headers=headers, data=data)

    return translate_language.json();
