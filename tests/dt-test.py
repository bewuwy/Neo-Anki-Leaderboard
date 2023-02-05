import datetime


if __name__ == "__main__":
    datetime_now = datetime.datetime.now()
    datetime_utc = datetime.datetime.utcnow()
    
    print("datetime_now:", datetime_now)
    print("datetime_utc:", datetime_utc)
