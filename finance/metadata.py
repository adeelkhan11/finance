import csv
import logging

logger = logging.getLogger(__name__)


class InterestRate:
    def __init__(self, data):
        self.__dict__ = data

        self.rate_percent = float(self.rate_percent)


class Metadata:
        interest_rates = None

        @classmethod
        def get_interest_rate(cls, bank, account, date):
            if cls.interest_rates is None:
                with open('metadata/interest.csv', 'r') as f:
                    reader = csv.DictReader(f)

                    data = [InterestRate(row) for row in reader]

                    cls.interest_rates = sorted(data, key=lambda x: x.bank + x.account + x.effective_from, reverse=True)

            for rate in cls.interest_rates:
                if rate.bank == bank \
                        and rate.account == account \
                        and rate.effective_from <= date:
                    return rate.rate_percent

            logger.critical('Interest rate not found for account %s-%s on date %s.', bank, account, date)
            logger.critical('>\n<'.join([', '.join(['%s:%s' % (k, str(v)) for k, v in r.__dict__.items()]) for r in cls.interest_rates]))
            exit(1)
