from typing import List
from course_prefixes_dataset_creation.course_prefixes_scraper import soc_scraper
from course_prefixes_dataset_creation.course_prefixes_scraper import course_catalog_scraper
import pandas as pd
from course_classes import Course_Prefix


def update_umd_courses(file_path='umd_course_prefixes.csv') -> List[Course_Prefix]:
    soc_scraper(file_path)
    course_catalog_scraper("https://academiccatalog.umd.edu/undergraduate/approved-courses/", file_path=file_path)
    course_catalog_scraper("https://academiccatalog.umd.edu/graduate/courses/", file_path=file_path)

    df = pd.read_csv(file_path)

    # Sort the DataFrame by the 'Course Prefix' column
    df_sorted = df.sort_values(by='COURSE PREFIX')

    # Write the sorted DataFrame back to the CSV file
    df_sorted.to_csv(file_path, index=False)

    df = pd.read_csv(file_path)

    return [Course_Prefix(row["COURSE PREFIX"], row["FULL FORM"]) for index, row in df.iterrows()]