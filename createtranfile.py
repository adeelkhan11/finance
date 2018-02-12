#!/usr/local/bin/python3
"""
Created on 8 Feb 2018

@author: adeelkhan
"""

import argparse
import csv
import datetime

from finance.financedb import FinanceDB


def main(bank, account, description, target_bank, target_account, reverse):
    db = FinanceDB()
    _ = db.connect('finance.db')

    tran_file = "data/{}_{}_{}.csv".format(target_bank, target_account, datetime.datetime.now().strftime('%Y_%m_%d'))

    t = (bank, account, '%{}%'.format(description))
    sql = """
        select tran_date, description, amount{}
        from tran
        where bank = ?
          and account = ?
          and description like ?
        order by tran_date, sequence
    """.format(' * -1' if reverse else '')

    with open(tran_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(db.query(sql, t))

    db.disconnect()


if __name__ == '__main__':
    import logging
    from finance import logutil

    root_logger = logutil.setup_logging()
    logger = logging.getLogger('loadallocations')

    parser = argparse.ArgumentParser(description='Generate transactions for loans.')
    parser.add_argument('bank',
                        help='the source bank')
    parser.add_argument('account',
                        help='the source account')
    parser.add_argument('description',
                        help='the unique text in payment descriptions')
    parser.add_argument('target_bank',
                        help='the target loan bank')
    parser.add_argument('target_account',
                        help='the target loan account')
    parser.add_argument('-r', '--reverse', action='store_true',
                        help='reverse the sign of the transaction amounts')

    args = parser.parse_args()

    main(args.bank, args.account, args.description, args.target_bank, args.target_account, args.reverse)
