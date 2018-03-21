#!/usr/local/bin/python3
"""
Created on 14 Mar 2018

@author: adeelkhan
"""

import argparse
import csv
import datetime

from finance.financedb import FinanceDB
from finance.textreport import TextReport


def load_accounts_from_file(filename):
    accounts = dict()
    with open(filename, 'rU') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) == 0:
                continue
            bank, account, reverse = row
            accounts['{} {}'.format(bank, account)] = reverse
    return accounts


def main(file_name):
    db = FinanceDB()

    _ = db.connect('finance.db')

    accounts = load_accounts_from_file(file_name)

    monthly_balances = db.calculate_monthly_balances()

    logger.debug('{} months.'.format(len(monthly_balances)))
    for month, balances in sorted(monthly_balances.items(), key=lambda x: x[0]):
        # print('{}: {}'.format(month, ', '.join(['{}:{}'.format(a, b) for a, b in balances.items() if b != 0])))
        calc_balance = 0
        for acc, bal in balances.items():
            if acc in accounts:
                if accounts[acc] == 'Y':
                    calc_balance -= bal
                else:
                    calc_balance += bal
        rollovers = db.get_rollovers(month)
        rollover = sum([r['amount'] for r in rollovers.values()])
        rollover2 = sum([r['amount'] for r in rollovers.values() if r['amount'] > 0])
        print('{},{:13,.2f},{:13,.2f},{:13,.2f}'.format(month, calc_balance, rollover,  rollover2))

    db.disconnect()


if __name__ == '__main__':
    import logging
    from finance import logutil

    root_logger = logutil.setup_logging()

    logger = logging.getLogger('balancehistory')

    parser = argparse.ArgumentParser(description='Show the past months balances.')
    parser.add_argument('-f', '--file', metavar='position-filename',
                        help='the file that defines which accounts to include',
                        default='metadata/position.csv')

    args = parser.parse_args()

    # print 'Loading allocations...'
    file = args.file
    logger.info("File: %s", file)

    main(file)
