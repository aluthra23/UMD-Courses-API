from datetime import datetime

from fastapi import HTTPException


def update_term_id():
    """
    Updates the term_id for the current semester
    """
    current_month = datetime.now().month
    current_year = datetime.now().year


    if current_month <= 2:
        term_id = f"{current_year}01"
    elif current_month <= 9:
        term_id = f"{current_year}08"
    else:
        term_id = f"{current_year + 1}01"


    return term_id.strip()

def check_term_id(term_id):
    if (len(term_id) != 6):
        raise HTTPException(status_code=404,
                            detail="Term ID must be 6 characters long and in YYYYMM format where MM must be 01 or 08!")
    elif not term_id.isdigit():
        raise HTTPException(status_code=404,
                            detail="Term ID must be a number and in YYYYMM format where MM must be 01 or 08!")
    elif int(term_id[2:4]) < 21:
        raise HTTPException(status_code=404,
                            detail="Year must be greater than 2020 and Term ID must be in YYYYMM format where MM must be 01 or 08!")
    elif int(term_id[4:6]) != 1 and int(term_id[4:6]) != 8:
        raise HTTPException(status_code=404,
                            detail="Month must be 01 or 08 and Term ID must be in YYYYMM format where MM must be 01 or 08!!")

# print(update_term_id())