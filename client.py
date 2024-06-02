import requests

urlCapture = 'http://127.0.0.1:5001/process_video'
urlTestVideo = 'http://127.0.0.1:5001/process_video_sent'


try:
    response = requests.post(urlCapture)
    response.raise_for_status()  # Raise an error for bad status codes
    print(response.json())
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
    if response is not None:
        print(f"Response content: {response.content}")

try:
    response = requests.post(urlTestVideo)
    response.raise_for_status()  # Raise an error for bad status codes
    print(response.json())
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
    if response is not None:
        print(f"Response content: {response.content}")
