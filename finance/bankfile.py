import logging

from finance.dbtable import Tran
from finance.financedb import FinanceDB
from finance.csvfile import CSVFile
from finance.banks import Banks

MONEY_FORMAT = "%11.2f"

logger = logging.getLogger(__name__)


class BankFile:
    def __init__(self, file_name):
        self.db = FinanceDB()
        self.c = self.db.connect('finance.db')
        self._tran = Tran(self.db)

        self.bank_score = {}

        self.csv_file = CSVFile(file_name)
        self.banks = Banks('metadata/banks.json')

        self.banks.determine_bank_account(self.csv_file.column_types, file_name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.disconnect()

    def read_transactions(self):
        # db_transactions = self.db.transactions()
        balance_value = None
        sequence_value = 0

        account_name = None

        result = []

        for row in self.csv_file.valuetable:
            sequence_value += 1
            date_value = row[self.banks.bank.date_index]
            description_value = row[self.banks.bank.desc_index]

            amount_part = 0 if self.banks.bank.amount_index is None \
                else self._null_to_zero(row[self.banks.bank.amount_index])
            credit_part = 0 if self.banks.bank.credit_index is None \
                else self._null_to_zero(row[self.banks.bank.credit_index])
            debit_part = 0 if self.banks.bank.debit_index is None \
                else self._null_to_zero(row[self.banks.bank.debit_index])

            amount_value = amount_part + credit_part - debit_part
            if amount_value == int(amount_value):
                amount_value = int(amount_value)

            if self.banks.bank.bal_index is not None:
                balance_value = self._null_to_zero(row[self.banks.bank.bal_index])

            if self.banks.bank.account_index is not None:
                account_name = row[self.banks.bank.account_index]

            t = dict(tran_date=date_value,
                     description=description_value,
                     amount=amount_value,
                     bank=self.banks.bank.name,
                     account=account_name,
                     balance=balance_value,
                     file_name=self.csv_file.file_name,
                     file_sequence=sequence_value)

            bank_accounts = self._tran.get_accounts_with_transaction(t)
            for bank_account in bank_accounts:
                if bank_account in self.bank_score:
                    self.bank_score[bank_account] += 1
                else:
                    self.bank_score[bank_account] = 1

            result.append(t)

        return result

    def save_transactions(self, transactions):
        next_account_name = self.db.new_account_name()
        # Get the account and save the transactions
        calculated_account_name = None
        if len(self.bank_score) > 0:
            sorted_x = sorted(self.bank_score.items(), key=lambda x: x[1], reverse=True)
            if sorted_x[0][1] > 1:
                calculated_account_name = sorted_x[0][0].split(':')[1]

        for t in transactions:
            account_name = next((a for a in [self.banks.bank.account_name,
                                             t['account'],
                                             calculated_account_name,
                                             next_account_name] if a is not None))
            transaction = dict(t)
            transaction['account'] = account_name

            self._tran.save(transaction)

        logger.info("%d new transactions found. %d transactions already exist in DB.",
                    self._tran.insert_count, self._tran.update_count)

    @staticmethod
    def _null_to_zero(value):
        if value.strip() == '':
            return 0
        return float(value.strip())
