#!/usr/bin/env python3

import argparse
import json
import requests
import sys
from datetime import datetime

SUPPORTED_BUILDS = {
    6002:  'https://support.microsoft.com/en-us/help/4343218', # 2008 SP2
    7601:  'https://support.microsoft.com/en-us/help/4009469', # 7 / 2008R2 SP1
    9200:  'https://support.microsoft.com/en-us/help/4009471', # 2012
    9600:  'https://support.microsoft.com/en-us/help/4009470', # 8.1 / 2012R2
    10240: 'https://support.microsoft.com/en-us/help/4000823', # Windows 10 1507 "RTM" "Threshold 1"
    10586: 'https://support.microsoft.com/en-us/help/4000824', # Windows 10 1511 "November Update" "Threshold 2"
    14393: 'https://support.microsoft.com/en-us/help/4000825', # Windows 10 1607 "Anniversary Update" "Redstone 1" / Server 2016
    15063: 'https://support.microsoft.com/en-us/help/4018124', # Windows 10 1703 "Creators Update" "Redstone 2"
    16299: 'https://support.microsoft.com/en-us/help/4043454', # Windows 10 1709 "Fall Creators Update" "Redstone 3"
    17134: 'https://support.microsoft.com/en-us/help/4099479', # Windows 10 1803 "Redstone 4"
    17763: 'https://support.microsoft.com/en-us/help/4464619', # Windows 10 1809 "Redstone 5" / Server 2019
}
BEGIN_MARKER = '"minorVersions":'
END_MARKER = ']\n'
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

# Updates types and whether they are cumulative or not
UPDATE_TYPES = {
    '': False, # legacy discontinued non-cumulative updates
    'security-only update': False,
    'monthly rollup': True,
    'os build monthly rollup': True,
    'preview of monthly rollup': True,
}

def fetch_security_updates(url):
    html = requests.get(url).text
    html = html.replace('\r\n', '\n')
    json_begin = html.find(BEGIN_MARKER)
    if json_begin == -1:
        sys.stderr.write('Unable to find marker {} in {}\n'.format(
            BEGIN_MARKER, url))
        sys.exit(1)
    json_begin += len(BEGIN_MARKER)
    json_end = html.find(END_MARKER, json_begin)
    if json_end == -1:
        sys.stderr.write('Unable to find marker {} in {}\n'.format(
            END_MARKER, url))
        sys.exit(1)
    json_end += len(END_MARKER)
    updates_json = html[json_begin:json_end]
    updates_json = json.loads(updates_json)
    updates = []
    for update in updates_json:
        if not set(('releaseVersion','id','releaseDate')).issubset(set(update.keys())):
            sys.stderr.write('Can\'t handle updates without id/releaseVersion/releaseDate\n')
            sys.exit(1)
        update_type = update['releaseVersion'].lower().strip()
        if 'os build' in update_type: # new >= 10.0 updates type name format, they are all cumulative
            update_type = 'monthly rollup'
        if update_type not in UPDATE_TYPES:
            sys.stderr.write('Update with unknown releaseVersion "{}"\n'.format(
                update['releaseVersion']))
            sys.stderr.write('\n' + str(update) + '\n')
            sys.exit(1)
        is_cumulative = UPDATE_TYPES[update_type]
        date = datetime.strptime(update['releaseDate'], DATE_FORMAT).date()
        updates.append((date, is_cumulative, update['id']))
    updates.sort(key=lambda x: x[0])
    return updates

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', type=argparse.FileType('w'), default=None)
    parser.add_argument('--sql', type=argparse.FileType('w'), default=None)
    args = parser.parse_args()
    if args.sql is None and args.csv is None:
        args.csv = sys.stdout
    if args.csv is not None:
        args.csv.write('build_number\tis_cumulative\tpublish_date\tkb_id\n')
        for build, url in SUPPORTED_BUILDS.items():
            updates = fetch_security_updates(url)
            for (date, is_cumulative, kb) in updates:
                args.csv.write('{}\t{}\t{}/{}/{}\t{}\n'.format(build,
                    ("1" if is_cumulative else "0"),
                    date.year, date.month, date.day, kb))
    if args.sql is not None:
        args.sql.write('\n')
        args.sql.write('''CREATE TABLE [kb_list](
            [build] [int] NOT NULL,
            [cumulative] [bit] NOT NULL,
	    [id] [varchar](255) NOT NULL,
	    [date] [date] NOT NULL)\n''')
        args.sql.write('INSERT INTO [kb_list] VALUES ')
        sql = []
        for build, url in SUPPORTED_BUILDS.items():
            updates = fetch_security_updates(url)
            for (date, is_cumulative, kb) in updates:
                sql.append("({},{},'KB{}','{}-{}-{}')".format(
                build, (1 if is_cumulative else 0), kb,
                date.year, date.month, date.day))
        args.sql.write(',\n    '.join(sql) + ';')

