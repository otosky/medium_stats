from datetime import datetime
import os
import argparse
from importlib.util import find_spec

extras = ['selenium', 'webdriver_manager']

def check_dependencies_missing(extras=extras):
    dependencies = [bool(find_spec(e)) for e in extras]
    if sum(dependencies) == len(extras):
        return []
    
    missing = [z[0] for z in zip(extras, dependencies) if not z[1]]
    return missing

def ensure_date_valid(dt):
        
    if not isinstance(dt, (datetime, str)):
        msg = f'argument "{dt}" must be of type string or datetime.datetime'
        raise TypeError(msg)

    if isinstance(dt, str):
        try:
            dt = datetime.strptime(dt, "%Y-%m-%d")
            return dt
        except ValueError:
            msg = f"'{dt}' is not a valid date - must be of form YYYY-MM-DD"
            raise ValueError(msg)

    return dt

def dt_formatter(dt, output):
    
    if type(dt) == str:
        dt = ensure_date_valid(dt)
    
    if output == 'json':
        dt = dt.strftime('%Y-%m-%dT%H:%M:%S')
    elif output == 'filename':
        dt = dt.strftime('%Y%m%dT%H%M%S')
        
    return dt    