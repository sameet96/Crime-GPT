import requests

url = 'http://127.0.0.1:5001/process_video'

try:
    response = requests.post(url)
    response.raise_for_status()  # Raise an error for bad status codes
    print(response.json())
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
    if response is not None:
        print(f"Response content: {response.content}")
