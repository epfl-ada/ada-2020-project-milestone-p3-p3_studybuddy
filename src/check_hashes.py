

import os
from download_dumps import path_data, base_url, get_url_suffix, download_file
from datetime import datetime
import requests
from time import sleep
import hashlib
import argparse


def parse_md5sum_output(line):
    return line.split('  ')


def get_checksum_files(files):
    # ------ DETERMINE CHECKSUM FILES TO DOWNLOAD
    files = list(filter(lambda s: s.endswith('.gz'), files))

    files_dates = set(
        fname.split('-')[1]
        for fname in files
    )

    dates = [datetime.strptime(datestr, '%Y%m%d') for datestr in files_dates]

    checksum_files = {
        get_url_suffix(date): base_url + get_url_suffix(date) + 'md5sums.txt'
        for date in dates
    }

    return checksum_files


def compute_file_md5sum(fp):
    if fp.endswith('.txt'):
        return None

    print(f'Computing checksum of {fp}')
    with open(fp, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('date', help='check files that have the given substring in their name',
                        default=None, nargs='?')
    args = parser.parse_args()
    subset = args.date

    files = os.listdir(path_data)

    print('Determining required checksum files...')
    checksum_files = get_checksum_files(files)
    checksum_files_url = list(checksum_files.values())
    checksum_files_datesuffix = list(checksum_files.keys())

    ckecksum_file_paths = []
    for suffix, url in checksum_files.items():
        output_path = 'checksums-' + suffix.split('/')[1] + '.txt'
        output_path = os.path.join(path_data, output_path)
        ckecksum_file_paths.append(output_path)
        if os.path.exists(output_path):
            continue

        statuscode = download_file(url, output_path)
        print(f'Downloaded {output_path}, {statuscode}')

    print('Aggregating checksum files...')
    checksum_data = []
    for f in ckecksum_file_paths:
        with open(f, 'r') as file:
            checksum_data.extend(file.read().strip('\n').split('\n'))

    checksum_data = list(map(parse_md5sum_output, checksum_data))
    checksum_data = {e[1]: e[0] for e in checksum_data}

    # Remove fext files
    files = list(filter(lambda fname: '.txt' not in fname, files))

    # Select only files the user wants to check
    if subset is not None:
        files = list(filter(lambda fname: subset in fname, files))

    # Get full files path
    files_path = map(lambda fname: os.path.join(path_data, fname), files)
    #files_path = list(files_path)[:10]

    # Compute checksums
    local_checksums = map(compute_file_md5sum, files_path)
    # Create dict of local checksums
    local_checksums = dict(zip(files, local_checksums))

    # Check local checksums against those on checksums.txt files
    validate = lambda fname: local_checksums[fname] == checksum_data.get(fname, None)
    corresp = list(map(validate, local_checksums))

    bad_checksum = dict(filter(lambda e: not e[1], zip(files, corresp)))

    print('\nList of bad checksum:')
    print('\n'.join(bad_checksum))

    with open('bad_checksums.txt', 'w') as f:
        f.write('\n'.join(bad_checksum.keys()))


if __name__ == '__main__':
    main()

