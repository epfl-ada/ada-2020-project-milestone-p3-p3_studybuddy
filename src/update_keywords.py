"""Generate a keyword list based on a template so that it perfectly matches names of Wikipedia articles.

Usage:
    1. Create a text file of newline-separated keywords, filename must end with '_template.<extension>'
    2. Go in root folder of project and run:
        $ python3 src/update_keywords.py <keyword-list-name>_template.txt <wiki-domain>
    3. Carefully review the output
    4. A file containing keywords reported in output is created
"""


import os
import argparse
from setup import *
from scrape_wiki import PageviewsClient
import pandas as pd
import numpy as np
import wikipedia as wiki
from concurrent.futures import ThreadPoolExecutor
import pathlib
import datetime


def read_keywords(fname):
    """Read and parse a file of keywords, supports comments (delimited by #)
    :param fname: name of file containing newline-separated keywords
    :return: list of strings
    """
    def process_line(line):
        i = line.find('#')
        if i == -1:
            return line
        return line[:i].strip()

    with open(fname, 'r', encoding='utf-8') as f:
        data = f.read().strip('\n').split('\n')

    # Handle comments
    data = list(map(process_line, data))
    # Delete empty lines (those containing only comments)
    data = list(filter(lambda s: len(s) > 0, data))
    return data


def request(articles, domain='de', **kwargs):
    """Wraps the function PageviewsClient.article_views

    :param list[str] articles: list of articles names (must match perfectly with Wikipedia article names)
    :param str domain: en, fr, ...
    :param kwargs: any argument provided to
    :return:
    """
    wrapped_kwargs = params.copy()
    wrapped_kwargs.update(kwargs)
    domain = domain + '.wikipedia'

    # Fetch
    p = PageviewsClient(contact)
    res = p.article_views(articles=articles, project=domain, **wrapped_kwargs)

    # Format results in a DataFrame
    res = pd.DataFrame(res).T
    # Replace None -> np.nan
    res = res.applymap(lambda elem: np.nan if elem is None else elem)
    # Sort by dates
    res.sort_index(inplace=True)

    return res


def search(articles, n_results=1, n_threads=10):
    """Wraps wikipedia.search function to find exact article names.

    :param list[str] articles:
    :param int n_results: number of suggestions returned per article
    :param int n_threads: number of parallel threads to run
    :return: dict[int, list], key is article name provided in argument, list is suggestions returned by API
    """
    with ThreadPoolExecutor(n_threads) as executor:
        f = lambda article: wiki.search(article, results=n_results)
        res = list(executor.map(f, articles))

    for article, ls in zip(articles, res):
        if len(ls) == 0:
            print(f'Warning! Article {article} has no suggestions.')

    return dict(zip(articles, res))


def main():
    # ------ User interaction
    parser = argparse.ArgumentParser()
    parser.add_argument('template', help='file containing newline-delimited keywords, filename pattern: *_template*')
    parser.add_argument('domain', help='wikipedia domain/project (en, de, fr, ...)')
    args = parser.parse_args()

    if not os.path.exists(args.template):
        raise ValueError(f'File "{args.template}" does not exist.')
    if not args.template.split('.')[0].endswith('_template'):
        raise ValueError('The keywords file must end with `_template`')

    # ------ Setup
    wiki.set_rate_limiting(rate_limit=True)
    wiki.set_lang(args.domain)

    # ------ Load keywords from file
    keywords = read_keywords(args.template)
    print(f'Loaded {len(keywords)} keywords')
    #print(keywords)
    #print(get_output_filename(args.template, args.domain))
    #exit()

    # ------ Fetch suggestions
    print('Fetching suggestions...')
    r = search(keywords, n_results=1)
    r = {key: value[0] for key, value in r.items()}

    # ------ Review
    print(f'Whole mapping:')
    pretty_print_dic(r)

    print('\nBelow is a more readable report (exact matches are not reported):')
    case_mismatch, no_match = {}, {}
    for k , val in r.items():
        if k == val:
            continue
        if k.lower() == val.lower():
            case_mismatch[k] = val
        elif k != val:
            no_match[k] = val

    print(f'Cases mismatch:')
    pretty_print_dic(case_mismatch)
    print(f'No match:')
    pretty_print_dic(no_match)

    # Write
    final_keywords = '\n'.join(r.values())
    outfile = get_output_filename(args.template, args.domain)
    header = get_header()
    with open(outfile, 'w') as f:
        f.write(header + final_keywords)
    print(f'Written in file {outfile}')


def pretty_print_dic(dic):
    for k, v in dic.items():
        print(f'- {k}: {v}')


def get_output_filename(template_fname, language):
    # File name without extension
    outfile = pathlib.Path(template_fname).stem
    # Remove the "_template" part in file name
    outfile = outfile[:outfile.rfind('_')]
    # Add language suffix if not in file name yet
    if f'_{language}' not in template_fname:
        outfile += f'_{language}'
    outfile += pathlib.Path(template_fname).suffix

    # Add parent directory
    outfile = os.path.join(os.path.dirname(template_fname), outfile)

    return outfile


def get_header():
    now = datetime.datetime.now()
    h = f"""
# File automatically generated by {__file__}, {now.strftime('%d-%m-%Y %H:%M:%S')}
# Do NOT edit this file, it will be overwritten

"""
    return h


if __name__ == '__main__':
    main()
