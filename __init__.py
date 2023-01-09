from aqt import mw, gui_hooks
import datetime

def log(msg):
    print(f"NAL: {msg}")

log("\n"*5)

log("="*20)
log("Anki leaderboard addon loaded")
log("="*20)

log("\n"*5)

def get_review_count_today():
    start_date = datetime.datetime.today()
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    end_date = datetime.datetime.today() + datetime.timedelta(days=1)
    
    start = int(start_date.timestamp() * 1000)
    end = int(end_date.timestamp() * 1000)

    reviews = mw.col.db.scalar("SELECT COUNT(*) FROM revlog WHERE id >= ? AND id < ? AND ease > 0", start, end)
    
    return reviews

def log_review_count():
    log(f"Review count today: {get_review_count_today()}")


gui_hooks.sync_did_finish.append(log_review_count)
