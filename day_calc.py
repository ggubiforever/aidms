from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
import re

# 파라메터 기준일, 기간
def get_date(today,days): #today str: 20210901 / days 는 3일 이전이면 -3, 3일 이후면 3
    today = datetime.strptime(today,'%Y%m%d')
    dayterm = today + timedelta(days=days)
    return dayterm

def get_month(today,months):
    today = datetime.strptime(today,'%Y%m%d')
    month_term = today + relativedelta(months=int(months))

    return month_term
