from finance.dbutil import DBUtil

MONEY_FORMAT = "%11.2f"


class FinanceDb(DBUtil):
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

            key = tran_date + bankname + (MONEY_FORMAT % amount) + description
            if key in result and '-'.join([bankname, account]) not in result[key].split(','):
                result[key] = ','.join([result[key], '-'.join([bankname, account])])
            else:
                result[key] = '-'.join([bankname, account])
                
        return result
