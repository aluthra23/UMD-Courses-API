import pandas as pd
import requests

base_url = "http://127.0.0.1:8000//classes"

df = pd.read_csv('./course_prefixes_dataset_creation/umd_course_prefixes.csv')

for course_prefix in df['COURSE PREFIX']:
    url = f"{base_url}/{course_prefix}"

    response = requests.get(url)

    if response.status_code != 200 or not response.json():
        print(f"Failed to fetch data for {course_prefix}")
