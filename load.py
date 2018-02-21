#!/usr/local/bin/python3
"""
Created on 12 Oct 2015

@author: adeelkhan
"""

import argparse
import os

from finance.bankfile import BankFile


def main(data_file):
    logger.info("Loading file: %s", data_file)

    with BankFile(data_file) as bank_file:
        transactions = bank_file.read_transactions()
        logger.debug("Saving transactions.")
        bank_file.save_transactions(transactions)


if __name__ == '__main__':
    import logging
    from finance import logutil
#    logging.lastResort = None
    root_logger = logutil.setup_logging()

    logger = logging.getLogger('loader')

    parser = argparse.ArgumentParser(description='Load transaction csv files.')
    parser.add_argument('file', metavar='file.csv',
                        help='the csv file to load')

    args = parser.parse_args()

    if not os.path.exists(args.file):
        logger.critical("File %s does not exist.", args.file)
        exit(1)

    main(args.file)
