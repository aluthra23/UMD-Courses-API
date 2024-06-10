import csv
import requests
from bs4 import BeautifulSoup
from course_classes import Gen_Ed
from typing import List


def all_gen_eds_scraper() -> List[Gen_Ed]:
    url = "https://app.testudo.umd.edu/soc/gen-ed/"

    response = requests.get(url)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all courses listed on the page
    gen_eds = soup.find_all('div', class_='subcategory')

    data = []
    # Iterate over each course acronym
    for entry in gen_eds:
        gen_ed = entry.text.strip()

        words = gen_ed.split('(')

        full_form = f"{words[0].strip()}"
        acronym = f"{words[1][:-1].strip()}"

        data.append(Gen_Ed(acronym, full_form))

    return data
