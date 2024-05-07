import datetime

def get_date():
    tdate = datetime.datetime.today()
    tdate = tdate.strftime('%Y%m%d')
    return tdate