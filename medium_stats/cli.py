from datetime import datetime, timedelta, timezone
import os
import argparse
import configparser
from inspect import cleandoc
from medium_stats.utils import valid_date, make_utc_explicit
from functools import partial
from inspect import cleandoc

USER_MODE_CHOICES = ['summary', 'events', 'articles', 'referrers']
PUB_MODE_CHOICES = ['events', 'story_overview', 'articles', 'referrers']

valid_date = partial(valid_date, error=argparse.ArgumentTypeError)

def valid_path(path):

    is_valid = os.path.exists(path)
    if not is_valid:
        msg = f"directory '{path}' does not exist"
        raise argparse.ArgumentTypeError(msg)
    return path

def create_directories(root_dir, handle, folders):

    sub_dir = f'{root_dir}/stats_exports/{handle}'
    if not os.path.exists(sub_dir):
        os.chdir(root_dir)
        for f in folders:
            dir_ = '{0}/{1}'.format(sub_dir, f)
            # TODO only make folder if doesn't already exist
            os.makedirs(dir_)
    
    return sub_dir

def get_argparser():

    def add_subarguments(parser):
        
        parser.add_argument('--output_dir', type=valid_path, metavar='PATH', default=os.getcwd(), help='output file directory')
        creds_group = parser.add_argument_group('creds')
        creds_group.add_argument('--creds', default=default_creds, help='.ini file path with "sid" and "uid" values')
        creds_group.add_argument('--sid', help='Medium session "sid" cookie value; REQUIRED if "--creds" path not supplied')
        creds_group.add_argument('--uid', help='your Medium "uid" cookie value; REQUIRED if "--creds" path not supplied')

        period_group = parser.add_argument_group('period')
        period_group.add_argument('--all', action='store_true', help='full history since your first publication')
        period_group.add_argument('--start', type=valid_date, help='stats start date, format=YYYY-MM-DD')
        period_group.add_argument('--end', type=valid_date, help='stats end date, format=YYYY-MM-DD')
        period_group.add_argument('--is-utc', action='store_true', help='start/end times are in UTC')

    cli_parser = argparse.ArgumentParser()
    subparser = cli_parser.add_subparsers(title='commands', dest='command')
    default_creds = os.path.join(os.path.expanduser('~'), '.medium_creds.ini')

    # cookie_fetcher
    usage = 'medium-stats fetch_cookies -u USERNAME --email EMAIL (--pwd PWD | --pw-in-env)'
    cf = subparser.add_parser('fetch_cookies', usage=usage, help='log in to Medium via Selenium and extract session cookies')
    cf.add_argument('-u', metavar='HANDLE', help='Medium username')
    login = cf.add_argument_group('login')
    login.add_argument('--email', metavar='EMAIL', help='login method email', required=True)
    pwd_group = login.add_mutually_exclusive_group(required=True)
    pwd_group.add_argument('--pwd', metavar='PWD', help='login method password')
    pwd_group.add_argument('--pwd-in-env', action='store_true', help="pulls Medium password from environment variable")
    cf.add_argument('--creds', default=default_creds, help='creds.ini file path with "sid" and "uid" values')


    # USER
    usage = '''\
    medium-stats scrape_user -u USERNAME [--output_dir DIR] \
    (--creds PATH | (--sid SID --uid UID)) \
    (--all | [--start PERIOD_START] [--end PERIOD END]) [--is-utc]\
    [--mode {summary, events, articles, referrers}]'''
    usage = usage.replace('    ', '')

    scrape_user = subparser.add_parser('scrape_user', usage=usage, help='get user statistics')
    scrape_user.add_argument('-u', metavar='USERNAME', help='your Medium username')
    
    add_subarguments(scrape_user)
    scrape_user.add_argument('--mode', nargs='*', 
                        choices=USER_MODE_CHOICES, default=USER_MODE_CHOICES, 
                        help='limit retrieval to particular statistics; defaults to all modes')
    
    # PUBLICATION
    usage = '''\
    medium-stats scrape_publication -u USERNAME -s PUBLICATION_SLUG [--output_dir DIR] \
    (--creds PATH | (--sid SID --uid UID)) \
    (--all | [--start PERIOD_START] [--end PERIOD_END]) [--is-utc]\
    [--mode {events, story_overview, articles, referrers}]'''
    usage = usage.replace('    ', '')

    scrape_pub = subparser.add_parser('scrape_publication', usage=usage, help='get publication statistics')
    scrape_pub.add_argument('-u', metavar='USERNAME', help='your Medium username')
    slug_msg = ''' 
    publication slug, e.g. "publication-name" if url is "medium.com/publication-name"
    '''
    scrape_pub.add_argument('-s', metavar='PUBLICATION_SLUG', help=cleandoc(slug_msg))
    add_subarguments(scrape_pub)
    scrape_pub.add_argument('--mode', nargs='*', 
                        choices=PUB_MODE_CHOICES, default=PUB_MODE_CHOICES, 
                        help='limit retrieval to particular statistics; defaults to all modes')

    return cli_parser

def parse_scraper_args(args, parser):

    args.creds = args.creds.replace('~', str(os.path.expanduser('~')))
    
    if not os.path.exists(args.creds):
        parser.error(f'''Creds File does not exist at: {args.creds}''')

    cookies_supplied = bool(args.sid or args.uid)
    if cookies_supplied and not bool(args.sid and args.uid):
        parser.error('Need both "sid" and "uid" arguments together.')
    
    if cookies_supplied:
        args.creds=None

    if not bool(args.all or args.start or args.end):
        parser.error('Period must be set as "--all" or a range with "--start" and/or "--stop" values')

    if args.all:
        if args.all and bool(args.start or args.end):
            parser.error('''Can't use "--all" flag with "start" or "end" arguments''')
        if args.all and args.is_utc:
            parser.error('''Can't use "--all" flag with "--is-utc" flag''')
        args.end = datetime.now(timezone.utc)
        args.start = datetime(year=1999, month=1, day=1, tzinfo=timezone.utc)
    else:
        if bool(args.start or args.end):
            if not args.end:
                end = datetime.now(timezone.utc)
                args.end = datetime(*end.timetuple()[:3]).replace(tzinfo=timezone.utc)
            if not args.start:
                start = args.end - timedelta(days=1)
                args.start = datetime(*start.timetuple()[:3]).replace(tzinfo=timezone.utc)

    # convert to UTC here
    make_utc = partial(make_utc_explicit, utc_naive=args.is_utc)
    args.start, args.end = map(make_utc, (args.start, args.end))

    # make sure start and end obey time-order
    if args.end < args.start:
        parser.error('Period "--end" cannot be prior to "--start"')

    return args

class MediumConfigHelper:

    def __init__(self, config_path, account_name):

        self.handle = account_name
        self.cookies = MediumConfigHelper._retrieve_cookies(config_path, account_name)
        self.sid = self.cookies['sid']
        self.uid = self.cookies['uid']
    
    @staticmethod
    def _validate_config(config_path, account_name):
        '''
        Checks to see if config file has correct sections:
        [account_name]
        sid = sid_here
        uid = uid_here
        '''

        config = configparser.ConfigParser()
        config.read(config_path)
        section = config.has_section(account_name)
        if not section:
            raise ValueError(f'Account name "{account_name}" not found in section headers')
        options = ['sid', 'uid']
        option_exists = [config.has_option(account_name, opt) for opt in options]
        if sum(option_exists) < len(options):
            raise ValueError('Config file not properly formed')
        
        return config

    @classmethod
    def _retrieve_cookies(cls, config_path, account_name):

        config_exists = os.path.exists(config_path)
        if not config_exists:
            raise ValueError('Config file does not exist')
        
        config = cls._validate_config(config_path, account_name)
        cookies = config[account_name]
        
        return dict(cookies)