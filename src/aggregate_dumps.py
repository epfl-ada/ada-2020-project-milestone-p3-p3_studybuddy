"""
Read raw dump files, extract certain domains only and aggregate hourly data to daily data.
"""

import pandas as pd
from download_dumps import path_data
import os
from concurrent.futures import ThreadPoolExecutor
import multiprocessing


keep_domains = [
    'en', 'fr', 'de', 'es'
]

path_aggreg = '/media/maousi/Raw/ada-wiki/aggreg'


def read_dump_file(fp):
    df = pd.read_csv(fp,
                     compression='gzip',
                     sep=' ',
                     header=None,
                     usecols=[0,1,2])
    df.columns = ['domain', 'article', 'views']
    return df


def process_dump_file(fp):
    df = read_dump_file(fp)
    print('Loaded', fp)

    df = df[df.domain.isin(keep_domains)]
    df = df[ (~df.domain.isna()) & (~df.article.isna()) ]
    return df


def aggregate_dump_files(filelist):
    with ThreadPoolExecutor(2) as executor:
        data = executor.map(process_dump_file, filelist)
        df = pd.concat(data)

    aggreg = df.groupby(['domain', 'article']).sum()
    return aggreg


def main():
    files = os.listdir(path_data)

    unique_days = set(map(lambda fname: fname.split('-')[1], files))
    data = []
    for day in unique_days:
        files_day = filter(lambda fname: day in fname, files)
        print('Loading', day)
        files_day = list(map(lambda fname: os.path.join(path_data, fname), files_day))[:2]
        if len(files_day) != 24:
            print(f'<WARNING> only {len(files_day)} files for date {day} <WARNING>')

        df = aggregate_dump_files(files_day)
        print(f'Loaded and processed data of day {day}')
        df['date'] = day
        data.append(df)

        outfile = os.path.join(path_aggreg, f'data_{day}.gz')
        df.to_csv(outfile,
                  index=False,
                  compression='gzip')
        break

    return data


if __name__ == '__main__':
    #main()
    pass
