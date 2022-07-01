import pandas as pd
import numpy as np
from khayyam import JalaliDatetime
from dateutil.relativedelta import relativedelta


def linear_interpolation(data:pd.DataFrame ,config:dict)-> dict:
    """ module to handle linear interpolation

    Args:
        data (pd.DataFrame): dataframe with missing data
        config (dict): configs for interpolation, including time, type, interpolation

    Returns:
        dict: interpolated dataframe
    """    
    data = fill_missing_dates(data, config['time'])
    data.rename({'index':'time'}, axis=1, inplace=True)

    ## apply interpolation
    data['vol'] = data['vol'].interpolate()
    data['time'] = data['time'].dt.strftime('%Y-%m-%d')
    
    if 'shamsi_time' in data.columns:
        data.drop(['time'], axis=1, inplace=True)
        data.rename({'shamsi_time':'time'}, axis=1, inplace=True)

    return data.to_dict()

def custom_interpolation(data:pd.DataFrame, config:dict) -> dict:
    """ module to handle different kinds of interpolation

    Args:
        data (pd.DataFrame): dataframe with missing data
        config (dict): configs for interpolation, including time, type, interpolation

    Returns:
        dict: interpolated dataframe
    """    
    data = fill_missing_dates(data, config['time'])
    data.rename({'index':'time'}, axis=1, inplace=True)

    ##apply interpolation
    if config['interpolation'] == 'spline' or config['interpolation'] == 'polynomial':
        data['vol'] = data['vol'].interpolate(config['interpolation'], order=5)
    else:
        data['vol'] = data['vol'].interpolate(config['interpolation'])
    data['time'] = data['time'].dt.strftime('%Y-%m-%d')
    
    ## prepare shamsi data
    if 'shamsi_time' in data.columns:
        data.drop(['time'], axis=1, inplace=True)
        data.rename({'shamsi_time':'time'}, axis=1, inplace=True)

    return data.to_dict()

def fill_missing_dates(data:pd.DataFrame, freq='daily')->pd.DataFrame:
    """ a module to fill missing dates for interpolation

    Args:
        data (pd.DataFrame): dataframe with missing dates
        freq (str, optional): time parameter in config dict. Defaults to 'daily'.

    Returns:
        pd.DataFrame: dataframed with filled dates
    """    
    if 'shamsi_time' in data.columns and freq=='daily':
        data = data.set_index("time").reindex(pd.date_range(data['time'].min(), data['time'].max()), fill_value=np.nan).reset_index()
        data.rename({'index':'time'}, axis=1, inplace=True)
        data['shamsi_time'] = data['time'].apply(lambda x:JalaliDatetime(x).strftime('%Y-%m-%d'))
        return data

    elif 'shamsi_time' in data.columns and freq=='monthly':
        data['time'] = data['time'].apply(lambda x: x+relativedelta(months=1))
        data['time'] = data['time'].apply(lambda x:x.replace(day=1))
        data = data.set_index("time").reindex(pd.date_range(data['time'].min(), data['time'].max(), freq='MS'), fill_value=np.nan).reset_index()
        data.rename({'index':'time'}, axis=1, inplace=True)
        data['shamsi_time'] = data['time'].apply(lambda x:JalaliDatetime(x).strftime('%Y-%m-01'))
        return data

    elif freq=='daily':
        return (
            data.set_index("time")
            .reindex(pd.date_range(data['time'].min(), data['time'].max()), fill_value=np.nan)
            .reset_index()
        )
    elif freq=='monthly':
        return (
            data.set_index("time")
            .reindex(pd.date_range(data['time'].min(), data['time'].max(), freq='MS'), fill_value=np.nan)
            .reset_index()
        )

def service2_interpolation(data:pd.DataFrame, config:dict) -> dict:
    data = fill_missing_dates_service2(data, config['time'])
    data.rename({'index':'time'}, axis=1, inplace=True)
    data['time'] = pd.to_datetime(data['time'])

    if config['skip_holiday']:
        ## drop thursdays
        data = data[data.time.dt.dayofweek != 3]
        ## drop fridays
        data = data[data.time.dt.dayofweek != 4]

    ## apply interpolation
    data['vol'] = data['vol'].interpolate(config['interpolation'])
    data['time'] = data['time'].dt.strftime('%Y-%m-%d')
    
    data.drop(['time'], axis=1, inplace=True)
    data.rename({'shamsi_time':'time'}, axis=1, inplace=True)

    return data.to_dict()

def fill_missing_dates_service2(data:pd.DataFrame, freq='daily') -> pd.DataFrame:
    if freq=='daily':
        data = data.set_index("time").reindex(pd.date_range(data['time'].min(), data['time'].max()), fill_value=np.nan).reset_index()
        data.rename({'index':'time'}, axis=1, inplace=True)
        data['shamsi_time'] = data['time'].apply(lambda x:JalaliDatetime(x).strftime('%Y-%m-%d'))
        return data

    elif freq=='monthly':
        data['time'] = data['time'].apply(lambda x: x+relativedelta(months=1))
        data['time'] = data['time'].apply(lambda x:x.replace(day=1))
        data = data.set_index("time").reindex(pd.date_range(data['time'].min(), data['time'].max(), freq='MS'), fill_value=np.nan).reset_index()
        data.rename({'index':'time'}, axis=1, inplace=True)
        data['shamsi_time'] = data['time'].apply(lambda x:JalaliDatetime(x).strftime('%Y-%m-01'))
        return data