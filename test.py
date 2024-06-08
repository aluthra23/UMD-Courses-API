import requests


response = requests.get("http://127.0.0.1:8000/")


if response.status_code != 200:
    print("Failed to fetch data")

print(response.json())