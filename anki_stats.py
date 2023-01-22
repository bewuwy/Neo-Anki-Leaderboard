import datetime
from aqt import mw

import consts


def get_review_count_today():
    start_date = datetime.datetime.today()
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

    end_date = datetime.datetime.today() + datetime.timedelta(days=1)

    start = int(start_date.timestamp() * 1000)
    end = int(end_date.timestamp() * 1000)

    reviews = mw.col.db.scalar(
        "SELECT COUNT(*) FROM revlog WHERE id >= ? AND id < ? AND ease > 0", start, end)

    return reviews


def get_review_count_since(dt):
    start = int(dt.timestamp() * 1000)

    reviews = mw.col.db.scalar(
        "SELECT COUNT(*) FROM revlog WHERE id >= ? AND ease > 0", start)

    return reviews

def get_daily_reviews_since(dt):
    end = datetime.datetime.today() + datetime.timedelta(days=1)
    start_i = dt
    start_i.replace(hour=0, minute=0, second=0, microsecond=0)
    
    data = {}
    
    while start_i < end:
        end_i = start_i + datetime.timedelta(days=1)
        
        start_id = int(start_i.timestamp() * 1000)
        end_id = int(end_i.timestamp() * 1000)
        
        reviews = mw.col.db.scalar(
            "SELECT COUNT(*) FROM revlog WHERE id >= ? AND id < ? AND ease > 0", start_id, end_id)
        
        data[consts.get_date_str(start_i)] = reviews
        
        start_i = end_i

    return data
