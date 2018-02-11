import datetime


def date_delta(date0, date1):
    d0 = datetime.datetime.strptime(date0, DATE_FORMAT)
    d1 = datetime.datetime.strptime(date1, DATE_FORMAT)

    delta = d1 - d0

    return delta.days


def increment_date(d, days=1):
    return (datetime.datetime.strptime(d, '%Y-%m-%d') + datetime.timedelta(days=days)).strftime('%Y-%m-%d')


def today():
    return datetime.datetime.now().strftime('%Y-%m-%d')
