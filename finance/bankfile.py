
import logging

from finance.financedb import FinanceDB
from finance.csvfile import CSVFile
from finance.banks import Banks

MONEY_FORMAT = "%11.2f"

logger = logging.getLogger(__name__)


class BankFile:
    def __init__(self, file_name):
        self.db = FinanceDB()
        self.c = self.db.connect('finance.db')

        self.bank_score = {}

        self.csv_file = CSVFile(file_name)
        self.banks = Banks('banks.json')

        self.banks.determine_bank_account(self.csv_file.column_types, file_name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.disconnect()

    def new_transactions(self):
        db_transactions = self.db.transactions()
        balanceval = None
        seqval = 0

        accountval = None

        result = []
        duplicated_count = 0
        new_count = 0
        for row in self.csv_file.valuetable:
            seqval += 1
            dateval = row[self.banks.bank.date_index]
            descval = row[self.banks.bank.desc_index]

            amountpart = 0 if self.banks.bank.amount_index is None \
                else self._null_to_zero(row[self.banks.bank.amount_index])
            creditpart = 0 if self.banks.bank.credit_index is None \
                else self._null_to_zero(row[self.banks.bank.credit_index])
            debitpart = 0 if self.banks.bank.debit_index is None \
                else self._null_to_zero(row[self.banks.bank.debit_index])

            amountval = amountpart + creditpart - debitpart

            if self.banks.bank.bal_index is not None:
                balanceval = self._null_to_zero(row[self.banks.bank.bal_index])

            if self.banks.bank.account_index is not None:
                accountval = row[self.banks.bank.account_index]

            t = (dateval, descval, amountval, self.banks.bank.name, accountval, balanceval, seqval)

            rowval = dateval + self.banks.bank.name + (MONEY_FORMAT % amountval) + descval
            if rowval in db_transactions:
                # print "Found %s" % rowval
                duplicated_count += 1
                for bacc in db_transactions[rowval].split(','):
                    if bacc in self.bank_score:
                        self.bank_score[bacc] += 1
                    else:
                        self.bank_score[bacc] = 1
            else:
                # print "Not found %s" % rowval
                new_count += 1
                result.append(t)

        logger.info("%d new transactions found. %d transactions already exist in DB.",
                    new_count, duplicated_count)
        return result

    def load_transactions(self, transactions):
        sql = """
            insert into tran (tran_date, description, amount, bank, account, balance, file_name, file_sequence)
            values (?, ?, ?, ?, ?, ?, ?, ?)
        """

        next_account_name = self.db.new_account_name()
        # Get the account and save the transactions
        calcaccountval = None
        if len(self.bank_score) > 0:
            sorted_x = sorted(self.bank_score.items(), key=lambda x: x[1], reverse=True)
            if sorted_x[0][1] > 3:
                calcaccountval = sorted_x[0][0].split('-')[1]

        for dateval, descval, amountval, self.banks.bank.name, fileaccountval, balanceval, seqval in transactions:
            if self.banks.bank.account_name is not None:
                accountval = self.banks.bank.account_name
            elif fileaccountval is not None:
                accountval = fileaccountval
            elif calcaccountval is not None:
                accountval = calcaccountval
            else:
                accountval = next_account_name
            t = (dateval, descval, amountval, self.banks.bank.name,
                 accountval, balanceval, self.csv_file.file_name, seqval)
            self.c.execute(sql, t)

    @staticmethod
    def _null_to_zero(value):
        if value.strip() == '':
            return 0
        return float(value.strip())
