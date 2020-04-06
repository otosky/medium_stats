from datetime import datetime, timezone
import os
import argparse
from importlib.util import find_spec
from functools import partial

extras = ['selenium', 'webdriver_manager']

def check_dependencies_missing(extras=extras):
    dependencies = [bool(find_spec(e)) for e in extras]
    if sum(dependencies) == len(extras):
        return []
    
    missing = [z[0] for z in zip(extras, dependencies) if not z[1]]
    return missing

def valid_date(string, error, to_utc=True):
    if len(string) > 10:
        try:
            dt = datetime.strptime(string, "%Y-%m-%dT%H:%M:%S")
            if to_utc:
                dt = dt.astimezone(timezone.utc)
            return dt
        except ValueError:
            msg = f"'{string}' cannot be parsed as datetime - must be of form YYYY-MM-DDThh:mm:ss"
            raise error(msg)
    else:
        try:
            dt = datetime.strptime(string, "%Y-%m-%d")
            if to_utc:
                dt = dt.astimezone(timezone.utc)
            return dt
        except ValueError:
            msg = f"'{string}' cannot be parsed as datetime - must be of form YYYY-MM-DD"
            raise error(msg)

valid_date = partial(valid_date, error=argparse.ArgumentTypeError, to_utc=False)

# def ensure_datetime(dt):
        
#     if not isinstance(dt, datetime):
#         msg = f'argument "{dt}" must be of type datetime.datetime'
#         raise TypeError(msg)
        
#     return dt

def dt_formatter(dt, output):
    
    if output == 'json':
        dt = dt.strftime('%Y-%m-%dT%H:%M:%S')
    elif output == 'filename':
        dt = dt.strftime('%Y%m%dT%H%M%S')
        
    return dt    

def make_utc_explicit(dt, utc_naive):

    if utc_naive:
        return dt.replace(tzinfo=timezone.utc)
    
    return dt.astimezone(timezone.utc)

def convert_datetime_to_unix(dt, ms=True):
    
    dt = dt.astimezone(timezone.utc)
    dt = int(dt.timestamp())
    
    if ms:
        dt = dt * 1000
    
    return dt