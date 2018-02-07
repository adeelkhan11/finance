#!/usr/local/bin/python3
"""
Created on 5 Feb 2018

@author: adeelkhan
"""

import csv
import re

from finance.dbutil import DBUtil


MONEY_FORMAT = "%11.2f"


def load_patterns(file_name='metadata/categories.csv'):
    patterns = []
    with open(file_name, 'rU') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) == 0:
                continue
            pattern, source, head, notes = row
            patterns.append({"pattern": pattern, "head": head, "source": source, "notes": notes})

    return patterns


def load_uncategorised_transactions(c):
    sql = '''select sequence, description, amount
        from tran
        where head is null
        order by sequence
        '''

    c.execute(sql)
    rows = c.fetchall()

    return rows


def categorise_transactions(c, transactions, patterns):
    new_rows = []
    for sequence, description, amount in transactions:
        for p in patterns:
            if re.search(p['pattern'], description, re.IGNORECASE):
                logger.info("Updating %5d %-40s %10.2f %2s %-20s", sequence, description[:40],
                            amount, p['head'], p['source'])
                new_rows.append([sequence, p['head'], p['source'], p['notes']])
                break

    logger.info('Updating categories...')
    sql = '''update tran
        set head = ?, source = ?, notes = ?
        where sequence = ?
        '''

    for sequence, head, source, notes in new_rows:
        t = (head, source, notes, sequence)
        c.execute(sql, t)

    logger.info("%d categories updated.", len(new_rows))


def print_uncategorised_transactions(c):
    sql = '''select sequence, bank, account, tran_date, description, amount
        from tran
        where head is null
        and bank not in ('Filter')
        and account not in ('Business')
        --and description not like 'PAYPAL%'
        and tran_date >= '2016-09-01'
        order by amount
        limit 30
        '''

    c.execute(sql)
    rows = c.fetchall()

    logger.info("Uncategorised transactions")
    for sequence, bank, account, tran_date, description, amount in rows:
        print("%5d %-8s %-8s %10s %10.2f %s" % (sequence, bank[:8], account[:8], tran_date, amount, description))


def main():
    patterns = load_patterns()

    db = DBUtil()
    c = db.connect('finance.db')

    logging.info('Categorising...')
    transactions = load_uncategorised_transactions(c)
    categorise_transactions(c, transactions, patterns)
    print_uncategorised_transactions(c)

    db.disconnect()


if __name__ == '__main__':
    import logging
    from finance import logutil

    root_logger = logutil.setup_logging()

    logger = logging.getLogger('categorise')

    main()
