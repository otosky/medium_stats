import requests, json
import argparse, configparser
from datetime import datetime, timedelta
from functools import partial
import os, re
from medium_stats.scraper import StatGrabber
from medium_stats.cli import create_directories, get_argparser, parse_scraper_args
from medium_stats.utils import dt_formatter
from medium_stats.cli import MediumConfigHelper

section_break = '\n{0}\n'.format('+' * 30)

mode_attrs = {
    'summary': {
        'title': 'Aggregated Summary Stats',
        'type': 'aggStats',
        'folder': 'agg_stats',
        'filename_suffix': 'summary_stats.json'
    },
    'events': {
        'title': 'Summary Event Logs',
        'type': 'aggEvents',
        'folder': 'agg_events',
        'filename_suffix': 'summary_events.json'
    },
    'articles': {
        'title': 'Article Event Logs',
        'type': 'postEvents',
        'folder': 'post_events',
        'filename_suffix': 'post_events.json'
    },
    'referrers': {
        'title': 'Referrer Data',
        'type': 'referrers',
        'folder': 'post_referrers',
        'filename_suffix': 'post_referrers.json'
    }
}

def get_stats(sg, mode, now, articles=None):

    extras = mode_attrs[mode]
    now_json = dt_formatter(now, 'json')
    
    if mode in ['events', 'articles']:
        period_start, period_stop = map(partial(dt_formatter, output='json'), 
                                        [sg.start, sg.stop])
    
    def template_data(mode):

        if mode in ['summary', 'referrers']:
            dict_ = {
                'timestamp': now_json,
                'type': extras['type']
            }
        elif mode in ['articles', 'events']:
            dict_ = {
                'periodBegin': period_start,
                'periodEnd': period_stop,
                'type': extras['type']
            }
        return dict_

    print(f'\nGetting {extras["title"]}...', end='\n\n')

    if mode == 'summary':
        agg_stats = sg.get_summary_stats()
        articles = sg.get_article_ids(agg_stats)
    
        data = {'data': {'post': agg_stats}}
    elif mode == 'events':
        non_attrib_events = sg.get_summary_stats(events=True)

        data = {'data': {'events': non_attrib_events}}

    elif mode == 'articles':
        
        data = sg.get_all_story_stats(articles)
        
    elif mode == 'referrers':
        
        data = sg.get_all_story_stats(articles, type_='referrer')
        
    else:
        raise ValueError('"mode" param must be of choice {summary, events, articles, referrers}')
    
    extras = template_data(mode)
    
    return {**data, **extras}

def write_stats(sg, data, mode, now, sub_dir):

    extras = mode_attrs[mode]
    now_prefix = dt_formatter(now, 'filename')
    period_start_f, period_stop_f = map(partial(dt_formatter, output='filename'), 
                                        [sg.start, sg.stop])
    
    filename = '{}/{}/{}_{}'.format(sub_dir, extras['folder'], 
                                    now_prefix, extras['filename_suffix'])
    if mode in ['events', 'articles']:
        filename = '{}/{}/{}_{}_{}'.format(sub_dir, extras['folder'], 
                                           period_stop_f, period_start_f,
                                           extras['filename_suffix'])
    path = sg.write_json(data, filename)
    print(f'{extras["title"]} written to:')
    print(path, section_break, sep='\n')
    return path

def unpack_email_pwd(args):

    env_flag = args.pwd_in_env
    if env_flag:
            password = os.environ.get('MEDIUM_AUTH_PWD')
    else:
        password = args.pwd
    
    return args.email, password


def main():

    ## PARSE ARGS
    parser = get_argparser()
    args = parser.parse_args()
    
    # TODO - make this a plain path; not a directory argument
    config_path = re.sub('\/$', '', args.creds)
    if not config_path:
        config_path = os.path.join(os.path.expanduser('~'), '.medium_creds.ini')
    
    command = args.command

    ## EXECUTE COMMANDS
    if command == 'fetch_cookies':
        from medium_stats.cookie_fetcher import MediumAuthorizer
        
        email, password = unpack_email_pwd(args)
        
        me = MediumAuthorizer(email, password)
        me.sign_in()
        me.save_cookies(config_path)
        print(section_break)
    
    elif command == 'scrape':
        args = parse_scraper_args(args, parser)
        username = args.u

        root_dir = args.output_dir
        if not root_dir:
            root_dir = os.getcwd()

        sub_dir = create_directories(root_dir)

        if args.all:
            end = datetime.utcnow()
            start = datetime(year=1999, month=1, day=1)
        else:
            end = args.end
            start = args.start

        cfg = MediumConfigHelper(config_path)
        me = StatGrabber(username, cfg.sid, cfg.uid, start, end)

        print('\nGetting Preliminary Data...', end='\n\n')
        # get summary stats to derive article_ids and user creation_time
        data = me.get_summary_stats()
        articles = me.get_article_ids(data)
        if 'summary' in args.mode:
            write_stats(me, data, 'summary', me.now, sub_dir)
        
        mode = list(args.mode)
        # go through remainder of modes
        remaining = [m for m in mode if m != 'summary']
        for m in remaining:
            if m == 'events':
                data = get_stats(me, m, me.now)
                print(data)
            else:
                data = get_stats(me, m, me.now, articles)
                print(data)
            write_stats(me, data, m, me.now, sub_dir)
    
    print('All done!')

if __name__=="__main__":
    main()