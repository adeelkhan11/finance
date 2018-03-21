#!/usr/local/bin/python3
"""
Created on 16 Mar 2018

@author: adeelkhan
"""

import argparse
import csv
import datetime

from finance.financedb import FinanceDB
from finance.textreport import TextReport


def load_tran_heads(db, filename):
    with open(filename, 'rU') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if 'sequence' not in row:
                continue
            if row['sequence'] != '':
                # print("sequence: {}".format(row['sequence']))
                tran = {'sequence': row['sequence'], 'head': row['head']}
                if row['source'].strip() != '':
                    tran['source'] = row['source']
                if db.saveDict('tran', ['sequence'], tran, updateOnly=True):
                    print('{} updated to {}'.format(row['sequence'], row['head']))


def main(file_name):
    db = FinanceDB()

    _ = db.connect('finance.db')

    load_tran_heads(db, file_name)

    db.disconnect()


if __name__ == '__main__':
    import logging
    from finance import logutil

    root_logger = logutil.setup_logging()

    logger = logging.getLogger('balancehistory')

    parser = argparse.ArgumentParser(description='Show the past months balances.')
    parser.add_argument('-f', '--file', metavar='tran-heads-filename',
                        help='the file that defines which defines transactions heads',
                        default='metadata/tran_heads.csv')

    args = parser.parse_args()

    # print 'Loading allocations...'
    file = args.file
    logger.info("File: %s", file)

    main(file)
