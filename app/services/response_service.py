import os
import requests

def get_openai_response(context, question):
    """Query OpenAI API to generate a response based on the context and question."""
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
        }
        payload = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": f"You are a helpful assistant. Context: {context}"},
                {"role": "user", "content": question}
            ]
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()

        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error querying OpenAI API: {str(e)}")
