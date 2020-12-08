"""
Read raw dump files, extract certain domains only and aggregate hourly data to daily data.
"""

import pandas as pd
from pandas.errors import ParserError
from download_dumps import path_data
import os
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
from time import time


keep_domains = [
    'en', 'fr', 'de', 'es'
]

path_aggreg = '/media/maousi/Raw/ada-wiki/aggreg'


def read_dump_file(fp):
    """Load gzip-compressed csv file"""
    df = pd.read_csv(fp,
                     compression='gzip',
                     sep=' ',
                     header=None,
                     usecols=[0,1,2],
                     # quoting=3 is a workaround of issue
                     # "Error tokenizing data. C error: EOF inside string starting at row ..."
                     quoting=3)
    # except ParserError as e:
    #     print('ParserError, using python engine')
    #     df = pd.read_csv(fp,
    #                      compression='gzip',
    #                      sep=' ',
    #                      header=None,
    #                      usecols=[0,1,2],
    #                      engine='python',
    #                      quoting=3)

    df.columns = ['domain', 'article', 'views']
    return df


def process_dump_file(fp):
    """Load dump file, keep only domains specified in `keep_domains`,
    remove items where article name or domain is missing."""
    df = read_dump_file(fp)
    print('Loaded', fp)

    df = df[df.domain.isin(keep_domains)]
    df = df[ (~df.domain.isna()) & (~df.article.isna()) ]
    return df



def aggregate_dump_files(filelist):
    """Load files in the list, group by domain and article and sum"""
    with ThreadPoolExecutor(4) as executor:
        data = executor.map(process_dump_file, filelist)
        df = pd.concat(data)

    aggreg = df.groupby(['domain', 'article']).sum()
    aggreg = aggreg.reset_index()
    return aggreg


def get_aggreg_filepath(day, path):
    outfile = os.path.join(path, f'data_{day}.gz')
    return outfile


def main():
    files = os.listdir(path_data)
    files = list(filter(lambda fname: fname.endswith('.gz'), files))

    unique_days = set(map(lambda fname: fname.split('-')[1], files))

    for day in unique_days:
        outfile = get_aggreg_filepath(day, path_aggreg)
        if os.path.exists(outfile):
            print('<WARNING> Skipping', day)
            continue # don't re-process data that was already aggregated

        print('Processing day', day)

        # Gather files that correspond to the same day
        files_day = filter(lambda fname: day in fname, files)
        files_day = list(map(lambda fname: os.path.join(path_data, fname), files_day))
        # Warn if not 24 files are present
        if len(files_day) != 24:
            print(f'<WARNING> only {len(files_day)} files for date {day} <WARNING>')

        # Load all files for the day
        start = time()
        df = aggregate_dump_files(files_day)
        print(f'Loaded and processed data of day {day} in {time()-start:.4} s')

        # Add column date
        df['date'] = day

        # Save in gzip-compressed .csv format
        start = time()
        df.to_csv(outfile,
                  index=False,
                  compression='gzip')
        del df
        print(f'Saved {outfile} in {time()-start:.4} s')


if __name__ == '__main__':
    main()


def process_aggreg_file(fp, kwd_lst):
    def read_aggreg_file(fp):
        return pd.read_csv(
            fp,
            compression='gzip'
        )

    def extract_kwds(df, kwd_lst):
        #print('df.article for', fp)
        mask = df.article.isin(kwd_lst)
        return df[mask]

    try:
        print(f'Loading {fp}')
        df = read_aggreg_file(fp)
        #print(f'Loaded {fp}')
    except EOFError as e:
        print(f'<ERROR> while reading {fp}: {e}')
        df = pd.DataFrame()

    return extract_kwds(df, kwd_lst)


def extract_keywords(keyword_lst):
    """Not intended to be used in a script, but call this function in an interpreter.
    You should manually test file integrity before running this, if you don't wanna loose faith in life :)
        $ gunzip -t <file>.gz
    Or even better, check all at once:
        $ for f in *; do echo $f; gunzip -t $f; done
    """

    aggreg_files = os.listdir(path_aggreg)
    aggreg_files = [os.path.join(path_aggreg, fname) for fname in aggreg_files]
    with ThreadPoolExecutor(2) as executor:
        f = lambda fp: process_aggreg_file(fp, keyword_lst)
        data = executor.map(f, aggreg_files)
        df = pd.concat(data)

    return df
