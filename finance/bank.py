

class Bank:
    def __init__(self, spec, bank_name=None):
        self.account_name = None
        if bank_name is None:
            self.name = spec['banks'][0]['name']
            self.column_names = spec['banks'][0]['colnames']
        else:
            for b in spec['banks']:
                if b['name'] == bank_name:
                    self.name = b['name']
                    self.column_names = b['colnames']

        self.date_index = self.column_names.index('date')
        self.desc_index = self.column_names.index('description')

        if 'balance' in self.column_names:
            self.bal_index = self.column_names.index('balance')
        else:
            self.bal_index = None

        if 'account' in self.column_names:
            self.account_index = self.column_names.index('account')
        else:
            self.account_index = None

        self.debit_index = self.column_names.index('debit') if 'debit' in self.column_names else None
        self.credit_index = self.column_names.index('credit') if 'credit' in self.column_names else None
        self.amount_index = self.column_names.index('amount') if 'amount' in self.column_names else None
