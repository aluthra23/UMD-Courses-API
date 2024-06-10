from course_prefixes_scraper import soc_scraper
from course_prefixes_scraper import course_catalog_scraper
import pandas as pd



# def update_umd_courses():
    soc_scraper()
    course_catalog_scraper("https://academiccatalog.umd.edu/undergraduate/approved-courses/")
    course_catalog_scraper("https://academiccatalog.umd.edu/graduate/courses/")

    df = pd.read_csv('umd_course_prefixes.csv')

    # Sort the DataFrame by the 'Course Prefix' column
    df_sorted = df.sort_values(by='COURSE PREFIX')

    # Write the sorted DataFrame back to the CSV file
    df_sorted.to_csv('umd_course_prefixes.csv', index=False)