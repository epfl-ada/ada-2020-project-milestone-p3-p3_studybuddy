

import os
import os.path
import argparse
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from time import sleep
import random


path_data = '/media/maousi/Raw/ada-wiki/dumps'
N_parallel = 3

base_url = 'https://dumps.wikimedia.org/other/pagecounts-raw/'
filename_pattern = 'pagecounts-{}-{}.gz'

start = '2015041'
end = '20150630'


def generate_time_range(start, end):
    def parse_date(date):
        if not isinstance(date, datetime):
            return datetime.strptime(date, '%Y%m%d')
        return date

    start = parse_date(start)
    end = parse_date(end)
    span = end - start

    for i in range( (span.days + 1) * 24):
        yield start + timedelta(hours=i)


def get_url_suffix(date):
    return date.strftime('%Y/%Y-%m/')


def generate_download_links(start, end):
    """Generator of all dump files from `start` date to `end` date."""

    def get_file_name(date):
        return filename_pattern.format(
            date.strftime('%Y%m%d'),
            date.strftime('%H%M%S')
        )

    for date in generate_time_range(start, end):
        file = get_file_name(date)
        url = base_url + get_url_suffix(date)

        yield file, url + file


def download_file(url, output_path):
    if os.path.exists(output_path):
        raise ValueError('Should not exist.')

    # Avoid error "503 Service temporarily unavailable"
    # https://stackoverflow.com/questions/52978264/503-error-when-downloading-wikipedia-dumps
    sleep(random.random() * 2)

    r = requests.get(url)
    with open(output_path, 'wb') as f:
        f.write(r.content)

    print(f'Downloaded {os.path.basename(output_path)}')

    return r.status_code


def main():
    pending = generate_download_links(start, end)
    downloaded = os.listdir(path_data)

    # Remove downloaded files from pending list
    pending = filter(
        lambda elem: elem[0] not in downloaded,
        pending
    )

    pending = list(pending)
    N = len(pending)
    print(f'{N} files to be downloaded...')

    with ThreadPoolExecutor(N_parallel) as executor:
        f = lambda e: download_file(e[1], os.path.join(path_data, e[0]))
        status_codes = list(executor.map(f, pending))


if __name__ == '__main__':
    main()

