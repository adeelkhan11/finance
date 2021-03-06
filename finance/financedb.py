import logging

from finance.dbutil import DBUtil

logger = logging.getLogger(__name__)


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
        sql = """select sequence, bank, account, tran_date, description, amount, calc_balance
            from tran
            order by tran_date, sequence
            """

        self.c.execute(sql)
        rows = self.c.fetchall()

        balances = dict()
        new_rows = []
        for sequence, bank, account, tran_date, description, amount, calc_balance in rows:
            acc = bank + ' ' + account
            if acc in balances:
                balances[acc] += amount
            else:
                balances[acc] = amount

            if round(balances[acc], 2) != calc_balance:
                new_rows.append([sequence, bank, account, tran_date, description, amount, round(balances[acc], 2)])

        return new_rows, balances

    def calculate_monthly_balances(self):
        sql = """select sequence, bank, account, tran_date, description, amount, calc_balance
            from tran
            order by tran_date, sequence
            """

        self.c.execute(sql)
        rows = self.c.fetchall()

        running_balances = dict()
        monthly_balances = dict()
        current_month = None
        for sequence, bank, account, tran_date, description, amount, calc_balance in rows:
            if current_month is not None and tran_date[:7] != current_month:
                monthly_balances[current_month] = dict()
                for acc, balance in running_balances.items():
                    monthly_balances[current_month][acc] = round(balance, 2)
            acc = bank + ' ' + account
            if acc in running_balances:
                running_balances[acc] += amount
            else:
                running_balances[acc] = amount
            current_month = tran_date[:7]

        return monthly_balances

    def update_balances(self, balances):
        sql = """update tran
            set calc_balance = ?
            where sequence = ?
            """

        for sequence, bank, account, tran_date, description, amount, calc_balance in balances:
            t = (calc_balance, sequence)
            self.c.execute(sql, t)

    def get_rollovers(self, month):
        sql = """select head, new_alloc + rollover + adjustment + used as rollover
        from allocation
        where month = ?
        and length(head) > 1
        and new_alloc > 0
        """
        return self.loadDictsFromQuery(['head'], ['amount'], sql, [month])

    def get_expenses(self, month):
        sql = """select ?, ifnull(head, '92'), sum(amount)
            from (select head, amount from tran
            where tran_date like ?
            and account not in ('Business', 'Home Loan', 'Vertigo', 'Loan', '037179432768')
            UNION ALL
            select head, 0
            from allocation
            where used != 0
            and month = ?)
            group by ifnull(head, '92')"""
        return self.loadDictsFromQuery(['month', 'head'], ['used'], sql, [month, month + '%', month])

    def save_expenses(self, expenses, rollovers):
        keys = ['month', 'head']
        for rec in expenses.values():
            if rec['head'] in rollovers:
                rec['rollover'] = rollovers[rec['head']]['amount']
            self.saveDict('allocation', keys, rec)

    def calculate_parent_allocations(self, allocations):
        # reset parent allocations
        for parent_alloc in [a for a in allocations.values() if len(a['head']) == 1]:
            for item in ['new_alloc', 'rollover', 'adjustment', 'used']:
                parent_alloc[item] = 0

        for alloc in allocations.values():
            if len(alloc['head']) == 2:
                parent_alloc = allocations["%s_%s" % (alloc['month'], alloc['head'][:1])]
                for item in ['new_alloc', 'rollover', 'adjustment', 'used']:
                    parent_alloc[item] = self.sumNullables([parent_alloc[item], alloc[item]])

    def save_parent_allocations(self, allocations):
        for alloc in allocations.values():
            if len(alloc['head']) == 1:
                self.saveDict('allocation', ['month', 'head'], alloc)

    def read_last_interest_date(self, bank, account):
        # First find the last interest payment if any
        sql = """select max(tran_date)
            from tran
            where bank = ?
              and account = ?
              and description = 'AUTO_INTEREST'
            """
        t = (bank, account)
        self.c.execute(sql, t)
        row = self.c.fetchone()
        last_interest_date = None

        if row is not None and row[0] is not None:
            last_interest_date = row[0]
        else:
            sql = """select min(tran_date)
                from tran
                where bank = ?
                  and account = ?
                """
            t = (bank, account)
            self.c.execute(sql, t)
            row = self.c.fetchone()
            if row is not None and row[0] is not None:
                last_interest_date = row[0]
            else:
                # This account doesn't have any transactions
                logger.critical("Error: Cannot calculate interest. Account %s-%s doesn't have any transactions.",
                                bank, account)
                exit(1)

        return last_interest_date

    def get_transactions(self, bank, account):
        sql = """select sequence, bank, account, tran_date, description, amount
            from tran
            where bank = ?
              and account = ?
            order by tran_date, sequence
            """
        t = (bank, account)
        self.c.execute(sql, t)
        rows = self.c.fetchall()

        return rows
