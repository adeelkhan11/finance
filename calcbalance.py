#!/usr/local/bin/python3
"""
Created on 5 Feb 2018

@author: adeelkhan
"""

import argparse
import math

from finance.financedb import FinanceDB


def main(database_file):
    db = FinanceDB()
    _ = db.connect(database_file)

    logger.info('Calculating balances...')
    new_rows, final_balances = db.calculate_balances()

    if len(new_rows) > 0:
        logger.info('Writing balances...')
        db.update_balances(new_rows)
    logger.info("%d balances updated.", len(new_rows))

    for bank in sorted(final_balances.keys()):
        if 'Manual' not in bank and not math.isclose(final_balances[bank], 0.0, abs_tol=0.001):
            logger.info("%-20s: " + db.MONEY_FORMAT, bank[:20], final_balances[bank])

    db.disconnect()


if __name__ == '__main__':
    import logging
    from finance import logutil

    root_logger = logutil.setup_logging()
    logger = logging.getLogger('calc balance')

    parser = argparse.ArgumentParser(description='Calculate balances for all accounts and report non-zero balances.')
    parser.add_argument('-f', '--dbfile', metavar='databasefile.db', default='finance.db',
                        help='the name of the database file')

    args = parser.parse_args()

    main(args.dbfile)
