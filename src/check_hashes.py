

import os
from src.download_dumps import path_data, base_url, get_url_suffix, download_file
from datetime import datetime
import requests
from time import sleep


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


def main():
    files = os.listdir(path_data)

    checksum_files = get_checksum_files(files)
    checksum_files_url = list(checksum_files.values())
    checksum_files_datesuffix = list(checksum_files.keys())

    file_paths = []
    for suffix, url in checksum_files.items():
        output_path = 'checksums-' + suffix.split('/')[1] + '.txt'
        output_path = os.path.join(path_data, output_path)
        file_paths.append(output_path)
        if os.path.exists(output_path):
            continue

        statuscode = download_file(url, output_path)

    checksum_data = []
    for f in file_paths:
        with open(f, 'r') as file:
            checksum_data.extend(file.read().strip('\n').split('\n'))

    checksum_data = list(map(parse_md5sum_output, checksum_data))
    checksum_data = {e[1]: e[0] for e in checksum_data}

    print(checksum_data)


if __name__ == '__main__':
    main()

