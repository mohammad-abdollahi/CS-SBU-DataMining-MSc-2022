from tokenize import String
from khayyam import JalaliDate
import pandas as pd


def parse_time(t):
    t = list(map(int, t.split('-')))
    return JalaliDate(t[0], t[1], t[2]).todate().strftime('%Y-%m-%d')

def convert_date(data:pd.DataFrame):
    data['shamsi_time'] = data['time']
    data['time'] = data['time'].apply(lambda x: pd.to_datetime(parse_time(x)))
    return data