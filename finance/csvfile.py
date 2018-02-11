import csv
import re
import logging

logger = logging.getLogger(__name__)


class CSVFile:
    def __init__(self, file_name):
        self.valuetable = []
        self.typetable = []
        self.file_name = file_name
        self.load(file_name)
        self.column_types = self.get_column_types(self.typetable)
        width = len(self.column_types)

        column_names = ['' for _ in range(width)]

        # Date column
        if self.column_types.count('date') == 1:
            col_index = self.column_types.index('date')
            column_names[col_index] = 'Date'
            try:
                date_col = [a[col_index] for a in self.valuetable]
            except IndexError:
                # print("A:", a)
                logger.debug("ValueTable:\n%s", "\n".join([', '.join(x) for x in self.valuetable]))
                raise
            file_order = self.check_order(date_col)
            if file_order == 'descending':
                self.valuetable.reverse()
        if self.column_types.count('text') == 1:
            column_names[self.column_types.index('text')] = 'Description'
        if self.column_types.count('decimal') == 1:
            column_names[self.column_types.index('decimal')] = 'Amount'

    def load(self, filename):
        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            rownum = 0
            for row in reader:
                if len(row) <= 2:
                    continue
                rownum += 1
                types = []
                values = []
                for v in row:
                    (value, valtype) = self.get_value_type(v)
                    values.append(value)
                    types.append(valtype)
                if rownum == 1 and len(frozenset(types)) == 1:
                    # ignore the header row
                    pass
                else:
                    self.valuetable.append(values)
                    self.typetable.append(types)

        logger.warning("%d rows read.", rownum)

    @staticmethod
    def check_order(lst):
        order = ''

        prev = None
        for a in lst:
            if prev is not None and a > prev:
                if order == 'descending':
                    return 'unknown'
                order = 'ascending'
            elif prev is not None and a < prev:
                if order == 'ascending':
                    return 'unknown'
                order = 'descending'
            prev = a

        return order

    @staticmethod
    def get_value_type(value):
        value = value.strip()
        valtype = ''

        if value == '':
            valtype = 'null'

        # Check for date type
        if re.match("([0-9]{4})-([01]?[0-9])-([0-3]?[0-9])$", value):
            valtype = 'date'
        m = re.match("([0-3]?[0-9])/([01]?[0-9])/([0-9]{4})$", value)
        if m:
            value = ("%s-%s-%s" % (m.group(3), m.group(2), m.group(1)))
            valtype = 'date'
        if valtype != '':
            return value, valtype

        # Check for numeric type
        if re.match("[+\-]?[0-9]*$", value):
            valtype = 'integer'
        if re.match("[+\-]?[0-9]*\.[0-9]*$", value):
            valtype = 'decimal'

        if valtype == '':
            valtype = 'text'

        return value, valtype

    @classmethod
    def get_column_types(cls, typetable):
        column_types = []
        pivottypes = cls._get_pivot(typetable)

        for row in pivottypes:
            collapsed_types = frozenset(row)

            nullable = ''
            coltype = 'text'
            if 'text' in collapsed_types:
                coltype = 'text'
            elif 'integer' in collapsed_types and 'decimal' in collapsed_types and len(collapsed_types) == 2:
                coltype = 'decimal'
            elif len(collapsed_types - frozenset(['null'])) > 1:
                coltype = 'text'
            elif 'date' in collapsed_types:
                coltype = 'date'
            elif 'integer' in collapsed_types:
                coltype = 'integer'
            elif 'decimal' in collapsed_types:
                coltype = 'decimal'

            if 'null' in collapsed_types:
                if len(collapsed_types) > 1:
                    nullable = 'nullable '
                else:
                    coltype = 'null'

            column_types.append(nullable + coltype)

        return column_types

    @staticmethod
    def _get_pivot(tbl):
        newtbl = []
        width = 0
        for row in tbl:
            if len(row) > width:
                width = len(row)
        for i in range(width):
            newtbl.append([])
        for row in tbl:
            for i in range(len(row)):
                newtbl[i].append(row[i])

        return newtbl
