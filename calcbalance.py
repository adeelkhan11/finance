#!/usr/local/bin/python3
"""
Created on 5 Feb 2018

@author: adeelkhan
"""

import math

from finance.financedb import FinanceDB


def main():
    db = FinanceDB()
    _ = db.connect('finance.db')

    logger.info('Calculating balances...')
    new_rows, final_balances = db.calculate_balances()

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

    main()
