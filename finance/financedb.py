from finance.dbutil import DBUtil


class FinanceDB(DBUtil):
    MONEY_FORMAT = "%11.2f"

    def __init__(self):
        super().__init__()

    def new_account_name(self):
        self.c.execute("select distinct account from tran")
        accounts = frozenset(r[0] for r in self.c.fetchall())
        i = 0

        account_name = 'acc' + str(i)
        while account_name in accounts:
            i += 1
            account_name = 'acc' + str(i)

        return account_name

    def transactions(self):
        sql = """
            select tran_date, amount, description, bank, account
            from tran
            """

        self.c.execute(sql)

        result = {}
        data = self.c.fetchall()
        for tran_date, amount, description, bankname, account in data:

            key = tran_date + bankname + (self.MONEY_FORMAT % amount) + description
            if key in result and '-'.join([bankname, account]) not in result[key].split(','):
                result[key] = ','.join([result[key], '-'.join([bankname, account])])
            else:
                result[key] = '-'.join([bankname, account])
                
        return result

    def calculate_balances(self):
        sql = '''select sequence, bank, account, tran_date, description, amount, calc_balance
            from tran
            order by tran_date, sequence
            '''

        self.c.execute(sql)
        rows = self.c.fetchall()

        balances = dict()
        new_rows = []
        for sequence, bank, account, tran_date, description, amount, calc_balance in rows:
            acc = bank + account
            if acc in balances:
                balances[acc] += amount
            else:
                balances[acc] = amount

            if round(balances[acc], 2) != calc_balance:
                new_rows.append([sequence, bank, account, tran_date, description, amount, round(balances[acc], 2)])

        return new_rows, balances

    def update_balances(self, balances):
        sql = '''update tran
            set calc_balance = ?
            where sequence = ?
            '''

        for sequence, bank, account, tran_date, description, amount, calc_balance in balances:
            t = (calc_balance, sequence)
            self.c.execute(sql, t)
