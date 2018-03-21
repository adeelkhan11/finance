import logging

from finance.financedb import FinanceDB

logger = logging.getLogger(__name__)


class DBTable:
    def __init__(self, db, table_name, keys, columns, order_by, **kwargs):
        self._db = db
        self._table_name = table_name
        self._keys = keys
        self._columns = columns
        self._order_by = order_by
        # These are columns that are automatically generated by the database
        self._auto_generate_columns = kwargs.get('auto_generate_columns')
        self._where = kwargs.get('where')
        self._key_values = None
        self._update_count = 0
        self._insert_count = 0

    def __iter__(self):
        """Fetch rows from the table."""
        cursor = self.select()

        for row in cursor:
            yield row

    @property
    def update_count(self):
        """The number of records updated in this session."""
        return self._update_count

    @property
    def insert_count(self):
        """The number of records inserted in this session."""
        return self._insert_count

    def select(self, **kwargs):
        """Fetch data from the table and return a cursor.

        Keyword arguments:
        columns -- subset of columns to fetch (default all columns)
        where -- where clause to filter the result
        order_by -- list of column names with optional direction to sort by
        """
        # keys = kwargs.get('keys', self._keys)
        columns = kwargs.get('columns', self._keys + self._columns)
        order_by = kwargs.get('order_by', self._order_by)
        where = kwargs.get('where', self._where)
        t = kwargs.get('t')

        sql = """
            SELECT {}
            FROM {}
            {}
            {}""".format(', '.join(columns),
                         self._table_name,
                         '' if where is None else 'WHERE {}'.format(where),
                         '' if order_by is None else 'ORDER BY {}'.format(', '.join(order_by)))

        c = self._db.conn.cursor()
        if t is None:
            cursor = c.execute(sql)
        else:
            cursor = c.execute(sql, t)

        return cursor

    def check_exists(self, row_dict):
        """Check the supplied row exists in the table based on the primary key."""
        if self._keys is not None and self._key_values is None:
            # build dictionary of unique column values for lookup to determine update or insert
            cursor = self.select(columns=self._keys)
            self._key_values = set([':'.join([str(c) for c in r]) for r in cursor])
            logger.debug('{} unique keys loaded.'.format(len(self._key_values)))
            for i, key in enumerate(self._key_values):
                if i > 3:
                    break
                logger.debug('Key: {}'.format(key))
        key = ':'.join([str(row_dict[c]) for c in self._keys])
        logger.debug('New key: {}'.format(key))

        return False if self._keys is None else key in self._key_values

    def save(self, row_dict):
        """Save the supplied row to the table."""
        c = self._db.conn.cursor()
        if self._keys is not None and self.check_exists(row_dict):
            update_columns = frozenset(self._columns)
            update_keys = frozenset(self._keys)
            if self._auto_generate_columns is not None:
                update_columns -= frozenset(self._auto_generate_columns)
                update_keys -= frozenset(self._auto_generate_columns)

            sql = """\
                UPDATE {}
                SET {}
                WHERE {}""".format(self._table_name,
                                   ', '.join(['{} = ?'.format(c) for c in update_columns if c in row_dict]),
                                   ' AND '.join(['{} = ?'.format(c) for c in update_keys]))
            t = tuple([row_dict.get(c) for c in list([c for c in update_columns if c in row_dict]) + list(update_keys)])
            self._update_count += 1
        else:
            insert_columns = frozenset(self._keys + self._columns)
            if self._auto_generate_columns is not None:
                insert_columns -= frozenset(self._auto_generate_columns)
            sql = """\
                INSERT INTO {} ({})
                VALUES ({})""".format(self._table_name,
                                      ', '.join(insert_columns),
                                      ', '.join(['?'] * len(insert_columns)))
            t = tuple([row_dict.get(c) for c in insert_columns])
            self._insert_count += 1
        # print(sql)
        # print(t)
        c.execute(sql, t)


class Tran(DBTable):
    def __init__(self, db):
        super().__init__(db, 'tran', ('bank', 'account', 'tran_date', 'description', 'amount'),
                         ('sequence', 'balance',
                          'file_name', 'file_sequence', 'calc_balance', 'head', 'source', 'notes'),
                         ('tran_date', 'sequence'),
                         auto_generate_columns=('sequence',))

        self._trans_accounts = None

    def get_accounts_with_transaction(self, row_dict):
        tran_key_columns = ('tran_date', 'description', 'amount')
        bank_account_columns = ('bank', 'account')
        if self._trans_accounts is None:
            # build dictionary of unique column values for lookup to determine update or insert
            cursor = self.select(columns=('bank', 'account', 'tran_date', 'description', 'amount'))
            self._trans_accounts = dict()
            for r in cursor:
                key = ':'.join([str(r[c]) for c in tran_key_columns])
                bank_account = ':'.join([r[c] for c in bank_account_columns])
                if key not in self._trans_accounts:
                    self._trans_accounts[key] = list()
                self._trans_accounts[key].append(bank_account)
            logger.debug('{} unique keys loaded.'.format(len(self._trans_accounts)))
            for i, key in enumerate(self._trans_accounts.keys()):
                if i > 3:
                    break
                logger.debug('Key: {}'.format(key))
        key = ':'.join([str(row_dict[c]) for c in tran_key_columns])
        logger.debug('New key: {}'.format(key))

        return self._trans_accounts[key] if key in self._trans_accounts else list()


def main():
    from finance import logutil
    #    logging.lastResort = None
    _ = logutil.setup_logging()

    db = FinanceDB()
    _ = db.connect('finance.db')

    tran = Tran(db)
    for i, row in enumerate(tran):
        print(dict(row))
        print([x for x in row])
        print(row[0])

        j = dict(row)

        del j['head']
        tran.save(j)
        j = dict(row)
        j['amount'] = 7.77
        tran.save(j)

        if i > 2:
            break
    tran.save(dict(tran_date='2018-02-23',
                   description='Test transaction',
                   bank='Test',
                   account='Test Account',
                   amount=500.25,
                   file_name='test',
                   file_sequence=7))
    db.disconnect()


if __name__ == '__main__':
    main()
