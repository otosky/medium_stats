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

def valid_date(string, error):
    if len(string) > 10:
        try:
            dt = datetime.strptime(string, "%Y-%m-%dT%H:%M:%S")
            return dt
        except ValueError:
            msg = f"'{string}' cannot be parsed as datetime - must be of form YYYY-MM-DDThh:mm:ss"
            raise error(msg)
    else:
        try:
            dt = datetime.strptime(string, "%Y-%m-%d")
            return dt
        except ValueError:
            msg = f"'{string}' cannot be parsed as datetime - must be of form YYYY-MM-DD"
            raise error(msg)

def dt_formatter(dt, output):
    
    if output == 'json':
        dt = dt.strftime('%Y-%m-%dT%H:%M:%S')
    elif output == 'filename':
        dt = dt.strftime('%Y%m%dT%H%M%S')
    else:
        raise ValueError(f'output param must be either "json" or "filename" not "{output}"')
        
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