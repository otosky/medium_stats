import requests, json
import argparse, configparser
from datetime import datetime, timedelta, timezone
from functools import partial
import os, re
from medium_stats.scraper import StatGrabberUser, StatGrabberPublication
from medium_stats.cli import create_directories, get_argparser, parse_scraper_args
from medium_stats.utils import dt_formatter
from medium_stats.cli import MediumConfigHelper

section_break = '\n{0}\n'.format('+' * 30)

common_mode_attrs = {
    'articles': {
        'title': 'Article Event Logs',
        'type': 'postEvents',
        'folder': 'post_events',
        'filename_suffix': 'post_events.json',
        'is_aggregated': False
    },
    'referrers': {
        'title': 'Referrer Data',
        'type': 'referrers',
        'folder': 'post_referrers',
        'filename_suffix': 'post_referrers.json',
        'is_aggregated': True
    }
}

user_mode_attrs = {
    'summary': {
        'title': 'Aggregated Summary Stats',
        'type': 'aggStats',
        'folder': 'agg_stats',
        'filename_suffix': 'summary_stats.json',
        'is_aggregated': True
    },
    'events': {
        'title': 'Summary Event Logs',
        'type': 'aggEvents',
        'folder': 'agg_events',
        'filename_suffix': 'summary_events.json',
        'is_aggregated': False
    }
}
user_mode_attrs = {**user_mode_attrs, **common_mode_attrs}

pub_mode_attrs = {
    'events': {
        'title': 'Views & Visitors Event Logs',
        'type': 'pubEvents',
        'folder': 'agg_events',
        'filename_suffix': 'summary_events.json',
        'is_aggregated': False
    },
    'story_overview': {
        'title': 'Stories Overview',
        'type': 'storiesOverview',
        'folder': 'stories_summary',
        'filename_suffix': 'stories_summary.json',
        'is_aggregated': True
    }
}
pub_mode_attrs = {**pub_mode_attrs, **common_mode_attrs}

def get_extra_attrs(sg, mode):

    if isinstance(sg, StatGrabberUser):
        extras = user_mode_attrs[mode]
    elif isinstance(sg, StatGrabberPublication):
        extras = pub_mode_attrs[mode]
    
    return extras

def get_stats(sg, mode, now, articles=None):

    extras = get_extra_attrs(sg, mode)
    
    now_json = dt_formatter(now, 'json')
    
    if mode in ['events', 'articles']:
        period_start, period_stop = map(partial(dt_formatter, output='json'), 
                                        [sg.start, sg.stop])
     # TODO - add if-statement to make sure that modes that need articles have articles passed in as arg
     # if mode in ['articles', 'referrals'] and not articles: raise someError

    print(f'\nGetting {extras["title"]}...', end='\n\n')

    if mode == 'summary':
        agg_stats = sg.get_summary_stats()
        articles = sg.get_article_ids(agg_stats)
    
        data = {'data': {'post': agg_stats}}
    elif mode == 'events':
        
        if isinstance(sg, StatGrabberUser):
            non_attrib_events = sg.get_summary_stats(events=True)
            data = {'data': {'events': non_attrib_events}}
        elif isinstance(sg, StatGrabberPublication):
            views = sg.get_events(type_='views')
            visitors = sg.get_events(type_='visitors')
            data = {'data': {'views': views, 'visitors': visitors}}

    elif mode == 'story_overview':

        stories = sg.get_all_story_overview()
        data = {'data': {'story': stories}}
    
    elif mode == 'articles':
        
        data = sg.get_all_story_stats(articles)
        
    elif mode == 'referrers':
        
        data = sg.get_all_story_stats(articles, type_='referrer')
    
    else:
        # TODO remove hardcoding from this message - make choice list dynamic from keys
        raise ValueError('"mode" param must be of choice {summary, events, story_overview, articles, referrers}')
    
    if extras['is_aggregated']:
        extras = {
                'timestamp': now_json,
                'type': extras['type']
            }
    else:
        extras = {
                'periodBegin': period_start,
                'periodEnd': period_stop,
                'type': extras['type']
            }
    
    return {**data, **extras}

def write_stats(sg, data, mode, now, sub_dir):

    extras = get_extra_attrs(sg, mode)
    now_prefix = dt_formatter(now, 'filename')
    period_start_f, period_stop_f = map(partial(dt_formatter, output='filename'), 
                                        [sg.start, sg.stop])
    
    filename = '{}/{}/{}_{}_{}'.format(sub_dir, extras['folder'], 
                                    now_prefix, sg.slug, extras['filename_suffix'])
    if mode in ['events', 'articles']:
        filename = '{}/{}/{}_{}_{}_{}'.format(sub_dir, extras['folder'], 
                                           period_stop_f, period_start_f,
                                           sg.slug, extras['filename_suffix'])
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
    
    command = args.command

    ## EXECUTE COMMANDS
    if command == 'fetch_cookies':
        from medium_stats.cookie_fetcher import MediumAuthorizer
        
        email, password = unpack_email_pwd(args)
        
        me = MediumAuthorizer(args.u, email, password)
        me.sign_in()
        me.save_cookies(args.creds)
        print(section_break)
    
    elif command in ['scrape_user', 'scrape_publication']:
        args = parse_scraper_args(args, parser)
        
        if args.creds:
            cfg = MediumConfigHelper(args.creds, args.u)
            sid, uid = cfg.sid, cfg.uid
        else:
            sid, uid = args.sid, args.uid

        modes = list(args.mode)

        get_folders = lambda x: [x[m]['folder'] for m in modes]

        print('\nGetting Preliminary Data...', end='\n\n')
        if command == 'scrape_user':
            username = args.u
            sg = StatGrabberUser(username, sid, uid, args.start, args.end, already_utc=True)
            folders = get_folders(user_mode_attrs)
            sub_dir = create_directories(args.output_dir, sg.slug, folders)
            
            # get summary stats to derive article_ids and user creation_time
            data = sg.get_summary_stats()
            articles = sg.get_article_ids(data)
            if 'summary' in modes:
                write_stats(sg, data, 'summary', sg.now, sub_dir)
            
        else:
            url = args.s
            sg = StatGrabberPublication(url, sid, uid, args.start, args.end, already_utc=True)
            folders = get_folders(pub_mode_attrs)
            sub_dir = create_directories(args.output_dir, sg.slug, folders)
            data = sg.get_all_story_overview()
            articles = sg.get_article_ids(data)
            if 'story_overview' in modes:
                write_stats(sg, data, 'story_overview', sg.now, sub_dir)

        # go through remainder of modes
        remaining = [m for m in modes if m not in ('summary', 'story_overview')]
        for m in remaining:
            if m == 'events':
                data = get_stats(sg, m, sg.now)
            else:
                data = get_stats(sg, m, sg.now, articles)
            write_stats(sg, data, m, sg.now, sub_dir)

    print('All done!')

if __name__=="__main__":
    main()