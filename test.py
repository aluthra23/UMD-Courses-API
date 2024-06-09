import requests


response = requests.get("http://127.0.0.1:8000/classes/asdf/sections")


if response.status_code != 200:
    print("Failed to fetch data", response.status_code)

print(response.json())