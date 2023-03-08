import datetime
from aqt import mw

import consts
import xp_system


#* REVIEW COUNTS

def get_review_count(day_dt=datetime.datetime.today()):    
    day_dt = day_dt.replace(hour=0, minute=0, second=0, microsecond=0)

    start = int(day_dt.timestamp() * 1000)
    end = int((day_dt + datetime.timedelta(days=1)).timestamp() * 1000)

    reviews = mw.col.db.scalar(
        "SELECT COUNT(*) FROM revlog WHERE id >= ? AND id < ? AND ease > 0", start, end)

    return reviews

def get_review_count_retention(day_dt=datetime.datetime.today()):
    day_dt = day_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    
    start = int(day_dt.timestamp() * 1000)
    end = int((day_dt + datetime.timedelta(days=1)).timestamp() * 1000)

    reviews = mw.col.db.scalar(
        "SELECT COUNT(*) FROM revlog WHERE id >= ? AND id < ? AND ease > 0", start, end)
    
    failed = mw.col.db.scalar(
        "SELECT COUNT(*) FROM revlog WHERE ease == 1 AND id >= ? AND id < ?", start, end)
    
    if reviews == 0:
        return 0, 0
    
    retention_rate = (reviews - failed) / reviews
    
    return reviews, retention_rate

def get_daily_reviews_since(dt):
    end = datetime.datetime.today() + datetime.timedelta(days=1)
    start_i = dt
    start_i.replace(hour=0, minute=0, second=0, microsecond=0)
    
    data = {}
    
    streak_current = 0
    streak_highest = 0
    
    while start_i < end:        
        reviews = get_review_count(start_i)
        
        if reviews > 0:        
            data[consts.get_date_str(start_i)] = reviews
            streak_current += 1
        else:
            if streak_current > streak_highest:
                streak_highest = streak_current
                
            # if its today, dont reset streak
            if start_i + datetime.timedelta(days=1) < end:
                streak_current = 0
        
        start_i += datetime.timedelta(days=1)

    return data, {"current": streak_current, "highest": streak_highest}

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

#* STREAK

def get_current_streak():
    """Get current daily streak

    Returns:
        int: streak
    """
    
    dt = datetime.datetime.utcnow()
    streak = 0
    
    r = get_review_count(dt)
    while r > 0:
        dt -= datetime.timedelta(days=1)
        r = get_review_count(dt)
        streak += 1
        
    return streak

#* OVERALL

def get_stats_daily_since(dt: datetime.datetime):
    """Get review count, retention rate and minutes since a given date (daily)

    Args:
        dt (datetime): datetime to start counting from
    """
    
    end = datetime.datetime.today() + datetime.timedelta(days=1)
    start_i = dt
    start_i.replace(hour=0, minute=0, second=0, microsecond=0)
    
    data = {}
    
    while start_i < end:        
        reviews, retention = get_review_count_retention(start_i)
        minutes = get_time_spent(start_i)
        
        if reviews > 0:        
            data[consts.get_date_str(start_i)] = {
                "reviews": reviews,
                "xp": xp_system.calc_xp(reviews, retention),
                "minutes": minutes
            }
        
        start_i += datetime.timedelta(days=1)

    return data
