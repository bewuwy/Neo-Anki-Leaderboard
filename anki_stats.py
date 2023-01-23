import datetime
from aqt import mw

import consts


#* REVIEW COUNTS

def get_review_count(day_dt=datetime.datetime.today()):    
    day_dt = day_dt.replace(hour=0, minute=0, second=0, microsecond=0)

    start = int(day_dt.timestamp() * 1000)
    end = int((day_dt + datetime.timedelta(days=1)).timestamp() * 1000)

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
        reviews = get_review_count(start_i)
        
        if reviews > 0:        
            data[consts.get_date_str(start_i)] = reviews
        
        start_i += datetime.timedelta(days=1)

    return data

#* TIME SPENT

def get_time_spent(day_dt=datetime.datetime.today(), minutes=True):
    
    # reset day_dt to 00:00:00
    day_dt = day_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    
    start = int(day_dt.timestamp() * 1000)
    end = int((day_dt + datetime.timedelta(days=1)).timestamp() * 1000)
    
    time = mw.col.db.scalar("SELECT SUM(time) FROM revlog WHERE id >= ? AND id < ?", start, end)
    if not time or time <= 0:
        return 0
    
    if minutes:
        time = time / 1000 / 60
        time = round(time, 1)
    
    return time
