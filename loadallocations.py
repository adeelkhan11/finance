#!/usr/local/bin/python3
"""
Created on 12 Oct 2015

@author: adeelkhan
"""

import argparse
import csv
import datetime

from finance.financedb import FinanceDB
from finance.textreport import TextReport


def load_allocations_from_file(db, filename, current_month, rollovers):
    with open(filename, 'rU') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) == 0:
                continue
            head, name, allocation = row
            db.saveDict('head', ['head'], {'head': head, 'name': name})
            alloc = {'month': current_month, 'head': head, 'new_alloc': db.nullToZero(allocation)}
            if head in rollovers:
                alloc['rollover'] = rollovers[head]['amount']
            db.saveDict('allocation', ['month', 'head'], alloc)


def main(current_month):
    db = FinanceDB()

    _ = db.connect('finance.db')

    previous_month = (datetime.datetime.strptime(current_month + '-01', "%Y-%m-%d")
                      - datetime.timedelta(days=1)).strftime('%Y-%m')

    rollovers = db.get_rollovers(previous_month)
    print("ROLLOVERS:", rollovers)
    expenses = db.get_expenses(current_month)
    db.save_expenses(expenses, rollovers)

    if args.file:
        load_allocations_from_file(db, args.file, current_month, rollovers)

    allocations = db.loadDicts('allocation', ['month', 'head'], ['new_alloc', 'rollover', 'adjustment', 'used'],
                               'month = ?', [current_month])
    db.calculate_parent_allocations(allocations)
    db.save_parent_allocations(allocations)

    report = TextReport(db, current_month)
    report.show_header()
    report.show_allocations(allocations)
    report.show_exceptions(allocations)
    db.disconnect()


if __name__ == '__main__':
    import logging
    from finance import logutil

    root_logger = logutil.setup_logging()

    logger = logging.getLogger('loadallocations')

    parser = argparse.ArgumentParser(description='Load allocations and calculate usage.')
    parser.add_argument('-m', '--month', metavar='yyyy-mm',
                        help='the month to process')
    parser.add_argument('-f', '--file', metavar='filename',
                        help='the allocation file to load')

    args = parser.parse_args()

    # print 'Loading allocations...'
    month = args.month if args.month else datetime.datetime.now().strftime('%Y-%m')
    logger.info("Month: %s", month)

    main(month)
