#!/usr/local/bin/python3
"""
Created on 8 Feb 2018

@author: adeelkhan
"""

import argparse
import datetime
import math

from finance.financedb import FinanceDB
from finance import dateutil

from finance.metadata import Metadata

DATE_FORMAT = "%Y-%m-%d"
INTEREST_PERIOD_DAYS = 30


def main(bank, account, interest_charge_date='9999-12-31'):
    db = FinanceDB()
    c = db.connect('finance.db')

    logger.info('Calculating interest for %s-%s...', bank, account)
    prev_interest_date = db.read_last_interest_date(bank, account)
    transactions = db.get_transactions(bank, account)

    balance = 0
    accrued_interest = 0
    next_interest_date = min(dateutil.increment_date(prev_interest_date, INTEREST_PERIOD_DAYS),
                             interest_charge_date)
    filename = 'AUTO_' + datetime.datetime.now().strftime('%Y_%m_%d_%H%M%S')
    file_seq = 0

    d = dateutil.increment_date(prev_interest_date)
    today = dateutil.increment_date(dateutil.today(), days=-5)
    transaction_cursor = 0

    while d < today:
        while d <= next_interest_date and d < today:
            while transaction_cursor < len(transactions):
                sequence, bank, account, tran_date, description, amount = transactions[transaction_cursor]
                if tran_date <= d:
                    balance += amount
                    transaction_cursor += 1
                else:
                    break

            interest = 0 if balance >= 0 else balance * (Metadata.get_interest_rate(bank, account, d)
                                                         / 100.0 / 365)
            accrued_interest += interest
            if not math.isclose(accrued_interest, 0.0, abs_tol=0.001):
                logger.debug('%s ' + ' '.join([db.MONEY_FORMAT] * 3), d, balance, interest, accrued_interest)

            d = dateutil.increment_date(d)

        if not math.isclose(accrued_interest, 0.0, abs_tol=0.001) and d > next_interest_date:
            balance += accrued_interest
            file_seq += 1
            t = (next_interest_date, 'AUTO_INTEREST', round(accrued_interest, 2), bank, account,
                 round(balance, 2), filename, file_seq)

            sql = """insert into tran (tran_date, description, amount, bank, account, calc_balance, file_name, file_sequence)
                values (?, ?, ?, ?, ?, ?, ?, ?)
            """
            c.execute(sql, t)

            logger.info('Added: %s %s %s ' + db.MONEY_FORMAT, next_interest_date, bank, account, accrued_interest)

            accrued_interest = 0
        next_interest_date = min(dateutil.increment_date(next_interest_date, INTEREST_PERIOD_DAYS),
                                 interest_charge_date)

    db.disconnect()


if __name__ == '__main__':
    import logging
    from finance import logutil

    root_logger = logutil.setup_logging()
    logger = logging.getLogger('calcinterest')

    parser = argparse.ArgumentParser(description='Generate interest transactions for a specific account.')
    parser.add_argument('bank')
    parser.add_argument('account')
    parser.add_argument('-d', '--date', metavar='yyyy-mm-dd', default='9999-12-31',
                        help='the date to post interest if different from 30 day cycle')

    args = parser.parse_args()

    main(args.bank, args.account, args.date)
