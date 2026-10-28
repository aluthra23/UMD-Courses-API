from datetime import datetime

from fastapi import HTTPException


def default_term_id(now=None):
    """The current or upcoming UMD term: spring through Feb 20, fall through September, then next spring."""
    now = now or datetime.now()
    if now.month == 1 or (now.month == 2 and now.day <= 20):
        return f"{now.year}01"
    if now.month <= 9:
        return f"{now.year}08"
    return f"{now.year + 1}01"


def update_term_id():
    return default_term_id()


def check_term_id(term_id):
    if len(term_id) != 6:
        raise HTTPException(status_code=400,
                            detail="Term ID must be 6 characters long and in YYYYMM format where MM must be 01 or 08!")
    elif not term_id.isdigit():
        raise HTTPException(status_code=400,
                            detail="Term ID must be a number and in YYYYMM format where MM must be 01 or 08!")
    elif int(term_id[0:4]) < datetime.now().year - 1:
        raise HTTPException(status_code=400,
                            detail=f"Year must be {datetime.now().year - 1} or greater!")
    elif int(term_id[4:6]) != 1 and int(term_id[4:6]) != 8:
        raise HTTPException(status_code=400,
                            detail="Month must be 01 or 08!")
