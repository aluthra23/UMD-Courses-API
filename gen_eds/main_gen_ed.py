from bs4 import BeautifulSoup
from course_classes import Gen_Ed
from helping_files import http_utils
from typing import List


def all_gen_eds_scraper() -> List[Gen_Ed]:
    """Every gen-ed category on Testudo. Raises on network/HTTP failures."""
    response = http_utils.fetch("https://app.testudo.umd.edu/soc/gen-ed/")
    soup = BeautifulSoup(response.text, 'html.parser')

    data = []
    for entry in soup.find_all('div', class_='subcategory'):
        full_form, separator, acronym = entry.text.strip().partition('(')
        if separator:
            data.append(Gen_Ed(acronym.rstrip(')').strip(), full_form.strip()))
    return data
