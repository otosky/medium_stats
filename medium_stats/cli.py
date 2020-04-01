from datetime import datetime, timedelta
import os
import argparse
import configparser
from inspect import cleandoc

MODE_CHOICES = ['summary', 'events', 'articles', 'referrers']

def valid_date(string):
    if len(string) > 10:
        try:
            return datetime.strptime(string, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            msg = f"'{string}' is not a valid datetime - must be of form YYYY-MM-DDThh:mm:ss"
            raise argparse.ArgumentTypeError(msg)
    else:
        try:
            return datetime.strptime(string, "%Y-%m-%d")
        except ValueError:
            msg = f"'{string}' is not a valid date - must be of form YYYY-MM-DD"
            raise argparse.ArgumentTypeError(msg)

def valid_path(path):

    is_valid = os.path.exists(path)
    if not is_valid:
        msg = f"directory '{path}' does not exist"
        raise argparse.ArgumentTypeError(msg)
    return path

def create_directories(root_dir):

    sub_dir = f'{root_dir}/stats_exports'
    if not os.path.exists(sub_dir):
        os.chdir(root_dir)
        os.makedirs('stats_exports')
        folders = ['agg_stats', 'agg_events', 'post_events', 'post_referrers']
        for f in folders:
            dir_ = '{0}/{1}'.format(sub_dir, f)
            os.makedirs(dir_)
    
    return sub_dir

def get_argparser():
    cli_parser = argparse.ArgumentParser()
    subparser = cli_parser.add_subparsers(title='commands', dest='command')
    default_creds = os.path.join(os.path.expanduser('~'), '.medium_creds.ini')

    # cookie_fetcher
    usage = 'medium-stats fetch_cookies -u USERNAME --email EMAIL (--pwd PWD | --pw-in-env)'
    cf = subparser.add_parser('fetch_cookies', usage=usage, help='log in to Medium via Selenium and extract session cookies')
    login = cf.add_argument_group('login')
    login.add_argument('--email', metavar='EMAIL', help='login method email', required=True)
    pwd_group = login.add_mutually_exclusive_group(required=True)
    pwd_group.add_argument('--pwd', metavar='PWD', help='login method password')
    pwd_group.add_argument('--pwd-in-env', action='store_true', help="pulls Medium password from environment variable")
    cf.add_argument('--creds', default=default_creds, help='creds.ini file path with "sid" and "uid" values')

    # scraper
    usage = '''\
    medium-stats scrape -u USERNAME [--output_dir DIR] \
    (--creds PATH | (--sid SID --uid UID)) \
    (--all | [--start PERIOD_START] [--end PERIOD END]) \
    [--mode {summary, events, articles, referrers}]'''
    usage = usage.replace('    ', '')

    scrape = subparser.add_parser('scrape', usage=usage, help='get statistics')
    scrape.add_argument('-u', metavar='USERNAME', help='your Medium username')
    scrape.add_argument('--output_dir', type=valid_path, metavar='PATH', default=os.getcwd(), help='output file directory')
    creds_group = scrape.add_argument_group('creds')
    creds_group.add_argument('--creds', default=default_creds, help='creds.ini file path with "sid" and "uid" values')
    creds_group.add_argument('--sid', help='Medium session "sid" cookie value; REQUIRED if "--creds" path not supplied')
    creds_group.add_argument('--uid', help='your Medium "uid" cookie value; REQUIRED if "--creds" path not supplied')

    period_group = scrape.add_argument_group('period')
    period_group.add_argument('--all', action='store_true', help='full history since your first publication')
    period_group.add_argument('--start', type=valid_date, help='stats start date, format=YYYY-MM-DD')
    period_group.add_argument('--end', type=valid_date, help='stats end date, format=YYYY-MM-DD')

    scrape.add_argument('--mode', nargs='*', 
                        choices=MODE_CHOICES, default=MODE_CHOICES, 
                        help='limit retrieval to particular statistics; defaults to all modes')
    
    return cli_parser

def parse_scraper_args(args, parser):

    cookies_supplied = bool(args.sid or args.uid)
    if cookies_supplied and not bool(args.sid and args.uid):
        parser.error('Need both "sid" and "uid" arguments together.')
    
    if args.creds and cookies_supplied:
        parser.error('Set creds via "creds" path or "sid" and "uid" arguments. Not both.')

    if not bool(args.all or args.start or args.end):
        parser.error('Period must be set as "--all" or a range with "--start" and/or "--stop" values')

    if args.all:
        if args.all and bool(args.start or args.end):
            parser.error('''Can't use "--all" flag with "start" or "end" arguments''')
    else:
        if bool(args.start or args.end):
            if not args.end:
                end = datetime.utcnow()
                args.end = datetime(*end.timetuple()[:3])
            if not args.start:
                start = args.end - timedelta(days=1)
                args.start = datetime(*start.timetuple()[:3])
        # make sure start and end obey time-order
        if args.end < args.start:
            parser.error('Period "--end" cannot be prior to "--start"')

    return args

class MediumConfigHelper:

    def __init__(self, config_path):

        self.cookies = self._retrieve_cookies(config_path)
        self.sid = self.cookies['sid']
        self.uid = self.cookies['uid']

    def _validate_config(self, config_path):

        config = configparser.ConfigParser()
        config.read(config_path)
        section = config.has_section('MEDIUM')
        if not section:
            raise ValueError('Config file not properly formed')
        options = ['sid', 'uid']
        option_exists = [config.has_option('MEDIUM', opt) for opt in options]
        if sum(option_exists) != len(options):
            raise ValueError('Config file not properly formed')
        
        return config

    def _retrieve_cookies(self, config_path):

        config_exists = os.path.exists(config_path)
        if not config_exists:
            raise ValueError('Config file does not exist')
        
        config = self._validate_config(config_path)
        cookies = config['MEDIUM']
        
        return dict(cookies)