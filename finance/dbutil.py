"""
Created on 16 Aug 2016

@author: adeelkhan
"""

import sqlite3
import logging

logger = logging.getLogger(__name__)


class DBUtil:
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        self.c = None
        self.conn = None
        
    def connect(self, database):
        self.conn = sqlite3.connect(database)
        self.conn.row_factory = sqlite3.Row
        self.c = self.conn.cursor()
        # self.conn.row_factory = sqlite3.Row
        return self.c
        
    def disconnect(self):
        self.conn.commit()
        self.conn.close()
    
    def nullToEmpty(self, value):
        if value is None:
            return ''
        return str(value)

    def nullToZero(self, value):
        if value is None:
            return 0.0
        if isinstance(value, str):
            if value.strip() == '':
                return 0.0
            else:
                return float(value.replace(',', ''))
        return value
    
    def sumNullables(self, values):
        total = 0
        for v in values:
            total += self.nullToZero(v)
        return total

    def query(self, sql, t):
        self.c.execute(sql, t)
        return self.c.fetchall()

    def checkExists(self, table, keys, values):
        where_clause = ' and '.join(["%s = ?" % k for k in keys])
        sql = "select count(*) from %s where %s" % (table, where_clause)
        self.c.execute(sql, tuple(values))
        result = self.c.fetchone()
        return result[0] > 0
    
    def getDictKey(self, mydict, keys):
        return '_'.join([str(mydict[k]) for k in keys])
    
    def convertRowsToDict(self, rows, keys, columns):
        all_columns = keys + columns
        column_count = len(all_columns)
        rows_dict = dict()
        for row in rows:
            row_dict = dict()
            for i in range(column_count):
                row_dict[all_columns[i]] = row[i] if all_columns[i] not in keys else str(row[i])
            rows_dict[self.getDictKey(row_dict, keys)] = row_dict
            #print self.getDictKey(row_dict, keys), row_dict
        return rows_dict
    
    def pivotDicts(self, data, rowkeys, columnkeys, value):
        result = dict()
        for row in data:
            rowkey = self.getDictKey(row, rowkeys)
            colkey = self.getDictKey(row, columnkeys)
            
            if rowkey not in result:
                result[rowkey] = dict()
            
            result[rowkey][colkey] = row[value]
        return result

    def loadDicts(self, table, keys, columns, filter_text="?=?", filter_values=(1, 1)):
        all_columns = keys + columns
        sql = "select %s from %s where %s" % (', '.join(all_columns), table, filter_text)
        self.c.execute(sql, tuple(filter_values))
        rows = self.c.fetchall()
    
        return self.convertRowsToDict(rows, keys, columns)
    
    def loadDictsFromQuery(self, keys, columns, sql, filter_values=None):
        if filter_values is None:
            self.c.execute(sql)
        else:
            self.c.execute(sql, tuple(filter_values))
        rows = self.c.fetchall()
    
        return self.convertRowsToDict(rows, keys, columns)
        
    def saveDict(self, table, keys, rec, updateOnly=False):
        columns = rec.keys()
        values = [rec[k] for k in columns]
        if keys is not None and self.checkExists(table, keys, [rec[k] for k in keys]):
            set_clause = ', '.join(["%s = ?" % k for k in columns if k not in keys])
            where_clause = ' and '.join(["%s = ?" % k for k in keys])
            sql = "update %s set %s where %s" % (table, set_clause, where_clause)
            #print sql
            updvals = [rec[k] for k in columns if k not in keys]
            updvals.extend([rec[k] for k in keys])
            #print updvals
            self.c.execute(sql, tuple(updvals))
        elif updateOnly:
            logger.warning("Value %s not found in table %s. Cannot update.",
                           '-'.join([rec[k] for k in keys]), table)
            return False
        else:
            sql = "insert into %s (%s) values (%s)" % (table, ', '.join(columns), ', '.join(['?'] * len(columns)))
            #print sql
            self.c.execute(sql, values)
        return True

