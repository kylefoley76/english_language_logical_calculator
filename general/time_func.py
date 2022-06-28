from datetime import datetime, timedelta, timezone
from dateutil import parser
import time

from abbreviations import *

bb=8

def combine_hour2day(hor, day):
    day = day.replace(hour=hor.hour)
    day = day.replace(minute=hor.minute)
    return day


def add_dates_wo_data(dct, today, blanks):
    lst_day = list(dct.keys())[-1]
    ldt = from_str2dt(lst_day)
    str1 = lst_day
    b = 0
    while str1 != today:
        ldt = ldt + timedelta(days=1)
        str1 = from_dt2str_yr_day(ldt)
        dct[str1] = blanks
        b += 1
        if b > 30:
            p ('caught in infinite loop in add_dates_wo_data function')
            sys.exit()
    return dct

def get_hour_min_now():
    return today_dat('hr_min')


def today_dat(kind='yr_day', adj=0):
    nw = time.time()
    nw = nw - (5 * 60 * 60)
    nw -= adj * 24 * 60 * 60
    hour = from_unix2dt(nw)
    if kind == 'yr_day':
        return from_dt2str_yr_day(hour)
    else:
        return from_dt2str_hr_min(hour)






def adjust_year(dt, tyear, skip_errors=0):
    if skip_errors == 0:
        tyear = int("20" + str(int(tyear)))
        return dt.replace(year=tyear)
    else:
        tyear = int("20" + str(tyear))
        try:
            dt.replace(year=tyear)
            return dt
        except:
            p('problem in adjust year function')
            return dt


def from_unix2dt(epoch, tz=0):
    """
    tz = 2 is eastern
    tz = 0 is pacific
    """

    if not tz:
        return datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=epoch)
    elif tz == 2:
        dt = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=epoch)
        return dt + timedelta(hours=3)
    else:
        dt = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=epoch)
        return dt - timedelta(hours=8)


def is_dt(obj):
    try:
        if type(obj) is datetime:
            return True

    except:
        return False


def from_dt2str_hr_min(dt):
    try:
        return dt.strftime("%H:%M")
    except:
        return dt


def from_dt2str_hour_sec(dt):
    try:
        return dt.strftime("%H:%M:%S")
    except:
        return dt


def from_dt2str_mon_sec(dt):
    try:
        return dt.strftime("%-m/%d %H:%M:%S")
    except:
        return dt


def from_dt2str_mon_min(dt):
    try:
        return dt.strftime("%-m/%d %H:%M")
    except:
        return dt


def from_dt2str_mon_day(dt):
    try:
        return dt.strftime("%-m/%d")
    except:
        return dt


def get_period(thour, lhour):
    try:
        thour = thour.strftime("%H:%M")
        thour = datetime.strptime(thour, "%H:%M")
    except:
        thour = parser.parse(thour)

    try:
        lhour = lhour.strftime("%H:%M")
        lhour = datetime.strptime(lhour, "%H:%M")
    except:
        lhour = parser.parse(lhour)

    quant = thour - lhour
    return quant.seconds / 3600


def from_dt2unix(dt):
    dt = dt - datetime(1970, 1, 1)
    return dt.total_seconds()


def from_unix2str_mon_min(num):
    ts_time = from_unix2dt(num)
    return from_dt2str_mon_min(ts_time)


def from_unix2str_hour_min(num):
    ts_time = from_unix2dt(num)
    return from_dt2str_hr_min(ts_time)


def from_unix2str_yr_day(num):
    ts_time = from_unix2dt(num)
    return from_dt2str_yr_day(ts_time)


def from_str2unix(str1):
    dt = from_str2dt(str1)
    return from_dt2unix(dt)


def from_str2dt(str1, error=0):
    if isinstance(str1, str):
        try:
            dt = parser.parse(str1)
            return dt
        except:
            p(f'failed to convert {str1} to datetime')
            if error:
                return 0

            raise Exception
    else:
        return str1


def from_gmt2pst(num):
    return num - (60 * 60 * 7)


def get_str_yr_day_now():
    now = datetime.now()
    return from_dt2str_yr_day(now)


def get_week_name(dt):
    return "w" + dt.strftime("%V") + " " + get_month_name(dt) + " " + get_abb_year(dt)


def get_week_num(dt):
    return dt.strftime("%V")


def from_dt2wk(dt, subtract7=False):
    if subtract7:
        dt = dt - timedelta(days=7)
    b = dt.weekday()
    if b == 6:
        start = dt
        end = dt + timedelta(days=6)
    else:
        start = dt - timedelta(days=b)
        start = start - timedelta(days=1)
        end = dt + timedelta(days=(5 - b))
    if start.month == end.month:
        str1 = str(start.month) + "/" + str(start.day) + " - " + str(end.day) + "/" + str(end.year)
    else:
        str1 = str(start.month) + "/" + str(start.day) + " - " + str(end.month) + "/" + str(end.day) + "/" + str(
            end.year)
    return str1


def get_month_name(dt):
    return dt.strftime("%b").lower()


def get_abb_year(dt):
    return dt.strftime("%y")


def from_dt2str_yr_day(dt):
    if not type(dt) == datetime: return dt
    return dt.strftime("%-m/%-d/%-y")


def from_dt2str_yr_mon(dt,yyyy=0):
    if not type(dt) == datetime: return dt
    if yyyy:
        return dt.strftime("%-m/%-Y")
    else:
        return dt.strftime("%-m/%-y")

def from_dt2_MMM_YYYY(dt):
    dct = {
        1:'jan',
        2:'feb',
        3:'mar',
        4:'apr',
        5:'may',
        6:'jun',
        7:'jul',
        8:'aug',
        9:'sept',
        10:'oct',
        11:'nov',
        12:'dec',
    }
    mon = dct.get(dt.month)
    year = dt.year
    return f'{mon} {year}'



def from_mon_str2year_day(str1):
    dct = {
        'jan': '1',
        'feb': '2',
        'mar': '3',
        'apr': '4',
        'may': '5',
        'jun': '6',
        'jul': '7',
        'aug': '8',
        'sep': '9',
        'oct': '10',
        'nov': '11',
        'dec': '12',
    }
    str2 = dct[str1[:3]]
    return f"{str2}/1/{str1[-2:]}"


def from_str_mon2unix(str1):
    str1 = from_mon_str2year_day(str1)
    return from_str2unix(str1)


def from_str_week2unix(str1):
    dt = from_week_end2day(str1)
    return from_dt2unix(dt)


def from_week_end2day(str1):
    lst = str1.split(" - ")
    if lst[1].count("/") > 1:
        lst = lst[1].split("/")
        return datetime(int(lst[2]), int(lst[0]), int(lst[1]))
    else:
        lst2 = lst[1].split("/")
        lst = lst[0].split("/")
        return datetime(int(lst2[1]), int(lst[0]), int(lst2[0]))
